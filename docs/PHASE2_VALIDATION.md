# Phase 2 acceptance evidence and remaining gates

**Source of truth:** Phase 2 PR (link attached after PR creation).

## Automated checks

At implementation commit: **pending CI verification**; do not interpret authored tests as passed before the GitHub Actions run finishes.

Existing Phase 0 contract validation must remain green. Phase 1 backend + web workflow must run on `main` and all pull requests; Phase 2 tests are added to its pytest + Ruff formatting coverage.

## Acceptance matrix

| Gate | Evidence | Status |
|---|---|---|
| Phase 1 merged into main | PR #2, merge `a54592fa950298dbe3732fe47b16b0db192a6228` | Verified |
| Phase 1 CI on main | Workflow `phase1.yml` changed on `main` at `12379168b3188025e6abc3ca22083cf29db7e0aa` | Configured; latest run pending review |
| FastAPI v1 composition, DI, deterministic errors | `apps/api/dermalens_api/` with black-box `tests/test_phase2_backend.py` | Implemented, pending CI |
| Default model unavailable and safety not approved | No artifact, `UnavailableModelRuntime`, `ReadinessGates` | Implemented, pending CI |
| Owner/auth and origin safety | Fail-closed verifier, `ensure_owner`, strict CORS tests | Implemented, pending CI |
| Sensitive data protection | No body logging, sanitization tests, no persistence | Implemented, pending CI |
| Windows/Antigravity external startup | Requires user-run PowerShell smoke tests | Not executed |
| Real model, clinical safety, real provider/deployment | Outside Phase 2 | Not implemented |

## Constraints

The Phase 0 `openapi.v1.json` remains a future full-product contract, not the exposed runtime OpenAPI description; unavailable domain endpoints remain absent. Phase 2 implements the contract's operational `HealthStatus`, protected `ModelStatus`, and `ErrorResponse` shapes. The app disables the public auto-generated OpenAPI endpoint until contract/completeness alignment and auth review are complete.

No external environment startup, medical or integration deployment is claimed. The research repo is never modified.
