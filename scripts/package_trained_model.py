"""Create a candidate-only manifest from privately obtained research checkpoint metadata.

Never fabricates model weights, training provenance, label ordering, evaluation metrics
or approval. The caller must supply exact run and environment metadata.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from services.cv.artifacts import EXPECTED_CATEGORIES, file_sha256, verify_artifacts

ALLOWED_OBJECTS = frozenset({
    "ResNet50Preprocess", "DenseNet121Preprocess", "ViTPreprocess",
    "ExtractCLSToken", "FocalLoss",
})


def package_candidate(
    checkpoint: Path,
    label_map: Path,
    *,
    model_id: str,
    version: str,
    source_commit: str,
    training_run_id: str,
    python_version: str,
    tensorflow_version: str,
    keras_version: str,
    custom_objects: tuple[str, ...] = (),
) -> dict[str, object]:
    """Produce integrity metadata, not a trained/approved model."""
    if checkpoint.suffix != ".keras" or not checkpoint.is_file() or checkpoint.stat().st_size == 0:
        raise ValueError("A nonempty private .keras checkpoint file is required")
    if label_map.name != "label_map.json" or not label_map.is_file():
        raise ValueError("Exact label_map.json file is required")
    if not re.fullmatch(r"[a-z][a-z0-9-]+", model_id):
        raise ValueError("Invalid model identifier")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("Version must be semantic major.minor.patch")
    if not re.fullmatch(r"[a-f0-9]{40}", source_commit):
        raise ValueError("Source commit must be an actual 40-digit hexadecimal SHA")
    if any(not value.strip() for value in (
        training_run_id, python_version, tensorflow_version, keras_version,
    )):
        raise ValueError("Real training provenance and framework versions required")
    if set(custom_objects) - ALLOWED_OBJECTS or len(set(custom_objects)) != len(custom_objects):
        raise ValueError("Unsupported or repeated Keras custom objects")
    mapping = json.loads(label_map.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict) or set(mapping) != {str(i) for i in range(6)}:
        raise ValueError("Exact research index-to-label map must cover 0..5")
    names = [mapping[str(i)] for i in range(6)]
    if not all(isinstance(x, str) for x in names):
        raise ValueError("Invalid label data")
    normalized = {" ".join(x.lower().replace("_", " ").split()) for x in names}
    if len(normalized) != 6 or normalized != EXPECTED_CATEGORIES:
        raise ValueError("Checkpoint classes do not match research taxonomy")
    return {
        "schema_version": "1",
        "model_id": model_id,
        "version": version,
        "status": "candidate",
        "source_repository": "https://github.com/shanmukhdatta/Facial_Skin_Diesease",
        "source_commit": source_commit,
        "training_run_id": training_run_id,
        "framework": {
            "name": "tensorflow-keras",
            "python_version": python_version,
            "tensorflow_version": tensorflow_version,
            "keras_version": keras_version,
        },
        "checkpoint": {
            "uri": "private://" + checkpoint.name,
            "filename": checkpoint.name,
            "sha256": file_sha256(checkpoint),
        },
        "label_map": {
            "uri": "private://" + label_map.name,
            "filename": label_map.name,
            "sha256": file_sha256(label_map),
            "count": 6,
            "format": "index-to-class-json",
        },
        "input": {
            "shape": [None, 224, 224, 3],
            "color_space": "RGB",
            "dtype": "float32",
            "pixel_min": 0,
            "pixel_max": 255,
            "resize": "PIL_BILINEAR",
            "normalization": "model_internal",
        },
        "output": {"kind": "softmax_probabilities", "shape": [None, 6], "class_count": 6},
        "custom_objects": list(custom_objects),
        "preprocessing_version": "research-pil-bilinear-224-v1",
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint", required=True, type=Path)
    p.add_argument("--label-map", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--model-id", required=True)
    p.add_argument("--version", required=True)
    p.add_argument("--source-commit", required=True)
    p.add_argument("--training-run-id", required=True)
    p.add_argument("--python-version", required=True)
    p.add_argument("--tensorflow-version", required=True)
    p.add_argument("--keras-version", required=True)
    p.add_argument("--custom-object", action="append", default=[])
    args = p.parse_args()
    package = package_candidate(
        args.checkpoint, args.label_map,
        model_id=args.model_id, version=args.version,
        source_commit=args.source_commit, training_run_id=args.training_run_id,
        python_version=args.python_version,
        tensorflow_version=args.tensorflow_version, keras_version=args.keras_version,
        custom_objects=tuple(args.custom_object),
    )
    if args.out.exists():
        p.error("Output already exists; do not silently replace a manifest")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    verify_artifacts(args.out, args.checkpoint, args.label_map)
    print("Candidate manifest verified by SHA256 and class map; checkpoint load NOT tested.")
    print("Clinical evaluation and approval: NOT performed.")


if __name__ == "__main__":
    main()
