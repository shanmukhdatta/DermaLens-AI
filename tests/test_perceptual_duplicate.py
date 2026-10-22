"""pHash complementary duplicate auditing on fictional generated photos only."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

from services.learning.leakage_audit import (
    DatasetRecord,
    _canonical_phash,
    audit_dataset,
)


def _sample() -> Image.Image:
    rng = np.random.default_rng(42)
    # Avoid clipping when brightness is increased, preserving source pattern.
    data = rng.integers(30, 170, size=(112, 132, 3), dtype=np.uint8)
    return Image.fromarray(data, mode="RGB")


def test_phash_alternative_encoding_and_brightness_cross_split(tmp_path: Path) -> None:
    sample = _sample()
    sample.save(tmp_path / "train.png")
    variant = ImageEnhance.Brightness(sample).enhance(1.08)
    variant.save(tmp_path / "test.png")
    (tmp_path / "cal.png").write_bytes((tmp_path / "test.png").read_bytes())
    # Distinct sources and subjects are a synthetic fixture, not actual patients.
    report = audit_dataset(
        [
            DatasetRecord("train.png", "train", "Acne", "real", "fixture-a"),
            DatasetRecord("test.png", "test", "Acne", "real", "fixture-b"),
        ],
        tmp_path,
    )
    assert report.possible_phash_cross_split_pairs >= 1
    assert report.possible_near_cross_split_pairs >= report.possible_phash_cross_split_pairs
    assert "PHASH_VISUAL_SIMILARITY_REQUIRES_MANUAL_REVIEW" in report.warnings
    assert not report.independent_test_cleared
    # No original path or photo data is published in review pair identifiers.
    assert "train.png" not in str(report.review_pair_tokens)
    assert "test.png" not in str(report.review_pair_tokens)


def test_phash_orientation_invariance(tmp_path: Path) -> None:
    original = _sample()
    original.save(tmp_path / "a.png")
    original.transpose(Image.Transpose.ROTATE_90).save(tmp_path / "b.png")
    assert _canonical_phash((tmp_path / "a.png").read_bytes()) == _canonical_phash(
        (tmp_path / "b.png").read_bytes()
    )
