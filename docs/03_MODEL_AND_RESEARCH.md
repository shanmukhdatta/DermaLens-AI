# Model and research provenance

Research (read-only): https://github.com/shanmukhdatta/Facial_Skin_Diesease

Verified repository files: `src/inference/predictor.py`, `scripts/run_inference.py`, `src/data/utils.py`, `src/models/custom_layers.py`, `src/models/losses.py`, `src/models/builder.py`, `src/models/backbones.py`, `src/evaluation/`, `scripts/run_training.py`. The code supports EfficientNetV2B0, ResNet50, DenseNet121, MobileNetV3Large and ViT_B16; existence of their loaders does **not** establish that any finished artifact is checked into GitHub.

**Observed repo state, 2026-10-13:** checkpoint files and `label_map.json` are not in the tracked default-branch inventory of either repo. Trained files may exist on Kaggle or the user's computer; do not claim model validation until provided and independently checked.

## Exact artifact ingress contract

Phase 9 integrates trained artifacts; Phase 1 establishes the contract and baseline tooling. Do not retrain existing weights.

1. Obtain ONE trusted `*_final.keras` or approved checkpoint and the label map **from the same training run**. Keep artifacts in private, access-controlled storage; do not commit images or checkpoints.
2. Compute SHA-256 separately for checkpoint and label map and record the exact hashes in the manifest; identify trusted producer, source revision, training run, license and evaluation provenance. Pin `tensorflow`, `keras` and Python compatibility discovered during loading.
3. Research label map is JSON object `{"0":"...",...,"5":"..."}`: numeric **indices**, not an assumed alphabetical list. Verify indices 0–5 appear exactly once and six label values match the intended set. Track literal map bytes with SHA-256.
4. Manifest declares N,H,W,C = 1,224,224,3, `float32`, `RGB`, pixel range 0–255 and `bilinear` resize. Both serialized model and declared preprocessing must be verified (no external scaling).
5. Safe custom objects must be code-reviewed and explicitly allowlisted. Source objects include `ResNet50Preprocess`, `DenseNet121Preprocess`, `ViTPreprocess`, `ExtractCLSToken`, `FocalLoss` (see original `CUSTOM_OBJECTS`). Import trusted local source only; never deserialize an untrusted checkpoint or use unsafe lambda deserialization.
6. Load with trusted compatible TensorFlow/Keras runtime, verify actual `input_shape`, actual `output_shape`, single-image prediction, finite nonnegative probabilities summing approximately 1, and deterministic fixture parity to research predictor. Match the exact label order and fail if incompatible.
7. Only after validation plus human approval may a manifest move from `candidate` through `staging` to `approved`. Phase 0 only establishes schema. Repository starts without a deployable artifact.

Machine-readable [manifest JSON schema](../models/manifests/model-manifest.schema.json); [integration checklist](../models/README.md).

A trained model on synthetic data is not validated clinically. Evaluate real-image generalization, data rights, stratified failure modes, calibration, abstention and OOD before any limited research deployment. Do not publish numeric performance not measured for this artifact.
