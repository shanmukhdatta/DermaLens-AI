"""Test split-leakage refusal and offline evaluation without any real medical images."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from services.learning.evaluation import REQUIRED, audit_rows, evaluate, read_table

LABELS = (
    "Acne", "Fungal_Infection", "Hyperpigmentation",
    "Normal_Skin", "Skin_Cancer", "Vitiligo",
)


def sample(index: int, split: str = "test", label_idx: int = 0) -> dict[str, str]:
    vec = ["0.02"] * 6
    vec[label_idx] = "0.9"
    return {
        "example_id": f"sample-{index}",
        "subject_id": f"subject-{index}",
        "content_sha256": f"{index:064x}",
        "split": split,
        "source": "fixture",
        "label": LABELS[label_idx],
        "model_version": "fixture-v0",
        "skin_tone_group": "not-recorded",
        "device_group": "not-recorded",
        **{f"prob_{j}": value for j, value in enumerate(vec)},
    }


def fixtures() -> list[dict[str, str]]:
    return [
        sample(1, "train"), sample(2, "calibration"),
        *[sample(i, "test", i % 6) for i in range(3, 15)],
    ]


def test_research_report_never_claims_clinical_validation() -> None:
    report = evaluate(fixtures(), LABELS)
    assert report["report_type"] == "research_evaluation_only"
    assert report["clinical_use_validated"] is False
    assert report["metrics"]["accuracy"] == 1.0
    assert report["splits"]["test"] == 12
    assert report["accuracy_95pct_subject_bootstrap_interval"] is None
    assert "Test partition is not exclusively real-world images." in report["warnings"]
    assert report["subgroups_min_n_10"]["source"]["fixture"]["n"] == 12


def test_subject_and_content_cross_split_leakage_rejected() -> None:
    for key in ("subject_id", "content_sha256"):
        rows = fixtures()
        rows[-1][key] = rows[0][key]
        with pytest.raises(ValueError, match="Leakage"):
            audit_rows(rows, LABELS)


@pytest.mark.parametrize("update", [
    {"prob_0": "nan"}, {"prob_0": "-0.2"},
    {"label": "unknown"}, {"split": "unknown"},
    {"model_version": "other-version"},
])
def test_bad_prediction_or_manifest_rejected(update: dict[str, str]) -> None:
    rows = fixtures()
    rows[-1].update(update)
    with pytest.raises(ValueError):
        audit_rows(rows, LABELS)


def test_duplicate_sample_id_rejected() -> None:
    rows = fixtures()
    rows[-1]["example_id"] = rows[0]["example_id"]
    with pytest.raises(ValueError, match="Duplicate"):
        audit_rows(rows, LABELS)


def test_reject_leaking_paths_or_identifiers_in_csv(tmp_path: Path) -> None:
    path = tmp_path / "predictions.csv"
    record = fixtures()[0]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=sorted(REQUIRED | {"image_path"}))
        writer.writeheader()
        writer.writerow({**record, "image_path": "/private/raw.jpg"})
    with pytest.raises(ValueError, match="identifiers"):
        read_table(path)


def test_small_subgroups_suppressed() -> None:
    rows = fixtures()
    rows[-1]["skin_tone_group"] = "groupB"
    report = evaluate(rows, LABELS)
    assert report["subgroups_min_n_10"]["skin_tone_group"]["groupB"] == {
        "n": 1, "suppressed": True
    }


def test_changed_labels_rejected() -> None:
    bad = ("Skin_Cancer",) * 6
    with pytest.raises(ValueError, match="six-category"):
        audit_rows(fixtures(), bad)
