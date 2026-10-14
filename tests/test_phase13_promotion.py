"""Phase 13 fictional-data tests. These numbers are not trained model performance."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from services.learning.promotion import compare_candidates, load_review_policy

LABELS = (
    "Acne", "Fungal_Infection", "Hyperpigmentation",
    "Normal_Skin", "Skin_Cancer", "Vitiligo",
)
HEADERS = (
    "example_id", "subject_id", "content_sha256", "split", "source",
    "label", "model_version", "skin_tone_group", "device_group",
    *(f"prob_{i}" for i in range(6)),
)


def create_inputs(root: Path) -> dict[str, Path]:
    mapping = root / "label_map.json"
    mapping.write_text(json.dumps({str(i): label for i, label in enumerate(LABELS)}))
    old = root / "baseline-fake.keras"
    new = root / "candidate-fake.keras"
    old.write_bytes(b"fictional old artifact, not a model")
    new.write_bytes(b"fictional new artifact, not a model")
    policy = root / "review-policy.json"
    policy.write_text(json.dumps({
        "policy_version": "1",
        "baseline_model_version": "baseline-fictional",
        "candidate_model_version": "candidate-fictional",
        "baseline_checkpoint_sha256": hashlib.sha256(old.read_bytes()).hexdigest(),
        "candidate_checkpoint_sha256": hashlib.sha256(new.read_bytes()).hexdigest(),
        "evaluation_dataset_id": "fictional-test-only",
        "data_rights_reviewed": True,
        "label_quality_reviewed": True,
        "test_split_locked": True,
        "minimum_test_subjects": 30,
        "minimum_per_class_support": 5,
        "minimum_macro_f1_delta": 0.0,
        "maximum_ece_increase": 0.0,
        "maximum_per_class_recall_drop": 0.0,
    }))
    rows = []
    for i in range(36):
        truth = i % 6
        vector = ["0.02"] * 6
        vector[truth] = "0.9"
        rows.append({
            "example_id": f"not-real-{i}",
            "subject_id": f"fictional-subject-{i}",
            "content_sha256": f"{i:064x}", "split": "test", "source": "real",
            "label": LABELS[truth], "skin_tone_group": "not-recorded",
            "device_group": "not-recorded",
            **{f"prob_{j}": vector[j] for j in range(6)},
        })
    def write(path: Path, version: str, data: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=HEADERS)
            writer.writeheader()
            for record in data:
                writer.writerow({**record, "model_version": version})
    baseline = root / "baseline.csv"
    candidate = root / "candidate.csv"
    write(baseline, "baseline-fictional", rows)
    write(candidate, "candidate-fictional", rows)
    return {
        "baseline_csv": baseline, "candidate_csv": candidate,
        "baseline_checkpoint": old, "candidate_checkpoint": new,
        "label_map_path": mapping, "policy_path": policy,
    }


def test_model_promotion_is_never_automatic(tmp_path: Path) -> None:
    args = create_inputs(tmp_path)
    result = compare_candidates(**args)
    assert result["decision"] == "ELIGIBLE_FOR_MANUAL_RESEARCH_REVIEW"
    assert result["automated_model_promotion"] is False
    assert result["clinical_release_authorized"] is False
    assert result["independent_test_subjects"] == 36
    assert result["reasons"] == []
    assert "fictional-subject" not in json.dumps(result)
    assert "not-real-0" not in json.dumps(result)


def test_candidate_regression_blocks_research_review(tmp_path: Path) -> None:
    args = create_inputs(tmp_path)
    with args["candidate_csv"].open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for record in rows:
        if record["label"] == LABELS[0]:
            for index in range(6):
                record[f"prob_{index}"] = "0.02"
            record["prob_1"] = "0.9"
    with args["candidate_csv"].open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    result = compare_candidates(**args)
    assert result["decision"] == "BLOCKED"
    assert "MACRO_F1_REGRESSION" in result["reasons"]
    assert "PER_CLASS_RECALL_REGRESSION" in result["reasons"]


def test_different_labels_or_evaluation_subjects_block_comparison(tmp_path: Path) -> None:
    args = create_inputs(tmp_path)
    with args["candidate_csv"].open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    rows[-1]["subject_id"] = "different-test-subject"
    with args["candidate_csv"].open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="data provenance"):
        compare_candidates(**args)


def test_mismatched_artifact_or_unsigned_policy_rejected(tmp_path: Path) -> None:
    args = create_inputs(tmp_path)
    args["candidate_checkpoint"].write_bytes(b"tampered version")
    with pytest.raises(ValueError, match="checkpoint"):
        compare_candidates(**args)
    data = json.loads(args["policy_path"].read_text())
    data["data_rights_reviewed"] = False
    args["policy_path"].write_text(json.dumps(data))
    with pytest.raises(ValueError, match="human evaluation assurance"):
        load_review_policy(args["policy_path"])


def test_too_few_independent_subjects_blocks_review(tmp_path: Path) -> None:
    args = create_inputs(tmp_path)
    with args["baseline_csv"].open(newline="", encoding="utf-8") as file:
        baseline = list(csv.DictReader(file))
    with args["candidate_csv"].open(newline="", encoding="utf-8") as file:
        candidate = list(csv.DictReader(file))
    for record in [*baseline, *candidate]:
        record["subject_id"] = f"subject-{int(record['example_id'].split('-')[-1]) % 10}"
    for path, rows in ((args["baseline_csv"], baseline), (args["candidate_csv"], candidate)):
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=HEADERS)
            writer.writeheader()
            writer.writerows(rows)
    result = compare_candidates(**args)
    assert result["decision"] == "BLOCKED"
    assert "INSUFFICIENT_TEST_SUBJECTS" in result["reasons"]
