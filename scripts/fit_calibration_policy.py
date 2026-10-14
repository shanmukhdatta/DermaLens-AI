"""Fit a non-deployable offline calibration experiment from a private prediction CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.calibration import fit_exploratory_policy
from services.learning.evaluation import read_table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target-error", type=float, default=0.10)
    arguments = parser.parse_args()
    label_map = json.loads(arguments.label_map.read_text(encoding="utf-8"))
    if not isinstance(label_map, dict) or set(label_map) != {str(i) for i in range(6)}:
        parser.error("Verified six-category label map is required")
    labels = tuple(label_map[str(i)] for i in range(6))
    candidate = fit_exploratory_policy(
        read_table(arguments.predictions), labels, target_error=arguments.target_error
    )
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(candidate.payload(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Saved research-only calibration candidate, not an approved clinical policy")


if __name__ == "__main__":
    main()
