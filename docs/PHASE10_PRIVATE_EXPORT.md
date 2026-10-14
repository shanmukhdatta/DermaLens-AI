# Phase 10 companion — checked, private real-model prediction export

This additive PR supplements Phase 10's evaluation CLI with an offline **actual checkpoint prediction exporter** rather than an invented probability table.

Requires Phase 9 verified checkpoint, label map and manifest, private rights-cleared photos and verified medical-category labels. All photo paths are restricted to an operator-provided private directory; checkpoint/content SHA256 verification and model-version/label-order checks fail closed.

Create a private JSON governance declaration with:
`rights_verified=true`, `labels_independently_verified=true`, `locked_test_split=true`, `evaluation_id`, `dataset_provenance`, `permission_reference`, `label_method`, `checkpoint_sha256` (the actual trained `.keras` file's SHA256).

Create an **untracked** private image CSV with exactly:
`example_id,subject_id,content_sha256,split,source,label,skin_tone_group,device_group,relative_image_path`.
For test cases `source` must be `real`. Person/group and exact image hashes must not leak between splits, and the test partition must have been frozen before evaluating.

Execute:
```bash
python -m scripts.export_verified_predictions \
  --model-manifest /private/model_manifest.json \
  --checkpoint /private/checkpoint.keras \
  --label-map /private/label_map.json \
  --dataset-manifest /private/evaluation_permission.json \
  --index-path /private/index.csv \
  --image-root /private/images \
  --output /private/private_predictions.csv

python -m scripts.evaluate_predictions \
  --predictions /private/private_predictions.csv \
  --label-map /private/label_map.json \
  --out /private/research_metrics.json
```

The exporter matches the **original PIL 224×224 RGB float32** training-inference contract; it does not use the new face quality pipeline or invent normalization. Prediction rows omit image paths. Source photographs and per-image predictions must **never** be committed to the public GitHub repository.

External work still required: provide legally acquired real photos and verified ground truth, subject/duplicate grouping, trained checkpoint, clinical review and original-model parity. Test fixtures use a fake runtime **only in tests** and establish no performance evidence. This PR does not activate public diagnosis or model readiness.
