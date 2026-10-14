"""Export real Keras predictions offline without copying private photographs to GitHub.

Requires an explicitly authorized, locked dataset manifest and verified model
artifact. Output contains only pseudonymous metadata and model probabilities.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image

from services.cv.artifacts import file_sha256, preprocess_compatible, verify_artifacts
from services.learning.evaluation import PROB_COLUMNS, REQUIRED, audit_rows

if TYPE_CHECKING:
    from services.cv.artifacts import VerifiedArtifacts
    from services.cv.ports import ModelRuntime

INDEX_COLUMNS = {
    "example_id", "subject_id", "content_sha256", "split", "source",
    "label", "skin_tone_group", "device_group", "relative_image_path"
}
MAX_FILES = 100000


def validate_dataset_permission(manifest: Path, verified: VerifiedArtifacts) -> None:
    """Statements are supplied by the data steward; software cannot certify licenses."""
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("Evaluation governance manifest must be a JSON object")
    for field in ("rights_verified", "labels_independently_verified", "locked_test_split"):
        if doc.get(field) is not True:
            raise ValueError(f"Missing evaluation governance approval: {field}")
    for field in ("evaluation_id", "dataset_provenance", "permission_reference", "label_method"):
        if not isinstance(doc.get(field), str) or not doc[field].strip():
            raise ValueError(f"Missing evaluation provenance: {field}")
    if doc.get("checkpoint_sha256") != file_sha256(verified.checkpoint_path):
        raise ValueError("Evaluation manifest checkpoint hash does not match verified model")


def read_private_index(index_path: Path) -> list[dict[str, str]]:
    with index_path.open("r", newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or set(reader.fieldnames) != INDEX_COLUMNS:
            raise ValueError("Private index column contract mismatch")
        if len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise ValueError("Duplicate private index headers")
        rows = list(reader)
    if not rows or len(rows) > MAX_FILES:
        raise ValueError("Private evaluation dataset must have 1–100000 rows")
    for row in rows:
        if None in row or any(value is None or not value.strip() for value in row.values()):
            raise ValueError("Malformed or incomplete private evaluation row")
        if row["split"] == "test" and row["source"] != "real":
            raise ValueError("Held-out model evaluation requires approved real photos")
    return rows


def export_predictions(
    *, model_manifest: Path, checkpoint: Path, label_map: Path,
    dataset_manifest: Path, index_path: Path, image_root: Path,
    output: Path, runtime: ModelRuntime | None = None,
) -> int:
    """Fully validate inputs before exclusively creating an owner-only CSV."""
    if output.exists():
        raise FileExistsError("Never overwrite existing private model predictions")
    verified = verify_artifacts(model_manifest, checkpoint, label_map)
    validate_dataset_permission(dataset_manifest, verified)
    index = read_private_index(index_path)
    root = image_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Private evaluation image root must be a directory")

    if runtime is None:
        from services.cv.keras_runtime import VerifiedKerasModel
        runtime = VerifiedKerasModel(model_manifest, checkpoint, label_map)
    output_rows: list[dict[str, str]] = []
    for entry in index:
        rel = Path(entry["relative_image_path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Private evaluation image path escapes dataset root")
        image_path = (root / rel).resolve(strict=True)
        if root not in image_path.parents or not image_path.is_file():
            raise ValueError("Private evaluation image is not within allowed directory")
        if file_sha256(image_path) != entry["content_sha256"]:
            raise ValueError("Evaluation image SHA256 differs from dataset index")
        with Image.open(image_path) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                raise ValueError("Unsupported private evaluation image format")
            if getattr(source, "n_frames", 1) != 1 or max(source.size) > 4096:
                raise ValueError("Unsupported private evaluation image shape or frame count")
            model_input = preprocess_compatible(source)
        prediction = runtime.predict(model_input)
        if prediction.ordered_labels != verified.ordered_labels:
            raise ValueError("Model output label order differs from verified package")
        if prediction.model_version != verified.version:
            raise ValueError("Model output version differs from verified package")
        row = {key: entry[key] for key in INDEX_COLUMNS if key != "relative_image_path"}
        row["model_version"] = prediction.model_version
        row.update({
            key: format(float(score), ".10g")
            for key, score in zip(PROB_COLUMNS, prediction.probabilities, strict=True)
        })
        output_rows.append(row)

    ordered_labels = verified.ordered_labels
    audit_rows(output_rows, ordered_labels)
    # No direct identifiers or source paths written. Private permissions at creation.
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=sorted(REQUIRED))
        writer.writeheader()
        writer.writerows(output_rows)
    return len(output_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce private real-model evaluation CSV")
    for key in (
        "model-manifest", "checkpoint", "label-map", "dataset-manifest",
        "index-path", "image-root", "output",
    ):
        parser.add_argument(f"--{key}", type=Path, required=True)
    opts = parser.parse_args()
    count = export_predictions(
        model_manifest=opts.model_manifest,
        checkpoint=opts.checkpoint,
        label_map=opts.label_map,
        dataset_manifest=opts.dataset_manifest,
        index_path=opts.index_path,
        image_root=opts.image_root,
        output=opts.output,
    )
    print(f"Exported {count} private model predictions. Not a clinical evaluation.")
    print("Do not commit the CSV or source photographs to a public repository.")


if __name__ == "__main__":
    main()
