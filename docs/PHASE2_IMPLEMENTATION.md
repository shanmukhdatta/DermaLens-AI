# Phase 2 — FastAPI backend skeleton

**Branch:** `phase-2-fastapi-backend-skeleton`. **Status:** Phase 2 implementation CI green on SHA `a50bb010cd735103663824842060086edf6b971e`; PR #3 remains open. See [validation](PHASE2_VALIDATION.md).

## Scope delivered

- A new `create_app(settings)` composition root wires a modular v1 router, an unavailable model adapter, an explicit policy readiness gate, and a rejecting identity verifier. No API data persistence, checkpoint, consented-upload pipeline, or RAG client is initialized.
- `/api/v1/health` is public and responds `200 {"status":"ok"}`. `/api/v1/readiness` responds `503 {"status":"not_ready"}` in the default build because both model runtime and safety policy are unavailable. Additional required probes can be injected and failure/exception closes readiness; the default cannot be made ready with a request header.
- `/api/v1/models/current` is a **protected metadata route**, returning the Phase 0 `ModelStatus` shape only after a verified-actor dependency. The default verifier rejects *all* tokens until Phase 3 connects real issuer/audience/key validation. No hardcoded demo login exists. Test-only dependency overrides do not ship in the app.
- Each response gets canonical or regenerated UUID request correlation, nosniff, frame-denial, restrictive CSP, cache prevention, referrer and permission policy. HSTS is set for staging/production. CORS permits exactly the configured origin; wildcard and insecure nonlocal origins fail configuration validation.
- HTTP errors have `error.code`, fixed non-sensitive `error.message` and matching `request_id` (Phase 0 schema), including 401, 404, 405, 422, 500. User-provided exception text and sensitive validation inputs are never reflected. Access logs contain only method, route template, status and correlation ID.
- `ensure_owner` enforces identity-based ownership with uniform not-found response. No owner-scoped data routes exist yet, and no self-declared ID is trusted.

## Deliberately not implemented

Analysis upload or CV decode, actual model inference, owner database, OIDC/JWT verification, image/prediction retention, feedback, RAG bot, rate limiting, deployment, clinical outputs and any treatment recommendations. Full protection against volumetric abuse and production threat modeling are later release gates.

## Developer commands

From repository root (PowerShell/Antigravity):

```powershell
git fetch origin
git checkout phase-2-fastapi-backend-skeleton
uv sync --python 3.11 --frozen --all-groups
uv run --frozen ruff check .
uv run --frozen ruff format --check apps packages services tests/test_api_foundation.py tests/test_phase2_backend.py
uv run --frozen mypy
uv run --frozen python scripts/validate_phase0.py
uv run --frozen python scripts/check_repository_hygiene.py
uv run --frozen python -m pytest -q
uv run --frozen uvicorn apps.api.dermalens_api.main:app --host 127.0.0.1 --port 8000
```

In another terminal, check `curl.exe -i http://127.0.0.1:8000/api/v1/health`, `/api/v1/readiness`, `/api/v1/models/current`. Expected HTTP statuses: `200`, `503`, `401` without valid external identity. Do **not** upload personal photos or expose this unfinished server publicly.

## Design considerations for Phase 3

Real OIDC verifier will verify cryptographic signature and JWK rotation, issuer, audience, expiration, clock skew and nonce/state when appropriate; secure actor-subject mapping into owner-scoped storage will be added with PostgreSQL migrations. Existing public operational endpoints must stay public. No API endpoint may accept a user-supplied owner ID.
