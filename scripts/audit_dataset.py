"""Run a non-identifying structural and duplicate audit over image manifests."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

from services.learning.leakage_audit import DatasetRecord, audit_dataset


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--threshold", type=int, default=5)
    args = parser.parse_args()
    with args.manifest.open(newline="", encoding="utf-8-sig") as stream:
        data = list(csv.DictReader(stream))
    fields = {"relative_path", "split", "label", "source", "subject_group"}
    if not data or not fields.issubset(data[0]):
        parser.error("CSV requires relative_path, split, label, source and subject_group")
    rows = [
        DatasetRecord(
            relative_path=x["relative_path"],
            split=cast(Any, x["split"]), label=x["label"],
            source=cast(Any, x["source"]),
            subject_group=x["subject_group"] or None,
        )
        for x in data
    ]
    outcome = audit_dataset(rows, args.root, hamming_threshold=args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(asdict(outcome), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "records": outcome.records, "review_flags": len(outcome.warnings),
        "possible_cross_split_pairs": len(outcome.review_pair_tokens),
        "independent_test_cleared": outcome.independent_test_cleared,
    }, sort_keys=True))
    return 1 if outcome.warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
