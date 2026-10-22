"""Export trusted research predictor scores for later offline service parity testing.

Must run in the original research repository's trusted TensorFlow environment.
Does NOT publish a clinical dataset, medical performance, or an approved model.
"""
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from services.cv.artifacts import file_sha256


def export_reference(
    research_repo: Path, checkpoint: Path, label_map: Path, image: Path
) -> dict[str, object]:
    if not (research_repo / "src" / "inference" / "predictor.py").is_file():
        raise ValueError("An exact local clone of the research repository is required")
    commit = subprocess.check_output(
        ["git", "-C", str(research_repo), "rev-parse", "HEAD"],
        text=True, stderr=subprocess.DEVNULL, timeout=10,
    ).strip()
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        raise ValueError("Cannot establish source commit provenance")
    if not checkpoint.is_file() or not image.is_file() or not label_map.is_file():
        raise ValueError("Missing private model, image or label map")
    sys.path.insert(0, str(research_repo.resolve()))
    predictor_module = importlib.import_module("src.inference.predictor")
    predictor = predictor_module.DiseasePredictor(
        model_path=checkpoint, label_map=label_map, img_size=224,
    )
    _, _, probabilities = predictor.predict_image(image)
    ordered_labels = [predictor.label_map[index] for index in range(6)]
    vector = np.asarray(probabilities, dtype=float).reshape(-1)
    if (
        vector.shape != (6,)
        or not np.isfinite(vector).all()
        or np.any(vector < 0)
        or np.any(vector > 1)
        or not np.isclose(vector.sum(), 1.0, atol=1e-4)
    ):
        raise ValueError("Original research predictor produced malformed probabilities")
    return {
        "source_commit": commit,
        "checkpoint_sha256": file_sha256(checkpoint),
        "image_sha256": file_sha256(image),
        "ordered_labels": ordered_labels,
        "probabilities": [float(v) for v in vector],
        "medical_diagnosis": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--research-repo", required=True, type=Path)
    p.add_argument("--checkpoint", required=True, type=Path)
    p.add_argument("--label-map", required=True, type=Path)
    p.add_argument("--image", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    if args.out.exists():
        p.error("Output already exists")
    result = export_reference(
        args.research_repo, args.checkpoint, args.label_map, args.image,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Private reference scores exported. This is NOT clinical validation.")


if __name__ == "__main__":
    main()
