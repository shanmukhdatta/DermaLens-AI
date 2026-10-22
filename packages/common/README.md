# packages/common — module technical guide

## Purpose and scope

Stable safe error envelopes and domain codes. Status: **Never leak private error details**. See root README and `docs/FINAL_FEATURE_AUDIT.md` for the release state.

## Direct file index

- `__init__.py` — Python module / executable logic
- `errors.py` — Python module / executable logic

## Architecture and internal workflow

Internal error -> safe fixed public message.

```mermaid
flowchart LR
    Entry[Entry point / caller] --> Validate[Validation or policy]
    Validate --> Module[common module]
    Module --> Outcome[Typed result / next layer]
```

## Public interfaces and integration

DomainError, ErrorCode, safe_error_payload. Consumers should use these boundaries rather than bypassing permissions, model integrity checks or consent.

## Dependencies and configuration

None. Do not commit secrets, patient photographs, model checkpoints or other sensitive artifacts.

## Verification

Run from repository root unless the command is an npm script (run npm scripts from `apps/web`):

```bash
python -m pytest -q tests/test_api_foundation.py
```

These are **recommended commands**, not a claim they were executed during this documentation change. Record commit SHA, test output and independent integration evidence before changing audit state.
