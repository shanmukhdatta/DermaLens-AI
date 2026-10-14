"""Compare two previously aggregated authorized research cohorts offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.drift import PopulationSummary, compare_populations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--current", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    arguments = parser.parse_args()
    report = compare_populations(
        PopulationSummary.from_file(arguments.baseline),
        PopulationSummary.from_file(arguments.current),
    )
    if arguments.out.exists():
        raise FileExistsError("Refuse to overwrite existing research report")
    arguments.out.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print("Aggregate research drift review:", report["status"])
    print("No automatic model retraining, diagnostic claim or deployment occurred.")


if __name__ == "__main__":
    main()
