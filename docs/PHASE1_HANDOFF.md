# Phase 1 handoff — repository engineering foundation

**Scope boundary:** Start only after review of [Phase 0 tracker](PHASE_TRACKER.md), architecture, ADRs, OpenAPI and manifest schema. Do not begin Phase 2 or integrate an unverified trained checkpoint. Original research repo remains unmodified.

## What to implement

1. Inspect the latest merged production branch and PR #1; reconcile any unmerged changes first.
2. Create the real application workspace matching [target directory structure](REPO_STRUCTURE.md): `apps/api` with Python 3.11+ package, `apps/web` with Next.js + TypeScript, and in-process `services/cv`, `services/rag`, `services/learning` Python module scaffolds **without fake production claims**.
3. Add development dependencies with reproducible lockfiles, typed settings from environment, structured error interface, unit testing, lint/typecheck/format scripts, a local API and frontend start command, and CI jobs for both workspaces.
4. Add tests proving imports/build/start and strict separation of real vs `TEST_ONLY` mock model adapters. With no checkpoint, analysis must be explicitly not ready; do not call simulated results real.
5. Keep the v1 OpenAPI and manifest contract valid; document any proposed breaking difference as a new ADR before changing behavior. Write code/config/test files and commit them on a new Phase 1 branch.
6. Run all feasible unit/lint/build checks in GitHub Actions. If graphical/browser validation must run in Antigravity, specify exact commands and mark it unverified until the user confirms results.
7. Update [phase tracker](PHASE_TRACKER.md) only after the acceptance gate, and add evidence/limitations/next-phase handoff.

## Phase 1 acceptance

- `apps/api` starts from an explicit `.env` template and can serve a safe no-model health response in dev.
- `apps/web` TypeScript production build is reproducible; visual app screens are not required yet.
- Typed boundaries match documented architecture; Python and TS lint/type/unit tests pass.
- Credentials and private face/model assets never enter Git; `.gitignore` and secret scans are checked.
- A clean clone can follow `README` developer setup instructions, with checkable CI run links and commit SHA.
- No actual inference or medical claims without the future Phase 9/10/11 gates.

## Ready-to-paste next-chat prompt

> Start **DermaLens AI Phase 1: Repository Engineering Foundation** in https://github.com/shanmukhdatta/DermaLens-AI. You are lead full-stack/CV/MLOps engineer. First inspect merged Phase 0 changes and read docs/01_SYSTEM_ARCHITECTURE.md, docs/PHASE_TRACKER.md, docs/REPO_STRUCTURE.md, docs/08_API_AND_DATA_FLOW.md, docs/03_MODEL_AND_RESEARCH.md, all ADRs, OpenAPI and manifest schema. Implement only Phase 1 on a new GitHub branch: Python/FastAPI workspace skeleton, Next.js TypeScript skeleton, modular in-process service packages, typed configuration, lint/typecheck/test setup, reproducible dependencies, run scripts and GitHub Actions CI. Write real code, tests and docs, run all feasible checks, fix failures, and open a PR. Do not modify the original research repo, claim clinical validity, fake model results, or proceed to Phase 2. Model-dependent functions must explicitly fail not-ready until a verified private checkpoint arrives in Phase 9. End with exact changed paths, commits, CI evidence, unrun tests, user actions and Phase 2 handoff.
