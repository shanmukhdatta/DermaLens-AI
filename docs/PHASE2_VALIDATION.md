# Phase 2 validation and acceptance evidence

**PR:** https://github.com/shanmukhdatta/DermaLens-AI/pull/3
**Verified application implementation SHA:** `a50bb010cd735103663824842060086edf6b971e`.
**Scope:** FastAPI backend skeleton only, not production diagnosis.

## Passing GitHub Actions evidence

- [Phase 0 architecture contracts — run 38441498054](https://github.com/shanmukhdatta/DermaLens-AI/actions/runs/38441498054): **success**. Python lint, Phase 0 schema/doc validation and contract tests passed.
- [Phase 1 backend/frontend checks — run 38441497916](https://github.com/shanmukhdatta/DermaLens-AI/actions/runs/38441497916): **success**, both Backend / contracts and Web build / typecheck / tests jobs.
- Backend: `ruff check .`, `ruff format --check`, `mypy` (27 checked source files), Phase 0 contract/schema validator, repository hygiene, `pytest -q`: **47 passed, 1 third-party warning** (Starlette TestClient `httpx` deprecation). No active test failures on the verified SHA.
- Frontend: locked npm install, ESLint, Vitest, Next.js production build, TypeScript checks — all passed; existing frontend shell remains unchanged.
- On `main`: after PR #2 merge, commit `12379168b3188025e6abc3ca22083cf29db7e0aa` enabled `phase1.yml` pushes to `main`. Both [Phase 1 run 38440384031](https://github.com/shanmukhdatta/DermaLens-AI/actions/runs/38440384031) and [Phase 0 run 38440384034](https://github.com/shanmukhdatta/DermaLens-AI/actions/runs/38440384034) succeeded at the tracker-corrected `main` SHA.

## Debug history

- Initial PR run failed Ruff import sorting, `collections.abc` typing and two long dict lines; corrected in `36ce34ead4790473e757dbbda0fc893bea0ad0a0`.
- Next run failed Ruff formatting of one test line; corrected in `34b6933d9bec9ada269fd265c2b0693eaf8f6897`.
- Next run passed lint/type but failed 6 pytest cases for generic unmatched-route 404 bodies: the handler was registered against FastAPI's subclass rather than Starlette's HTTPException base. Corrected in `a50bb010cd735103663824842060086edf6b971e`; **47 tests green**.

## Acceptance gates

| Gate | Result |
|---|---|
| PR #2 merged and reviewed main state | Verified |
| Phase 1 complete CI on `main` | Enabled and verified with successful main push runs |
| FastAPI routing, independently testable composition and dependency overrides | Passed |
| Liveness contract `200 ok`, default readiness `503 not_ready` | Passed |
| Fail-closed identity, owner guard and protected model metadata | Passed |
| Canonical request IDs, fixed redacted error envelope and 404/405/422/500 | Passed |
| Strict origin validation, preflight, security headers and no credentialed CORS | Passed |
| Phase 0 OpenAPI contract and manifest preserved | Passed validation |
| Secret/private-artifact tracked-path hygiene | Passed (not a full external security audit) |
| Windows PowerShell/Antigravity local server smoke and browser review | **Not executed here** |
| Real OIDC provider, DB isolation, image processing, trained inference, clinical review | **Not implemented — future phases** |
| Human PR #3 review and merge | **Pending** |

## Known limits

- Contract file `packages/contracts/openapi.v1.json` still specifies the *future full product*; unavailable business endpoints are not exposed. `/api/v1/models/current` requires verified authentication and defaults to 401 because no real token-verifying OIDC adapter has shipped. With a **test-only** trusted verifier override, it returns `{"ready":false,"model_id":null,"model_version":null}`.
- API OpenAPI public generation is disabled pending full contract alignment/auth review. No rate limiter or production deployment is claimed. No health data or images were supplied in automated tests.
- The older test-run failures listed above were corrected; do not equate these with failures on the final verified application SHA.
- The original research repo `shanmukhdatta/Facial_Skin_Diesease` was never written to. Phase 3 must start only after Phase 2 review/merge.
