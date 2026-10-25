# GEMINI.md — DermaLens AI Persistent Project Handoff

> **Purpose:** The permanent "open this first" context file for Google Antigravity / Gemini or another coding agent. Read this file **before editing anything**. It records what is built, what remains, how to test it, and how to resume work across sessions.
>
> **Last reconciled:** 2026-10-25, after PR [#37](https://github.com/shanmukhdatta/DermaLens-AI/pull/37), merged to `main` at `0570cda6aeadd4ccc286bbbf99924e0acacea0ed`. Snapshot is not a claim that all tasks are finished. **The status can become stale: always check Git history and CI before using it.**
>
> **Project:** https://github.com/shanmukhdatta/DermaLens-AI  
> **Original research:** https://github.com/shanmukhdatta/Facial_Skin_Diesease  
> **Owner intent:** An honest, polished, publicly inspectable, recruiter-ready AI/software-engineering **research showcase** now; connect and validate private model weights and more advanced integrations later. Reinforcement learning is optional future research, NOT a v1 milestone.

## 0. Mandatory startup procedure (every new session)

1. Run `git status --short`, `git branch --show-current`, `git fetch origin`, `git log -5 --oneline` and `git rev-parse HEAD`. **Never reset, overwrite, delete, or discard uncommitted user work.** If working tree has changes, inspect them.
2. Read this `GEMINI.md`, the root [README](README.md), [deployment guide](docs/RECRUITER_DEPLOYMENT.md), [gap checklist](docs/FINAL_GAP_CLOSURE_CHECKLIST.md), [phase tracker](docs/PHASE_TRACKER.md) and relevant module docs **before proposing changes**. Note dated/stale docs (e.g. the phase tracker describes PRs through October 14).
3. Check merged PRs and real GitHub Actions checks for the actual branch SHA. Check the relevant issue(s) and PRs; record actionable errors, not unsubstantiated claims.
4. Select the **highest priority unblocked** item in section 4. Work in an isolated feature branch with small, reviewable commits/PRs. Maintain contracts and privacy; do not rewrite completed modules without a demonstrable need.
5. Run relevant tests, document pass/fail/skipped/blocked **and their real commands**, then update the status, task checkbox and session log below in the SAME PR. Include real CI URL/SHA and limitations.
6. Do not claim a live URL, running service, passed tests, model metrics, clinical validation or completion without direct evidence. **A checked task means acceptance evidence exists**, not just source code.

**Resume prompt to paste into Antigravity:**
> Read `GEMINI.md` first, then `README.md` and `docs/FINAL_GAP_CLOSURE_CHECKLIST.md`. Compare the current branch and CI with the recorded snapshot. Tell me (a) what is verified complete, (b) what is pending/blocked, and (c) the next unblocked task. Implement only that agreed task using our existing architecture. Run tests, fix failures, open a PR, and update `GEMINI.md` with exact evidence. Never pretend the medical classifier is connected or publish private model/data files. Preserve uncommitted changes and do not merge automatically if checks fail.

## 1. Project identity and safety boundaries

DermaLens AI is a **modular facial skin-condition research-engineering platform** with Next.js, FastAPI, optional PostgreSQL/OIDC, image suitability checks, candidate Keras model adapters, research evaluation, documentation retrieval, telemetry and deployment packaging.

The research label space comprises six top-level categories:

- Acne
- Fungal Infection
- Hyperpigmentation
- Normal Skin
- Skin Cancer
- Vitiligo

**DO NOT** describe these as live medical diagnoses, cancer clearance, validated severity/subtype grading or a licensed medical device. "Normal Skin" is a research label, not clinical reassurance. The classifier's real serialized checkpoint is **not included**; without independent validation, a raw probability is not clinical confidence and a Grad-CAM heatmap is not proof of a lesion.

**Hard invariant:** production research-analysis mode must stay disabled. Never remove fail-closed readiness, security controls, source validation, upload-size bounds or consent requirements to make a demo look complete. No synthetic/fake model output or performance claims, no fake metrics and no model-weight download at public request time. No raw facial photos, private datasets, checkpoints, OIDC credentials, Grok tokens, encryption keys or logs with personal data in Git or public build artifacts.

## 2. Snapshot: what actually exists now

**Reference point:** `main` after merged PR [#37](https://github.com/shanmukhdatta/DermaLens-AI/pull/37), SHA `0570cda6…` (2026-10-25).

**Observed evidence:** PR #37's final branch checks passed: 133 Python tests (68 non-failing warnings), 17 web tests (8 test files), backend/web lint and type checks, Next.js production build, Phase 0 contracts, Compose configuration and Docker staging smoke. The post-merge main `phase0`, `phase1` and `phase8` CI jobs also passed. These are **automated software checks only**, not manual Vercel/Antigravity browser E2E or medically approved inference.

| Subsystem | Code state | Actual readiness / next proof |
| --- | --- | --- |
| Architecture, contracts, ADRs and source structure | **Implemented** | Keep docs and runtime contracts in sync |
| Research training/evaluation/generation source | **Imported** to `research/legacy/`, MIT attribution and source SHA retained | Research source snapshot, **not** proof of trained weights, completed experiments or clinical measurements |
| Next.js frontend, responsive white-and-green UI | **Implemented; CI passed** | Inspect real browsers (desktop/mobile, keyboard, contrast, links) and Vercel preview |
| FastAPI routes, middleware and typed errors | **Implemented; tested** | Deploy independent nonclinical API; real-host checks |
| Image quality and single-face baseline | **Implemented** (`services/cv/quality.py`, Haar, file/face/blur/brightness) | Check real authorized photos and production ingress, no clinical assessment |
| Face alignment and ROI | **Experimental offline helper** (`services/cv/face_geometry.py`) | Compare ROI vs original whole-frame model input on held-out data before enabling |
| Six-class Keras model adapter + manifest/parity CLIs | **Code implemented** | **BLOCKED:** real authorized `.keras`, exact `label_map.json`, training SHA/versions and permitted golden images |
| Model-backed nonclinical analysis/results | **Protected experimental source coded** | **BLOCKED:** weights, real OIDC/DB integration, external safety validation; disabled in production |
| Calibration, OOD, abstention, Grad-CAM | **Offline helpers coded** | **BLOCKED:** model-backed held-out validation, reviewed thresholds and XAI suitability |
| Database, owner history, consent, feedback | **Source and automated tests implemented** | Real OIDC provider + PostgreSQL + browser flow and security/retention E2E |
| Documentation search | **Lexical cited lookup implemented**; Grok adapter protected | Persistent semantic embedding/vector RAG and live provider verification **incomplete** |
| Research report viewer | **Browser-local aggregate JSON UI implemented** | Browser testing with lawful non-identifying aggregate fixture |
| Versioning, drift and CI/MLOps | **Foundational code/CI exists** | Durable telemetry, real staging, backups, distributed limits, alerts, rollback and deployment verification |
| Public Vercel site | **Deployable source/config prepared** | **Not yet verified deployed**; insert URL only after real release |
| Reinforcement learning | **Not implemented by design** | OPTIONAL FUTURE RESEARCH ONLY |

**What is NOT done:** clinical validation; an actual trained checkpoint wired to live predictions; medically defensible uncertainty/XAI; verified production sign-in; full semantic vector RAG; external deployment E2E; real staging monitoring/security approval. **Do not call the complete README Definition of Done achieved.**

## 3. Authoritative architecture and code map

Preserve the current modular architecture. Do not turn this into a monolith with research training dependencies bundled into the live website.

| Path | Responsibility |
| --- | --- |
| `apps/web/` | Next.js 16 / React 19, public web pages, bounded `/api/public/quality` and `/api/public/docs` same-origin proxies |
| `apps/api/dermalens_api/` | FastAPI composition, config, routers, security boundaries |
| `services/cv/` | Safe image checks, OpenCV face detector, research geometry, verified Keras adapter, Grad-CAM |
| `services/learning/` | Evaluation, calibration, leakage checking, feedback, drift, candidate review |
| `services/persistence/` | Accounts/results/feedback persistence, encryption, retention |
| `services/rag/` | Allowlisted Markdown indexing, lexical citations, protected Grok adapter |
| `packages/` | Shared security, telemetry and contracts |
| `research/legacy/` | Snapshot of original training/generation/evaluation/inference source and notebooks; isolated optional heavy dependencies |
| `models/manifests/` | Model artifact JSON schema, **not weights** |
| `scripts/` | Model packaging/parity, audit/evaluation, smoke, private retention tools |
| `infra/docker/`, `compose.yaml` | Container packaging/local test stack |
| `render.yaml` | Optional nonclinical container API hosting blueprint |
| `docs/` | Architecture, requirements, security, runbooks and task acceptance proof |
| `tests/` | Python and API tests; `apps/web/src/lib/*.test.ts` for TypeScript |

**Preserve model preprocessing contract:** PIL RGB → bilinear 224×224 → float32 [0,255] → internal model preprocessing; never normalize twice. Do not replace full-frame model inputs with face crops until an independent comparative evaluation approves that change.

Relevant sources: [system design](docs/01_SYSTEM_ARCHITECTURE.md), [CV contract](docs/02_COMPUTER_VISION_PIPELINE.md), [model research](docs/03_MODEL_AND_RESEARCH.md), [API specification](docs/API_SPECIFICATION.md), [privacy](docs/09_PRIVACY_AND_SAFETY.md), [model parity runbook](docs/MODEL_ARTIFACT_PARITY_RUNBOOK.md). The [archived master blueprint](docs/ORIGINAL_MASTER_PLAN.md) is conceptual and historical; consult it for intent, **not implementation status**.

## 4. Work queue — checked = independently verified, not just coded

Choose a task in priority order. Each ID must have **owner/branch, acceptance evidence, and last-updated date** when completed. A blocked task must retain a specific unblock condition. Keep this section synchronized with changes.

### Milestone R0 — Public recruiter showcase (NO trained model needed)

- [x] **R0-01 — Research source, licensing and project clarity.** Original MIT research code/notebooks imported under `research/legacy/` and old blueprint archived; transparent recruiter README (merged PR #37, 2026-10-25).
- [x] **R0-02 — White/green frontend, accurate six-class research overview.** Homepage and pipeline explanation built and tested in CI; NOT a manual visual QA claim (PR #37, 2026-10-25).
- [x] **R0-03 — Split-hosting baseline.** Vercel frontend plan, Render Docker API blueprint, safe same-origin proxies and deployment guide merged and CI-tested (PR #37, 2026-10-25).
- [ ] **R0-04 — Fresh local desktop/mobile and keyboard QA.** On Windows/Antigravity: clean clone, launch web and API, inspect all pages, loading/empty/error states, browser console, color contrast, focus, resizing, links, consent and no unexpected medical results. **Accept:** screenshots + environment + test table and reproducible issues/fixes on a PR.
- [ ] **R0-05 — Vercel preview and verified public UI.** Create/connect Vercel project with `apps/web` root; verify deployment of actual SHA. Backend absent must show explicit 503/unavailable, not fake results. **Accept:** actual URL, runtime build log, SHA, responsive browser smoke and rollback instructions.
- [ ] **R0-06 — Optional live nonclinical FastAPI host.** Deploy container with HTTPS + exact origin, enable only bounded image checks + lexical docs; test authorized images, wrong file type, 8 MB limit, multiple/no-face handling and API downtime. **Accept:** URL, real HTTP results and server logs redacted; no facial image persisted. Production classifier remains off.
- [ ] **R0-07 — Recruiter demonstration polish.** After a real deployment, add verified live URL, screenshots, architectural overview, feature-status comparison and test/CI badges. Verify README/code links and privacy wording. **Accept:** screenshots/links and PR reviewed at real SHA, no invented metrics or fake classifier demos.

**R0 exit criterion:** A recruiter can visit a real hosted, professional, responsive website, understand the six-class *research plan*, use only genuinely hosted nonclinical demo capabilities and inspect the source/architecture. A public medical AI prediction is **NOT** an R0 requirement.

### Milestone R1 — User-account and nonclinical application integration

- [ ] **R1-01 — OIDC and database integration.** Configure real provider (no credentials in Git), protected browser session, PostgreSQL migrations, user consent, session expiry, user ownership, export, deletion and feedback. **Accept:** real browser E2E + security tests; external credentials/provider needed.
- [ ] **R1-02 — Full documentation assistant.** Complete embeddings + approved persistent vector retrieval if retaining the original RAG scope; provider-grounded responses with citations and abstention; live provider key testing. **Accept:** adversarial docs-question tests, source validity, no image/health content sent to LLM, protected secrets.
- [ ] **R1-03 — Production operations engineering.** Durable monitoring and alerting, distributed ingress limits, health/liveness, backup/restore, secrets rotation, incident/retention rehearsal and rollback. **Accept:** real-host staging evidence and reviewed threat model, not merely files in repository.

### Milestone R2 — Verified private research inference (NOT public clinical release)

- [ ] **R2-01 — Original checkpoint + manifest and label map.** **BLOCKED on actual authorized private `.keras`, original ordered label map, training source SHA, runtime versions and golden image reference outputs**. Run `docs/MODEL_ARTIFACT_PARITY_RUNBOOK.md` and record digest/parity results. No private material in Git.
- [ ] **R2-02 — Subject-disjoint real benchmark and data rights.** **BLOCKED on independently labeled, legally usable real images and expert review.** Detect duplicates/leakage and measure per-class precision/recall, calibration, site/device and subgroup reliability with confidence intervals.
- [ ] **R2-03 — Calibrated policies / OOD / XAI.** Choose thresholds from held-out real data; test abstention and unknown input; verify architecture-specific Grad-CAM availability and explainability limitations. **BLOCKED until R2-01/R2-02**.
- [ ] **R2-04 — Protected end-to-end research-analysis flow.** Wire real artifact to existing gated POST/GET/DELETE analysis, history, consent and feedback, with immutable model/version metadata; independently verify no raw-image storage and fail-closed errors. **BLOCKED until R1-01 + R2-01**. Keep the research-only endpoint off in `production`.
- [ ] **R2-05 — Face preprocessing comparison.** Compare baseline whole-frame vs candidate face alignment/ROI on the SAME disjoint test cases. Approve changes only with measured performance, no additional normalization.

### Milestone R3 — Independent medical/security review (separate from coding)

- [ ] **R3-01 — External clinical/domain review and regulatory/privacy assessment.** Real population performance, safety, retention/deletion, risk management, security and any appropriate approval. No claims of a medical diagnostic service before actual authorization.
- [ ] **R3-02 — Controlled learning from curated expert-validated feedback.** Candidate evaluation and manual promotion/rollback only; feedback is not automatic truth.
- [ ] **FUTURE / OPTIONAL — Severity grading, lesion segmentation and reinforcement learning.** Only with separately sourced validated labels/rewards, explicit research question and comparator baseline. **Not a Version 1 release blocker.**

## 5. Immediate next action (when no newer changes supersede this)

**First next task: R0-04** — Fresh manual browser verification of the white/green app, preferably using Antigravity on Windows. Then **R0-05** (Vercel preview and verified URL), then optionally **R0-06** (independently hosted quality/docs API), then **R0-07** (update public recruiter README). Do not prematurely start model checkpoint integration or RL.

At the start of each session, first check if any task was already completed in newer PRs; move forward rather than duplicating it.

## 6. Verification and local startup commands

### Windows PowerShell (recommended for Antigravity)

```powershell
git status --short
git fetch origin
git switch main
git pull --ff-only origin main
git rev-parse HEAD

# Backend (Python 3.11; uv installed)
uv sync --python 3.11 --frozen --all-groups
uv pip install --python .venv\Scripts\python.exe -r requirements-persistence.txt -r requirements-cv.txt -r requirements-rag.txt
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync ruff format --check apps packages services
uv run --frozen --no-sync mypy apps packages services
uv run --frozen --no-sync python -m pytest -q
uv run --frozen --no-sync python -m scripts.validate_phase0
uv run --frozen --no-sync python -m scripts.check_repository_hygiene

# Terminal A: nonclinical local backend (does not need weights)
$env:DERMALENS_ENABLE_IMAGE_QUALITY_CHECKS="true"
uv run --frozen --no-sync uvicorn apps.api.dermalens_api.main:app --host 127.0.0.1 --port 8000

# Terminal B: web
cd apps/web
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run dev
```

*If the working tree is dirty, DO NOT blindly `git switch` or `pull`; inspect it and preserve user changes.* Commands above assume a clean checkout. Open `http://localhost:3000`; the local web gateway defaults to `http://127.0.0.1:8000` if no explicit server-side API host is configured.

### Docker disposable local smoke

```bash
# Set DERMALENS_POSTGRES_PASSWORD privately in an untracked .env first
docker compose config -q
docker compose up --build -d --wait
docker compose ps
docker compose logs --no-color --tail=100
# Follow docs/FINAL_ENGINEERING_HANDOFF.md for migrations and operational smoke
docker compose down
```

Do NOT run `docker compose down --volumes` against anyone's valuable database. Never commit the `.env` file or logs with tokens/photos.

### Evidence standards

For each changed feature, record: **commit SHA; exact command; test count/exit code; relevant CI URL; API routes; browser/device; screenshot path if lawful and sanitized; PASS/FAIL/BLOCKED; what was NOT tested.** Fix reproducible failures before merging. Failing external requirements remain BLOCKED rather than assumed complete. Do not add mock scores to public displays.

**2026-10-25 verified software evidence:** PR [#37](https://github.com/shanmukhdatta/DermaLens-AI/pull/37), merged `0570cda6…`; PR checks 133 Python passed, 17 web passed, Next.js build/lint/types and Docker staging smoke passed. Production deployment **not verified**.

## 7. Deployment checklist — keep honest public behavior

- Vercel: Import GitHub repository, framework Next.js, **Root Directory `apps/web`**, Node 22+, use a preview first.
- A Vercel-only site is valid: homepage, architecture, privacy, research report can work; `/check` and `/assistant` must return an honest error without the backend.
- Optional API host: deploy `infra/docker/api.Dockerfile` via `render.yaml` or equivalent. Set `DERMALENS_ENV=production`, `DERMALENS_PUBLIC_WEB_ORIGIN=https://<exact-vercel-host>`, `DERMALENS_ENABLE_IMAGE_QUALITY_CHECKS=true`; keep model analysis, image storage and experimental endpoints disabled.
- Configure Vercel's **server-only** `DERMALENS_WEB_API_BASE_URL=https://<actual-api-host>` after the backend is reachable. Never expose auth credentials in `NEXT_PUBLIC_*`.
- Check `GET /api/v1/health` (200); `GET /api/v1/readiness` may intentionally return 503 because medically approved inference is unavailable. Treat it as **readiness**, not server liveness.
- Verify real status for `/`, `/check`, `/assistant`, `/research`, `/history`, `/how-it-works`, `/privacy`.
- Keep the README live-link placeholder until Vercel genuinely deploys and a browser check passes. If the service is unavailable, display disabled/unavailable rather than fake predictions.
- Apply backups, TLS, monitoring, rate-limit and retention reviews before enabling real accounts/health-data handling.

[Full deployment runbook](docs/RECRUITER_DEPLOYMENT.md)

## 8. After-action protocol — update this file every time

At the end of **every material coding/testing/deployment session**:

1. Refresh the **Last reconciled** date, verified reference SHA and CI status in sections 0 and 2.
2. Update the exact `R*-##` checklist task(s): checked only when acceptance evidence exists; keep BLOCKED items and dependencies explicit; never erase pending work.
3. Update the **Immediate next action** in section 5. State the smallest reproducible next task and any prerequisites.
4. Add a new entry to `Session history` below containing the *real* action, PR/commit, tested outcomes, remaining problems and next task.
5. Update README/phase/gap docs as necessary to avoid contradictory statements. Do not silently reclassify 144 historical checklist requirements as complete.
6. Commit `GEMINI.md` alongside the feature's PR, and verify CI after edits. If an Antigravity session ends without GitHub push, mark changes **LOCAL / UNCOMMITTED** and record the changed paths; never imply the remote main was changed.

### Session history (append newest first; do not rewrite prior evidence)

| Date (IST) | Session / evidence | Real outcome | Next action |
| --- | --- | --- | --- |
| 2026-10-25 | PR [#37](https://github.com/shanmukhdatta/DermaLens-AI/pull/37) → `0570cda6` | Imported original source snapshot; new green/white frontend, nonclinical public proxies, recruiter README and deployment runbook. 133 Python + 17 web tests and Docker staging smoke passed on PR. Live Vercel UI and clinical analysis **not verified**. | R0-04 manual browser QA, then R0-05 Vercel preview |

**Template for future entries:**

```text
Date/time (IST):
Branch + before/after SHA:
Task IDs:
Changed files/modules:
What changed and why:
Commands/tests (actual output): PASS / FAIL / SKIPPED / BLOCKED
CI/PR/deployment evidence links:
Remaining blockers:
Next exact action:
```

## 9. Completion definition — never confuse three different milestones

**Engineering showcase COMPLETE (R0):** public Vercel URL inspected, clear model-unavailable behavior, functional available nonclinical routes or honest unavailable states, documented architecture, accessible responsive UI, and verifiable CI/browser evidence.

**Integrated private research system COMPLETE (R1 + R2):** real identity/data integration, original checkpoint parity, reproducible model-backed research results with honest uncertainty and guarded feedback, valid held-out evaluation and expert-reviewed limitations. This **does not** mean clinical approval.

**Clinical deployment complete (R3):** only if independently justified and authorized with clinical, privacy, security and relevant regulatory safeguards. Never infer this from code being merged.

**Owner's present priority:** **R0 first**. Model integration later. Reinforcement learning remains explicitly deferred.
