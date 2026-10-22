"""Private image-to-prediction CSV integration tests; no clinical data or weights."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image

from scripts.build_private_prediction_table import collect_predictions, write_results
from services.cv.ports import RawPrediction

LABELS = ("acne", "fungal infection", "hyperpigmentation", "normal skin", "skin cancer", "vitiligo")
FIELDS = (
    "image_path",
    "example_id",
    "subject_id",
    "split",
    "source",
    "label",
    "skin_tone_group",
    "device_group",
)


class FixtureRuntime:
    @property
    def ready(self) -> bool:
        return True

    def predict(self, rgb_float32_batch: NDArray[np.float32]) -> RawPrediction:
        assert rgb_float32_batch.shape == (1, 224, 224, 3)
        assert rgb_float32_batch.dtype == np.float32
        return RawPrediction(
            model_id="fictional-fixture-only",
            model_version="fixture-v1",
            ordered_labels=LABELS,
            probabilities=(0.75, 0.05, 0.05, 0.05, 0.05, 0.05),
        )


def fixtures(
    tmp_path: Path, *, leak_subject: bool = False, bad_path: bool = False
) -> tuple[Path, Path]:
    root = tmp_path / "private-inputs"
    root.mkdir()
    Image.new("RGB", (256, 256), color=(50, 100, 180)).save(root / "a.png")
    Image.new("RGB", (256, 256), color=(170, 100, 30)).save(root / "b.png")
    manifest = tmp_path / "private-manifest.csv"
    examples = [
        dict(
            zip(
                FIELDS,
                (
                    "a.png", "original-a", "person-one", "train",
                    "fixture", "acne", "unknown", "unknown",
                ),
                strict=True,
            )
        ),
        dict(zip(FIELDS, (
            "../private-inputs/b.png" if bad_path else "b.png", "original-b",
            "person-one" if leak_subject else "person-two",
            "test", "fixture", "acne", "unknown", "unknown"
        ), strict=True)),
    ]
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(examples)
    return root, manifest


def test_private_csv_is_real_runtime_connected_and_pseudonymized(tmp_path: Path) -> None:
    root, manifest = fixtures(tmp_path)
    rows = collect_predictions(manifest, root, b"private fixture key" * 4, FixtureRuntime(), LABELS)
    assert len(rows) == 2
    assert rows[0]["example_id"] != "original-a"
    assert rows[0]["subject_id"] != "person-one"
    assert "image_path" not in rows[0]
    assert rows[0]["content_sha256"] != rows[1]["content_sha256"]
    csv_path, report_path = tmp_path / "out" / "predictions.csv", tmp_path / "out" / "report.json"
    report: dict[str, Any] = write_results(rows, LABELS, csv_path, report_path)
    assert report["clinical_use_validated"] is False
    assert report["metrics"]["n"] == 1
    assert "original-a" not in csv_path.read_text(encoding="utf-8")
    assert "person-one" not in csv_path.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_results(rows, LABELS, csv_path, report_path)


def test_split_leakage_rejects_entire_batch_before_writes(tmp_path: Path) -> None:
    root, manifest = fixtures(tmp_path, leak_subject=True)
    with pytest.raises(ValueError, match="Leakage"):
        collect_predictions(manifest, root, b"private fixture key" * 4, FixtureRuntime(), LABELS)


def test_relative_paths_cannot_escape_image_root(tmp_path: Path) -> None:
    root, manifest = fixtures(tmp_path, bad_path=True)
    with pytest.raises(ValueError, match="relative"):
        collect_predictions(manifest, root, b"private fixture key" * 4, FixtureRuntime(), LABELS)


def test_pseudonym_key_cannot_be_guessed_short(tmp_path: Path) -> None:
    root, manifest = fixtures(tmp_path)
    with pytest.raises(ValueError, match="32"):
        collect_predictions(manifest, root, b"short", FixtureRuntime(), LABELS)
