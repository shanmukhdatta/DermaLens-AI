# docs — module technical guide

## Purpose and scope

Architecture, phase trackers, ADRs, safety requirements, handoff and audits. Status: **Never mark a feature done because its description exists**. See root README and `docs/FINAL_FEATURE_AUDIT.md` for the release state.

## Direct file index

- `01_SYSTEM_ARCHITECTURE.md` — module source or configuration
- `02_COMPUTER_VISION_PIPELINE.md` — module source or configuration
- `03_MODEL_AND_RESEARCH.md` — module source or configuration
- `04_BACKEND_ARCHITECTURE.md` — module source or configuration
- `05_RAG_ASSISTANT.md` — module source or configuration
- `06_FEEDBACK_AND_CONTINUAL_LEARNING.md` — module source or configuration
- `07_MLOPS_AND_DEPLOYMENT.md` — module source or configuration
- `08_API_AND_DATA_FLOW.md` — module source or configuration
- `09_PRIVACY_AND_SAFETY.md` — module source or configuration
- `ABUSE_CONTROLS.md` — module source or configuration
- `DRIFT_MONITORING.md` — module source or configuration
- `FINAL_ENGINEERING_HANDOFF.md` — module source or configuration
- `OFFLINE_PIPELINE_IMPLEMENTATION.md` — module source or configuration
- `PHASE0_VALIDATION.md` — module source or configuration
- `PHASE10_HANDOFF.md` — module source or configuration
- `PHASE10_IMPLEMENTATION.md` — module source or configuration
- `PHASE10_PRIVATE_EXPORT.md` — module source or configuration
- `PHASE11_HANDOFF.md` — module source or configuration
- `PHASE11_IMPLEMENTATION.md` — module source or configuration
- `PHASE12_HANDOFF.md` — module source or configuration
- `PHASE12_IMPLEMENTATION.md` — module source or configuration
- `PHASE13_CHECKPOINT_POLICY.md` — module source or configuration
- `PHASE13_IMPLEMENTATION.md` — module source or configuration
- `PHASE1_HANDOFF.md` — module source or configuration
- `PHASE1_IMPLEMENTATION.md` — module source or configuration
- `PHASE1_VALIDATION.md` — module source or configuration
- `PHASE2_HANDOFF.md` — module source or configuration
- `PHASE2_IMPLEMENTATION.md` — module source or configuration

## Architecture and internal workflow

README spec -> code implementation -> audit/acceptance matrix.

```mermaid
flowchart LR
    Entry[Entry point / caller] --> Validate[Validation or policy]
    Validate --> Module[docs module]
    Module --> Outcome[Typed result / next layer]
```

## Public interfaces and integration

01–09 architecture series, README_FEATURE_AUDIT, IMPLEMENTATION_CHECKLIST. Consumers should use these boundaries rather than bypassing permissions, model integrity checks or consent.

## Dependencies and configuration

All docs must reflect actual source and external blockers. Do not commit secrets, patient photographs, model checkpoints or other sensitive artifacts.

## Verification

Run from repository root unless the command is an npm script (run npm scripts from `apps/web`):

```bash
python -m scripts.validate_phase0
```

These are **recommended commands**, not a claim they were executed during this documentation change. Record commit SHA, test output and independent integration evidence before changing audit state.

## Current research-evaluation additions

- [Confusion-matrix, sensitivity, specificity, and denominator semantics](EVALUATION_CONFUSION_METRICS.md)
- [Dual perceptual-hash independent image split review](PERCEPTUAL_DUPLICATE_AUDIT.md)
- [Gap-closure acceptance by code path](FINAL_GAP_CLOSURE_CHECKLIST.md)
- [Technical research and architecture decisions](TECHNICAL_RESEARCH_DECISIONS.md)
