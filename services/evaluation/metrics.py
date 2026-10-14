"""Aggregate research metrics on an independently labeled real test split."""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from services.evaluation.audit import EvaluatedRow, EvaluationManifest, load_manifest, load_predictions


def _metrics(rows: list[EvaluatedRow], labels: tuple[str, ...]) -> dict[str, Any]:
    truth = np.asarray([row.true_index for row in rows], dtype=int)
    probability = np.asarray([row.probabilities for row in rows], dtype=float)
    predicted = probability.argmax(axis=1)
    n = len(rows)
    matrix = np.zeros((len(labels), len(labels)), dtype=int)
    for actual, predicted_index in zip(truth, predicted, strict=True):
        matrix[actual, predicted_index] += 1
    per_class: dict[str, dict[str, Any]] = {}
    f1_scores: list[float] = []
    for i, name in enumerate(labels):
        tp = int(matrix[i, i])
        support = int(matrix[i].sum())
        predicted_count = int(matrix[:, i].sum())
        precision = tp / predicted_count if predicted_count else None
        recall = tp / support if support else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and precision + recall > 0
            else (0.0 if support > 0 else None)
        )
        per_class[name] = {
            "support": support, "precision": precision,
            "recall": recall, "f1": f1,
        }
        if f1 is not None:
            f1_scores.append(f1)
    conf = probability.max(axis=1)
    accuracy = float((truth == predicted).mean())
    expected = np.zeros_like(probability)
    expected[np.arange(n), truth] = 1.0
    ece = 0.0
    for bin_index in range(10):
        lo, hi = bin_index / 10, (bin_index + 1) / 10
        in_bin = (conf >= lo) & ((conf <= hi) if bin_index == 9 else (conf < hi))
        if in_bin.any():
            ece += float(in_bin.mean()) * abs(
                float((truth[in_bin] == predicted[in_bin]).mean()) - float(conf[in_bin].mean())
            )
    return {
        "count": n,
        "accuracy": accuracy,
        "macro_f1_supported_classes": float(np.mean(f1_scores)) if f1_scores else None,
        "classes_without_support": [name for name in labels if per_class[name]["support"] == 0],
        "multiclass_brier": float(np.mean(np.sum((probability - expected) ** 2, axis=1))),
        "negative_log_likelihood": float(np.mean(-np.log(np.maximum(probability[np.arange(n), truth], 1e-12)))),
        "expected_calibration_error_10_bins": ece,
        "per_class": per_class,
        "confusion_matrix_actual_rows": matrix.tolist(),
    }


def _cluster_interval(rows: list[EvaluatedRow], *, seed: int = 42, repeats: int = 300) -> dict[str, Any]:
    """Cluster-bootstrap accuracy by declared independent subject/group, not by photograph."""
    groups: dict[str, list[EvaluatedRow]] = defaultdict(list)
    for row in rows:
        groups[row.group_id].append(row)
    if len(groups) < 20:
        return {"available": False, "reason": "fewer_than_20_independent_groups"}
    keys = sorted(groups)
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(repeats):
        sample = rng.integers(0, len(keys), len(keys))
        draw = [row for index in sample for row in groups[keys[int(index)]]]
        values.append(sum(int(row.true_index == int(np.argmax(row.probabilities))) for row in draw) / len(draw))
    return {
        "available": True, "method": "group_cluster_bootstrap", "seed": seed,
        "repeats": repeats, "percentile_95": [float(x) for x in np.percentile(values, [2.5, 97.5])],
    }


def evaluate(rows: list[EvaluatedRow], manifest: EvaluationManifest) -> dict[str, Any]:
    test = [row for row in rows if row.split == "test"]
    summary = _metrics(test, manifest.ordered_labels)
    subgroups: dict[str, Any] = {}
    for field in ("skin_tone_group", "device_group"):
        groups: dict[str, list[EvaluatedRow]] = defaultdict(list)
        for row in test:
            if row.subgroups.get(field):
                groups[row.subgroups[field]].append(row)
        subgroups[field] = {
            name: {"count": len(group_rows), "accuracy": _metrics(group_rows, manifest.ordered_labels)["accuracy"]}
            for name, group_rows in sorted(groups.items()) if len(group_rows) >= 20
        }
    return {
        "report_version": "1",
        "status": "RESEARCH_ONLY_NOT_CLINICALLY_VALIDATED",
        "evaluation_id": manifest.evaluation_id,
        "model_sha256": manifest.model_sha256,
        "ordered_labels": list(manifest.ordered_labels),
        "label_provenance": manifest.label_provenance,
        "license_or_permission": manifest.license_or_permission,
        "collection_description": manifest.collection_description,
        "test_results": summary,
        "accuracy_interval": _cluster_interval(test),
        "subgroups_with_at_least_20_samples": subgroups,
        "split_counts": {split: sum(row.split == split for row in rows) for split in ("train", "calibration", "test")},
        "limitations": [
            "Ground truth and subject grouping require independent verification.",
            "No conclusions about clinical sensitivity, cancer screening, or public diagnostic safety.",
            "Skin-tone and device subgroups are descriptive and may be incomplete.",
            "Confidence is a model score, not clinical certainty.",
        ],
    }


def evaluate_files(manifest_path: Path, predictions_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    rows = load_predictions(predictions_path, manifest)
    report = evaluate(rows, manifest)
    report["predictions_file_sha256"] = hashlib.sha256(predictions_path.read_bytes()).hexdigest()
    return report


def save_report(path: Path, report: dict[str, Any]) -> None:
    if path.exists():
        raise FileExistsError("Refuse to overwrite an existing report")
    # Aggregated reporting: sample IDs, image paths and raw photographs are never serialized.
    path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
