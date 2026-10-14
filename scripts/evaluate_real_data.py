"""CLI for real-world, research-only held-out model evaluation."""
from __future__ import annotations

import argparse
from pathlib import Path

from services.evaluation.metrics import evaluate_files, save_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate independent real test predictions")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = evaluate_files(args.manifest, args.predictions)
    save_report(args.output, report)
    print("Research-only aggregate report written; NOT clinical validation.")
    print(f"Real held-out test cases: {report['test_results']['count']}")


if __name__ == "__main__":
    main()
