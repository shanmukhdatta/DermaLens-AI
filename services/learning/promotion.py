"""Offline candidate regression decision; never performs automated model promotion."""

from __future__ import annotations

import hashlib
from typing import Any

from services.learning.evaluation import _stats, audit_rows


def compare_candidate(
    baseline: list[dict[str, str]],
    candidate: list[dict[str, str]],
    ordered_labels: tuple[str, ...],
    *,
    minimum_test_groups: int = 30,
) -> dict[str, Any]:
    """Compare strictly identical held-out real-image populations and label order.

    A passing research regression test only queues external review; it does
    not change the serving model or approve medical use.
    """
    audit_rows(baseline, ordered_labels)
    audit_rows(candidate, ordered_labels)
    if minimum_test_groups < 30:
        raise ValueError("Minimum independent test groups cannot be weakened")
    old_test = {row["example_id"]: row for row in baseline if row["split"] == "test"}
    new_test = {row["example_id"]: row for row in candidate if row["split"] == "test"}
    if set(old_test) != set(new_test):
        raise ValueError("Candidate and baseline must evaluate identical examples")
    if baseline[0]["model_version"] == candidate[0]["model_version"]:
        raise ValueError("Candidate version must differ from baseline model version")
    demographics = ("subject_id", "content_sha256", "label", "source")
    for sample_id, old in old_test.items():
        new = new_test[sample_id]
        if any(old[field] != new[field] for field in demographics):
            raise ValueError("Candidate and baseline evaluation cohort differs")
        if old["source"] != "real":
            raise ValueError("Only reviewed real-domain test results are eligible")
    if len({item["subject_id"] for item in old_test.values()}) < minimum_test_groups:
        raise ValueError("Too few independent held-out subjects for candidate review")
    cohort = "|".join(
        ":".join((record["example_id"], record["content_sha256"], record["label"]))
        for record in sorted(old_test.values(), key=lambda record: record["example_id"])
    )
    cohort_sha = hashlib.sha256(cohort.encode("utf-8")).hexdigest()
    baseline_stats = _stats(list(old_test.values()), ordered_labels)
    candidate_stats = _stats(list(new_test.values()), ordered_labels)
    regressions: list[str] = []
    if candidate_stats["macro_f1"] < baseline_stats["macro_f1"]:
        regressions.append("MACRO_F1_REGRESSION")
    if candidate_stats["brier_multiclass"] > baseline_stats["brier_multiclass"]:
        regressions.append("BRIER_CALIBRATION_REGRESSION")
    for label in ordered_labels:
        if (
            candidate_stats["per_class"][label]["recall"]
            < baseline_stats["per_class"][label]["recall"]
        ):
            regressions.append("RECALL_REGRESSION:" + label)
    return {
        "kind": "offline_research_regression_gate",
        "clinical_use_approved": False,
        "auto_deployed": False,
        "automatic_promotion_permitted": False,
        "same_held_out_cohort_sha256": cohort_sha,
        "held_out_subject_groups": len({item["subject_id"] for item in old_test.values()}),
        "baseline_model_version": baseline[0]["model_version"],
        "candidate_model_version": candidate[0]["model_version"],
        "baseline": {
            "macro_f1": baseline_stats["macro_f1"],
            "brier_multiclass": baseline_stats["brier_multiclass"],
        },
        "candidate": {
            "macro_f1": candidate_stats["macro_f1"],
            "brier_multiclass": candidate_stats["brier_multiclass"],
        },
        "regressions": regressions,
        "review_state": "rejected_by_research_gate"
        if regressions
        else "awaiting_independent_review",
        "warning": "Passing this gate does not authorize deployment or medical claims.",
    }
