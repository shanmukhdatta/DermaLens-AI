"""Real-image evaluation contracts, provenance, leakage checks and aggregate metrics.

All probability fixtures are synthetic calculations, NOT trained checkpoint outputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import pytest

from services.evaluation.audit import load_manifest, load_predictions
from services.evaluation.metrics import evaluate_files, save_report

LABELS = [
    "Acne", "Fungal_Infection", "Hyperpigmentation",
    "Normal_Skin", "Skin_Cancer", "Vitiligo",
]
HEADERS = [
    "sample_id", "group_id", "image_sha256", "split", "source", "true_label",
    "skin_tone_group", "device_group", *(f"p_{n}" for n in range(6)),
]


def make_manifest(tmp_path: Path) -> Path:
    destination = tmp_path / "evaluation_manifest.json"
    destination.write_text(json.dumps({
        "evaluation_id": "fixture-only-never-a-real-evaluation",
        "model_sha256": "a" * 64,
        "ordered_labels": LABELS,
        "authorized_for_evaluation": True,
        "independent_real_data": True,
        "disjoint_subject_groups": True,
        "locked_test_split": True,
        "label_provenance": "synthetic labels for automated tests only",
        "license_or_permission": "test fixture only",
        "collection_description": "unreal synthetic evaluation fixture",
    }), encoding="utf-8")
    return destination


def make_rows(count: int = 24) -> list[dict[str, str]]:
    rows = []
    for i in range(count):
        label_index = i % 6
        scores = [0.02] * 6
        scores[label_index] = 0.9
        rows.append({
            "sample_id": f"fictional-{i}",
            "group_id": f"fictional-group-{i}",
            "image_sha256": hashlib.sha256(f"not-an-image-{i}".encode()).hexdigest(),
            "split": "test", "source": "real", "true_label": LABELS[label_index],
            "skin_tone_group": "undisclosed", "device_group": "fixture-camera",
            **{f"p_{j}": str(scores[j]) for j in range(6)},
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as source:
        writer = csv.DictWriter(source, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def test_perfect_fixture_metrics_are_not_clinical_claims(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    csv_file = tmp_path / "test_predictions.csv"
    write_csv(csv_file, make_rows())
    report = evaluate_files(manifest, csv_file)
    result = report["test_results"]
    assert result["accuracy"] == 1.0
    assert result["macro_f1_supported_classes"] == 1.0
    assert result["count"] == 24
    assert result["classes_without_support"] == []
    assert result["multiclass_brier"] > 0
    assert len(result["confusion_matrix_actual_rows"]) == 6
    assert report["accuracy_interval"]["available"] is True
    assert report["status"] == "RESEARCH_ONLY_NOT_CLINICALLY_VALIDATED"
    assert "fictional-0" not in json.dumps(report)
    assert report["subgroups_with_at_least_20_samples"]["device_group"]["fixture-camera"]["count"] == 24
    destination = tmp_path / "aggregate.json"
    save_report(destination, report)
    assert "fictional-0" not in destination.read_text()
    with pytest.raises(FileExistsError):
        save_report(destination, report)


@pytest.mark.parametrize("field", [
    "authorized_for_evaluation", "independent_real_data",
    "disjoint_subject_groups", "locked_test_split",
])
def test_require_explicit_provenance_declarations(tmp_path: Path, field: str) -> None:
    path = make_manifest(tmp_path)
    data = json.loads(path.read_text())
    data[field] = False
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="declaration"):
        load_manifest(path)


def test_reject_content_leak_between_splits(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    rows = make_rows()
    duplicate = dict(rows[0])
    duplicate["sample_id"] = "other"
    duplicate["group_id"] = "different-group"
    duplicate["split"] = "calibration"
    rows.append(duplicate)
    csv_file = tmp_path / "preds.csv"
    write_csv(csv_file, rows)
    with pytest.raises(ValueError, match="content leak"):
        load_predictions(csv_file, load_manifest(manifest))


def test_reject_subject_leak_between_splits(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    rows = make_rows()
    row = dict(rows[0])
    row["sample_id"] = "other"
    row["image_sha256"] = "b" * 64
    row["split"] = "calibration"
    rows.append(row)
    file = tmp_path / "preds.csv"
    write_csv(file, rows)
    with pytest.raises(ValueError, match="Group or subject leak"):
        load_predictions(file, load_manifest(manifest))


@pytest.mark.parametrize("field,value", [
    ("true_label", "Untrained Disease"),
    ("source", "synthetic"),
    ("p_0", "nan"),
    ("p_0", "-0.5"),
    ("p_0", "0.999999"),
    ("split", "deployment"),
])
def test_reject_invalid_ground_truth_and_model_scores(tmp_path: Path, field: str, value: str) -> None:
    manifest = make_manifest(tmp_path)
    rows = make_rows()
    rows[0][field] = value
    file = tmp_path / "preds.csv"
    write_csv(file, rows)
    with pytest.raises(ValueError):
        load_predictions(file, load_manifest(manifest))


def test_no_real_test_rows_or_duplicate_identifiers(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    rows = make_rows()
    for row in rows:
        row["split"] = "train"
    file = tmp_path / "preds.csv"
    write_csv(file, rows)
    with pytest.raises(ValueError, match="No independently"):
        load_predictions(file, load_manifest(manifest))
    rows[-1] = dict(rows[0])
    rows[-1]["split"] = "test"
    write_csv(file, rows)
    with pytest.raises(ValueError, match="Duplicate sample"):
        load_predictions(file, load_manifest(manifest))


def test_sparse_groups_are_suppressed(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    file = tmp_path / "preds.csv"
    rows = make_rows(12)
    write_csv(file, rows)
    report = evaluate_files(manifest, file)
    assert report["accuracy_interval"]["available"] is False
    assert report["subgroups_with_at_least_20_samples"]["device_group"] == {}


def test_missing_classes_are_reported_not_hidden(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    file = tmp_path / "preds.csv"
    write_csv(file, make_rows(1))
    report = evaluate_files(manifest, file)
    assert len(report["test_results"]["classes_without_support"]) == 5
    assert report["status"].startswith("RESEARCH_ONLY")


def test_csv_disallows_raw_image_paths_and_extra_personal_fields(tmp_path: Path) -> None:
    manifest = make_manifest(tmp_path)
    file = tmp_path / "preds.csv"
    rows = make_rows()
    with file.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=[*HEADERS, "image_rel_path"])
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "image_rel_path": "/private/face.jpg"})
    with pytest.raises(ValueError, match="column contract"):
        load_predictions(file, load_manifest(manifest))
