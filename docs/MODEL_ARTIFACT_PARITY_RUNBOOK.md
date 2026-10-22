# Candidate model packaging and research-predictor parity

## Scope

These tools eliminate guesswork when introducing a privately trained six-class research checkpoint. They DO NOT fetch, synthesize or fabricate model weights, clinical validation, labels or approvals. Production medical analysis remains disabled until independent clinical and security acceptance.

Source architecture: the original research repository has a DiseasePredictor in src/inference/predictor.py. It converts images to RGB, resizes with PIL bilinear to 224x224, casts raw pixel values to float32 and relies on the saved model for preprocessing. The DermaLens Keras adapter uses the same contract. The following tools compare their real model outputs.

## Step A: Obtain authorized original artifacts

Use the actual trained .keras checkpoint, its exact label_map.json, source code commit SHA and truthful framework versions from the original Kaggle training run. Keep these in an untracked private directory. No checkpoint or facial photo should enter the public GitHub repository.

## Step B: Create a checksum-verified candidate manifest

Run from DermaLens-AI root, replacing placeholders with observed values:

~~~bash
python -m scripts.package_trained_model \
  --checkpoint /private/model.keras \
  --label-map /private/label_map.json \
  --out /private/model-manifest.json \
  --model-id my-actual-research-run \
  --version 0.1.0 \
  --source-commit <actual-40-character-research-commit> \
  --training-run-id <actual-training-run-id> \
  --python-version <actual-python-version> \
  --tensorflow-version <actual-tensorflow-version> \
  --keras-version <actual-keras-version>
~~~

Pass --custom-object once for each actual serialized Keras custom object. Do not guess. The file always has candidate status; no approval is implied. The CLI checks file checksums and six-class map, but DOES NOT certify that a checkpoint can be deserialized or classify correctly. Run the existing verify_model_package.py --load-model separately in the matching environment.

## Step C: Export reference from original predictor

Clone the exact source commit into a trusted local research checkout with its dependencies and TensorFlow. Run:

~~~bash
python -m scripts.export_original_predictor_reference \
  --research-repo /private/Facial_Skin_Diesease \
  --checkpoint /private/model.keras \
  --label-map /private/label_map.json \
  --image /private/golden-sample.jpg \
  --out /private/original-reference.json
~~~

This is a reference score vector, not a diagnosis. Choose lawful, approved sample images and retain original research image and weights offline.

## Step D: Verify DermaLens adapter parity

~~~bash
python -m scripts.check_model_parity \
  --manifest /private/model-manifest.json \
  --checkpoint /private/model.keras \
  --label-map /private/label_map.json \
  --image /private/golden-sample.jpg \
  --reference-json /private/original-reference.json \
  --atol 0.00001 \
  --out /private/parity-report.json
~~~

A passing comparison means source SHA, checkpoint SHA, image SHA, ordered class labels and predicted probability vector agree within tolerance. It does NOT imply real-world accuracy. Repeat on multiple independently sourced reference images and all model architectures you intend to serve.

## Step E: Independent research and clinical validation

Use scripts.build_private_prediction_table with approved private data, then scripts.evaluate_predictions and scripts.fit_calibration_policy. Existing leakage-audit tools can detect group and image-split collisions. Cross-source near-duplicates, site/device shifts, labels, subgroup performance and patient-level independence require review by qualified staff. Synthetic images cannot stand in for independent real clinical data.

The original research training repository stores source code but no .keras weight file in its tracked Git tree (checked October 22, 2026). An actual trained checkpoint, label map, independent real images and evidence are external inputs.

**Hard gate:** neither these CLIs nor their tests automatically enable a production diagnostic endpoint, certify medical safety, or bypass approved clinical review.

## Reference guidance

- https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/good-machine-learning-practice-medical-device-development-guiding-principles
- https://www.gov.uk/government/publications/good-machine-learning-practice-for-medical-device-development-guiding-principles/good-machine-learning-practice-for-medical-device-development-guiding-principles
