"""Write a research-only candidate-versus-baseline regression report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.evaluation import read_table
from services.learning.promotion import compare_candidate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    label_map = json.loads(args.label_map.read_text(encoding="utf-8"))
    if not isinstance(label_map, dict) or set(label_map) != {str(i) for i in range(6)}:
        parser.error("Exact research label map is required")
    labels = tuple(label_map[str(i)] for i in range(6))
    result = compare_candidate(
        read_table(args.baseline), read_table(args.candidate), labels
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(result["review_state"])
    print("No model weights, staging flags or serving registry state were changed.")


if __name__ == "__main__":
    main()
