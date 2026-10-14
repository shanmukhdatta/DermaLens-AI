"""Strict input validation, provenance and split-leakage checks for offline evaluation."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

HASH = re.compile(r"^[a-f0-9]{64}$")
ALLOWED_SPLITS = frozenset({"train", "calibration", "test"})
ALLOWED_SOURCES = frozenset({"real", "synthetic"})
IDENTIFIER_COLUMNS = (
    "sample_id", "group_id", "image_sha256", "split", "source", "true_label"
)
SUBGROUPS = ("skin_tone_group", "device_group")


@dataclass(frozen=True)
class EvaluationManifest:
    evaluation_id: str
    model_sha256: str
    ordered_labels: tuple[str, ...]
    label_provenance: str
    license_or_permission: str
    collection_description: str


@dataclass(frozen=True)
class EvaluatedRow:
    sample_id: str
    group_id: str
    image_sha256: str
    split: str
    source: str
    true_index: int
    probabilities: tuple[float, ...]
    subgroups: dict[str, str]


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 1000:
        raise ValueError(f"Missing or invalid {field}")
    return value.strip()


def load_manifest(path: Path) -> EvaluationManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Evaluation manifest must be an object")
    for field in (
        "authorized_for_evaluation", "independent_real_data",
        "disjoint_subject_groups", "locked_test_split",
    ):
        if data.get(field) is not True:
            raise ValueError(f"Evaluation declaration not satisfied: {field}")
    labels = data.get("ordered_labels")
    if (
        not isinstance(labels, list) or len(labels) != 6
        or not all(isinstance(value, str) and value.strip() for value in labels)
        or len(set(labels)) != 6
    ):
        raise ValueError("Expected six distinct labels in verified model order")
    model_sha256 = _nonempty(data.get("model_sha256"), "model_sha256")
    if not HASH.fullmatch(model_sha256):
        raise ValueError("Expected a real checkpoint SHA256 fingerprint")
    return EvaluationManifest(
        evaluation_id=_nonempty(data.get("evaluation_id"), "evaluation_id"),
        model_sha256=model_sha256,
        ordered_labels=tuple(labels),
        label_provenance=_nonempty(data.get("label_provenance"), "label_provenance"),
        license_or_permission=_nonempty(data.get("license_or_permission"), "license_or_permission"),
        collection_description=_nonempty(
            data.get("collection_description"), "collection_description"
        ),
    )


def load_predictions(path: Path, manifest: EvaluationManifest) -> list[EvaluatedRow]:
    expected = set(IDENTIFIER_COLUMNS) | set(SUBGROUPS) | {
        f"p_{i}" for i in range(len(manifest.ordered_labels))
    }
    rows: list[EvaluatedRow] = []
    by_sample: set[str] = set()
    by_hash: dict[str, str] = {}
    by_group: dict[str, str] = {}
    with path.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Missing or repeated CSV headers")
        if set(reader.fieldnames) != expected:
            raise ValueError("CSV column contract mismatch; raw image paths are prohibited")
        for line_no, item in enumerate(reader, start=2):
            if line_no > 200002:
                raise ValueError("Evaluation input exceeds configured sample count")
            if None in item or any(value is None for value in item.values()):
                raise ValueError("Malformed CSV row")
            sample = _nonempty(item["sample_id"], "sample_id")
            group = _nonempty(item["group_id"], "group_id")
            digest = _nonempty(item["image_sha256"], "image_sha256")
            split = _nonempty(item["split"], "split")
            source_name = _nonempty(item["source"], "source")
            label = _nonempty(item["true_label"], "true_label")
            if sample in by_sample:
                raise ValueError("Duplicate sample identifier")
            by_sample.add(sample)
            if not HASH.fullmatch(digest):
                raise ValueError("Invalid image content fingerprint")
            if split not in ALLOWED_SPLITS or source_name not in ALLOWED_SOURCES:
                raise ValueError("Invalid source or split")
            if split == "test" and source_name != "real":
                raise ValueError("Held-out evaluation must contain independently labeled real images")
            if label not in manifest.ordered_labels:
                raise ValueError("Unknown or incorrectly ordered ground-truth label")
            if digest in by_hash and by_hash[digest] != split:
                raise ValueError("Image content leak across dataset splits")
            if group in by_group and by_group[group] != split:
                raise ValueError("Group or subject leak across dataset splits")
            by_hash[digest] = split
            by_group[group] = split
            try:
                probabilities = tuple(float(item[f"p_{i}"]) for i in range(6))
            except (TypeError, ValueError) as exc:
                raise ValueError("Non-numeric model scores") from exc
            arr = np.asarray(probabilities, dtype=np.float64)
            if (
                not np.all(np.isfinite(arr)) or np.any(arr < 0.0)
                or np.any(arr > 1.0) or not np.isclose(arr.sum(), 1.0, atol=1e-3)
            ):
                raise ValueError("Invalid probability distribution")
            subgroups = {name: item[name].strip() for name in SUBGROUPS}
            rows.append(EvaluatedRow(
                sample, group, digest, split, source_name,
                manifest.ordered_labels.index(label), probabilities, subgroups,
            ))
    if not any(row.split == "test" for row in rows):
        raise ValueError("No independently held-out real test cases")
    return rows
