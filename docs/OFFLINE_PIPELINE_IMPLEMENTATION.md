# Offline real-artifact analysis orchestration

This new code ties image suitability → original predictor-compatible preprocessing → verified ModelRuntime → explicit policy abstention **offline**. It has no HTTP analysis route, does not persist patient photos, does not return a medical recommendation, and cannot mark clinical readiness as true.

- `services/cv/offline_pipeline.py` preserves full-frame RGB, 224×224 PIL bilinear, float32 [0,255] (internal model preprocessing), while reporting bounded suitability and the exact runtime model/pipeline identifiers. Default output omits per-image private probabilities.
- `services/cv/face_geometry.py` tests face boxes, eye detection/roll estimation and optional ROI crop, without silently changing the trained model input. The new ROI transforms require an independent, rights-cleared held-out comparison before activation.
- Tests use a labelled fixture stub **only** to verify software control flow, not performance, diagnosis, face alignment quality or artifact compatibility.

Still blocked: real original trained checkpoint, approved independent labels/images, genuine preprocessing parity, calibration/uncertainty and independent clinical/legal review. Even a passing model package and source tests must not make the public endpoint available.
