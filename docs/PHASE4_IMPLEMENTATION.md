# Phase 4 — Ephemeral image suitability API

## Implementation
`POST /api/v1/images/check` accepts a **raw binary** JPEG/PNG/WebP request body, not multipart. The endpoint is disabled by default: `DERMALENS_ENABLE_IMAGE_QUALITY_CHECKS=true` enables it only where deployment ingress protections and applicable rate limiting are in place.

A request is bounded to 8 MiB before decoding; parsed images have bounded dimensions, valid known formats, one frame and applied EXIF orientation. No image bytes or EXIF are persisted. OpenCV's replaceable Haar detector supplies an *engineering baseline* face-count gate; blur and exposure numeric signals are **uncalibrated warnings only**. The output says `medical_analysis_available: false` and never includes a skin condition, severity, subtype, or diagnosis. No face crop/alignment feeds a classifier yet. No model loading happens in this phase.

An image being marked `accepted` means only it passed the current upload suitability checks; it does **not** imply that the skin is healthy, unhealthy, or assessable medically. A face detector's false-negative/false-positive behavior must be checked on appropriately licensed real photographs before relying on it. No public medical inference is unlocked.

Install development extension after foundation dependencies:
```sh
uv pip install --python .venv/bin/python -r requirements-cv.txt
uv run --frozen --no-sync python -m pytest tests/test_phase4_image_quality.py -q
```
Future phases may add better detectors and model-specific ROI handling **only after inference parity and held-out validation**.
