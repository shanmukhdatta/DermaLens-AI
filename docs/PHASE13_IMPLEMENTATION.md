# Phase 13 — Controlled offline model-improvement review

Implements a **manual research promotion eligibility gate**, not deployment or automatic training. Candidate model improvements can be experimented with offline (for example in Kaggle); only separately validated labels and explicitly opted-in research data may enter those experiments.

## Inputs

Two **private** Phase 10 prediction CSV files (baseline and candidate) with the **same dataset examples and exact label/subject/image hashes**, six-class exact label map and two distinct local checkpoint files. Reuse the untouched held-out real test set; never tune candidates on this test set. Fit/choose hyperparameters on training/validation and tune calibration/policy on a separate calibration partition.

Provide a private review policy JSON containing:
- `policy_version: "1"`
- `baseline_model_version`, `candidate_model_version` and `evaluation_dataset_id` (pseudonymous IDs)
- `baseline_checkpoint_sha256` and `candidate_checkpoint_sha256`
- `data_rights_reviewed: true`, `label_quality_reviewed: true`, `test_split_locked: true` (external human declarations, not independently verified by code)
- `minimum_test_subjects` (at least 30), `minimum_per_class_support` (at least 5)
- `minimum_macro_f1_delta`, `maximum_ece_increase`, `maximum_per_class_recall_drop` explicitly agreed before test review

Usage:
```bash
python -m scripts.evaluate_candidate_promotion \
 --baseline-csv /private/baseline_predictions.csv \
 --candidate-csv /private/candidate_predictions.csv \
 --baseline-checkpoint /private/baseline.keras \
 --candidate-checkpoint /private/candidate.keras \
 --label-map /private/label_map.json \
 --policy /private/research_review_policy.json \
 --output /private/review_report.json
```

The gate verifies checkpoint byte hashes, sample and subject identity, real held-out test source, exact model versions, leakage-aware CSV validation, minimum subject and class support, macro-F1, exploratory ECE and per-class recall regression against policy thresholds. It produces an aggregate `BLOCKED` or `ELIGIBLE_FOR_MANUAL_RESEARCH_REVIEW` state. There is **no API route, online update, automatic training, model registry promotion or production deployment**.

All research-review eligibility results have `clinical_release_authorized: false` and `automated_model_promotion: false`. Medical safety and clinical effectiveness require independent assessment beyond these simple statistical checks. A small per-class support minimum is a code guard, not an adequate clinical evaluation target.

## Blockers

Real checkpoint and validated domain-shift baseline, robust external images and independent labels, feedback consent and clinician review, security/privacy release signoff and manual deployment approval remain necessary. Synthetic unit tests or a model passing these gates cannot justify public medical use.
