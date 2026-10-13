# Phase 1 validation and acceptance evidence

**GitHub source of truth**: https://github.com/shanmukhdatta/DermaLens-AI/pull/2
**Verified source commit**: `841bd5914a1ac4e828f3f0e93e04a250aed256da` (prior to documentation-only verification update).

## Passing automated evidence

- Phase 1 PR CI: https://github.com/shanmukhdatta/DermaLens-AI/actions/runs/38436661549 — **success**, both jobs.
- Phase 0 regression CI: https://github.com/shanmukhdatta/DermaLens-AI/actions/runs/38436661560 — **success**.
- Backend: `ruff check .`, `ruff format --check apps packages services tests/test_api_foundation.py`, `mypy`, `scripts/validate_phase0.py`, `python -m pytest -q`, repository hygiene — all passed.
- Python pytest: **12 passed, 1 warning** (third-party Starlette TestClient `httpx` deprecation). This is not an application test failure; should be tracked when updating dependencies.
- Frontend: `npm run lint`, `npm test` (2 tests passed), `npm run build` (Next.js compiled and static pages generated), `npm run typecheck` — all passed.
- Python dependency lock: `uv.lock` committed; npm dependency lock: `apps/web/package-lock.json` committed. A scoped bootstrapping workflow produced both and was removed after generation. CI now installs from immutable lockfiles.
- All synthetic/mock classifier outputs remain disabled; no actual checkpoint was provided. Neither repo in Git contains a deployable checkpoint.

## Explicit limitations / unverified items

- No external Windows Antigravity run, live browser accessibility review, live Windows startup or device test. User can run commands in [Phase 1 implementation](PHASE1_IMPLEMENTATION.md).
- No upload, model inference, data persistence, identity/authorization, RAG, feedback, container/deployment, CI deployment, real-images validation or clinical validation.
- Repo hygiene verifies forbidden tracked path classes, not a full professional secret-scanning assessment. Real secret scanning is a later release gate.
- Nonblocking build warnings: Starlette TestClient suggests `httpx2`; GitHub hosted action runtime reports Node.js deprecation for older checkout/setup action versions.
- No file from `shanmukhdatta/Facial_Skin_Diesease` was modified.

## Acceptance

**Engineering baseline verified by CI.** Leave Phase 1 tracker `In review` until PR #2 is merged and local Antigravity startup has been verified. Do not claim deployed or production-ready medical functionality. Phase 2 is not started.
