"""Research-only promotion comparison; does not write to the deployed model registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.promotion import compare_candidates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in (
        "baseline-csv", "candidate-csv", "baseline-checkpoint", "candidate-checkpoint",
        "label-map", "policy", "output",
    ):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    report = compare_candidates(
        baseline_csv=args.baseline_csv, candidate_csv=args.candidate_csv,
        baseline_checkpoint=args.baseline_checkpoint,
        candidate_checkpoint=args.candidate_checkpoint,
        label_map_path=args.label_map, policy_path=args.policy,
    )
    if args.output.exists():
        raise FileExistsError("Refusing to overwrite a previous review report")
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Research candidate review: {report['decision']}")
    print("No deployed model was modified. Clinical release remains unauthorized.")


if __name__ == "__main__":
    main()
