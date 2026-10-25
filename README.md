# DermaLens AI

**A modular, privacy-conscious facial skin research platform — from image checks to reproducible model engineering.**

[![Backend and frontend CI](https://github.com/shanmukhdatta/DermaLens-AI/actions/workflows/phase1.yml/badge.svg)](https://github.com/shanmukhdatta/DermaLens-AI/actions/workflows/phase1.yml)
[![Architecture validation](https://github.com/shanmukhdatta/DermaLens-AI/actions/workflows/phase0.yml/badge.svg)](https://github.com/shanmukhdatta/DermaLens-AI/actions/workflows/phase0.yml)

> **Project status — October 2026:** The public-facing application, image suitability checks, FastAPI backend, accounts/feedback source, evaluation utilities and deployment infrastructure are implemented at differing levels of verification. **No trained skin-classification checkpoint is connected in the public deployment, and this is not a clinically validated diagnostic tool.** If the image-check API is not hosted, the frontend explains that the service is unavailable instead of simulating results.

## Why this project exists

A research classifier is not a usable AI product by itself. DermaLens AI explores the engineering around a facial skin image classifier: safe input validation, consistent preprocessing, artifact provenance, explainability, uncertainty, privacy-aware services, optional user feedback, reproducible evaluation and deployment.

The interface is designed to help visitors understand the research and inspect real engineering features **without mistaking an unfinished AI model for a diagnosis**.

**Try the running app:** _Public deployment URL to be added after deployment._

**Research source:** [Facial_Skin_Diesease](https://github.com/shanmukhdatta/Facial_Skin_Diesease). A licensed, isolated source snapshot is also available in [research/](research/README.md).

## What visitors can explore

| Feature | What exists in this repository | Public/release status |
| --- | --- | --- |
| White-and-green Next.js experience | Homepage, pipeline explanation, six-class research overview, privacy and documentation pages | Implemented; browser acceptance pending |
| Image suitability check | JPEG/PNG/WebP decoding, basic brightness and sharpness signals, exactly-one-face gate | Available only with a configured running API; **not disease detection** |
| Model adapter | Private checkpoint/label-map contract, SHA256 manifest, original predictor parity scripts | Implemented; **real weights and parity evidence pending** |
| Facial preprocessing | OpenCV Haar baseline, experimental eye alignment and proposed ROI crops | ROI transformations are not enabled for real model serving until evaluated |
| Six-class skin research | Acne, Fungal Infection, Hyperpigmentation, Normal Skin, Skin Cancer, Vitiligo | Supported research label space; live classification disabled |
| Calibration, OOD and Grad-CAM | Offline evaluation and explainability modules | Requires trained checkpoint, held-out metrics and expert review |
| Accounts, history and feedback | OIDC architecture, privacy-scoped database APIs, encrypted nonclinical result metadata and feedback controls | Live provider/account browser verification pending |
| Documentation assistant | Cited lexical lookup; protected Grok adapter for curated documents | Lexical search when API online; semantic vector RAG not complete |
| Research dashboard | Browser-local aggregate JSON metrics viewer | Implemented; user-provided non-identifying report only |
| MLOps | Docker, GitHub Actions, manifests, metrics, drift and offline review gates | Engineering foundation; live staging/monitoring/release evidence pending |
| Reinforcement learning | Intentionally omitted | Future optional research only |

### Technical stack

**Frontend:** Next.js 16, React 19, TypeScript, responsive accessible CSS.  
**Backend:** FastAPI, Python 3.11, modular service interfaces, Pydantic, SQLAlchemy/Alembic.  
**Computer vision:** OpenCV/Pillow, Keras model adapter, optional research Grad-CAM and calibration.  
**Data and security:** PostgreSQL, OIDC/JWKS verification, consent, encrypted analysis metadata, no default raw photo retention.  
**Operations:** Docker Compose, GitHub Actions and external deployment manifests.

## Architecture

```text
Browser / Next.js (Vercel)
  |-- Home, research, architecture, privacy, docs
  |-- Quality check (same-origin server proxy)
  |-- Optional owner account / feedback (needs live OIDC)
  |
  v HTTPS (server-to-server; only when API is configured)
FastAPI (container host)
  |-- bounded image decoder, blur/brightness, face count
  |-- model manifest + fail-closed research adapter
  |-- offline calibration / OOD / XAI research
  |-- owner-scoped history + moderated feedback
  |-- cited documentation retrieval
  |-- request limits, logs, telemetry
  |
  +--> PostgreSQL (optional for public demo; required for accounts)
  +--> Private authorized model files (NOT bundled)
```

**Production safety boundary:** Live diagnosis, cancer screening/rule-out, severity grading and clinical interpretation are not implemented or authorized. The gated nonclinical research analysis endpoint cannot be enabled in the production environment.

Detailed decisions are kept in [the architecture](docs/01_SYSTEM_ARCHITECTURE.md), [computer vision contract](docs/02_COMPUTER_VISION_PIPELINE.md), [model research](docs/03_MODEL_AND_RESEARCH.md), [backend](docs/04_BACKEND_ARCHITECTURE.md), [RAG](docs/05_RAG_ASSISTANT.md), [feedback](docs/06_FEEDBACK_AND_CONTINUAL_LEARNING.md), [MLOps](docs/07_MLOPS_AND_DEPLOYMENT.md), [API contracts](docs/08_API_AND_DATA_FLOW.md), and [privacy](docs/09_PRIVACY_AND_SAFETY.md). The earlier full conceptual blueprint is archived in [docs/ORIGINAL_MASTER_PLAN.md](docs/ORIGINAL_MASTER_PLAN.md); it is a plan, **not a claim of completion**.

## Where the code lives

```text
apps/api/                 FastAPI app, typed routes, middleware, auth gates
apps/web/                 Next.js site and bounded same-origin public proxy
services/cv/              Image quality, model adapter, alignment, Grad-CAM
services/learning/        Evaluation, calibration, feedback, drift, leakage
services/persistence/     Database, encryption, scoped history/retention
services/rag/             Approved-document retrieval and provider adapter
packages/                 Shared contracts, security and telemetry
models/manifests/         Versioned model manifest schema (not weights)
research/legacy/          Licensed original research source and notebooks
scripts/                  Reproducibility, audits, manifests and evaluation
infra/docker/             Separate API/web Dockerfiles
docs/                     Contracts, ADRs, runbooks and honest gap tracking
tests/                    Backend, contracts, privacy and research-unit tests
render.yaml               Optional container API deployment blueprint
```

## Run locally

Prerequisites: Python 3.11, Node.js 22+, npm, [uv](https://docs.astral.sh/uv/). Docker Desktop is optional.

**Frontend only** (public pages work; image checks/docs search show unavailable without an API):

```bash
cd apps/web
npm ci
npm run dev
```

Open http://localhost:3000.

**Backend and frontend** (two terminals at repository root):

```bash
uv sync --python 3.11 --frozen --all-groups
uv pip install --python .venv/bin/python -r requirements-cv.txt -r requirements-persistence.txt -r requirements-rag.txt
DERMALENS_ENABLE_IMAGE_QUALITY_CHECKS=true uv run --frozen --no-sync uvicorn apps.api.dermalens_api.main:app --host 127.0.0.1 --port 8000
```

On Windows PowerShell, use `$env:DERMALENS_ENABLE_IMAGE_QUALITY_CHECKS="true"` before the `uv run` command and `.venv\Scripts\python.exe` for pip installation. Run `npm run dev` separately in `apps/web/`; the development proxy defaults to localhost:8000.

**Docker local integration:**

```bash
# Put DERMALENS_POSTGRES_PASSWORD=<strong private value> in an untracked .env
docker compose up --build -d --wait
docker compose ps
docker compose down
```

Never publish a development Compose stack directly to the internet or commit private facial images/weights.

## Tests and reproducibility

```bash
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync ruff format --check .
uv run --frozen --no-sync mypy apps packages services
uv run --frozen --no-sync python -m pytest -q
uv run --frozen --no-sync python -m scripts.validate_phase0
cd apps/web
npm ci && npm run lint && npm run typecheck && npm test && npm run build
```

The research snapshot is preserved separately and excluded from the production linter/runtime to avoid conflating original training experiments with application acceptance. Historical CI evidence: see [engineering handoff](docs/FINAL_ENGINEERING_HANDOFF.md). **A passing software test is not a clinical model evaluation.**

## Deploy the public research showcase

The recommended architecture is **Vercel for `apps/web/`** plus an optional separate FastAPI container host. The public website can deploy **without the model, database or backend** and honestly display unavailable features.

1. Create a Vercel project linked to this repository. Set **Root Directory = `apps/web`**, framework Next.js, Node.js 22+.
2. Optionally deploy the API from [render.yaml](render.yaml) using the Dockerfile. Provide a real HTTPS public web origin; keep all medical analysis flags disabled.
3. Set Vercel **`DERMALENS_WEB_API_BASE_URL=https://<your-api-host>`** if you want real image quality checks and documentation search. This is a server-only variable; no weights or secrets in `NEXT_PUBLIC_*`.
4. Rebuild Vercel; test the homepage, quality flow, network failures, documents, privacy and mobile layout. Accounts require separately verified OIDC.
5. Add the real site URL above after testing. Keep protected medical inference disabled.

See [deployment runbook](docs/RECRUITER_DEPLOYMENT.md) for environment variables, security gates, deployment decisions, smoke tests and rollback.

## When a trained model becomes available

**Do not copy arbitrary `.keras` weights into GitHub or Vercel.** Use an authorized, privately stored checkpoint, exact `label_map.json`, training/source commit and SHA256 manifest; follow [the model parity runbook](docs/MODEL_ARTIFACT_PARITY_RUNBOOK.md). Reproduce original predictor outputs first, then validate on independent rights-cleared real photographs with subgroup and OOD review. This is separate from releasing the public engineering showcase.

The shipped production app must keep inference disabled until the safety and deployment gates are actually met.

## Status, limitations and next steps

- **Built:** UI/UX, safe image-check backend, modular APIs, research source snapshot, nonclinical analysis adapters, account/privacy foundations, evaluation tools, CI and container deployment files.
- **Still to validate:** Full real-browser E2E, independent external model evaluation, identity-provider integration, production monitoring/privacy/security, semantic vector RAG and expert assessment of XAI.
- **Optional future research:** severity grading, improved segmentation, controlled model improvement and reinforcement learning only with validated outcomes.

Track specific blockers in [the gap closure checklist](docs/FINAL_GAP_CLOSURE_CHECKLIST.md) and [the phase tracker](docs/PHASE_TRACKER.md). The research archive preserves original [MIT license attribution](research/legacy/LICENSE). The platform source is MIT-licensed in [LICENSE](LICENSE).

## Responsible use

Do not use this prototype to diagnose, exclude, grade or treat disease, especially cancer. A prediction score or Grad-CAM image is not clinical evidence. Uploaded face photos require permission. Real-world human/clinical evaluation and the appropriate privacy and regulatory review are separate release requirements.

**Engineering goal:** make a research classifier reproducible, understandable and operable — while being explicit about what remains unvalidated.
