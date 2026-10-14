"""Synthetic fixture regression tests for checkpoint-bound manual research review."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from services.learning.review_policy import evaluate_with_policy

LABELS = (
    "Acne", "Fungal_Infection", "Hyperpigmentation",
    "Normal_Skin", "Skin_Cancer", "Vitiligo",
)
COLUMNS = (
    "example_id", "subject_id", "content_sha256", "split", "source",
    "label", "model_version", "skin_tone_group", "device_group",
    *(f"prob_{i}" for i in range(6)),
)


def fixtures(root: Path) -> dict[str, Path]:
    old = root / "old-fake.keras"
    new = root / "new-fake.keras"
    old.write_bytes(b"NOT a trained checkpoint old")
    new.write_bytes(b"NOT a trained checkpoint new")
    mapping = root / "label_map.json"
    mapping.write_text(json.dumps({str(i): label for i, label in enumerate(LABELS)}))
    policy = root / "policy.json"
    policy.write_text(json.dumps({
        "policy_version": "1",
        "baseline_version": "old-fixture",
        "candidate_version": "new-fixture",
        "dataset_id": "synthetic-fixture-only",
        "baseline_sha256": hashlib.sha256(old.read_bytes()).hexdigest(),
        "candidate_sha256": hashlib.sha256(new.read_bytes()).hexdigest(),
        "data_rights_reviewed": True,
        "label_quality_reviewed": True,
        "locked_test_split": True,
        "minimum_class_support": 5,
        "minimum_macro_f1_improvement": 0.0,
        "maximum_ece_increase": 0.0,
    }))
    baseline = root / "old.csv"
    candidate = root / "new.csv"

    def write(path: Path, model: str) -> None:
        with path.open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=COLUMNS)
            writer.writeheader()
            for i in range(30):
                index = i % 6
                scores = ["0.02"] * 6
                scores[index] = "0.9"
                writer.writerow({
                    "example_id": f"fictional-{i}",
                    "subject_id": f"fictional-subject-{i}",
                    "content_sha256": f"{i:064x}",
                    "split": "test",
                    "source": "real",
                    "label": LABELS[index],
                    "model_version": model,
                    "skin_tone_group": "not-recorded",
                    "device_group": "not-recorded",
                    **{f"prob_{j}": scores[j] for j in range(6)},
                })
    write(baseline, "old-fixture")
    write(candidate, "new-fixture")
    return {
        "baseline_path": baseline, "candidate_path": candidate,
        "label_map_path": mapping, "baseline_checkpoint": old,
        "candidate_checkpoint": new, "policy_path": policy,
    }


def test_same_fixture_only_qualifies_for_manual_review(tmp_path: Path) -> None:
    report = evaluate_with_policy(**fixtures(tmp_path))
    assert report["decision"] == "AWAITING_INDEPENDENT_REVIEW"
    assert report["clinical_release_approved"] is False
    assert report["auto_deployment_allowed"] is False
    assert report["subjects_on_test"] == 30
    assert report["reasons"] == []
    assert "fictional-subject" not in json.dumps(report)


def test_changed_artifact_and_missing_rights_are_rejected(tmp_path: Path) -> None:
    config = fixtures(tmp_path)
    config["candidate_checkpoint"].write_bytes(b"changed fake checkpoint")
    with pytest.raises(ValueError, match="Checkpoint"):
        evaluate_with_policy(**config)
    config = fixtures(tmp_path)
    policy = json.loads(config["policy_path"].read_text())
    policy["label_quality_reviewed"] = False
    config["policy_path"].write_text(json.dumps(policy))
    with pytest.raises(ValueError, match="provenance"):
        evaluate_with_policy(**config)


def test_declared_improvement_policy_can_block_candidate(tmp_path: Path) -> None:
    config = fixtures(tmp_path)
    policy = json.loads(config["policy_path"].read_text())
    policy["minimum_macro_f1_improvement"] = 0.05
    config["policy_path"].write_text(json.dumps(policy))
    result = evaluate_with_policy(**config)
    assert result["decision"] == "BLOCKED"
    assert "BELOW_DECLARED_MACRO_F1_IMPROVEMENT" in result["reasons"]
