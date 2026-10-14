"""Offline candidate-vs-baseline evaluation; never automatically promotes a medical model."""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from services.cv.artifacts import file_sha256
from services.learning.evaluation import audit_rows, evaluate, read_table

SHA256 = re.compile(r"^[0-9a-f]{64}$")
PUBLIC_ID = re.compile(r"^[a-zA-Z0-9_.-]{1,120}$")
IDENTITY_COLUMNS = (
    "example_id", "subject_id", "content_sha256", "split",
    "source", "label", "skin_tone_group", "device_group",
)


@dataclass(frozen=True)
class ReviewPolicy:
    baseline_model_version: str
    candidate_model_version: str
    baseline_checkpoint_sha256: str
    candidate_checkpoint_sha256: str
    evaluation_dataset_id: str
    minimum_test_subjects: int
    minimum_per_class_support: int
    minimum_macro_f1_delta: float
    maximum_ece_increase: float
    maximum_per_class_recall_drop: float


def _metric_threshold(value: Any, field: str, lower: float, upper: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError(f"Invalid review-policy metric threshold: {field}")
    result = float(value)
    if not math.isfinite(result) or not lower <= result <= upper:
        raise ValueError(f"Invalid review-policy metric threshold: {field}")
    return result


def load_review_policy(path: Path) -> ReviewPolicy:
    """Requires explicit versioned policy and separate human data-rights declarations."""
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("policy_version") != "1":
        raise ValueError("Unsupported reviewed policy format")
    for check in ("data_rights_reviewed", "label_quality_reviewed", "test_split_locked"):
        if doc.get(check) is not True:
            raise ValueError(f"Missing human evaluation assurance: {check}")
    for key in (
        "baseline_model_version", "candidate_model_version", "evaluation_dataset_id"
    ):
        if not isinstance(doc.get(key), str) or not PUBLIC_ID.fullmatch(doc[key]):
            raise ValueError(f"Invalid research review identifier: {key}")
    for field in ("baseline_checkpoint_sha256", "candidate_checkpoint_sha256"):
        if not isinstance(doc.get(field), str) or not SHA256.fullmatch(doc[field]):
            raise ValueError(f"Invalid checkpoint digest: {field}")
    if doc["baseline_checkpoint_sha256"] == doc["candidate_checkpoint_sha256"]:
        raise ValueError("New candidate must not have identical checkpoint bytes")
    subjects = doc.get("minimum_test_subjects")
    samples = doc.get("minimum_per_class_support")
    if type(subjects) is not int or subjects < 30:
        raise ValueError("Review policy must require at least 30 independent test subjects")
    if type(samples) is not int or samples < 5:
        raise ValueError("Review policy must require at least five test examples per class")
    return ReviewPolicy(
        baseline_model_version=doc["baseline_model_version"],
        candidate_model_version=doc["candidate_model_version"],
        baseline_checkpoint_sha256=doc["baseline_checkpoint_sha256"],
        candidate_checkpoint_sha256=doc["candidate_checkpoint_sha256"],
        evaluation_dataset_id=doc["evaluation_dataset_id"],
        minimum_test_subjects=subjects,
        minimum_per_class_support=samples,
        minimum_macro_f1_delta=_metric_threshold(doc.get("minimum_macro_f1_delta"), "macro_f1", -1, 1),
        maximum_ece_increase=_metric_threshold(doc.get("maximum_ece_increase"), "ece", 0, 1),
        maximum_per_class_recall_drop=_metric_threshold(
            doc.get("maximum_per_class_recall_drop"), "class_recall", 0, 1
        ),
    )


def compare_candidates(
    *,
    baseline_csv: Path,
    candidate_csv: Path,
    baseline_checkpoint: Path,
    candidate_checkpoint: Path,
    label_map_path: Path,
    policy_path: Path,
) -> dict[str, Any]:
    """Only a research review recommendation; no write to the model registry."""
    policy = load_review_policy(policy_path)
    if (
        file_sha256(baseline_checkpoint) != policy.baseline_checkpoint_sha256
        or file_sha256(candidate_checkpoint) != policy.candidate_checkpoint_sha256
    ):
        raise ValueError("Submitted checkpoint does not match review policy")
    mapping = json.loads(label_map_path.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict) or set(mapping) != {str(i) for i in range(6)}:
        raise ValueError("Exact six-class label mapping is required")
    labels = tuple(mapping[str(i)] for i in range(6))
    baseline = read_table(baseline_csv)
    candidate = read_table(candidate_csv)
    audit_rows(baseline, labels)
    audit_rows(candidate, labels)
    if baseline[0]["model_version"] != policy.baseline_model_version:
        raise ValueError("Baseline report model version does not match review policy")
    if candidate[0]["model_version"] != policy.candidate_model_version:
        raise ValueError("Candidate report model version does not match review policy")
    baseline_lookup = {row["example_id"]: row for row in baseline}
    candidate_lookup = {row["example_id"]: row for row in candidate}
    if baseline_lookup.keys() != candidate_lookup.keys():
        raise ValueError("Candidate and baseline must cover exactly the same evaluation examples")
    for key in baseline_lookup:
        if any(
            baseline_lookup[key][field] != candidate_lookup[key][field]
            for field in IDENTITY_COLUMNS
        ):
            raise ValueError("Candidate and baseline data provenance or labels differ")
    test = [row for row in baseline if row["split"] == "test"]
    if not test or any(row["source"] != "real" for row in test):
        raise ValueError("Candidate review requires a real-only held-out test split")
    groups = {row["subject_id"] for row in test}
    reasons: list[str] = []
    if len(groups) < policy.minimum_test_subjects:
        reasons.append("INSUFFICIENT_TEST_SUBJECTS")
    base_report = evaluate(baseline, labels)
    candidate_report = evaluate(candidate, labels)
    a = base_report["metrics"]
    b = candidate_report["metrics"]
    for name in labels:
        if min(a["per_class"][name]["support"], b["per_class"][name]["support"]) < policy.minimum_per_class_support:
            reasons.append("INSUFFICIENT_PER_CLASS_SUPPORT")
            break
    macro_delta = round(b["macro_f1"] - a["macro_f1"], 6)
    ece_delta = round(b["ece_10_bins_exploratory"] - a["ece_10_bins_exploratory"], 6)
    class_drops = {
        name: round(a["per_class"][name]["recall"] - b["per_class"][name]["recall"], 6)
        for name in labels
    }
    if macro_delta < policy.minimum_macro_f1_delta:
        reasons.append("MACRO_F1_REGRESSION")
    if ece_delta > policy.maximum_ece_increase:
        reasons.append("CALIBRATION_REGRESSION")
    if any(drop > policy.maximum_per_class_recall_drop for drop in class_drops.values()):
        reasons.append("PER_CLASS_RECALL_REGRESSION")
    return {
        "report_type": "OFFLINE_RESEARCH_CANDIDATE_REVIEW",
        "decision": "BLOCKED" if reasons else "ELIGIBLE_FOR_MANUAL_RESEARCH_REVIEW",
        "clinical_release_authorized": False,
        "automated_model_promotion": False,
        "evaluation_dataset_id": policy.evaluation_dataset_id,
        "baseline_model_version": policy.baseline_model_version,
        "candidate_model_version": policy.candidate_model_version,
        "independent_test_subjects": len(groups),
        "test_sample_count": len(test),
        "macro_f1_delta": macro_delta,
        "ece_delta": ece_delta,
        "per_class_recall_drop": class_drops,
        "reasons": sorted(set(reasons)),
        "input_sha256": {
            "baseline_predictions": file_sha256(baseline_csv),
            "candidate_predictions": file_sha256(candidate_csv),
            "review_policy": file_sha256(policy_path),
        },
        "mandatory_manual_checks": [
            "Verify checkpoint serialization and model/inference parity.",
            "Review real-image labels, licensing, subject separation and subgroup behavior.",
            "Require qualified clinician and independent risk review before medical use.",
            "Stage/release deployment requires separate explicit approval and rollback.",
        ],
    }
