"""No-mock diagnosis: research-only calibration and fail-closed decision tests."""

from __future__ import annotations

import numpy as np
import pytest

from services.cv.gradcam import ExplanationUnavailable, gradcam_heatmap
from services.learning.calibration import (
    abstaining_decision,
    fit_exploratory_policy,
    temperature_scaled,
)

LABELS = (
    "Acne",
    "Fungal_Infection",
    "Hyperpigmentation",
    "Normal_Skin",
    "Skin_Cancer",
    "Vitiligo",
)


def record(i: int, split: str, *, source: str = "real") -> dict[str, str]:
    correct_class = i % 6
    values = ["0.01"] * 6
    values[correct_class] = "0.95"
    return {
        "example_id": f"research-fixture-{i}",
        "subject_id": f"subject-fixture-{i}",
        "content_sha256": f"{i:064x}",
        "split": split,
        "source": source,
        "label": LABELS[correct_class],
        "model_version": "fictional-only",
        "skin_tone_group": "unspecified",
        "device_group": "unspecified",
        **{f"prob_{n}": score for n, score in enumerate(values)},
    }


def rows() -> list[dict[str, str]]:
    return [
        *[record(i, "calibration") for i in range(1, 121)],
        *[record(i, "test") for i in range(121, 151)],
    ]


def test_scaling_keeps_probabilities_normalized() -> None:
    batch = np.asarray([[0.95, 0.01, 0.01, 0.01, 0.01, 0.01]])
    result = temperature_scaled(batch, 2.0)
    assert np.isclose(result.sum(), 1.0)
    assert int(result.argmax(axis=1)[0]) == 0


def test_policy_never_approves_itself_or_unlocks_public_inference() -> None:
    policy = fit_exploratory_policy(rows(), LABELS)
    assert policy.status == "research_only_unapproved"
    assert policy.ood_validated is False
    assert policy.xai_validated is False
    assert policy.calibration_subject_groups == 120
    assert (
        abstaining_decision((0.95, 0.01, 0.01, 0.01, 0.01, 0.01), "fictional-only", policy)[
            "status"
        ]
        == "abstained"
    )
    experimental = abstaining_decision(
        (0.95, 0.01, 0.01, 0.01, 0.01, 0.01),
        "fictional-only",
        policy,
        offline_research_mode=True,
    )
    assert experimental["medical_diagnosis"] is False
    assert experimental["status"] == "research_candidate_only"
    assert (
        abstaining_decision(
            (0.95, 0.01, 0.01, 0.01, 0.01, 0.01),
            "different-model",
            policy,
            offline_research_mode=True,
        )["status"]
        == "abstained"
    )


def test_insufficient_or_fake_calibration_data_rejected() -> None:
    with pytest.raises(ValueError, match="Insufficient"):
        fit_exploratory_policy(rows()[:20] + rows()[-30:], LABELS)
    faked = rows()
    faked[0]["source"] = "fixture"
    with pytest.raises(ValueError, match="Insufficient"):
        fit_exploratory_policy(faked, LABELS)


def test_no_gradcam_for_unsupported_model() -> None:
    with pytest.raises(ExplanationUnavailable):
        gradcam_heatmap(
            object(),
            np.zeros((1, 224, 224, 3), dtype=np.float32),
            class_index=3,
            convolution_layer_name="nonexistent",
        )


def test_reject_invalid_research_probabilities() -> None:
    with pytest.raises(ValueError):
        temperature_scaled(np.asarray([[0.5, float("nan"), 0, 0, 0, 0]]), 1)
    assert abstaining_decision((0.3, 0.7), "x", None)["status"] == "abstained"
