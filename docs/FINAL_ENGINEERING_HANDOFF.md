# DermaLens AI — final local engineering verification handoff

**Main-branch engineering state:** Backend and Next.js, bounded image quality, offline Keras adapter plus abstaining research pipeline, owner-scoped SQLAlchemy accounts/history/feedback, privacy-first documentation search, Grok adapter, local Docker/PostgreSQL, evaluation and offline calibration, eye/ROI experimentation, Grad-CAM research helper, private aggregate drift checks, rate budgets and browser-local evaluation UI are present. GitHub Actions is an engineering code gate, not proof of medical safety.

## Windows + Antigravity full local verification

1. `git clone https://github.com/shanmukhdatta/DermaLens-AI.git` if absent; otherwise `git fetch origin`. In the checked-out repository run `git switch main; git pull --ff-only origin main; git status --short; git rev-parse HEAD`. Preserve all local changes and report them; never force-reset uncommitted files.
2. Install Python 3.11 and Node.js >=22; from the repo root run:
   ```powershell
   uv sync --python 3.11 --frozen --all-groups
   uv pip install --python .venv\Scripts\python.exe -r requirements-persistence.txt -r requirements-cv.txt -r requirements-rag.txt
   uv run --frozen --no-sync ruff check .
   uv run --frozen --no-sync ruff format --check .
   uv run --frozen --no-sync mypy apps packages services
   uv run --frozen --no-sync python -m pytest -q
   uv run --frozen --no-sync python -m scripts.validate_phase0
   ```
   Use documented alternatives if actual CLI entrypoints differ and report the correction rather than claiming success.
3. In `apps/web`: `npm ci; npm run lint; npm test; npm run typecheck; npm run build`. Test responsive screens in real browsers including /, /check, /assistant, /research, /history, /how-it-works, /privacy. On /research use an **aggregate** JSON report only, not raw personal photos or predictions.
4. In root terminal, set a unique local-only `DERMALENS_POSTGRES_PASSWORD` and run `docker compose up --build -d --wait`, `docker compose exec -T api /opt/dermalens/.venv/bin/alembic upgrade head`, then `uv run --frozen --no-sync python -m scripts.operational_smoke`. Inspect `docker compose ps`, `docker compose logs --no-color --tail=100` (redact credentials, tokens, photos). Run `docker compose down` when done; DO NOT delete persistent volumes.
5. Verify actual image upload (JPEG, PNG, WebP), corrupt/oversize rejection, no/multiple face rejection, warning states, 429 rate limit, no raw-photo persistence; validate 503 inference readiness and absence of POST /api/v1/analyses in the current nonclinical build.
6. Re-run migrations and ownership/consent tests using disposable PostgreSQL; **do not invent OIDC tokens or keys**. Real sign-in and real Grok require external identity provider and API credentials.
7. Record exact commands, exit codes, pytest test counts, routes checked, screenshots, browser console errors, CI SHA and PASS/FAIL/BLOCKED for each README feature. Fix only reproducible integration bugs on a fresh branch/PR, never silently merge.

## Release gates still NOT implemented or independently verified

- Actual trained `.keras` checkpoint, exact `label_map.json`, checksum-verified manifest and original research predictor parity.
- Independently labeled, rights-cleared real-image benchmark and leakage-reviewed subject-disjoint train/calibration/test with inclusive capture populations.
- Clinically defensible uncertainty, OOD, unknown classes, temperature/abstention policy, XAI quality and alignment/ROI transformation parity.
- **Public analysis creation/structured result**, stored owned history integration, user-facing verified login, feedback UX and explainability overlay. Current analysis endpoint stays absent; quality checks are NOT diagnosis.
- Real semantic embedding + pgvector RAG and provider API live verification. Current public docs explorer is lexical; protected Grok backend is not a public medical assistant.
- Production cloud staging, distributed rate limiting, penetration/security/privacy tests, image deletion/retention policy, encrypted object storage, persistent observability, rollback and clinical/regulatory approval.

**Model connection readiness:** after engineering QA, securely provide the checkpoint/label map/manifest and approved parity images privately. These artifacts are intentionally ignored by Git. The next PR must integrate verified loading and model-version tracking behind fail-closed gates and demonstrate real independent evaluation before any diagnostic route is exposed.

See docs/README_FEATURE_AUDIT.md and GitHub Issue #20. This handoff never claims README section 51 is fully complete.
