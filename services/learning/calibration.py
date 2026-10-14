"""Offline research calibration and default-abstaining safety policy.

No artifact generated here is approved for medical or consumer-facing inference.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import sqrt
from typing import Any

import numpy as np

from services.learning.evaluation import PROB_COLUMNS, audit_rows


@dataclass(frozen=True)
class ResearchCalibration:
    """Exploratory only; always requires an independent clinical release gate."""

    model_version: str
    ordered_labels: tuple[str, ...]
    temperature: float
    experimental_threshold: float | None
    target_error: float
    calibration_subject_groups: int
    calibration_count: int
    status: str = "research_only_unapproved"
    ood_validated: bool = False
    xai_validated: bool = False

    def payload(self) -> dict[str, Any]:
        return asdict(self)


def temperature_scaled(values: np.ndarray, temperature: float) -> np.ndarray:
    """Scale probabilities in log space, preserving class order and normalization."""
    if (
        values.ndim != 2
        or values.shape[1] != 6
        or not np.isfinite(values).all()
        or np.any(values < 0)
        or np.any(values > 1)
        or not np.allclose(values.sum(axis=1), 1.0, atol=1e-4)
        or not np.isfinite(temperature)
        or temperature <= 0
    ):
        raise ValueError("Expected valid six-class probability rows and positive temperature")
    logits = np.log(np.clip(values, 1e-12, 1)) / temperature
    logits = logits - logits.max(axis=1, keepdims=True)
    exponent = np.exp(logits)
    return np.asarray(exponent / exponent.sum(axis=1, keepdims=True), dtype=np.float64)


def _wilson_upper(errors: int, accepted: int, z: float = 1.96) -> float:
    """Conservative approximate upper bound on the observed selective error rate."""
    if accepted == 0:
        return 1.0
    fraction = errors / accepted
    scale = 1 + z * z / accepted
    centre = fraction + z * z / (2 * accepted)
    spread = z * sqrt((fraction * (1 - fraction) + z * z / (4 * accepted)) / accepted)
    return min(1.0, (centre + spread) / scale)


def fit_exploratory_policy(
    rows: list[dict[str, str]],
    labels: tuple[str, ...],
    *,
    target_error: float = 0.10,
    minimum_calibration_groups: int = 50,
) -> ResearchCalibration:
    """Fit temperature and a *research-only* selective-risk candidate on calibration split.

    The held-out test records are audited for leakage but never used in fitting.
    """
    audit_rows(rows, labels)
    if not 0 < target_error < 1 or minimum_calibration_groups < 30:
        raise ValueError("Unsupported calibration parameters")
    calibration = [row for row in rows if row["split"] == "calibration"]
    unique_subjects = {row["subject_id"] for row in calibration}
    if len(unique_subjects) < minimum_calibration_groups or any(
        row["source"] != "real" for row in calibration
    ):
        raise ValueError("Insufficient independent real-world calibration groups")
    probabilities = np.asarray(
        [[float(row[column]) for column in PROB_COLUMNS] for row in calibration],
        dtype=float,
    )
    true_indices = np.asarray([labels.index(row["label"]) for row in calibration], dtype=int)
    temperatures = np.geomspace(0.5, 5.0, 81)
    losses = []
    for candidate in temperatures:
        scaled = temperature_scaled(probabilities, float(candidate))
        losses.append(
            float(
                -np.mean(
                    np.log(np.clip(scaled[np.arange(len(calibration)), true_indices], 1e-12, 1))
                )
            )
        )
    best_temperature = float(temperatures[int(np.argmin(losses))])
    scaled = temperature_scaled(probabilities, best_temperature)
    confident = scaled.max(axis=1)
    correct = scaled.argmax(axis=1) == true_indices
    chosen: float | None = None
    # Evaluate candidates on calibration data only. Never claim clinical safety.
    for threshold in np.unique(confident):
        picked = confident >= threshold
        accepted = int(picked.sum())
        if accepted < 30:
            continue
        errors = int(np.count_nonzero(~correct[picked]))
        if _wilson_upper(errors, accepted) <= target_error:
            chosen = float(threshold)
            break
    return ResearchCalibration(
        model_version=rows[0]["model_version"],
        ordered_labels=labels,
        temperature=round(best_temperature, 7),
        experimental_threshold=chosen,
        target_error=target_error,
        calibration_subject_groups=len(unique_subjects),
        calibration_count=len(calibration),
    )


def abstaining_decision(
    probabilities: tuple[float, ...],
    model_version: str,
    policy: ResearchCalibration | None,
    *,
    offline_research_mode: bool = False,
) -> dict[str, Any]:
    """Fail closed by default, including when offline research policy is missing."""
    base: dict[str, Any] = {
        "status": "abstained",
        "reason": "POLICY_NOT_VALIDATED",
        "medical_diagnosis": False,
    }
    if not offline_research_mode or policy is None:
        return base
    if (
        policy.status != "research_only_unapproved"
        or policy.model_version != model_version
        or policy.experimental_threshold is None
        or len(probabilities) != 6
    ):
        return base
    try:
        scaled = temperature_scaled(np.asarray([probabilities], dtype=float), policy.temperature)[0]
    except (ValueError, TypeError):
        return base
    index = int(np.argmax(scaled))
    if scaled[index] < policy.experimental_threshold:
        return {**base, "reason": "EXPERIMENTAL_LOW_CONFIDENCE"}
    return {
        "status": "research_candidate_only",
        "medical_diagnosis": False,
        "class_index": index,
        "category": policy.ordered_labels[index],
        "experimental_calibrated_score": round(float(scaled[index]), 5),
        "warning": "Not validated or authorized for clinical use.",
    }
