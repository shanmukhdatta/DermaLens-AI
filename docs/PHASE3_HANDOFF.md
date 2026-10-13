# Phase 3 handoff — persistence and accounts (DO NOT start automatically)

Phase 2 closes only after CI and PR review/merge. Begin from merged `main`; reconcile tracker status and audit regression tests before new code. Preserve Phase 0 contract/ADRs, Phase 1 reproducible workspace and Phase 2 security middleware/headers.

## Phase 3 deliverables

1. PostgreSQL, SQLAlchemy 2 and Alembic with reproducible migrations; explicit relational ownership, foreign keys, deletion and retention metadata for future analyses/feedback. No raw face storage by default.
2. Real OIDC identity adapter (issuer/audience/signature/JWKS/expiry validation); no unsigned/self-declared subjects, never derive an owner from a caller-provided request field. Use least-privilege DB roles and secret-injected settings.
3. Owner-scoped persistence repositories and transactions; prevent IDOR, cross-user enumeration, unauthorized deletion and mismatched consent. No persisted history without verified actor and valid purpose/consent.
4. Concurrency, idempotency and failure tests with a disposable test database; migration up/down tests and authorization tests for own/other/missing records. Keep CI deterministic.
5. Retention policy specification, data export/deletion risk review and explicit blockers for public data collection. Avoid starting image processing, model loading, feedback service, RAG or deployment.
6. Update `docs/PHASE_TRACKER.md` and validation evidence, prepare Phase 4 handoff after reviewing PR. Do not modify `shanmukhdatta/Facial_Skin_Diesease`.

**Current inherited contracts:** public health `200`, default readiness `503`, all tokens denied until real verifier added, private model metadata with no trained artifact. Never manufacture prediction fixtures as real results.
