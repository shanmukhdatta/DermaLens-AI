# Offline privacy-minimal drift reporting

This provides a documented, testable *offline* aggregate data-shift investigation helper. It does not store individual facial photos, class scores, device metadata, user IDs or medical records. The input files are research aggregates created separately from authorized, permissioned datasets with six integer predicted-class counts and optional aggregate quality rejections.

Compare two **distinct** cohorts for the same checksum-approved model version using:
```sh
python -m scripts.review_population_drift \
  --baseline /private/cohort_baseline.json \
  --current /private/cohort_current.json \
  --out /private/drift_review.json
```
Every input must contain `schema_version=1`, `aggregated_research_data=true`, `cohort_id`, `model_version`, `count`, `class_counts` as six nonnegative integers summing to count, and `quality_rejection_count` as a nonnegative integer. At least 100 samples per cohort are required. Jensen–Shannon distance >=0.15 flags **INVESTIGATE**, not "concept drift proven". The cutoff is a heuristic engineering alert, not empirically validated. Never infer disease prevalence, clinical correctness or population health from predicted class histograms. Do not auto-trigger training/deployment or publish subgroup counts that could identify people. Real model measurement, label validation, access-controlled monitoring, tracing, dashboards and release reviews remain external blockers.
