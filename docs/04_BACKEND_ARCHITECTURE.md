# Backend and persistence boundaries (planned)

Tech: Python FastAPI + Pydantic v2 + SQLAlchemy 2/Alembic + PostgreSQL. A modular monolith exposes `/api/v1`. Scope-specific services use repositories rather than raw shared ORM objects; transactions are bounded by request/use-case. Sensitive uploads stay inside transient request memory and are cleaned up on every exit path.

Modules: `apps/api` (router, middleware, typed errors, auth, DI), `services/cv` (quality/face/ROI/adapter/decision/XAI), `services/rag` (approved-doc retrieval), `services/learning` (moderated feedback and offline candidates), `packages/contracts` (versioned public schemas), `packages/security` (auth/policies), `infra/database` (migrations). No internal network service needed initially.

**Identity & access:** external OIDC with server-side identity verification; no self-asserted user IDs. Every analysis, history row, artifact, feedback and deletion is scoped to authenticated subject; no cross-tenant joins/access. Auth required for persistent history/feedback; unauthenticated sessions may be allowed for ephemeral analysis behind stricter quotas only if deployed safely. Signed URLs must be short-lived and owner-authorized.

**Transactions/data model draft:** `users(id, provider_subject, created_at, deleted_at)`, `analyses(id, owner_id, created_at, status, reason_code, model_id, model_version, manifest_hash, label_map_hash, preprocessing_version, pipeline_version, probability_json, quality_json, consent_mode)`, `feedback(id, analysis_id, owner_id, rating, proposed_label, review_state, created_at)`, `artifacts(id, analysis_id, storage_key, purpose, retention_deadline)`, `audit_events(id, actor_id, action, target_id, timestamp)`, `rag_documents(id, digest, origin, version)`. Exact normalized schema/migrations are Phase 3; always protect delete cascades and access paths.

**Reliability:** idempotent create semantics using `Idempotency-Key` scoped per actor and endpoint, request correlation ID, request/response timeouts, bounded uploads/concurrency, stable error codes and structured error contract. Dependencies such as missing model cause explicit 503, not dummy inference. No fallback to diagnosis from documentation chatbot. Transactional metadata does not imply image retention. Redact content and filesystem paths from logs and traces.

See [versioned API contract](../packages/contracts/openapi.v1.json) and [privacy](09_PRIVACY_AND_SAFETY.md).
