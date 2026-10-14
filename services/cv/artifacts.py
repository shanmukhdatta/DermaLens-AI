"""Strict offline checkpoint/label integrity and research preprocessing contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

EXPECTED_CATEGORIES = frozenset(
    {"acne", "fungal infection", "hyperpigmentation", "normal skin", "skin cancer", "vitiligo"}
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for data in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def _category_key(value: str) -> str:
    return " ".join(value.replace("_", " ").lower().strip().split())


@dataclass(frozen=True)
class VerifiedArtifacts:
    model_id: str
    version: str
    status: str
    checkpoint_path: Path
    label_map_path: Path
    ordered_labels: tuple[str, ...]
    custom_objects: tuple[str, ...]


def verify_artifacts(
    manifest_path: Path, checkpoint_path: Path, label_map_path: Path
) -> VerifiedArtifacts:
    """Never download arbitrary manifest URIs or guess trained weights."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object")
    expected = {
        "schema_version": "1",
        "source_repository": "https://github.com/shanmukhdatta/Facial_Skin_Diesease",
    }
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("Unsupported model manifest or research provenance")
    if (
        not isinstance(manifest.get("source_commit"), str)
        or len(manifest["source_commit"]) != 40
        or any(char not in "0123456789abcdef" for char in manifest["source_commit"])
    ):
        raise ValueError("Missing verified research commit")
    if manifest.get("status") not in {"candidate", "staging", "approved"}:
        raise ValueError("Unavailable model lifecycle state")
    framework = manifest.get("framework")
    if (
        not isinstance(framework, dict)
        or framework.get("name") != "tensorflow-keras"
        or any(
            not framework.get(name)
            for name in ("python_version", "tensorflow_version", "keras_version")
        )
        or not manifest.get("preprocessing_version")
    ):
        raise ValueError("Incomplete training environment metadata")
    checkpoint = manifest.get("checkpoint", {})
    mapping = manifest.get("label_map", {})
    if not isinstance(checkpoint, dict) or not isinstance(mapping, dict):
        raise ValueError("Missing artifact metadata")
    if checkpoint.get("filename") != checkpoint_path.name or not checkpoint_path.name.endswith(
        ".keras"
    ):
        raise ValueError("Checkpoint name does not match manifest")
    if mapping.get("filename") != label_map_path.name or label_map_path.name != "label_map.json":
        raise ValueError("Label map filename is not verified")
    if file_sha256(checkpoint_path) != checkpoint.get("sha256"):
        raise ValueError("Checkpoint integrity verification failed")
    if file_sha256(label_map_path) != mapping.get("sha256"):
        raise ValueError("Label mapping integrity verification failed")
    inputs = manifest.get("input")
    outputs = manifest.get("output")
    required_input = {
        "shape": [None, 224, 224, 3],
        "color_space": "RGB",
        "dtype": "float32",
        "pixel_min": 0,
        "pixel_max": 255,
        "resize": "PIL_BILINEAR",
        "normalization": "model_internal",
    }
    if not isinstance(inputs, dict) or any(inputs.get(k) != v for k, v in required_input.items()):
        raise ValueError("Model input preprocessing is incompatible")
    if (
        not isinstance(outputs, dict)
        or outputs.get("shape") != [None, 6]
        or outputs.get("class_count") != 6
        or outputs.get("kind") != "softmax_probabilities"
    ):
        raise ValueError("Model output incompatible with six-class research head")
    labels: Any = json.loads(label_map_path.read_text(encoding="utf-8"))
    if not isinstance(labels, dict) or set(labels) != {str(i) for i in range(6)}:
        raise ValueError("Label indices must cover 0..5")
    ordered = tuple(labels[str(i)] for i in range(6))
    if not all(isinstance(item, str) and item for item in ordered):
        raise ValueError("Invalid label")
    if frozenset(_category_key(name) for name in ordered) != EXPECTED_CATEGORIES:
        raise ValueError("The model's six categories do not match the documented head")
    if mapping.get("count") != 6 or mapping.get("format") != "index-to-class-json":
        raise ValueError("Label mapping manifest is invalid")
    custom: Any = manifest.get("custom_objects")
    allowed = {
        "ResNet50Preprocess",
        "DenseNet121Preprocess",
        "ViTPreprocess",
        "ExtractCLSToken",
        "FocalLoss",
    }
    if not isinstance(custom, list) or any(
        not isinstance(x, str) or x not in allowed for x in custom
    ):
        raise ValueError("Unsupported serialized model objects")
    model_id = manifest.get("model_id")
    version = manifest.get("version")
    if not isinstance(model_id, str) or not model_id or not isinstance(version, str) or not version:
        raise ValueError("Missing model identity")
    return VerifiedArtifacts(
        model_id=model_id,
        version=version,
        status=manifest["status"],
        checkpoint_path=checkpoint_path,
        label_map_path=label_map_path,
        ordered_labels=ordered,
        custom_objects=tuple(custom),
    )


def preprocess_compatible(image: Image.Image) -> np.ndarray:
    """Exact original predictor: RGB, PIL bilinear 224, float32 0..255, 1 batch."""
    rgb = image.convert("RGB").resize((224, 224), Image.Resampling.BILINEAR)
    rgb_f32 = np.asarray(rgb, dtype=np.float32)
    return np.clip(rgb_f32, 0.0, 255.0)[None, ...]
