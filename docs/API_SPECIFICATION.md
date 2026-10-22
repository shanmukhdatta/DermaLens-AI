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

**New protected research routes:** POST `/api/v1/analyses` accepts JPEG/PNG/WebP <=8MB after signed OIDC actor authentication, prior history consent, enabled analysis workflow and migrations. GET / DELETE `/api/v1/analyses/{analysis_id}` enforce account ownership and expiry. Only quality/reason/abstention metadata is stored for <=30 days; no original image or unvalidated diagnosis. Without `DERMALENS_ENABLE_ANALYSIS_WORKFLOW`, upload remains unavailable after authentication. Anonymous calls return 401.

**Next.js BFF:** `/api/private/account`, `account/history-consent`, `account/analyses`, `analyses`, and `analyses/{uuid}` forward the verified OIDC access token only from server-side Auth.js session. A browser cannot specify the account identifier or bearer token. Login requires a real configured OIDC issuer. The previously frozen `packages/contracts/openapi.v1.json` needs regeneration for these new routes; Python sources are authoritative until then.
