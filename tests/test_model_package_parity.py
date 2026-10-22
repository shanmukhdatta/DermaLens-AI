"""Artifact/package and independent-predictor parity tests using fictional fixtures."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.package_trained_model import package_candidate
from services.cv.artifacts import verify_artifacts
from services.cv.parity import verify_prediction_parity
from services.cv.ports import RawPrediction

LABELS = (
    "Acne", "Fungal Infection", "Hyperpigmentation",
    "Normal Skin", "Skin Cancer", "Vitiligo",
)


def test_candidate_manifest_checksums_are_real_and_status_is_not_approved(tmp_path: Path) -> None:
    checkpoint = tmp_path / "weights.keras"
    mapping = tmp_path / "label_map.json"
    checkpoint.write_bytes(b"FICTIONAL CHECKPOINT - cannot be loaded as model")
    mapping.write_text(json.dumps({str(i): name for i, name in enumerate(LABELS)}))
    package = package_candidate(
        checkpoint, mapping,
        model_id="fixture-candidate", version="0.1.0", source_commit="a" * 40,
        training_run_id="fixture-only",
        python_version="3.11", tensorflow_version="2.16", keras_version="3",
    )
    assert package["status"] == "candidate"
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(package))
    result = verify_artifacts(path, checkpoint, mapping)
    assert result.ordered_labels == LABELS
    assert result.status == "candidate"
    checkpoint.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="integrity"):
        verify_artifacts(path, checkpoint, mapping)


def test_model_package_rejects_incorrect_labels(tmp_path: Path) -> None:
    checkpoint = tmp_path / "weights.keras"
    label = tmp_path / "label_map.json"
    checkpoint.write_bytes(b"fixture")
    label.write_text(json.dumps({str(i): "fictional" for i in range(6)}))
    with pytest.raises(ValueError, match="research taxonomy"):
        package_candidate(
            checkpoint, label, model_id="model", version="1.0.0",
            source_commit="b" * 40, training_run_id="fixture",
            python_version="3.11", tensorflow_version="2.16", keras_version="3",
        )


def test_parity_checks_versions_images_class_index_and_values() -> None:
    probabilities = (0.35, 0.12, 0.11, 0.10, 0.09, 0.23)
    pred = RawPrediction("fixture", "0.1.0", LABELS, probabilities)
    ref = {
        "image_sha256": "1" * 64,
        "checkpoint_sha256": "2" * 64,
        "source_commit": "3" * 40,
        "ordered_labels": list(LABELS),
        "probabilities": list(probabilities),
    }
    values = {
        "image_sha256": "1" * 64,
        "checkpoint_sha256": "2" * 64,
        "source_commit": "3" * 40,
    }
    result = verify_prediction_parity(ref, pred, **values)
    assert result["software_parity_verified"] is True
    assert result["clinical_accuracy_verified"] is False
    with pytest.raises(ValueError, match="source"):
        verify_prediction_parity(ref, pred, **{**values, "image_sha256": "0" * 64})
    with pytest.raises(ValueError, match="label indices"):
        verify_prediction_parity({**ref, "ordered_labels": list(LABELS[::-1])}, pred, **values)
    with pytest.raises(ValueError, match="parity"):
        verify_prediction_parity(
            {**ref, "probabilities": [0.4, 0.07, 0.11, 0.1, 0.09, 0.23]},
            pred,
            **values,
        )
