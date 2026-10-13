# API and communication contracts — v1

Machine-readable spec: [OpenAPI 3.1 JSON](../packages/contracts/openapi.v1.json). This is a design contract; endpoints do **not** exist during Phase 0.

- `POST /api/v1/analyses`: `multipart/form-data`, required `image` and `consent_mode` (`ephemeral` default or `history_metadata`). Server validates type/size, images never sent to Grok. Authorized history only with authenticated owner. `202` is not assumed: synchronous design returns `200` or explicit rejection/error with typed payload.
- `GET /api/v1/analyses[?limit=...]`, `GET /api/v1/analyses/{id}`, `DELETE /api/v1/analyses/{id}`: owner-only history/erasure; ephemeral analyses never persisted for retrieval.
- `POST /api/v1/analyses/{id}/feedback`: owner only, requires persisted analysis; feedback does not change classification weights.
- `POST /api/v1/copilot/query`: curated-doc questions only; response includes verified source references or refusal.
- `GET /api/v1/models/current`, `GET /api/v1/health`, `GET /api/v1/readiness`: safe metadata / liveness / dependency readiness, without secrets.

**CVOutcome** states are `completed`, `abstained`, `rejected` and `failed`. `prediction` is nullable and only populated when policy permits showing an experimental classification; `explainability.available` defaults false. Probability arrays/map are always keyed against the verified *artifact* label order, not assumed class alphabetical order. The response distinguishes `raw_top_probability` from validated calibration.

**Errors:** response contains `error.code`, `error.message`, `request_id`. Codes include `INVALID_IMAGE`, `UNSUPPORTED_IMAGE_TYPE`, `IMAGE_TOO_LARGE`, `IMAGE_QUALITY_TOO_LOW`, `NO_FACE_DETECTED`, `MULTIPLE_FACES_DETECTED`, `MODEL_NOT_READY`, `POLICY_NOT_VALIDATED`, `INFERENCE_FAILED`, `OUT_OF_DISTRIBUTION`, `RAG_UNAVAILABLE`, `NOT_AUTHORIZED`, `NOT_FOUND`, `RATE_LIMITED`, `INTERNAL_ERROR`. Failures are never converted into optimistic results.

The API must always show research-only and non-diagnostic limitations, plus an appropriate professional-evaluation message on uncertainty. Any user data export endpoint must be designed and documented before public deployment.
