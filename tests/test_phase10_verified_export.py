"""Synthetic-fixture checks for the private, checksum-verified prediction exporter."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from scripts import export_verified_predictions as exporter
from services.cv.artifacts import VerifiedArtifacts
from services.cv.ports import RawPrediction

LABELS = (
    "Acne", "Fungal_Infection", "Hyperpigmentation",
    "Normal_Skin", "Skin_Cancer", "Vitiligo",
)


class FixtureRuntime:
    def __init__(self, version: str = "fixture-v1") -> None:
        self.version = version

    @property
    def ready(self) -> bool:
        return True

    def predict(self, image: object) -> RawPrediction:
        import numpy as np

        assert isinstance(image, np.ndarray)
        assert image.shape == (1, 224, 224, 3)
        assert image.dtype == np.float32
        return RawPrediction(
            model_id="fixture-only", model_version=self.version,
            ordered_labels=LABELS, probabilities=(0.9, 0.02, 0.02, 0.02, 0.02, 0.02),
        )


def setup_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    root = tmp_path / "private"
    root.mkdir()
    image = root / "fixture.jpg"
    Image.new("RGB", (300, 300), (80, 60, 110)).save(image)
    checkpoint = tmp_path / "fake-checkpoint.keras"
    checkpoint.write_bytes(b"FAKE DATA; NOT A MODEL")
    sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    approved = tmp_path / "permission.json"
    approved.write_text(json.dumps({
        "rights_verified": True, "labels_independently_verified": True,
        "locked_test_split": True, "evaluation_id": "fixture",
        "dataset_provenance": "synthetic test", "permission_reference": "fictional",
        "label_method": "unit test only", "checkpoint_sha256": sha,
    }), encoding="utf-8")
    index = tmp_path / "index.csv"
    record = {
        "example_id": "fictional-example", "subject_id": "fictional-subject",
        "content_sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
        "split": "test", "source": "real", "label": LABELS[0],
        "skin_tone_group": "not-recorded", "device_group": "fixture-device",
        "relative_image_path": "fixture.jpg",
    }
    with index.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=sorted(exporter.INDEX_COLUMNS))
        writer.writeheader()
        writer.writerow(record)
    artifacts = VerifiedArtifacts(
        model_id="fixture-only", version="fixture-v1", status="candidate",
        checkpoint_path=checkpoint, label_map_path=tmp_path / "label_map.json",
        ordered_labels=LABELS, custom_objects=(),
    )
    monkeypatch.setattr(exporter, "verify_artifacts", lambda *args: artifacts)
    return {
        "model_manifest": tmp_path / "not-real-manifest.json", "checkpoint": checkpoint,
        "label_map": artifacts.label_map_path, "dataset_manifest": approved,
        "index_path": index, "image_root": root, "output": tmp_path / "result.csv",
    }


def test_export_is_private_and_path_free(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    args = setup_fixture(tmp_path, monkeypatch)
    result = exporter.export_predictions(**args, runtime=FixtureRuntime())
    assert result == 1
    with args["output"].open(newline="", encoding="utf-8") as source:
        records = list(csv.DictReader(source))
    assert len(records) == 1
    assert "relative_image_path" not in records[0]
    assert "prob_0" in records[0] and records[0]["prob_0"] == "0.9"
    with pytest.raises(FileExistsError):
        exporter.export_predictions(**args, runtime=FixtureRuntime())


def test_reject_path_escape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    args = setup_fixture(tmp_path, monkeypatch)
    rows = exporter.read_private_index(args["index_path"])
    rows[0]["relative_image_path"] = "../fake-checkpoint.keras"
    with args["index_path"].open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=sorted(exporter.INDEX_COLUMNS))
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="escapes"):
        exporter.export_predictions(**args, runtime=FixtureRuntime())


def test_reject_permission_or_checkpoint_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    args = setup_fixture(tmp_path, monkeypatch)
    permission = json.loads(args["dataset_manifest"].read_text())
    permission["locked_test_split"] = False
    args["dataset_manifest"].write_text(json.dumps(permission))
    with pytest.raises(ValueError, match="approval"):
        exporter.export_predictions(**args, runtime=FixtureRuntime())
    permission["locked_test_split"] = True
    permission["checkpoint_sha256"] = "a" * 64
    args["dataset_manifest"].write_text(json.dumps(permission))
    with pytest.raises(ValueError, match="checkpoint"):
        exporter.export_predictions(**args, runtime=FixtureRuntime())


def test_reject_runtime_version_mismatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    args = setup_fixture(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="version"):
        exporter.export_predictions(**args, runtime=FixtureRuntime("wrong-version"))
