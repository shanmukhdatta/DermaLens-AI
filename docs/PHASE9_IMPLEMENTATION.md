# Phase 9 — Trained checkpoint integration adapter

## Real artifact boundary

Implemented: SHA256 of both trusted `.keras` checkpoint and exact `label_map.json`, schema-version/source and six-class validation with underscore aliases, input contract RGB 224x224 float32 [0,255] PIL bilinear/model-internal normalization, lazy TensorFlow loader with research-matching custom layers, Keras shape and probability checks, and a CLI package-integrity test.

These files are private; nothing automatically downloads them or copies research weights to GitHub. The original research source remains unchanged. The model is **not configured, supplied, loaded or evaluated** in CI; CI fixture checkpoint bytes are explicitly fictional and cannot be loaded as a model. Keras deserialization with real weights must be run on local/Kaggle with matching TensorFlow/Keras versions, approved licenses and source commit. See `models/README.md`.

Use:
```bash
python -m scripts.verify_model_package --manifest /private/manifest.json --checkpoint /private/model.keras --label-map /private/label_map.json --load-model
```

The API keeps the model unavailable and readiness 503 until the real package and a separately validated safety policy are ready. No `/analyses` diagnosis endpoint has been activated, and no clinical claims are made. **Acceptance remains blocked on real checkpoint, parity fixtures and real-world calibration.**
