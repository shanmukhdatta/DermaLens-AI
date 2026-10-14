"""Offline private-image inference exporter using one checksum-verified real Keras checkpoint.

Only run against legally acquired, independently verified private data.
Never upload generated per-image probabilities or source data to public Git.
"""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path

from PIL import Image

from services.cv.artifacts import file_sha256, preprocess_compatible, verify_artifacts
from services.cv.keras_runtime import VerifiedKerasModel
from services.evaluation.audit import IDENTIFIER_COLUMNS, SUBGROUPS, load_manifest


def export_predictions(
    *, evaluation_manifest: Path, dataset_csv: Path, image_root: Path,
    model_manifest: Path, checkpoint: Path, label_map: Path, output: Path
) -> int:
    if output.exists():
        raise FileExistsError("Refusing to overwrite private predictions")
    metadata = load_manifest(evaluation_manifest)
    verified = verify_artifacts(model_manifest, checkpoint, label_map)
    if verified.ordered_labels != metadata.ordered_labels:
        raise ValueError("Evaluation class order does not match verified Keras model")
    if file_sha256(checkpoint) != metadata.model_sha256:
        raise ValueError("Evaluation manifest does not identify the supplied checkpoint")
    with dataset_csv.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        expected = set(IDENTIFIER_COLUMNS) | set(SUBGROUPS) | {"image_rel_path"}
        if reader.fieldnames is None or set(reader.fieldnames) != expected:
            raise ValueError("Private dataset CSV column contract mismatch")
        records = list(reader)
    if not records or len(records) > 200000:
        raise ValueError("Dataset size outside allowed bounds")
    resolved_root = image_root.resolve(strict=True)
    # Load checkpoint only after metadata and class order validation.
    runtime = VerifiedKerasModel(model_manifest, checkpoint, label_map)
    rows: list[dict[str, str]] = []
    names = [*IDENTIFIER_COLUMNS, *SUBGROUPS, *(f"p_{i}" for i in range(6))]
    for entry in records:
        raw_path = entry.get("image_rel_path", "")
        rel = Path(raw_path)
        if not raw_path or rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Image path must remain inside the private evaluation root")
        image_path = (resolved_root / rel).resolve(strict=True)
        if resolved_root not in image_path.parents or not image_path.is_file():
            raise ValueError("Private evaluation image escapes the allowed root")
        if file_sha256(image_path) != entry["image_sha256"]:
            raise ValueError("Image content fingerprint differs from declared dataset")
        with Image.open(image_path) as image:
            if image.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("Evaluation image uses an unsupported format")
            values = preprocess_compatible(image)
        output_prediction = runtime.predict(values)
        row = {name: entry[name] for name in (*IDENTIFIER_COLUMNS, *SUBGROUPS)}
        row.update({f"p_{i}": format(score, ".10g")
                    for i, score in enumerate(output_prediction.probabilities)})
        rows.append(row)
    # Use exclusive creation with owner-only permissions; never print image paths.
    fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Export private real checkpoint scores offline")
    for name in (
        "evaluation-manifest", "dataset-csv", "image-root",
        "model-manifest", "checkpoint", "label-map", "output"
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    arguments = parser.parse_args()
    n = export_predictions(
        evaluation_manifest=arguments.evaluation_manifest,
        dataset_csv=arguments.dataset_csv, image_root=arguments.image_root,
        model_manifest=arguments.model_manifest, checkpoint=arguments.checkpoint,
        label_map=arguments.label_map, output=arguments.output,
    )
    print(f"Exported {n} private prediction rows (no photos or path fields in output).")
    print("Do not commit this CSV. Model scores are not clinical probabilities.")


if __name__ == "__main__":
    main()
