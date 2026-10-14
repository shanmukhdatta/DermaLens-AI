"""Checkpoint-bound external research-review policy atop the offline regression gate."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from services.cv.artifacts import file_sha256
from services.learning.evaluation import _stats, read_table
from services.learning.promotion import compare_candidate

SHA = re.compile(r"^[a-f0-9]{64}$")
NAME = re.compile(r"^[A-Za-z0-9_.-]{1,120}$")


def _number(document: dict[str, Any], key: str, low: float, high: float) -> float:
    raw = document.get(key)
    if isinstance(raw, bool) or not isinstance(raw, (float, int)):
        raise ValueError(f"Review policy requires numeric {key}")
    value = float(raw)
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f"Invalid research review threshold: {key}")
    return value


def _policy(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("policy_version") != "1":
        raise ValueError("Review policy must be a versioned JSON object")
    for name in ("data_rights_reviewed", "label_quality_reviewed", "locked_test_split"):
        if data.get(name) is not True:
            raise ValueError(f"Human provenance review absent: {name}")
    for name in ("baseline_version", "candidate_version", "dataset_id"):
        value = data.get(name)
        if not isinstance(value, str) or not NAME.fullmatch(value):
            raise ValueError(f"Invalid review policy identifier: {name}")
    for name in ("baseline_sha256", "candidate_sha256"):
        value = data.get(name)
        if not isinstance(value, str) or not SHA.fullmatch(value):
            raise ValueError(f"Invalid pinned checkpoint fingerprint: {name}")
    if data["baseline_sha256"] == data["candidate_sha256"]:
        raise ValueError("Candidate checkpoint must differ from baseline bytes")
    required = data.get("minimum_class_support")
    if type(required) is not int or required < 5:
        raise ValueError("At least five test examples per category required for a review gate")
    _number(data, "minimum_macro_f1_improvement", 0, 1)
    _number(data, "maximum_ece_increase", 0, 1)
    return data


def evaluate_with_policy(
    *,
    baseline_path: Path,
    candidate_path: Path,
    label_map_path: Path,
    baseline_checkpoint: Path,
    candidate_checkpoint: Path,
    policy_path: Path,
) -> dict[str, Any]:
    """Return research-review eligibility only, NEVER deployment permission."""
    policy = _policy(policy_path)
    if (
        file_sha256(baseline_checkpoint) != policy["baseline_sha256"]
        or file_sha256(candidate_checkpoint) != policy["candidate_sha256"]
    ):
        raise ValueError("Checkpoint bytes do not match external review-policy fingerprints")
    label_map = json.loads(label_map_path.read_text(encoding="utf-8"))
    if not isinstance(label_map, dict) or set(label_map) != {str(i) for i in range(6)}:
        raise ValueError("Six-class exact-index label map required")
    labels = tuple(label_map[str(i)] for i in range(6))
    baseline = read_table(baseline_path)
    candidate = read_table(candidate_path)
    if (
        baseline[0]["model_version"] != policy["baseline_version"]
        or candidate[0]["model_version"] != policy["candidate_version"]
    ):
        raise ValueError("Prediction model versions differ from policy")
    # Canonical research regression gate compares the exact held-out real cohort.
    review = compare_candidate(baseline, candidate, labels)
    old_test = [row for row in baseline if row["split"] == "test"]
    new_test = [row for row in candidate if row["split"] == "test"]
    old_stats = _stats(old_test, labels)
    new_stats = _stats(new_test, labels)
    reasons = list(review["regressions"])
    insufficient = any(
        old_stats["per_class"][label]["support"] < policy["minimum_class_support"]
        for label in labels
    )
    if insufficient:
        reasons.append("INSUFFICIENT_PER_CLASS_TEST_SUPPORT")
    macro_delta = round(new_stats["macro_f1"] - old_stats["macro_f1"], 5)
    ece_delta = round(
        new_stats["ece_10_bins_exploratory"] - old_stats["ece_10_bins_exploratory"], 5
    )
    if macro_delta < policy["minimum_macro_f1_improvement"]:
        reasons.append("BELOW_DECLARED_MACRO_F1_IMPROVEMENT")
    if ece_delta > policy["maximum_ece_increase"]:
        reasons.append("EXCEEDS_DECLARED_ECE_INCREASE")
    return {
        "report_type": "CHECKPOINT_BOUND_OFFLINE_RESEARCH_REVIEW",
        "decision": "BLOCKED" if reasons else "AWAITING_INDEPENDENT_REVIEW",
        "clinical_release_approved": False,
        "auto_deployment_allowed": False,
        "dataset_id": policy["dataset_id"],
        "baseline_version": policy["baseline_version"],
        "candidate_version": policy["candidate_version"],
        "subjects_on_test": review["held_out_subject_groups"],
        "macro_f1_delta": macro_delta,
        "ece_delta": ece_delta,
        "reasons": sorted(set(reasons)),
        "cohort_sha256": review["same_held_out_cohort_sha256"],
        "policy_sha256": file_sha256(policy_path),
        "human_review_required": True,
        "note": "Checksums and statistical comparisons cannot establish clinical effectiveness.",
    }
