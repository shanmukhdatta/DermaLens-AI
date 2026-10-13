# Phase 2 handoff — FastAPI backend skeleton

Phase 2 must **not** begin automatically. Only start after Phase 1 CI, local review and merge.

## Exact next-chat prompt

> Implement **DermaLens AI Phase 2 — FastAPI Backend Skeleton** in https://github.com/shanmukhdatta/DermaLens-AI. First audit merged Phase 1 and read README.md, docs/PHASE_TRACKER.md, docs/01_SYSTEM_ARCHITECTURE.md, docs/04_BACKEND_ARCHITECTURE.md, docs/08_API_AND_DATA_FLOW.md, docs/09_PRIVACY_AND_SAFETY.md, all ADRs, and the machine-readable OpenAPI/manifest contracts. Create a new Phase 2 branch. Implement only Phase 2: a robust FastAPI application composition root, dependency injection, structured request IDs and typed error middleware, liveness/readiness with optional-resource checks that fail closed, an auth boundary with correctly isolated public/private route dependencies (no fabricated authentication), strict CORS/security-header policy, versioned router skeleton and contract-based tests. Do not build persistence, user accounts, CV image handling or trained inference, RAG provider calls, feedback persistence, or deploy publicly; those belong to later phases. Unavailable model stays MODEL_NOT_READY; no fake results. Write complete working code, CI tests and docs, run checks and fix failures, open PR, update phase tracker with evidence, and provide exact changed paths, pass/fail status, blockers and Phase 3 handoff. Do not modify the original research repository or start Phase 3.

## Phase 2 gate

- Safe, testable composition/middleware and dependency overrides.
- Aligned OpenAPI v1 response/error contracts for implemented endpoints (no fictitious extra live features).
- No sensitive request body or secret leaks via errors/logs.
- CI unit/integration tests for liveness/readiness, middleware, permission boundaries, and error codes.
- Model readiness remains false until verified future artifact/policy integration.
