# Phase 1 engineering foundation

**Status:** code implemented and GitHub Actions green on commit `841bd5914a1ac4e828f3f0e93e04a250aed256da`; PR #2 remains under review. Local Windows/Antigravity validation has not been witnessed.
**Inherited baseline:** Phase 0 PR #1 squash-merged to main at `4c1ff050dd8a0ea39ee83b667cbe0388d6899939`.
**Scope:** real web/backend framework entry points and testable in-process ports; **no** trained model, clinical diagnosis, authentication, persistence, RAG provider, feedback collection or uploads.

## Architecture and boundary

- Python `apps.api.dermalens_api.main:app` uses FastAPI and a `Settings` object with `DERMALENS_` environment prefix. Only `GET /api/v1/health` and `GET /api/v1/readiness` are implemented. The latter always returns `503 {"status":"not_ready"}` until verified model and safety requirements are met.
- `services/cv` defines `ModelRuntime` and `CVPipeline` protocols, and `UnavailableModelRuntime` raises `ModelNotReady` for `predict`; **not a test double or trained model**.
- `services/rag` and `services/learning` expose only ports/immutable types, not live provider or database implementations. `packages/common` defines a typed, sanitized public error envelope. `packages/security` describes consent labels but does not claim live authentication.
- Next.js `apps/web` renders a publicly safe static research/foundation notice. It never collects images or calls the backend and does not imply that medical analysis is functional.
- No `tensorflow`, Grok credentials, model files or image datasets are needed in Phase 1.

## Dependency reproducibility

- Python uses `pyproject.toml` and a committed `uv.lock`, with `uv sync --frozen --all-groups`.
- Frontend uses exact versions in `apps/web/package.json` and a committed `apps/web/package-lock.json`, with `npm ci`.
- A temporary, branch-scoped CI bootstrap generated and committed the two lockfiles, then was **removed**. All ongoing workflows use committed lockfiles with `uv sync --frozen` and `npm ci`. To intentionally update dependencies, regenerate lockfiles on a controlled branch, review diffs, and commit them.
- `.github/workflows/phase1.yml` runs backend lint, format, typecheck, Phase 0 contracts, unit tests, secret-file hygiene, frontend lint, test, Next production build and TypeScript checks. Both checkouts are isolated. The original `phase0.yml` remains dedicated to the Phase 0 contract tests.

## Local setup (Windows PowerShell / Antigravity)

Prerequisites: Git, Python 3.11, Node 22, npm 10+, [uv](https://docs.astral.sh/uv/getting-started/installation/). For build repeatability use the committed lockfiles; do not regenerate them for ordinary development.

```powershell
git clone https://github.com/shanmukhdatta/DermaLens-AI.git
cd DermaLens-AI
git checkout phase-1-engineering-foundation

Copy-Item .env.example .env
uv sync --python 3.11 --frozen --all-groups

# Terminal A: API
uv run --frozen uvicorn apps.api.dermalens_api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open a **second** terminal:

```powershell
cd DermaLens-AI/apps/web
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Expected: frontend at http://localhost:3000, API process at http://127.0.0.1:8000. Confirm API without sending faces:

```powershell
curl.exe -i http://127.0.0.1:8000/api/v1/health
# Expected: HTTP 200 {"status":"ok"}

curl.exe -i http://127.0.0.1:8000/api/v1/readiness
# Expected: HTTP 503 {"status":"not_ready"}
```

Automated local checks:

```powershell
# Repo root
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen mypy
uv run --frozen python scripts/validate_phase0.py
uv run --frozen python -m pytest -q

# In apps/web
npm run lint
npm test
npm run build
npm run typecheck
```

**Restrictions:** do not use `--host 0.0.0.0` on public networks or expose this unfinished API publicly. Do not upload facial images to this release. `.env`, private datasets and model artifacts must not be committed. If a clean checkout of the phase branch doesn't work, record commands/output and fix before marking acceptance complete.

## Unimplemented release gates

No authentication, owner access controls, database, encryption/erasure jobs, consent screens, rate limiting, image-quality/face detection, model checksum parity, calibration, explainability, RAG, telemetry or deployed container environment. These are assigned to the later phases in `PHASE_TRACKER.md`.

Framework releases can receive security advisories; review published advisories and upgrade/test dependencies before any production exposure. Developer dependencies can have low risk during private development without constituting production approval.

## Acceptance notes

Complete only when GitHub Actions for the final Phase 1 branch commit reports all jobs success and the PR is reviewed/merged. Local Antigravity browser check is external unless specifically observed. The initial scope is a running framework skeleton, not a user-facing skin-condition product.
