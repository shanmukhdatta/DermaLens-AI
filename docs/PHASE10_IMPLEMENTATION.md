# Phase 10 — Reproducible real-world evaluation pipeline

**Status:** Evaluation code is implemented. Actual independent real-data measurements remain **blocked** until users supply authorized private images, verified labels and a checksum-verified, loadable Keras checkpoint.

## Inputs and constraints

1. Checkpoint + exact label map + Phase 9 model manifest must pass `scripts.verify_model_package`.
2. Create an **untracked**, private `evaluation_manifest.json` with the exact label order, real model SHA256, `evaluation_id`, `label_provenance`, `collection_description`, and `license_or_permission`; explicitly set `authorized_for_evaluation`, `independent_real_data`, `disjoint_subject_groups` and `locked_test_split` to `true` only when justified.
3. Create a private CSV with columns: `sample_id,group_id,image_sha256,split,source,true_label,skin_tone_group,device_group,image_rel_path`. `split` is train/calibration/test. Group all images from the same subject or near-duplicate capture into the same group. Keep calibration independent of test and **freeze the test split before threshold selection**. Keep all photos and per-image probabilities outside public Git.
4. Collect externally verified ground truth and provenance from qualified sources. The `Skin_Cancer` research class cannot be treated as a clinical screening label without specialist validation.

## Run offline prediction export (not hosted on API)

```sh
python -m scripts.predict_evaluation_set \
  --evaluation-manifest /private/evaluation_manifest.json \
  --dataset-csv /private/dataset_index.csv \
  --image-root /private/images \
  --model-manifest /private/model_manifest.json \
  --checkpoint /private/model.keras \
  --label-map /private/label_map.json \
  --output /private/private_predictions.csv
```

The exporter verifies checkpoint SHA and class order, local-only image path containment, and each content SHA; it then feeds **the original research preprocessing** (RGB, 224×224 PIL bilinear, float32 0..255, internal normalization) to the real Keras runtime. It does not upload or store facial images; individual probabilities are written in a private file with owner-only permissions.

```sh
python -m scripts.evaluate_real_data \
  --manifest /private/evaluation_manifest.json \
  --predictions /private/private_predictions.csv \
  --output /private/aggregated_results.json
```

The evaluator rejects unknown labels, invalid probability distributions, duplicate sample IDs, and hash/subject group leakage across train/calibration/test. Only independently labeled real `test` records contribute to accuracy, macro-F1, per-class metrics, Brier, negative log-likelihood, 10-bin ECE, confusion matrix, and a subject-cluster bootstrap CI when at least 20 independent test groups exist.

Only subgroups with at least 20 test samples appear in the public aggregate report; no individual photo paths, sample IDs, SHA identifiers or predictions are included. The report is **research-only**, does not authorize diagnosis or skin cancer screening, and does not claim the labels were independently validated by this software. This sample-size suppression is a reporting safeguard, not a statistical power guarantee.

## Required before Phase 11

- At least one independently labeled and rights-cleared real-image evaluation collection.
- Subject- and near-duplicate-group disjoint train/calibration/test partitions, reviewed by humans.
- Real model checkpoint parity against the original research code.
- Verified label provenance, skin appearance and capture-device representation.
- Evaluation report and clinician-supported risk review for medical claims.

Without these, Phase 11 uncertainty and model promotion remain blocked. No numeric performance claims may be published from synthetic CI fixtures.
