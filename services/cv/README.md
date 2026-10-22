# services/cv — module technical guide

## Purpose and scope

Bounded image parsing, experimental face geometry, model manifest and offline inference helpers. Status: **No actual model checkpoint present; public clinical inference blocked**. See root README and `docs/FINAL_FEATURE_AUDIT.md` for the release state.

## Direct file index

- `__init__.py` — Python module / executable logic
- `artifacts.py` — Python module / executable logic
- `face_geometry.py` — Python module / executable logic
- `gradcam.py` — Python module / executable logic
- `keras_runtime.py` — Python module / executable logic
- `offline_pipeline.py` — Python module / executable logic
- `ports.py` — Python module / executable logic
- `quality.py` — Python module / executable logic
- `runtime.py` — Python module / executable logic

## Architecture and internal workflow

Decode -> face/quality -> verified manifest -> offline model -> abstention.

```mermaid
flowchart LR
    Entry[Entry point / caller] --> Validate[Validation or policy]
    Validate --> Module[cv module]
    Module --> Outcome[Typed result / next layer]
```

## Public interfaces and integration

inspect_image, verify_artifacts, VerifiedKerasModel, analyze_offline. Consumers should use these boundaries rather than bypassing permissions, model integrity checks or consent.

## Dependencies and configuration

requirements-cv.txt; local private checkpoint only for offline research. Do not commit secrets, patient photographs, model checkpoints or other sensitive artifacts.

## Verification

Run from repository root unless the command is an npm script (run npm scripts from `apps/web`):

```bash
python -m pytest -q tests/test_phase4_image_quality.py tests/test_offline_research_pipeline.py tests/test_phase9_artifacts.py
```

These are **recommended commands**, not a claim they were executed during this documentation change. Record commit SHA, test output and independent integration evidence before changing audit state.
