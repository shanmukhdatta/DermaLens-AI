"""Offline integrity tool, never downloads a checkpoint or claims clinical validity."""
from __future__ import annotations

import argparse
from pathlib import Path

from services.cv.artifacts import verify_artifacts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--load-model", action="store_true")
    args = parser.parse_args()
    verified = verify_artifacts(args.manifest, args.checkpoint, args.label_map)
    print(f"Checksums and metadata matched: {verified.model_id} {verified.version}")
    print(f"Model state: {verified.status} (not a clinical approval)")
    if args.load_model:
        from services.cv.keras_runtime import VerifiedKerasModel

        VerifiedKerasModel(args.manifest, args.checkpoint, args.label_map)
        print("Keras model deserialized and tensor shapes checked (not an accuracy test)")


if __name__ == "__main__":
    main()
