"""Independent-image dataset integrity audit: exact and near-duplicate leakage.

Reports potential visual duplicates for human review. Image similarity is never
used to invent patient identities or clinician ground-truth labels.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from PIL import Image, ImageOps

MAX_RECORDS = 250_000
MAX_IMAGE_BYTES = 20 * 1024 * 1024
MAX_REVIEW_PAIRS = 100_000
SPLITS = frozenset({"train", "calibration", "validation", "test"})
SOURCES = frozenset({"real", "synthetic"})


@dataclass(frozen=True)
class DatasetRecord:
    relative_path: str
    split: Literal["train", "calibration", "validation", "test"]
    label: str
    source: Literal["real", "synthetic"]
    subject_group: str | None = None


@dataclass(frozen=True)
class AuditIssue:
    code: str
    image_pair_hash: str | None = None


@dataclass(frozen=True)
class DatasetAudit:
    records: int
    split_counts: dict[str, int]
    real_records: int
    missing_subject_groups: int
    cross_split_subject_groups: int
    exact_cross_split_pairs: int
    possible_near_cross_split_pairs: int
    review_pair_tokens: tuple[str, ...]
    warnings: tuple[str, ...]
    possible_phash_cross_split_pairs: int = 0

    @property
    def independent_test_cleared(self) -> bool:
        """Conservative structural signal only, NOT clinical validation."""
        return (
            self.split_counts.get("test", 0) > 0
            and self.split_counts.get("calibration", 0) > 0
            and self.missing_subject_groups == 0
            and self.cross_split_subject_groups == 0
            and self.exact_cross_split_pairs == 0
            and self.possible_near_cross_split_pairs == 0
            and self.possible_phash_cross_split_pairs == 0
            and self.real_records == self.records
        )


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_dhash(raw: bytes) -> int:
    """64-bit dHash canonicalized across eight image orientations."""
    with Image.open(BytesIO(raw)) as image:
        image.load()
        base = ImageOps.exif_transpose(image).convert("L")
        hashes = []
        for mirror in (False, True):
            oriented = ImageOps.mirror(base) if mirror else base
            for rotation in (0, 90, 180, 270):
                resized = oriented.rotate(rotation, expand=True).resize(
                    (9, 8), Image.Resampling.BILINEAR
                )
                pixels = list(resized.getdata())
                value = 0
                for y in range(8):
                    for x in range(8):
                        value = (value << 1) | int(pixels[y * 9 + x] > pixels[y * 9 + x + 1])
                hashes.append(value)
    return min(hashes)


def _phash_single(image: Image.Image) -> int:
    """64-bit low-frequency perceptual hash, excluding DC for its threshold.

    Median DCT coefficients are robust to moderate global illumination changes.
    Similarity indicates a candidate duplicate; it does NOT establish identity.
    """
    gray = np.asarray(
        image.convert("L").resize((32, 32), Image.Resampling.BILINEAR),
        dtype=np.float32,
    )
    coefficients = cv2.dct(gray)[:8, :8].ravel()
    threshold = float(np.median(coefficients[1:]))
    result = 0
    for value in coefficients:
        result = (result << 1) | int(float(value) > threshold)
    return result


def _canonical_phash(raw: bytes) -> int:
    """Orientation-robust pHash, independent of gradient-based dHash."""
    with Image.open(BytesIO(raw)) as image:
        image.load()
        base = ImageOps.exif_transpose(image).convert("RGB")
        variants = []
        for mirror in (False, True):
            oriented = ImageOps.mirror(base) if mirror else base
            for degrees in (0, 90, 180, 270):
                variants.append(_phash_single(oriented.rotate(degrees, expand=True)))
    return min(variants)


def _near_pairs(
    hashes: list[int],
    rows: list[DatasetRecord],
    digests: list[str],
    threshold: int,
) -> set[tuple[int, int]]:
    """Exact <=7-bit candidate generation with independent 8-byte buckets."""
    buckets: dict[tuple[int, int], list[int]] = defaultdict(list)
    pairs: set[tuple[int, int]] = set()
    for index, value in enumerate(hashes):
        candidates: set[int] = set()
        for segment in range(8):
            chunk = (value >> (segment * 8)) & 255
            candidates.update(buckets[(segment, chunk)])
            buckets[(segment, chunk)].append(index)
        for previous in candidates:
            if rows[previous].split == rows[index].split:
                continue
            if digests[previous] == digests[index]:
                continue
            if (value ^ hashes[previous]).bit_count() <= threshold:
                pairs.add((previous, index))
                if len(pairs) > MAX_REVIEW_PAIRS:
                    raise ValueError(
                        "Too many near-duplicate review pairs; split audit into smaller batches"
                    )
    return pairs


def _safe_file(root: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("Dataset paths must be relative to the dataset root")
    real_root = root.resolve(strict=True)
    candidate = (real_root / relative).resolve(strict=True)
    if not candidate.is_relative_to(real_root) or not candidate.is_file():
        raise ValueError("Dataset entry escapes the approved image root")
    if candidate.stat().st_size > MAX_IMAGE_BYTES or candidate.stat().st_size == 0:
        raise ValueError("Dataset image outside size limits")
    return candidate


def _pair_token(one: str, two: str) -> str:
    """A nonreversible identifier for auditing without exposing filenames."""
    return hashlib.sha256(("|".join(sorted((one, two)))).encode()).hexdigest()[:16]


def audit_dataset(
    rows: list[DatasetRecord], root: Path, *, hamming_threshold: int = 5
) -> DatasetAudit:
    """Check structural integrity and surface cross-split potential leakage.

    Hash matches indicate potential duplicate images, not necessarily the
    same person; close similarity is a review flag, not an automatic merge.
    """
    if not rows or len(rows) > MAX_RECORDS:
        raise ValueError("Manifest must contain 1..250000 records")
    if not 0 <= hamming_threshold <= 7:
        raise ValueError("Hamming threshold must be within 0..7")
    seen_paths: set[str] = set()
    splits: dict[str, int] = defaultdict(int)
    subjects: dict[str, set[str]] = defaultdict(set)
    digest_groups: dict[str, list[int]] = defaultdict(list)
    hashes: list[int] = []
    phashes: list[int] = []
    digests: list[str] = []
    absent = 0
    real_count = 0
    for idx, row in enumerate(rows):
        if row.relative_path in seen_paths:
            raise ValueError("Repeated manifest path (potential split duplication)")
        seen_paths.add(row.relative_path)
        if row.split not in SPLITS or row.source not in SOURCES or not row.label:
            raise ValueError("Invalid split, source or label")
        if row.source == "real":
            real_count += 1
        if row.subject_group is None or not row.subject_group.strip():
            absent += 1
        else:
            subjects[row.subject_group].add(row.split)
        splits[row.split] += 1
        image_bytes = _safe_file(root, row.relative_path).read_bytes()
        digest = _digest(image_bytes)
        digests.append(digest)
        digest_groups[digest].append(idx)
        try:
            hashes.append(_canonical_dhash(image_bytes))
            phashes.append(_canonical_phash(image_bytes))
        except (OSError, ValueError, Image.DecompressionBombError) as exc:
            raise ValueError("Invalid image in dataset manifest") from exc
    cross_subjects = sum(len(group_splits) > 1 for group_splits in subjects.values())
    exact_pairs: set[tuple[int, int]] = set()
    for ids in digest_groups.values():
        for i, left in enumerate(ids):
            for right in ids[i + 1 :]:
                if rows[left].split != rows[right].split:
                    exact_pairs.add((left, right))
                    if len(exact_pairs) > MAX_REVIEW_PAIRS:
                        raise ValueError(
                            "Too many exact duplicate pairs; split audit into smaller batches"
                        )
    potential = _near_pairs(hashes, rows, digests, hamming_threshold)
    perceptual = _near_pairs(phashes, rows, digests, hamming_threshold)
    combined = potential | perceptual
    if len(combined) > MAX_REVIEW_PAIRS:
        raise ValueError("Too many duplicate review pairs for bounded reporting")
    tokens = tuple(
        sorted(
            {
                _pair_token(digests[a] + ":" + str(a), digests[b] + ":" + str(b))
                for a, b in exact_pairs | combined
            }
        )
    )
    warnings: list[str] = []
    if absent:
        warnings.append("UNKNOWN_SUBJECT_IDENTITY_NOT_PATIENT_INDEPENDENT")
    if cross_subjects:
        warnings.append("SUBJECT_GROUP_CROSSES_SPLITS")
    if exact_pairs:
        warnings.append("EXACT_IMAGE_DUPLICATES_CROSS_SPLIT")
    if potential:
        warnings.append("VISUAL_SIMILARITY_REQUIRES_MANUAL_REVIEW")
    if perceptual:
        warnings.append("PHASH_VISUAL_SIMILARITY_REQUIRES_MANUAL_REVIEW")
    if real_count != len(rows):
        warnings.append("SYNTHETIC_DATA_NOT_INDEPENDENT_CLINICAL_VALIDATION")
    if not splits.get("test") or not splits.get("calibration"):
        warnings.append("MISSING_INDEPENDENT_TEST_OR_CALIBRATION_SPLIT")
    return DatasetAudit(
        records=len(rows),
        split_counts=dict(sorted(splits.items())),
        real_records=real_count,
        missing_subject_groups=absent,
        cross_split_subject_groups=cross_subjects,
        exact_cross_split_pairs=len(exact_pairs),
        possible_near_cross_split_pairs=len(combined),
        possible_phash_cross_split_pairs=len(perceptual),
        review_pair_tokens=tokens,
        warnings=tuple(warnings),
    )
