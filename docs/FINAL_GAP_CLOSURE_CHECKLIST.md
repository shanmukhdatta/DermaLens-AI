# DermaLens AI — Final Gap Closure Checklist (2026-10-22)

**Audit standard:** A "coded" component is not automatically integrated into a deployed user journey, clinically validated, or regulatory-approved. Current work is in PR #28 and must pass CI before merge.

| ID | Required workflow | Newly implemented code | Remaining real verification / blocker | State |
|---|---|---|---|---|
| A | Real compatible checkpoint + model labels | `VerifiedKerasModel`, manifest/checksum validation already present; new configured local-load integration in FastAPI | A real approved six-class checkpoint, label map, provenance, parity fixtures, runtime/device test and independent calibration | **External model needed** |
| B | Independent evaluation and leakage controls | `leakage_audit.py`, CLI, synthetic-fixture tests; prior evaluation/calibration/aggregate visualization | Rights-cleared subject-labeled real facial photos, dedup human review, clinical labels, subgroup statistics | **Source implemented, clinical proof pending** |
| C | Protected image → inference → result workflow | Nonproduction POST/GET/DELETE API, OIDC guard, bounded images, verified local Keras adapter, encrypted SQLAlchemy rows, result TTL | Live external issuer, compatible weights, full browser integration, model validation | **Research backend and BFF research UI written; live integration not verified** |
| D | Secure registration/login, history UI | Existing issuer-JWKS JWT verification, account/consent/export/erasure and history listing; protected analysis result retrieval now added | OIDC BFF login, account and consent history UI have merged via PR #29; real IdP credentials and browser end-to-end testing remain pending; the research-only upload, owner result and deletion UI now exists in PR #32 via the OIDC BFF | **Incomplete** |
| E | Privacy/security production assurances | Fernet-authenticated encrypted metadata, no raw-image persistence, rate limits, no storage by default, TTL sweep and ownership tests | Security review, legal applicability review, incident plan, approved secure cloud storage if added, penetration testing, key rotation drills | **Partial** |
| F | Full documentation-grounded vector RAG | Existing lexical docs index and opt-in Grok adapter | Semantic embedding, persistent vector index, real provider validation | **Partial** |
| G | Model safety and explainability | Offline exploratory calibration/Grad-CAM modules | Real OOD, clinically defensible thresholds, explanation stability and approval | **External evidence needed** |
| H | Production observability and deployment | Compose, CI, in-process bounded telemetry, disposable smoke | Durable metrics, tracing, backups, TLS ingress, deployment rollback and security review | **Partial** |

## What was really run

CI on the PR exercises Ruff, mypy, Python unit/integration tests, Next.js lint/typecheck/build and disposable Compose staging smoke. These checks do not show the application working with a live clinical checkpoint or real OIDC accounts. Record final exact commit, run URLs and statuses in PR review before merging.

## Clinical boundaries

Never expose an automatically interpreted diagnosis or skin-cancer rule-out result without independent medically supervised evaluation. Research-only scores are uncalibrated and presented as such. Do not turn the existing `ResearchCalibration` exploratory candidate into a "clinical" threshold by renaming it. Real clinical validation cannot be invented from test fixtures.

## Supplemental evaluation implementation — PR #33

- Added complete 6×6 actual-vs-predicted confusion matrix and per-class TP, TN, FP, FN, sensitivity and specificity. Undefined denominators appear as null, never guessed zero.
- Extended the offline image split audit with independent DCT-based pHash across all 8 orientations, in addition to existing SHA-256 and gradient-based dHash. Outputs are pseudonymous review candidates only. Pair report is bounded and rejects overwhelming duplicate batches rather than claiming successful validation.
- Acceptance tests in `tests/test_evaluation_confusion.py` and `tests/test_perceptual_duplicate.py`; CI status is attached to the PR and must pass before any merge.
- Real model weights, licensed independent clinical test data, validated OOD/calibration thresholds, live OIDC provider and release assurance remain external blockers; no clinical effectiveness has been measured.
