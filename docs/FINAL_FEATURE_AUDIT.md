# DermaLens AI — final feature audit (implementation pass 2026-10-22)

This is a **source and integration evidence audit, not a production release certificate**. Based on the README, merged engineering modules, and documented handoff: 144 requirement rows are tracked in `docs/IMPLEMENTATION_CHECKLIST.md`. The 15-coded/129-partial numbers are an earlier frozen checklist snapshot and have not been recalculated after subsequent implementation PRs. They must not be presented as updated test coverage. **No new run, deployment or medical benchmark is implied by the checklist.**

| Area | Findings | Release state |
|---|---|---|
| Frontend | Next.js pages and APIs for quality checks, docs lookup, aggregate research visualization; orange/white accessible design work in this branch | Coded protected OIDC BFF, owner history and research feedback; live provider E2E remains unverified; no clinical results |
| FastAPI | Typed routes, CORS, auth boundaries, request budget, readiness and upload-quality endpoint | OIDC-protected experimental POST/GET/DELETE now implemented but disabled in production; no public diagnostic API |
| Persistence | SQLAlchemy models, Alembic revisions, owner-scoped history/feedback, offline TTL pruning CLI with dry-run | Encrypted research result migration and consent/ownership checks coded; real OIDC deployment remains external |
| Computer vision | Image guards, manifest integrity, Keras adapter, offline quality & research helpers | **No actual trusted classifier checkpoint connected** |
| RAG | Documentation retrieval, citations, optional protected Grok client | Public lexical retrieval; not persistent semantic RAG |
| Model research | Offline evaluation, calibration and controlled candidate review | New leakage-audit CLI added; still no verified held-out patient benchmark or model promotion |
| Ops | Docker Compose, GitHub workflows, operational scripts | CI gates exist; real cloud staging and penetration review pending |

## Unimplemented / blocked critical acceptance

- Real patient-safe analysis creation, results, uncertainty and explainability with verified model/provenance.
- Live OIDC-provider login and real-browser E2E, independent security review, and clinically authorized diagnostic results; research-only history/feedback UI are coded.
- Durable encrypted image storage and fully proven retention/erasure (disabled by default).
- Approved real-world population evaluation, calibration, OOD testing and clinical/regulatory sign-off.
- Real provider-key RAG verification, persistent vector store and production observability.

## What counts as verified

**Implemented and tested:** a specific command actually passed against the reported SHA; **implemented, untested:** code exists without executed evidence in this pass; **partial:** functionality or required workflow missing; **blocked:** external artifact, service, evidence or authority required; **missing:** no code. Do not replace these definitions with marketing claims.

The updated palette is a visual change and does not alter medical capabilities or the platform's fail-closed model readiness. See `docs/FINAL_ENGINEERING_HANDOFF.md` for local verification commands and `docs/README_FEATURE_AUDIT.md` for the prior exhaustive 2026-10-14 architecture-to-source review.

## New implementation branch — PR #28

The research-only API, encrypted research result metadata, independent split-leakage audit, and associated tests are additional source-level functionality. They do **not** claim clinical readiness. The old summary of nonclinical frontend functionality remains unchanged. Require passing CI on final SHA, OIDC provider integration, private checkpoint parity, representative licensed real-image assessment, security review, and safe browser experience before any product release.

## Later implementation details

- PR #33 merged: guarded user feedback interface and encrypted result-to-row identity binding. CI suites passed, but real provider/browser testing is still unverified.
- Candidate model packaging and original-versus-serving predictor parity scripts added on the subsequent model integration branch. No checkpoint weights or patient images are committed. See docs/MODEL_ARTIFACT_PARITY_RUNBOOK.md.
- Model package files, actual original inference parity, independently labelled real-world population evidence, professional medical review and production security acceptance remain external gates. The application is NOT a clinical diagnostic product.
