"""Evaluate an offline metadata/probability CSV; no image uploads or clinical claims."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.evaluation import evaluate, read_table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    mapping = json.loads(args.label_map.read_text(encoding="utf-8"))
    if not isinstance(mapping, dict) or set(mapping) != {str(i) for i in range(6)}:
        parser.error("Exact six-index label map required")
    labels = tuple(mapping[str(i)] for i in range(6))
    report = evaluate(read_table(args.predictions), labels)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Research evaluation written: {args.out}; clinical validation: false")


if __name__ == "__main__":
    main()
