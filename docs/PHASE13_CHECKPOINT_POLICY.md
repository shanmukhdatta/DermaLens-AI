# Phase 13 follow-up — checkpoint-bound review policy

This supplements the canonical Phase 13 PR's consent-gated curation and offline regression checks. It **does not** add a second promotion engine or deployment path.

The new `review_candidate_with_policy` CLI uses that existing `compare_candidate` function, then adds a private, versioned, human-configured evaluation policy containing:
- `policy_version: "1"`
- `baseline_version`, `candidate_version`, `dataset_id`
- `baseline_sha256`, `candidate_sha256` (SHA256 of actual checkpoint files)
- `data_rights_reviewed`, `label_quality_reviewed`, `locked_test_split` set to true only when independently confirmed
- `minimum_class_support` (at least 5; this minimum alone is **not** sufficient for clinical validation)
- `minimum_macro_f1_improvement`, `maximum_ece_increase` predeclared before viewing the test scores

Example invocation:
```bash
python -m scripts.review_candidate_with_policy \
  --baseline-path /private/old_predictions.csv \
  --candidate-path /private/new_predictions.csv \
  --label-map-path /private/label_map.json \
  --baseline-checkpoint /private/old.keras \
  --candidate-checkpoint /private/new.keras \
  --policy-path /private/review_policy.json \
  --output /private/checkpoint_bound_review.json
```

This wrapper rejects changed checkpoint hashes, incorrect model versions, insufficient test coverage, performance regression and undeclared provenance. The result can only be `BLOCKED` or `AWAITING_INDEPENDENT_REVIEW`; it never updates the model registry or serving weights. External clinical and privacy approval is still mandatory for any medical use. The policy declarations are supplied by reviewers—the code **cannot** authenticate their truth.
