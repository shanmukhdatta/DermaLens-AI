"""Offline privacy-preserving class-frequency drift investigation.

Aggregated predictions are only research population signals, never health
incidence estimates, and MUST NOT automatically retrain or deploy a model.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EXPECTED_COUNT = 6


@dataclass(frozen=True)
class PopulationSummary:
    cohort_id: str
    model_version: str
    count: int
    class_counts: tuple[int, ...]
    quality_rejection_count: int

    @classmethod
    def from_file(cls, path: Path) -> PopulationSummary:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict):
            raise ValueError("Population summary must be a JSON object")
        if doc.get("schema_version") != 1 or doc.get("aggregated_research_data") is not True:
            raise ValueError("Summary must explicitly declare aggregated research provenance")
        for key in ("cohort_id", "model_version"):
            if not isinstance(doc.get(key), str) or not doc[key] or len(doc[key]) > 100:
                raise ValueError(f"Invalid research summary field: {key}")
        values = doc.get("class_counts")
        if (
            not isinstance(values, list) or len(values) != EXPECTED_COUNT
            or any(type(v) is not int or v < 0 for v in values)
        ):
            raise ValueError("Expected six nonnegative integer class-count aggregates")
        total = doc.get("count")
        rejected = doc.get("quality_rejection_count")
        if type(total) is not int or total <= 0 or sum(values) != total:
            raise ValueError("Invalid or inconsistent aggregate sample count")
        if type(rejected) is not int or rejected < 0:
            raise ValueError("Invalid aggregate image-quality rejection count")
        return cls(
            doc["cohort_id"], doc["model_version"], total,
            tuple(values), rejected,
        )


def compare_populations(
    baseline: PopulationSummary, current: PopulationSummary, *, minimum_size: int = 100
) -> dict[str, Any]:
    """Return review advice rather than auto-acting on a potentially shifted sample."""
    if baseline.model_version != current.model_version:
        raise ValueError("Cannot interpret drift across different trained model versions")
    if baseline.cohort_id == current.cohort_id:
        raise ValueError("Baseline and current datasets must differ")
    if minimum_size < 50:
        raise ValueError("Minimum cohort size must be at least 50")
    if min(baseline.count, current.count) < minimum_size:
        return {
            "report_type": "RESEARCH_DRIFT_CHECK",
            "status": "INSUFFICIENT_AGGREGATE_EVIDENCE",
            "minimum_size": minimum_size,
            "auto_retraining_enabled": False,
            "medical_interpretation": False,
        }
    a = [count / baseline.count for count in baseline.class_counts]
    b = [count / current.count for count in current.class_counts]
    midpoint = [(p + q) / 2 for p, q in zip(a, b, strict=True)]

    def divergence(values: list[float]) -> float:
        return sum(
            p * math.log(p / m, 2)
            for p, m in zip(values, midpoint, strict=True)
            if p > 0 and m > 0
        )

    js_distance = math.sqrt(max(0.0, (divergence(a) + divergence(b)) / 2))
    return {
        "report_type": "RESEARCH_DRIFT_CHECK",
        "status": "INVESTIGATE" if js_distance >= 0.15 else "NO_FLAG",
        "js_distance": round(js_distance, 6),
        "model_version": baseline.model_version,
        "baseline_count": baseline.count,
        "current_count": current.count,
        "baseline_quality_rejections": baseline.quality_rejection_count,
        "current_quality_rejections": current.quality_rejection_count,
        "notes": (
            "Class-frequency drift is a heuristic sampling signal, not a proof "
            "of error, disease prevalence, OOD detection or model safety."
        ),
        "auto_retraining_enabled": False,
        "medical_interpretation": False,
    }
