# DermaLens AI — Actual API surface

Source of truth: `packages/contracts/openapi.v1.json` and route modules in `apps/api/dermalens_api/routers/`. Request/response schemas are enforced by the application and must not be inferred from future README examples.

| Method and route | Current behavior |
|---|---|
| GET `/api/v1/health` | Liveness only; is **not** medical/model readiness |
| GET `/api/v1/readiness` | Returns 503 while trusted model is unavailable |
| GET `/api/v1/models/current` | Protected model status; does not enable classification |
| POST `/api/v1/images/check` | Bounded photo quality check; no medical class/result, no image storage |
| GET `/api/v1/docs/search?q=...` | Public project-document text retrieval with citations |
| GET `/api/v1/account` | Authenticated history consent state |
| PUT `/api/v1/account/history-consent` | Consent update / revocation |
| GET `/api/v1/account/analyses` | Owner-scoped saved metadata, where available |
| GET `/api/v1/account/export` | Authenticated account metadata export |
| DELETE `/api/v1/account` | Delete actor account, associated data |
| POST/GET/DELETE `/api/v1/analyses/{analysis_id}/feedback` | Owner-checked research feedback on a verified completed analysis |
| POST `/api/v1/copilot/query` | Optional protected documentation-only provider (when enabled) |

**Not present:** public POST `/api/v1/analyses` and GET analysis result. Their presence in an earlier *proposed* API list is not a claim of implementation. Enable only after independent model, data, calibration, privacy and safety acceptance, otherwise keep fail-closed.
