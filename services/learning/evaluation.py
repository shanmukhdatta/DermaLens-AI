"""Offline prediction-table audit and honest research metrics; never clinical validation."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from services.cv.artifacts import EXPECTED_CATEGORIES

SPLITS = {"train", "calibration", "test"}
SOURCES = {"real", "synthetic", "fixture"}
PROB_COLUMNS = tuple(f"prob_{i}" for i in range(6))
REQUIRED = frozenset(
    {
        "example_id",
        "subject_id",
        "content_sha256",
        "split",
        "source",
        "label",
        "model_version",
        "skin_tone_group",
        "device_group",
        *PROB_COLUMNS,
    }
)


def _normalize_label(label: str) -> str:
    return " ".join(label.replace("_", " ").lower().strip().split())


def read_table(path: Path) -> list[dict[str, str]]:
    """Read metadata and predictions only; no raw images or paths."""
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or not REQUIRED.issubset(set(reader.fieldnames)):
            raise ValueError("Prediction table missing required column(s)")
        if {"image_path", "filename", "raw_image", "email", "name"} & set(reader.fieldnames):
            raise ValueError(
                "Prediction metadata must not include direct identifiers or image paths"
            )
        return [dict(row) for row in reader]


def audit_rows(rows: list[dict[str, str]], ordered_labels: tuple[str, ...]) -> None:
    """Reject leakage, incompatible label maps, corrupt predictions and mixed versions."""
    if (
        len(ordered_labels) != 6
        or {_normalize_label(v) for v in ordered_labels} != EXPECTED_CATEGORIES
    ):
        raise ValueError("Exact six-category research mapping is required")
    if not rows or not any(row["split"] == "test" for row in rows):
        raise ValueError("At least one held-out test record is required")
    example_ids: set[str] = set()
    subjects: dict[str, str] = {}
    content_hashes: dict[str, str] = {}
    versions: set[str] = set()
    accepted_labels = set(ordered_labels)
    for row in rows:
        if row["split"] not in SPLITS or row["source"] not in SOURCES:
            raise ValueError("Invalid split or source")
        if row["label"] not in accepted_labels or not row["model_version"]:
            raise ValueError("Invalid label or missing model version")
        versions.add(row["model_version"])
        sample_id = row["example_id"]
        subject = row["subject_id"]
        checksum = row["content_sha256"]
        if (
            not sample_id
            or not subject
            or len(checksum) != 64
            or any(ch not in "0123456789abcdef" for ch in checksum)
        ):
            raise ValueError("Invalid sample, subject group, or content hash")
        if sample_id in example_ids:
            raise ValueError("Duplicate example ID")
        example_ids.add(sample_id)
        for item, table in ((subject, subjects), (checksum, content_hashes)):
            old_split = table.setdefault(item, row["split"])
            if old_split != row["split"]:
                raise ValueError("Leakage: subject or image content crosses dataset splits")
        try:
            values = np.asarray([float(row[col]) for col in PROB_COLUMNS], dtype=float)
        except (TypeError, ValueError, KeyError) as exc:
            raise ValueError("Invalid probability vector") from exc
        if (
            not np.isfinite(values).all()
            or np.any(values < 0)
            or np.any(values > 1)
            or not np.isclose(values.sum(), 1.0, atol=1e-4, rtol=1e-4)
        ):
            raise ValueError("Invalid probability distribution")
    if len(versions) != 1:
        raise ValueError("Do not combine different model versions in one report")


def _stats(rows: list[dict[str, str]], labels: tuple[str, ...]) -> dict[str, Any]:
    y_true = np.asarray([labels.index(x["label"]) for x in rows], dtype=int)
    prob = np.asarray([[float(x[k]) for k in PROB_COLUMNS] for x in rows])
    prediction = np.argmax(prob, axis=1)
    correct = prediction == y_true
    total = len(rows)
    class_metrics = {}
    per_class_f1 = []
    for cls_idx, name in enumerate(labels):
        tp = int(np.sum((prediction == cls_idx) & (y_true == cls_idx)))
        fp = int(np.sum((prediction == cls_idx) & (y_true != cls_idx)))
        fn = int(np.sum((prediction != cls_idx) & (y_true == cls_idx)))
        support = int(np.sum(y_true == cls_idx))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
        per_class_f1.append(f1)
        class_metrics[name] = {
            "support": support,
            "precision": round(precision, 5),
            "recall": round(recall, 5),
            "f1": round(f1, 5),
        }

    confidence = prob.max(axis=1)
    bins = np.minimum((confidence * 10).astype(int), 9)
    ece = 0.0
    for i in range(10):
        selected = bins == i
        if selected.any():
            ece += float(
                selected.mean() * abs(confidence[selected].mean() - correct[selected].mean())
            )
    one_hot = np.eye(len(labels))[y_true]
    brier = float(np.mean(np.sum((prob - one_hot) ** 2, axis=1)))
    nll = float(-np.mean(np.log(np.clip(prob[np.arange(total), y_true], 1e-12, 1))))
    exploratory = {}
    for threshold in (0.5, 0.7, 0.9):
        selected = confidence >= threshold
        covered = int(selected.sum())
        exploratory[str(threshold)] = {
            "coverage": round(covered / total, 5),
            "error_rate_if_selected": round(float(1 - correct[selected].mean()), 5)
            if covered
            else None,
        }
    return {
        "n": total,
        "accuracy": round(float(correct.mean()), 5),
        "macro_f1": round(float(np.mean(per_class_f1)), 5),
        "brier_multiclass": round(brier, 5),
        "negative_log_likelihood": round(nll, 5),
        "ece_10_bins_exploratory": round(ece, 5),
        "per_class": class_metrics,
        "exploratory_selective_risk_not_deployment_thresholds": exploratory,
    }


def evaluate(rows: list[dict[str, str]], labels: tuple[str, ...]) -> dict[str, Any]:
    """Report held-out metrics with provenance and conservative subgroup suppression."""
    audit_rows(rows, labels)
    test = [r for r in rows if r["split"] == "test"]
    metrics = _stats(test, labels)
    by_source = Counter(row["source"] for row in test)
    subgroups: dict[str, dict[str, Any]] = {}
    for attribute in ("source", "skin_tone_group", "device_group"):
        groups: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
        for row in test:
            groups[row[attribute] or "unreported"].append(row)
        subgroups[attribute] = {}
        for group, subset in sorted(groups.items()):
            if len(subset) < 10:
                subgroups[attribute][group] = {"n": len(subset), "suppressed": True}
            else:
                reduced = _stats(subset, labels)
                subgroups[attribute][group] = {
                    "n": len(subset),
                    "accuracy": reduced["accuracy"],
                    "macro_f1": reduced["macro_f1"],
                }
    warnings = ["Research metrics do not establish clinical validity."]
    if set(by_source) != {"real"}:
        warnings.append("Test partition is not exclusively real-world images.")
    if len({r["subject_id"] for r in test}) < 30:
        warnings.append("Fewer than 30 independent held-out subject groups; intervals omitted.")
        accuracy_interval = None
    else:
        # Cluster bootstrap by person/group, not by images from the same subject.
        grouped: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
        for row in test:
            grouped[row["subject_id"]].append(row)
        members = list(grouped.values())
        rng = np.random.default_rng(42)
        trials = []
        for _ in range(400):
            indices = rng.integers(0, len(members), size=len(members))
            sample = [row for i in indices for row in members[int(i)]]
            trials.append(_stats(sample, labels)["accuracy"])
        accuracy_interval = [
            round(float(np.quantile(trials, 0.025)), 5),
            round(float(np.quantile(trials, 0.975)), 5),
        ]
    return {
        "report_type": "research_evaluation_only",
        "clinical_use_validated": False,
        "model_version": rows[0]["model_version"],
        "splits": dict(Counter(row["split"] for row in rows)),
        "held_out_sources": dict(by_source),
        "held_out_subject_groups": len({r["subject_id"] for r in test}),
        "metrics": metrics,
        "accuracy_95pct_subject_bootstrap_interval": accuracy_interval,
        "subgroups_min_n_10": subgroups,
        "warnings": warnings,
    }
