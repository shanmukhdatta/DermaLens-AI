"""Leakage audit tests use synthetic fixture images only."""
from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from services.learning.leakage_audit import DatasetRecord, audit_dataset


def _create(folder: Path, name: str, *, pattern: int) -> None:
    image = Image.new("RGB", (40, 40))
    for y in range(40):
        for x in range(40):
            image.putpixel((x, y), ((x * 3 + pattern) % 256, (y * 5) % 256, x + y))
    image.save(folder / name)


def _row(path: str, split: str, subject: str | None, source: str = "real") -> DatasetRecord:
    return DatasetRecord(path, split, "Acne", source, subject)  # type: ignore[arg-type]


def test_exact_cross_split_duplicate_detected(tmp_path: Path) -> None:
    _create(tmp_path, "train.png", pattern=1)
    (tmp_path / "test.png").write_bytes((tmp_path / "train.png").read_bytes())
    _create(tmp_path, "cal.png", pattern=4)
    outcome = audit_dataset([
        _row("train.png", "train", "group-a"),
        _row("test.png", "test", "group-b"),
        _row("cal.png", "calibration", "group-c"),
    ], tmp_path)
    assert outcome.exact_cross_split_pairs == 1
    assert not outcome.independent_test_cleared
    assert "EXACT_IMAGE_DUPLICATES_CROSS_SPLIT" in outcome.warnings


def test_unknown_groups_and_synthetic_cannot_pass(tmp_path: Path) -> None:
    _create(tmp_path, "one.png", pattern=1)
    report = audit_dataset([_row("one.png", "test", None, "synthetic")], tmp_path)
    assert report.missing_subject_groups == 1
    assert not report.independent_test_cleared
    assert "UNKNOWN_SUBJECT_IDENTITY_NOT_PATIENT_INDEPENDENT" in report.warnings


def test_reject_escaping_root_and_bad_threshold(tmp_path: Path) -> None:
    _create(tmp_path, "one.png", pattern=1)
    with pytest.raises(ValueError, match="relative"):
        audit_dataset([_row("../one.png", "test", "x")], tmp_path)
    with pytest.raises(ValueError, match="Hamming"):
        audit_dataset([_row("one.png", "test", "x")], tmp_path, hamming_threshold=8)


def test_known_subject_cross_split_rejected(tmp_path: Path) -> None:
    _create(tmp_path, "one.png", pattern=1)
    _create(tmp_path, "two.png", pattern=45)
    result = audit_dataset([
        _row("one.png", "train", "same-patient"),
        _row("two.png", "test", "same-patient"),
    ], tmp_path)
    assert result.cross_split_subject_groups == 1
    assert not result.independent_test_cleared
