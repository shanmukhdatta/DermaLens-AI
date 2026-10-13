# Contract ownership

Phase 0 `openapi.v1.json` and the model manifest schema remain the authoritative contracts.
In Phase 1 only `GET /api/v1/health` (200) and `GET /api/v1/readiness` (503) are served.
Other endpoints are **not implemented**, including `/analyses`, user accounts, feedback,
model status and `/copilot/query`. Tests verify this explicitly.

An HTTP 404 for an unimplemented API route is not a prediction or a mock response.
`UnavailableModelRuntime` always raises the typed `MODEL_NOT_READY` exception.
Phase 2 will implement coherent typed error responses and request correlation across the API.
