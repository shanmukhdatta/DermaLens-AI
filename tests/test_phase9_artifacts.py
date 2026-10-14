"""Artifact SHA and exact preprocessing checks with explicitly non-model fixture bytes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from services.cv.artifacts import preprocess_compatible, verify_artifacts


def make_artifact_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    checkpoint = tmp_path / "fictional-test-only.keras"
    checkpoint.write_bytes(b"this is not a trained model")
    labels = tmp_path / "label_map.json"
    labels.write_text(
        json.dumps(
            {
                "0": "Acne",
                "1": "Fungal_Infection",
                "2": "Hyperpigmentation",
                "3": "Normal_Skin",
                "4": "Skin_Cancer",
                "5": "Vitiligo",
            }
        )
    )
    def digest(file: Path) -> str:
        return hashlib.sha256(file.read_bytes()).hexdigest()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "source_repository": "https://github.com/shanmukhdatta/Facial_Skin_Diesease",
                "model_id": "test-fixture",
                "version": "0.0.1",
                "status": "candidate",
                "source_commit": "a" * 40,
                "framework": {
                    "name": "tensorflow-keras",
                    "python_version": "3.11",
                    "tensorflow_version": "test",
                    "keras_version": "test",
                },
                "preprocessing_version": "test-fixture",
                "checkpoint": {
                    "uri": "private://fixture",
                    "filename": checkpoint.name,
                    "sha256": digest(checkpoint),
                },
                "label_map": {
                    "uri": "private://fixture",
                    "filename": labels.name,
                    "sha256": digest(labels),
                    "count": 6,
                    "format": "index-to-class-json",
                },
                "input": {
                    "shape": [None, 224, 224, 3],
                    "color_space": "RGB",
                    "dtype": "float32",
                    "pixel_min": 0,
                    "pixel_max": 255,
                    "resize": "PIL_BILINEAR",
                    "normalization": "model_internal",
                },
                "output": {"shape": [None, 6], "class_count": 6, "kind": "softmax_probabilities"},
                "custom_objects": [],
            }
        )
    )
    return manifest, checkpoint, labels


def test_artifact_checksum_and_label_contract(tmp_path: Path) -> None:
    manifest, checkpoint, labels = make_artifact_fixture(tmp_path)
    model = verify_artifacts(manifest, checkpoint, labels)
    assert model.version == "0.0.1"
    assert model.ordered_labels[1] == "Fungal_Infection"
    checkpoint.write_bytes(b"modified mock checkpoint")
    with pytest.raises(ValueError, match="integrity"):
        verify_artifacts(manifest, checkpoint, labels)


def test_reject_changed_preprocessing(tmp_path: Path) -> None:
    manifest, checkpoint, labels = make_artifact_fixture(tmp_path)
    data = json.loads(manifest.read_text())
    data["input"]["normalization"] = "external_normalization"
    manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="preprocessing"):
        verify_artifacts(manifest, checkpoint, labels)


def test_research_compatible_input_shape_dtype_and_range() -> None:
    image = Image.new("RGB", (500, 320), (170, 88, 210))
    batch = preprocess_compatible(image)
    assert batch.shape == (1, 224, 224, 3)
    assert batch.dtype == np.float32
    assert np.array_equal(batch[0, 0, 0], np.array([170, 88, 210], dtype=np.float32))
