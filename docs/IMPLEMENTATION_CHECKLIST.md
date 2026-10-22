# DermaLens AI — Implementation checklist and traceability

**Scope:** Existing root README §§1–57 and `docs/README_FEATURE_AUDIT.md`, reviewed 2026-10-22. This is an explicit engineering inventory of 141 implementation and acceptance requirements. It does **not** assert that all requirements are complete.

**Source hierarchy:** README + ADRs → applicable phase documents → current code → acceptance evidence. Older README conceptual phase numbering differs from docs/PHASE_TRACKER.md; the latter governs engineering sequencing.

**Status:** I = code exists (current checkout not retested); P = partial/code or independent acceptance missing. External model and patient evaluation are not fabricated. A passing synthetic unit test never establishes clinical readiness.

| ID | Source | Requirement | State | Source files | Verification / external gate |
|---|---|---|---|---|---|
| REQ-001 | README §§3–7 | Separate research and production repositories | I | `README.md; docs/01_SYSTEM_ARCHITECTURE.md` | `docs/adr; scripts/validate_phase0.py` |
| REQ-002 | README §§3–7 | Six-class category contract | I | `README.md; docs/01_SYSTEM_ARCHITECTURE.md` | `docs/adr; scripts/validate_phase0.py` |
| REQ-003 | README §§3–7 | Document product boundaries and non-goals | I | `README.md; docs/01_SYSTEM_ARCHITECTURE.md` | `docs/adr; scripts/validate_phase0.py` |
| REQ-004 | README §§3–7 | Document combined request flow | I | `README.md; docs/01_SYSTEM_ARCHITECTURE.md` | `docs/adr; scripts/validate_phase0.py` |
| REQ-005 | README §§3–7 | Preserve research preprocessing contract | I | `README.md; docs/01_SYSTEM_ARCHITECTURE.md` | `docs/adr; scripts/validate_phase0.py` |
| REQ-006 | README §§3–7 | Document research augmentation provenance | I | `README.md; docs/01_SYSTEM_ARCHITECTURE.md` | `docs/adr; scripts/validate_phase0.py` |
| REQ-007 | README §8.1 | Restrict accepted image formats | I | `services/cv/quality.py; apps/api/dermalens_api/routers/images.py` | `tests/test_phase4_image_quality.py` |
| REQ-008 | README §8.1 | Enforce bounded payload bytes | I | `services/cv/quality.py; apps/api/dermalens_api/routers/images.py` | `tests/test_phase4_image_quality.py` |
| REQ-009 | README §8.1 | Reject invalid image decoding | I | `services/cv/quality.py; apps/api/dermalens_api/routers/images.py` | `tests/test_phase4_image_quality.py` |
| REQ-010 | README §8.1 | Enforce acceptable image dimensions | I | `services/cv/quality.py; apps/api/dermalens_api/routers/images.py` | `tests/test_phase4_image_quality.py` |
| REQ-011 | README §8.1 | Handle multiple animation frames | I | `services/cv/quality.py; apps/api/dermalens_api/routers/images.py` | `tests/test_phase4_image_quality.py` |
| REQ-012 | README §8.1 | Normalize photo orientation and image metadata | I | `services/cv/quality.py; apps/api/dermalens_api/routers/images.py` | `tests/test_phase4_image_quality.py` |
| REQ-013 | README §§8.2–8.5 | Measure brightness as engineering warning | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-014 | README §§8.2–8.5 | Measure blur as engineering warning | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-015 | README §§8.2–8.5 | Detect missing faces | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-016 | README §§8.2–8.5 | Reject multiple faces | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-017 | README §§8.2–8.5 | Check minimum face region size | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-018 | README §§8.2–8.5 | Experiment with eye pose alignment | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-019 | README §§8.2–8.5 | Experiment with facial ROI crop | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-020 | README §§8.2–8.5 | Validate ROI across real demographic groups | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-021 | README §§8.2–8.5 | Validate alignment parity against trained model | P | `services/cv/quality.py; services/cv/face_geometry.py` | `tests/test_phase4_image_quality.py; tests/test_offline_research_pipeline.py` |
| REQ-022 | README §§8.6–8.7, 12 | Convert RGB to documented 224x224 inputs | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-023 | README §§8.6–8.7, 12 | Preserve bilinear preprocessing parity | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-024 | README §§8.6–8.7, 12 | Validate checkpoint checksum | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-025 | README §§8.6–8.7, 12 | Validate label-map checksum | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-026 | README §§8.6–8.7, 12 | Validate six-class label ordering | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-027 | README §§8.6–8.7, 12 | Load serialized Keras custom objects | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-028 | README §§8.6–8.7, 12 | Validate model tensor input and output | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-029 | README §§8.6–8.7, 12 | Reject malformed probability vector | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-030 | README §§8.6–8.7, 12 | Obtain real verified .keras checkpoint | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-031 | README §§8.6–8.7, 12 | Verify original predictor parity with approved fixtures | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-032 | README §§8.6–8.7, 12 | Release validated user-facing inference | P | `services/cv/artifacts.py; services/cv/keras_runtime.py; services/cv/offline_pipeline.py` | `tests/test_phase9_artifacts.py; tests/test_offline_research_pipeline.py` |
| REQ-033 | README §§9–11 | Implement offline probability calibration | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-034 | README §§9–11 | Implement offline uncertainty decision gate | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-035 | README §§9–11 | Require independent calibration split | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-036 | README §§9–11 | Validate OOD on real unfamiliar conditions | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-037 | README §§9–11 | Evaluate synthetic-to-real domain shift | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-038 | README §§9–11 | Implement research Grad-CAM | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-039 | README §§9–11 | Validate explanation stability and clinical interpretability | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-040 | README §§9–11 | Create approved and access-controlled user explanation artifact | P | `services/learning/calibration.py; services/cv/gradcam.py` | `tests/test_phase10_evaluation.py; tests/test_offline_research_pipeline.py` |
| REQ-041 | README §§13–14, 29–30 | Maintain model-manifest format | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-042 | README §§13–14, 29–30 | Enforce model file integrity | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-043 | README §§13–14, 29–30 | Preserve version and preprocessing metadata | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-044 | README §§13–14, 29–30 | Support offline benchmark pipeline | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-045 | README §§13–14, 29–30 | Compare candidate and baseline checkpoints | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-046 | README §§13–14, 29–30 | Require locked test set and provenance | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-047 | README §§13–14, 29–30 | Implement secure model registry and promotions | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-048 | README §§13–14, 29–30 | Implement approval and rollback workflow | P | `models/manifests/model-manifest.schema.json; scripts/verify_model_package.py; scripts/review_candidate_with_policy.py` | `tests/test_phase13b_review_policy.py; tests/test_phase9_artifacts.py` |
| REQ-049 | README §§15–18 | Compose FastAPI application | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-050 | README §§15–18 | Validate API requests | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-051 | README §§15–18 | Reject unauthenticated protected requests | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-052 | README §§15–18 | Enforce owner-scoped access | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-053 | README §§15–18 | Expose liveness | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-054 | README §§15–18 | Expose fail-closed readiness | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-055 | README §§15–18 | Expose model status | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-056 | README §§15–18 | Implement public POST analyses | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-057 | README §§15–18 | Implement analysis GET by identifier | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-058 | README §§15–18 | Implement paginated analysis list | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-059 | README §§15–18 | Return verified structured analysis result | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-060 | README §§15–18 | Handle API exception mapping and request IDs | P | `apps/api/dermalens_api; packages/contracts/openapi.v1.json` | `tests/test_phase2_backend.py; tests/test_api_foundation.py` |
| REQ-061 | README §§19–21 | Create SQLAlchemy account model | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-062 | README §§19–21 | Create consent model | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-063 | README §§19–21 | Create analysis metadata model | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-064 | README §§19–21 | Create feedback model | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-065 | README §§19–21 | Maintain PostgreSQL migrations | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-066 | README §§19–21 | Require verified OIDC actor | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-067 | README §§19–21 | Support opt-in history consent | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-068 | README §§19–21 | Return owner-scoped history | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-069 | README §§19–21 | Delete consent-revoked history metadata | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-070 | README §§19–21 | Allow account export | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-071 | README §§19–21 | Allow account erasure | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-072 | README §§19–21 | Implement encrypted object storage with short-lived access | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-073 | README §§19–21 | Enforce raw-photo retention and deletion jobs | P | `services/persistence; infra/database/migrations; apps/api/dermalens_api/routers/account.py` | `tests/test_phase3_persistence.py` |
| REQ-074 | README §§22–25 | Accept moderated user feedback | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-075 | README §§22–25 | Prevent duplicate/conflicting feedback | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-076 | README §§22–25 | Ensure feedback belongs to actor | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-077 | README §§22–25 | Expose feedback deletion | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-078 | README §§22–25 | Use consent/rights-gated offline curation | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-079 | README §§22–25 | Require independently validated research labels | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-080 | README §§22–25 | Exclude raw user clicks from automatic model promotion | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-081 | README §§22–25 | Support explicit researcher review | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-082 | README §§22–25 | Connect real results to verified history and feedback user interface | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-083 | README §§22–25 | Train optional reranker only after evaluation | P | `services/learning/feedback.py; services/learning/curation.py; services/learning/review_policy.py` | `tests/test_phase6_feedback.py; tests/test_phase13_improvement.py` |
| REQ-084 | README §§26–28 | Search curated project documentation | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-085 | README §§26–28 | Produce citations and section references | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-086 | README §§26–28 | Fail closed on undocumented question | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-087 | README §§26–28 | Restrict medical advice | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-088 | README §§26–28 | Implement optional protected Grok adapter | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-089 | README §§26–28 | Verify real Grok provider integration | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-090 | README §§26–28 | Implement embedding-based retrieval | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-091 | README §§26–28 | Implement persistent vector index or pgvector | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-092 | README §§26–28 | Incrementally rebuild changed documents | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-093 | README §§26–28 | Ensure indexed sources match versioned documentation | P | `services/rag/index.py; services/rag/grok.py; apps/api/dermalens_api/routers/docs_search.py` | `tests/test_phase7_rag.py; tests/test_integration_docs_search.py` |
| REQ-094 | README §§31–36 | Emit bounded structured request telemetry | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-095 | README §§31–36 | Enforce CORS policy | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-096 | README §§31–36 | Enforce HTTP security headers | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-097 | README §§31–36 | Validate OIDC JWKS signatures | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-098 | README §§31–36 | Apply bounded per-process rate limits | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-099 | README §§31–36 | Create privacy-preserving aggregate drift calculations | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-100 | README §§31–36 | Implement distributed production abuse throttling | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-101 | README §§31–36 | Implement durable metrics and tracing | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-102 | README §§31–36 | Create alert policy and operational dashboard | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-103 | README §§31–36 | Undertake privacy/threat and penetration reviews | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-104 | README §§31–36 | Validate clinical safety of output copy | P | `packages/telemetry; packages/security; services/learning/drift.py` | `tests/test_phase12_telemetry.py; tests/test_api_rate_limits.py` |
| REQ-105 | README §§37–40 | Create homepage | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-106 | README §§37–40 | Create image-check screen | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-107 | README §§37–40 | Create technical explainer screen | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-108 | README §§37–40 | Create privacy page | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-109 | README §§37–40 | Create docs explorer | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-110 | README §§37–40 | Create local research evaluation viewer | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-111 | README §§37–40 | Add responsive layout and keyboard navigation | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-112 | README §§37–40 | Use warm orange-and-white visual design | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-113 | README §§37–40 | Handle upload loading/error/success | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-114 | README §§37–40 | Handle API connection errors | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-115 | README §§37–40 | Implement verified sign-in user interface | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-116 | README §§37–40 | Implement user history screen | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-117 | README §§37–40 | Implement medically reviewed analysis result screen | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-118 | README §§37–40 | Implement explanation overlay and uncertainty UI | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-119 | README §§37–40 | Integrate moderated feedback UI | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-120 | README §§37–40 | Conduct end-to-end browser accessibility testing | P | `apps/web/src/app; apps/web/src/lib; apps/web/src/components` | `apps/web/src/lib/*.test.ts; manual browser testing` |
| REQ-121 | README §§41–44, 47–49 | Provide modular Python and Next.js repository | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-122 | README §§41–44, 47–49 | Pin frontend dependencies | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-123 | README §§41–44, 47–49 | Define Python dependency lock | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-124 | README §§41–44, 47–49 | Provide Docker build recipes | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-125 | README §§41–44, 47–49 | Provide local PostgreSQL Compose | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-126 | README §§41–44, 47–49 | Supply example environment variables | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-127 | README §§41–44, 47–49 | Provide CI lint/type/build/tests | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-128 | README §§41–44, 47–49 | Provide contract and schema tests | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-129 | README §§41–44, 47–49 | Provide runtime smoke script | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-130 | README §§41–44, 47–49 | Verify real staging TLS and deployment | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-131 | README §§41–44, 47–49 | Verify secrets rotation and backups | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-132 | README §§41–44, 47–49 | Document production rollback and monitoring | P | `.github/workflows; infra/docker; compose.yaml; tests` | `tests/test_repository_hygiene.py; scripts/operational_smoke.py` |
| REQ-133 | README §§45–46, 50–57 | Implement offline aggregate evaluation | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-134 | README §§45–46, 50–57 | Enforce split-aware subject grouping | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-135 | README §§45–46, 50–57 | Review dataset rights and clinical labels | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-136 | README §§45–46, 50–57 | Report per-class metrics and calibration | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-137 | README §§45–46, 50–57 | Benchmark against diverse real capture conditions | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-138 | README §§45–46, 50–57 | Preserve final acceptance definition | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-139 | README §§45–46, 50–57 | Keep documentation synchronized with code | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-140 | README §§45–46, 50–57 | Run full local and CI integration acceptance | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |
| REQ-141 | README §§45–46, 50–57 | Complete independent production safety review | P | `scripts/evaluate_predictions.py; scripts/export_verified_predictions.py; docs/README_FEATURE_AUDIT.md` | `tests/test_phase10_verified_export.py; docs/FINAL_ENGINEERING_HANDOFF.md` |

## Checklist summary

- 141 traceable lines; I=12, P=129. **No I entry is automatically promoted to "verified" solely by writing this matrix.**
- Most urgent release gaps: checkpoint + exact label map, real-world benchmarking, validated abstention, secure analyses API, authenticated UI, medical privacy review.
- Real data, external credentials, security approval and deployment execution require independent evidence.

## Update protocol

1. Revisit individual IDs when code/contract changes, record the exact file and test.
2. Change status to verified only with executed test name, commit SHA and environment evidence.
3. Do not infer medical efficacy, measured accuracy or model availability from CI.
4. Leave analysis creation disabled until the documented clinical-safety gates are independently accepted.
