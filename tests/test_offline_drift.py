"""Artificial population distributions, never real measured disease data."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from services.learning.drift import PopulationSummary, compare_populations


def make(cohort: str, counts: tuple[int, ...]) -> PopulationSummary:
    return PopulationSummary(cohort, "research-model-fixture", sum(counts), counts, 3)


def test_distinct_research_populations_flag_large_shift() -> None:
    old = make("old", (100, 100, 100, 100, 100, 100))
    new = make("new", (560, 8, 8, 8, 8, 8))
    report = compare_populations(old, new)
    assert report["status"] == "INVESTIGATE"
    assert 0 < report["js_distance"] < 1
    assert report["auto_retraining_enabled"] is False
    assert report["medical_interpretation"] is False
    assert "person" not in json.dumps(report)
    assert compare_populations(old, make("same-shape", (100,) * 6))["status"] == "NO_FLAG"


def test_small_or_mismatched_cohorts_fail_closed() -> None:
    small = make("small", (5,) * 6)
    result = compare_populations(make("old", (100,) * 6), small)
    assert result["status"] == "INSUFFICIENT_AGGREGATE_EVIDENCE"
    assert result["auto_retraining_enabled"] is False
    with pytest.raises(ValueError):
        compare_populations(make("a", (100,) * 6), make("a", (100,) * 6))
    with pytest.raises(ValueError):
        compare_populations(
            make("a", (100,) * 6),
            PopulationSummary("b", "changed-checkpoint", 600, (100,) * 6, 0),
        )


def test_parser_rejects_pseudodata_and_inconsistent_counts(tmp_path: Path) -> None:
    path = tmp_path / "aggregate.json"
    original = {
        "schema_version": 1, "aggregated_research_data": True,
        "cohort_id": "sample", "model_version": "fixture",
        "count": 100, "class_counts": [20, 20, 20, 20, 10, 10],
        "quality_rejection_count": 0,
    }
    path.write_text(json.dumps(original))
    assert PopulationSummary.from_file(path).count == 100
    for bad in (
        {**original, "class_counts": [0] * 6},
        {**original, "aggregated_research_data": False},
        {**original, "class_counts": [True, 0, 0, 0, 0, 0]},
    ):
        path.write_text(json.dumps(bad))
        with pytest.raises(ValueError):
            PopulationSummary.from_file(path)
