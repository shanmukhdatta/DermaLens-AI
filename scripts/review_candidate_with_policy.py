"""Apply an external checkpoint-bound review policy to the Phase 13 research gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.learning.review_policy import evaluate_with_policy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for field in (
        "baseline-path", "candidate-path", "label-map-path",
        "baseline-checkpoint", "candidate-checkpoint", "policy-path", "output",
    ):
        parser.add_argument(f"--{field}", type=Path, required=True)
    a = parser.parse_args()
    report = evaluate_with_policy(
        baseline_path=a.baseline_path,
        candidate_path=a.candidate_path,
        label_map_path=a.label_map_path,
        baseline_checkpoint=a.baseline_checkpoint,
        candidate_checkpoint=a.candidate_checkpoint,
        policy_path=a.policy_path,
    )
    if a.output.exists():
        raise FileExistsError("Do not overwrite an existing candidate review report")
    a.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(report["decision"])
    print("Model promotion and clinical use remain disabled.")


if __name__ == "__main__":
    main()
