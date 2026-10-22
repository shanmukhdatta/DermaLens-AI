"""Synthetic pHash leakage fixtures, no real patient images."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from services.learning.duplicate_audit import scan_splits


def _image(path: Path, *, seed: int, mirror: bool = False) -> None:
    rng = np.random.default_rng(seed)
    pixels = rng.integers(0, 255, (80, 110, 3), dtype=np.uint8)
    if mirror:
        pixels = pixels[:, ::-1]
    Image.fromarray(pixels).save(path, "PNG")


def _manifest(tmp_path: Path, items: list[tuple[str, str, str, str]]) -> Path:
    csvpath = tmp_path / "manifest.csv"
    with csvpath.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "example_id",
                "relative_path",
                "split",
                "source",
                "label",
                "subject_id",
            ],
        )
        writer.writeheader()
        for identifier, filename, split, subject in items:
            writer.writerow(
                {
                    "example_id": identifier,
                    "relative_path": filename,
                    "split": split,
                    "source": "fixture",
                    "label": "acne",
                    "subject_id": subject,
                }
            )
    return csvpath


def test_near_duplicates_across_splits_flagged_without_images_in_report(tmp_path: Path) -> None:
    _image(tmp_path / "a.png", seed=12)
    Image.open(tmp_path / "a.png").transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(
        tmp_path / "b.png", "PNG"
    )
    manifest = _manifest(
        tmp_path,
        [
            ("id-a", "a.png", "train", "subject-a"),
            ("id-b", "b.png", "test", "subject-b"),
        ],
    )
    report = scan_splits(manifest, tmp_path, distance_threshold=5)
    assert report["status"] == "REVIEW_REQUIRED"
    assert report["cross_split_near_candidates"]
    assert "relative_path" not in str(report)
    assert "a.png" not in str(report)


def test_exact_duplicate_and_patient_overlap_refused(tmp_path: Path) -> None:
    _image(tmp_path / "a.png", seed=20)
    (tmp_path / "b.png").write_bytes((tmp_path / "a.png").read_bytes())
    manifest = _manifest(
        tmp_path,
        [
            ("first", "a.png", "train", "subject-a"),
            ("second", "b.png", "test", "subject-b"),
        ],
    )
    with pytest.raises(ValueError, match="exact image leakage"):
        scan_splits(manifest, tmp_path)
    _image(tmp_path / "b.png", seed=30)
    shared = _manifest(
        tmp_path,
        [
            ("first", "a.png", "train", "shared"),
            ("second", "b.png", "test", "shared"),
        ],
    )
    with pytest.raises(ValueError, match="patient-level leakage"):
        scan_splits(shared, tmp_path)


def test_path_escape_rejected(tmp_path: Path) -> None:
    _image(tmp_path / "a.png", seed=8)
    manifest = _manifest(tmp_path, [("only", "../a.png", "test", "")])
    with pytest.raises(ValueError, match="relative image path"):
        scan_splits(manifest, tmp_path)
