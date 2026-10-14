# DermaLens AI — README feature implementation and release audit

Audited 2026-10-14 against root README sections 1–57, current source and merged implementation PRs.

**Definitions:** Implemented = committed and covered by automated checks for this specific component, not clinical readiness. Partial = useful code but incomplete end-to-end operation. Blocked = awaiting real model, independent data, credentials, or approvals. Optional = excluded from v1.

| README scope | Code/evidence | Verified outcome |
|---|---|---|
| Architecture, contracts and ADRs (1–7, 41–43, 53–57) | README, docs/01–09 and docs/adr | Implemented architecture docs; separate execution roadmap |
| File-format/size/dimension/frame and basic quality gates (8.1–8.2) | services/cv/quality.py and POST /api/v1/images/check | Implemented bounded decoding and engineering heuristics; blur/brightness are warnings, not calibrated medical quality |
| Face detector (8.3) | HaarFaceDetector | Implemented basic single-face checks, not validated on diverse real photos |
| Eye/pose alignment and skin ROI (8.4–8.5) | services/cv/face_geometry.py, tests/test_offline_research_pipeline.py | Research eye geometry/crop algorithms coded and tested with fixtures; NOT approved for inference or validated against the research model |
| Preprocessing, Keras adapter and manifest (4, 8.6–8.7, 12) | services/cv/artifacts.py, keras_runtime.py, offline_pipeline.py, verify_model_package.py | Offline guarded image-to-runtime pipeline now implemented (PR #22); real checkpoint loading, preprocessing parity and approved serving still blocked |
| Structured analysis API, results and versions (7, 15–18, 38, 51) | contracts/openapi.v1.json | NOT IMPLEMENTED; POST /api/v1/analyses intentionally returns 404 until safe validated model path exists |
| Calibration, OOD, abstention (9–10, 32) | services/learning/calibration.py | Offline research helpers; real OOD, calibrated release policy and integration blocked |
| XAI / Grad-CAM (11, 46) | services/cv/gradcam.py | Research helper only; no approved overlay artifact or real-model performance test |
| Research evaluation and integrity (10, 13–14, 45) | scripts/evaluate_predictions.py, scripts/export_verified_predictions.py | Testable offline evaluator, real measurements/ground-truth validation blocked |
| FastAPI, security identity and errors (15, 33–35) | apps/api, packages/security | Tested OIDC verifier and bounded anonymous request budgets (PR #23); live OIDC, distributed ingress rate limits, security review still pending |
| Database, privacy and history (19–21) | services/persistence, Alembic, accounts APIs | Backend implementation with tests; UI sign-in/history unavailable until real identity provider configured; image storage disabled |
| Feedback and offline learning (22–25, 39) | services/learning | Owner-scoped feedback and offline curation/regression gate; actual user loop needs analyzed cases, confirmed consent and credentials |
| Documentation RAG (26–28, 40) | services/rag/index.py, grok.py, public docs/search and web assistant | Protected Grok adapter + operational public lexical citations; semantic vector embedding/pgvector and real provider testing pending |
| Frontend experience (37, 51) | apps/web/src/app | Quality screen, documentation explorer and browser-local aggregate research viewer (PR #25); medical results/XAI/history/live feedback awaiting model and login |
| Model registry and controlled promotion (12, 14, 23, 29–30) | model manifest, scripts/review_candidate*.py | Manifest and offline human-review gates; no live registry/release authorization |
| Telemetry, traces, drift (31–32) | middleware, packages/telemetry/runtime.py, services/learning/drift.py | In-memory operational metrics and offline aggregate JS-distance drift investigator (PR #24); no durable production monitoring, distributed tracing or real live-drift alerts |
| CI, Docker, staging (35, 44, 47–49) | GitHub Actions, Dockerfiles, compose.yaml | CI and disposable Compose smoke implemented; real cloud staging/browser E2E, TLS, scanning and rollback pending |
| Secondary reranker/RL (24–25) | Proposal only | Optional research extensions, excluded from v1 |

## Product acceptance status

The complete README section 51 is **NOT satisfied**. A user cannot yet upload a photo and receive a verified, reliable model result with uncertainty, explainability, saved metadata and integrated feedback. Quality acceptance alone is never a medical finding. Neither synthetic unit tests nor deployment smoke authorizes clinical use.

Next: obtain selected private trained .keras checkpoint, exact label_map.json, manifest and approved real evaluation fixtures; reproduce original research inference and evaluate model/ROI alignment compatibility, implement guarded analysis orchestration and real operating policy. Then verify authentication, privacy, browser UX, chatbot provider and private staging. Keep readiness 503 and analysis 404 until the protected inference path has passed independent review. See docs/FINAL_ENGINEERING_HANDOFF.md for test instructions and source of truth; code merged does not mean user acceptance.
