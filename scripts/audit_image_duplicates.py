"""Run a local cross-split exact/near-duplicate audit on licensed image manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.duplicate_audit import scan_splits


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--manifest", type=Path, required=True)
    cli.add_argument("--image-root", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    cli.add_argument("--threshold-bits", type=int, default=5)
    args = cli.parse_args()
    report = scan_splits(args.manifest, args.image_root, distance_threshold=args.threshold_bits)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "total_images": report["total_images"],
                "near_candidates": len(report["cross_split_near_candidates"]),
                "report": str(args.out),
            }
        )
    )


if __name__ == "__main__":
    main()
