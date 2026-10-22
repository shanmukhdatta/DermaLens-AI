# Private offline model benchmark: image-to-evaluation integration

This code fills a pipeline gap between the **existing SHA256-verified Keras checkpoint adapter**
(`services/cv/keras_runtime.py`) and the existing research evaluator
(`services/learning/evaluation.py`). It does **not** distribute pretrained weights, private
datasets, clinical validation or medical inference.

## Scope and security

- Runs locally/Kaggle using private `.keras`, `label_map.json`, model manifest and an
  explicit, permissioned image dataset. No real user images are downloaded or committed.
- A private CSV manifest lists relative image paths and source/split/label/group information.
  The manifest must have exactly these headers:

  ```csv
  image_path,example_id,subject_id,split,source,label,skin_tone_group,device_group
  ```

- Split values: `train`, `calibration`, `test`; source values: `real`, `synthetic`,
  `fixture`. Label must match the trained index-to-category mapping exactly. For privacy,
  identifiers are HMAC-pseudonymized before export; private paths never appear in results.
- **Real, deidentified subject IDs are necessary for patient-level leakage control.** When
  reliable subject IDs do not exist, do not claim a patient-disjoint or independent clinical
  evaluation. Exact-file SHA256 checks catch identical copies, not all near duplicates.
- All image reads are bounded and format checked; samples outside the private image root or
  invalid rows abort the entire job rather than being silently excluded. This preserves the
  trained full-frame PIL preprocessing; no unverified ROI/EXIF transformation is inserted.
- The private outputs contain probability vectors and research metrics, **not diagnoses**.
  Calibration, OOD robustness, demographic validity, clinical review and release approval
  remain separate blocked requirements.

## Running with a supplied model and data

Install TensorFlow compatible with the manifest and the repository's research training
environment, plus the project's Python requirements, inside Kaggle or a private machine.
Keep model artifacts and image input directories outside Git.

Generate a strong key once, store it outside the repository:

```python
from pathlib import Path
import secrets
Path("/private/pseudonym-key.bin").write_bytes(secrets.token_bytes(32))
```

Run this CLI from the repository root (these are example private file paths, not included artifacts):

```bash
python -m scripts.build_private_prediction_table \
  --manifest /private/model-manifest.json \
  --checkpoint /private/model.keras \
  --label-map /private/label_map.json \
  --input-csv /private/input-manifest.csv \
  --image-root /private/images \
  --pseudonym-key-file /private/pseudonym-key.bin \
  --predictions-out /private/outputs/predictions.csv \
  --evaluation-out /private/outputs/evaluation.json
```

The CSV feeds existing offline calibration and comparison tools; the JSON includes
subject-bootstrap confidence intervals when the dataset supports them. Tests use only
fictional generated images and fixture predictions. They **do not prove model quality**.

Known external tasks: obtain the real model from its authorized source; confirm exact research
predictor parity; collect rights-cleared independent subject-labeled clinical images; run
evaluations; commission review of safety, privacy and clinical validity; configure a separately
approved analysis service only after these gates.

See `docs/PHASE9_HANDOFF.md` and `docs/FINAL_ENGINEERING_HANDOFF.md`.
