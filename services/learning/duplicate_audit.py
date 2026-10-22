"""Offline rights-aware image dataset split and near-duplicate audit.

Inputs are local permitted files referenced by a pseudonymous manifest.
Reports deliberately omit raw filenames and image pixels. Perceptual-hash
matches are *review candidates*, not proven duplicates or clinical outcomes.
"""

from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageOps

SPLITS = frozenset({"train", "calibration", "test"})
SOURCES = frozenset({"real", "synthetic", "fixture"})
REQUIRED = frozenset({"example_id", "relative_path", "split", "source", "label"})
MAX_IMAGES = 1500
MAX_IMAGE_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class ImageSignature:
    example_id: str
    split: str
    subject_id: str | None
    sha256_hex: str
    signatures: tuple[int, ...]


def _phash(image: Image.Image) -> int:
    tiny = np.asarray(
        image.convert("L").resize((32, 32), Image.Resampling.BILINEAR), dtype=np.float32
    )
    coeff = cv2.dct(tiny)[:8, :8]
    selected = coeff.flatten()
    median = float(np.median(selected[1:]))  # skip DC illumination
    result = 0
    for value in selected:
        result = (result << 1) | int(float(value) > median)
    return result


def _all_orientations(image: Image.Image) -> tuple[int, ...]:
    rgb = ImageOps.exif_transpose(image).convert("RGB")
    out: set[int] = set()
    for angle in (0, 90, 180, 270):
        rotated = rgb.rotate(angle, expand=True)
        out.add(_phash(rotated))
        out.add(_phash(ImageOps.mirror(rotated)))
    return tuple(sorted(out))


def _bounded_image(root: Path, relative: str) -> Path:
    if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("relative image path must stay within authorized root")
    path = root / relative
    if path.is_symlink() or not path.is_file():
        raise ValueError("image missing or symbolic-link traversal prohibited")
    if path.resolve().is_relative_to(root.resolve()) is False:
        raise ValueError("image outside authorized dataset root")
    if path.stat().st_size <= 0 or path.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError("unsupported image byte length")
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise ValueError("unsupported file extension")
    return path


def scan_splits(
    manifest_csv: Path, image_root: Path, *, distance_threshold: int = 5
) -> dict[str, Any]:
    """Flag visually close *cross-split* images; refuse exact/subject leakage.

    No patient IDs = no patient-level independence claim. Operator must review
    any near matches and decide if the test set remains independent.
    """
    if not 1 <= distance_threshold <= 12:
        raise ValueError("perceptual Hamming threshold must be 1..12")
    with manifest_csv.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError("manifest must declare example_id,relative_path,split,source,label")
        if {"patient_name", "email", "medical_record_number"} & set(reader.fieldnames):
            raise ValueError("raw direct identifiers are forbidden in evaluation manifest")
        rows = list(reader)
    if not rows or len(rows) > MAX_IMAGES:
        raise ValueError(f"audit supports 1..{MAX_IMAGES} images per batch")
    found_ids: set[str] = set()
    seen_subjects: dict[str, str] = {}
    found_hashes: dict[str, str] = {}
    signatures: list[ImageSignature] = []
    for row in rows:
        identifier = row["example_id"]
        split, source = row["split"], row["source"]
        if (
            not identifier
            or identifier in found_ids
            or split not in SPLITS
            or source not in SOURCES
        ):
            raise ValueError("duplicate example_id or invalid data split/source")
        if not row["label"]:
            raise ValueError("label cannot be empty")
        found_ids.add(identifier)
        subject = row.get("subject_id", "").strip() or None
        if subject:
            previous = seen_subjects.setdefault(subject, split)
            if previous != split:
                raise ValueError("patient-level leakage across evaluation splits")
        path = _bounded_image(image_root, row["relative_path"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        previous_split = found_hashes.setdefault(digest, split)
        if previous_split != split:
            raise ValueError("exact image leakage across evaluation splits")
        with Image.open(path) as img:
            if img.format not in {"JPEG", "PNG", "WEBP"} or getattr(img, "n_frames", 1) != 1:
                raise ValueError("animated or unsupported image")
            if min(img.size) < 32 or max(img.size) > 4096:
                raise ValueError("invalid image dimensions")
            signature = _all_orientations(img)
        signatures.append(
            ImageSignature(
                example_id=identifier,
                split=split,
                subject_id=subject,
                sha256_hex=digest,
                signatures=signature,
            )
        )
    near: list[dict[str, Any]] = []
    for index, left in enumerate(signatures):
        for right in signatures[index + 1 :]:
            if left.split == right.split:
                continue
            distance = min((a ^ b).bit_count() for a in left.signatures for b in right.signatures)
            if distance <= distance_threshold:
                near.append(
                    {
                        "example_a": left.example_id,
                        "example_b": right.example_id,
                        "distance": distance,
                        "splits": sorted((left.split, right.split)),
                        "disposition": "REQUIRES_MANUAL_IMAGE_REVIEW",
                    }
                )
    return {
        "status": "REVIEW_REQUIRED" if near else "HASH_SCREEN_PASSED_NOT_CLINICALLY_VALIDATED",
        "total_images": len(signatures),
        "total_real_images": sum(row["source"] == "real" for row in rows),
        "subject_id_coverage": sum(row.get("subject_id", "").strip() != "" for row in rows),
        "threshold_bits": distance_threshold,
        "cross_split_near_candidates": near[:1000],
        "truncated_candidates": len(near) > 1000,
        "warning": "pHash can miss edited duplicates and yield false positives; "
        "verify near pairs manually and separately audit patient provenance.",
    }
