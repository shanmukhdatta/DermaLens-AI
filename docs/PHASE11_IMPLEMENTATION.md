# Phase 11 — Research-only calibration, abstention and XAI adapter

## Implemented
- Offline temperature scaling using independent `calibration` rows from the private Phase 10 prediction table.
- Exploratory threshold selection using a conservative binomial Wilson upper bound on *calibration* error and a minimum accepted subset size. Requires 50 or more independently grouped **real** calibration examples by default; held-out test data is checked for leakage but not used to select the policy.
- Version-linked `ResearchCalibration` metadata with `status=research_only_unapproved`, `ood_validated=false`, `xai_validated=false`.
- An explicit **abstain-by-default** policy: normal runtime always returns `POLICY_NOT_VALIDATED`, regardless of model confidence. Offline research mode can examine a research candidate category but cannot authorize clinical use.
- Grad-CAM helper for supported convolutional layers only. It returns a normalized attention map if actual Keras gradients exist, otherwise raises `ExplanationUnavailable`; no fallback fake heatmaps or lesion localization claims.

## Limitations / gates

These are *research building blocks*, **not** a completed clinical calibration, OOD system, Grad-CAM evaluation or release authorization. Model checkpoints and real calibration/test data were not provided. A threshold tested on calibration data is not automatically safe for patients. We do not expose a patient-facing inference route or promote any candidate threshold. OOD assessment and real model-specific XAI visualization require licensed external evaluation and expert review. Safety checks must be fully integrated and validated before any public analysis endpoint is enabled.

## Offline command

```sh
python -m scripts.fit_calibration_policy --predictions /private/predictions.csv --label-map /private/label_map.json --output /private/research_calibration.json
```

No production or staging configuration will load this generated JSON automatically.
