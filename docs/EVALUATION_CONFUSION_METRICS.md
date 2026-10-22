# Research evaluation — confusion matrix and diagnostic rates

**Research only.** These metrics are calculated from the held-out labels supplied by the operator and are not proof of clinical effectiveness.

`scripts/evaluate_predictions.py` reports the six-class confusion matrix in `metrics.confusion_matrix`: rows correspond to **ground-truth class**, columns to **model prediction**, ordered exactly by the trusted model-producer's `label_map.json`. Every valid class is represented even if its test support is zero.

For each class `c` versus all other classes:

- Sensitivity/recall = TP / (TP + FN), **null** when no actual test examples of class c.
- Specificity = TN / (TN + FP), **null** when no actual non-c examples.
- Precision = TP / (TP + FP) and F1 remain reported for historical compatibility.
- Integer TP/TN/FP/FN counts are included so that denominators and prevalence are visible.

Absence of class support must not be interpreted as a measured sensitivity of 0%. Small samples, synthetic examples, repeated subjects, unverified labels, and domain shift invalidate any clinical performance generalization. The held-out test must remain independent of the training/calibration splits. For sensitive subgroup analyses, the existing minimum-group-size suppression is preserved.

Example (with real, properly authorized private metadata, not an image upload):

```bash
python scripts/evaluate_predictions.py \
  --predictions PRIVATE_PSEUDONYMOUS_TABLE.csv \
  --label-map PRIVATE_PRODUCER_LABEL_MAP.json \
  --out PRIVATE_RESEARCH_REPORT.json
```

This produces a reproducible structural research report, not a deployment threshold or skin-cancer rule-out tool.
