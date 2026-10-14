# Phase 10 — Offline, leakage-aware real-world evaluation

This phase implements the **evaluation machinery**, not a completed domain-shift study. No licensed, clinician-verified real-image benchmark or trained checkpoint was provided to this repository. Until those arrive, **there are no reported model metrics or claims of clinical readiness**.

## Privacy-preserving prediction table

A local CSV includes columns: `example_id,subject_id,content_sha256,split,source,label,model_version,skin_tone_group,device_group,prob_0,...,prob_5`. No images, paths, names or emails. IDs must be pseudonymous and must never be reversible public identifiers. Their use is limited to auditing split leakage. Store the CSV privately; do not check sensitive records into Git.

- Split is one of `train`, `calibration`, `test`. A person/subject group and identical content SHA256 must **never** cross splits. No duplicate example IDs.
- Test data should use independently held-out, suitably licensed real images with qualified ground-truth annotations; source `fixture` in tests is not validation.
- Label order must be the exported `label_map.json`, not guessed alphabetical order. Probabilities must sum to 1 and use one consistent model version.
- Output: class-level precision/recall/F1, macro-F1, accuracy, multiclass Brier, NLL, exploratory ECE and risk/coverage, demographic/device strata with groups smaller than 10 suppressed, and a subject-cluster bootstrap accuracy interval when at least 30 held-out independent subjects exist.
- Never select operating thresholds on the test split. The reported 0.5/0.7/0.9 coverage curves are **exploratory**, not deployment-ready or clinical thresholds. Calibrate only on the calibration split, lock the policy, and evaluate on the untouched test split.
- Data provenance, skin-tone labeling method, actual clinical annotation quality, subgroup sufficiency, dataset licenses, confidence intervals, and real-domain shift require external professional review.

## Run locally (on approved private prediction tables)

```sh
python -m scripts.evaluate_predictions --predictions /private/test_predictions.csv --label-map /private/label_map.json --out /private/evaluation_report.json
```

The command reports only measured evaluation results. It **does not** run the image classifier; use the actual verified Phase 9 model runtime to generate probability records offline first. There is no live consumer diagnostic service in Phase 10.

Next: Phase 11 calibration/OOD/abstention policies and XAI, conditional on legitimate real-world calibration data.
