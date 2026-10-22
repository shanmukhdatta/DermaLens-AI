"""Compare an integrity-verified Keras adapter to original predictor reference scores.

No network calls, clinical diagnosis, automatic model promotion or private image export.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from services.cv.artifacts import file_sha256, preprocess_compatible
from services.cv.keras_runtime import VerifiedKerasModel
from services.cv.parity import verify_prediction_parity


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--label-map", type=Path, required=True)
    p.add_argument("--image", type=Path, required=True)
    p.add_argument("--reference-json", type=Path, required=True)
    p.add_argument("--atol", type=float, default=1e-5)
    p.add_argument("--out", type=Path)
    args = p.parse_args()

    runtime = VerifiedKerasModel(args.manifest, args.checkpoint, args.label_map)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    reference = json.loads(args.reference_json.read_text(encoding="utf-8"))
    if not isinstance(reference, dict):
        p.error("Reference must be a JSON object")
    with Image.open(args.image) as image:
        batch = preprocess_compatible(image)
    prediction = runtime.predict(batch)
    report = verify_prediction_parity(
        reference, prediction,
        source_commit=manifest["source_commit"],
        image_sha256=file_sha256(args.image),
        checkpoint_sha256=file_sha256(args.checkpoint),
        atol=args.atol,
    )
    if args.out:
        if args.out.exists():
            p.error("Report path already exists")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Software inference parity: PASS. Clinical accuracy: NOT VERIFIED.")


if __name__ == "__main__":
    main()
