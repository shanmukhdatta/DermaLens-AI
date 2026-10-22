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
5. Verify actual image upload (JPEG, PNG, WebP), corrupt/oversize rejection, no/multiple face rejection, warning states, 429 rate limit, no raw-photo persistence; validate 503 clinical inference readiness and absence of POST /api/v1/analyses in the **default** nonclinical build. A separate experimental nonproduction feature flag now registers a guarded research-only analysis API; its existence is not diagnostic release readiness.
6. Re-run migrations and ownership/consent tests using disposable PostgreSQL; **do not invent OIDC tokens or keys**. Real sign-in and real Grok require external identity provider and API credentials.
7. Record exact commands, exit codes, pytest test counts, routes checked, screenshots, browser console errors, CI SHA and PASS/FAIL/BLOCKED for each README feature. Fix only reproducible integration bugs on a fresh branch/PR, never silently merge.

## Release gates still NOT implemented or independently verified

- Actual trained `.keras` checkpoint, exact `label_map.json`, checksum-verified manifest and original research predictor parity.
- Independently labeled, rights-cleared real-image benchmark and leakage-reviewed subject-disjoint train/calibration/test with inclusive capture populations.
- Clinically defensible uncertainty, OOD, unknown classes, temperature/abstention policy, XAI quality and alignment/ROI transformation parity.
- **Clinical public analysis/structured result** and clinically approved explainability overlay are NOT released. The research-only guarded analysis/results and browser owner-history/feedback source now exist, while live OIDC-provider verification, real model assets and specialist review remain external.
- Real semantic embedding + pgvector RAG and provider API live verification. Current public docs explorer is lexical; protected Grok backend is not a public medical assistant.
- Production cloud staging, distributed rate limiting, penetration/security/privacy tests, image deletion/retention policy, encrypted object storage, persistent observability, rollback and clinical/regulatory approval.

**Model connection readiness:** use the newly implemented candidate-only manifest and original-predictor parity scripts with real private checkpoint, label map, source SHA and permitted images. These artifacts remain outside Git. Real loading, measured parity, external clinical benchmarking and medical approval must precede any future clinical release.

See docs/README_FEATURE_AUDIT.md and GitHub Issue #20. This handoff never claims README section 51 is fully complete.

## Additional integration guides (October 2026)

- `docs/OIDC_BROWSER_INTEGRATION.md`: optional verified browser identity BFF. Populate web and API issuer/client settings, run real browser login tests, confirm metadata ownership and consent; no verified identity provider is bundled.
- `docs/PRIVATE_MODEL_BENCHMARK.md`: offline private image CSV -> verified Keras runtime -> pseudonymized probability table -> subject-leakage-reviewed research metrics. Requires private real checkpoint, exact label map, dataset rights, real subject IDs and independent expert review. No public diagnosis endpoint is enabled.

## 2026-10-22 code and acceptance update

- PR #32 merged the authenticated nonproduction experimental analysis route, privacy-preserving encrypted result and browser research workflow. Production medical inference remains disabled.
- PR #33 merged research feedback controls and ciphertext record-identity checks.
- PR #34 merged evaluation confusion/sensitivity/specificity and stronger perceptual duplicate audit.
- PR #35 merged model packaging and original research-predictor parity CLIs. No real trained checkpoint or clinical cohort was available to execute that parity.
- GitHub Actions on the PR #35 head passed backend lint/typecheck/tests (132 Python tests passed with 68 warnings), frontend lint/tests/build, architecture contracts and Docker staging smoke. Those automated checks are not a clinical or production security audit.
- `docs/FINAL_GAP_CLOSURE_CHECKLIST.md` now records which source features exist and precisely which external evidence remains. Do not claim full README clinical acceptance.
