"""Fictional examples exercise offline vetting; never clinical performance claims."""
from __future__ import annotations

import pytest

from services.learning.curation import validate_training_manifest
from services.learning.promotion import compare_candidate

LABELS = (
    "Acne",
    "Fungal_Infection",
    "Hyperpigmentation",
    "Normal_Skin",
    "Skin_Cancer",
    "Vitiligo",
)


def record(i: int, model: str) -> dict[str, str]:
    cls = i % 6
    p = ["0.02"] * 6
    p[cls] = "0.9"
    return {
        "example_id": f"fictional-example-{i}",
        "subject_id": f"fictional-person-{i}",
        "content_sha256": f"{i:064x}",
        "split": "test",
        "source": "real",
        "label": LABELS[cls],
        "model_version": model,
        "skin_tone_group": "not-recorded",
        "device_group": "not-recorded",
        **{f"prob_{n}": x for n, x in enumerate(p)},
    }


def test_offline_equal_performance_never_promotes_automatically() -> None:
    old = [record(i, "baseline-fixture") for i in range(1, 37)]
    new = [record(i, "candidate-fixture") for i in range(1, 37)]
    report = compare_candidate(old, new, LABELS)
    assert report["review_state"] == "awaiting_independent_review"
    assert report["clinical_use_approved"] is False
    assert report["auto_deployed"] is False
    assert report["regressions"] == []
    assert len(report["same_held_out_cohort_sha256"]) == 64


def test_rejects_candidate_regression() -> None:
    old = [record(i, "baseline-fixture") for i in range(1, 37)]
    new = [record(i, "candidate-fixture") for i in range(1, 37)]
    new[2].update({"prob_0": "0.9", "prob_3": "0.02"})
    report = compare_candidate(old, new, LABELS)
    assert report["review_state"] == "rejected_by_research_gate"
    assert "MACRO_F1_REGRESSION" in report["regressions"]


def test_rejects_mismatched_cohort_or_same_model() -> None:
    old = [record(i, "baseline-fixture") for i in range(1, 37)]
    new = [record(i, "candidate-fixture") for i in range(1, 37)]
    new[4]["subject_id"] = "unexpected-person"
    with pytest.raises(ValueError, match="cohort differs"):
        compare_candidate(old, new, LABELS)
    same_model = [record(i, "baseline-fixture") for i in range(1, 37)]
    with pytest.raises(ValueError, match="must differ"):
        compare_candidate(old, same_model, LABELS)


def test_curated_manifest_never_uses_user_vote_as_ground_truth() -> None:
    approved = {
        "sample_sha256": "a" * 64,
        "subject_group": "pseudonymous-group-1",
        "verified_category": "Acne",
        "review_state": "validated",
        "review_evidence_sha256": "b" * 64,
        "consent_scope": "research_training",
        "rights_verified": True,
        "label_source": "clinician_verified",
    }
    result = validate_training_manifest([approved])
    assert result["image_bytes_included"] is False
    assert result["clinical_authorization"] is False
    for key, value in (
        ("review_state", "pending"),
        ("consent_scope", "history_metadata"),
        ("rights_verified", False),
        ("label_source", "user_feedback"),
    ):
        row = {**approved, key: value}
        with pytest.raises(ValueError):
            validate_training_manifest([row])


def test_curation_rejects_identifiers_and_duplicate_images() -> None:
    item = {
        "sample_sha256": "a" * 64,
        "subject_group": "group",
        "verified_category": "Acne",
        "review_state": "validated",
        "review_evidence_sha256": "b" * 64,
        "consent_scope": "research_training",
        "rights_verified": True,
        "label_source": "researcher_verified",
    }
    with pytest.raises(ValueError, match="forbidden"):
        validate_training_manifest([{**item, "email": "hidden@example.com"}])
    with pytest.raises(ValueError, match="Duplicated"):
        validate_training_manifest([item, item])
