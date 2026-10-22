# DermaLens AI — final feature audit (implementation pass 2026-10-22)

This is a **source and integration evidence audit, not a production release certificate**. Based on the README, merged engineering modules, and documented handoff: 142 requirement rows are tracked in `docs/IMPLEMENTATION_CHECKLIST.md`. 13 were identified as coded capabilities in the PR #27 snapshot, and 129 were partial or awaiting external acceptance; this is NOT a refreshed post-PR #29/31 count. **No new run, deployment or medical benchmark is implied by the checklist.**

| Area | Findings | Release state |
|---|---|---|
| Frontend | Next.js pages and APIs for quality checks, docs lookup, aggregate research visualization; orange/white accessible design work in this branch | Research UX plus coded OIDC sign-in and metadata-only history; real provider browser sign-in unverified; no medical results |
| FastAPI | Typed routes, CORS, auth boundaries, request budget, readiness and upload-quality endpoint | Source present; no public `POST /api/v1/analyses` |
| Persistence | SQLAlchemy models, Alembic revisions, owner-scoped history/feedback, offline TTL pruning CLI with dry-run | Code present; real DB/OIDC deployment not independently confirmed |
| Computer vision | Image guards, manifest integrity, Keras adapter, offline quality & research helpers | **No actual trusted classifier checkpoint connected** |
| RAG | Documentation retrieval, citations, optional protected Grok client | Public lexical retrieval; not persistent semantic RAG |
| Model research | Offline evaluation, calibration and controlled candidate review | No verified held-out patient benchmark or model promotion |
| Ops | Docker Compose, GitHub workflows, operational scripts | CI gates exist; real cloud staging and penetration review pending |

## Unimplemented / blocked critical acceptance

- Real patient-safe analysis creation, results, uncertainty and explainability with verified model/provenance.
- Real-provider verification of the newly implemented OIDC BFF and owner-scoped history UX (PR #29), plus clinical analysis feedback workflow and browser E2E.
- Durable encrypted image storage and fully proven retention/erasure (disabled by default).
- Approved real-world population evaluation, calibration, OOD testing and clinical/regulatory sign-off.
- Real provider-key RAG verification, persistent vector store and production observability.

## What counts as verified

**Implemented and tested:** a specific command actually passed against the reported SHA; **implemented, untested:** code exists without executed evidence in this pass; **partial:** functionality or required workflow missing; **blocked:** external artifact, service, evidence or authority required; **missing:** no code. Do not replace these definitions with marketing claims.

The updated palette is a visual change and does not alter medical capabilities or the platform's fail-closed model readiness. See `docs/FINAL_ENGINEERING_HANDOFF.md` for local verification commands and `docs/README_FEATURE_AUDIT.md` for the prior exhaustive 2026-10-14 architecture-to-source review.

## Subsequent engineering progress (not clinical clearance)

- **PR #29 (merged):** Authorization Code + PKCE browser BFF, short-lived encrypted HttpOnly sessions, allowlisted account proxy, owner-scoped history/consent/export/deletion frontend. GitHub code checks passed; independent live-provider login/security review pending. See `docs/OIDC_BROWSER_INTEGRATION.md`.
- **PR #31 (current implementation branch):** Private offline batch inference using a supplied integrity-verified Keras checkpoint and label map, HMAC-pseudonymized subject/example metadata, leakage-audited CSV and nonclinical evaluation JSON. Fixture-only CI tests do not establish clinical accuracy. See `docs/PRIVATE_MODEL_BENCHMARK.md`.
- The 142-row requirements matrix deliberately continues to treat clinical/end-to-end requirements as partial until real external evidence is available. Never treat added source files as proof of clinical readiness.
