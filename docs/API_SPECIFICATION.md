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
| POST `/api/v1/analyses` | **OIDC-protected research-only** raw image submission, consent + real-checkpoint gated, disabled in production; output explicitly nonclinical |
| GET/DELETE `/api/v1/analyses/{analysis_id}` | Owner-only encrypted experimental result retrieval / deletion, blocked unless research mode is configured |
| POST `/api/v1/copilot/query` | Optional protected documentation-only provider (when enabled) |

**Not present:** any publicly available diagnostic-classification API. The protected research endpoints cannot be used for clinical conclusions and remain off by default. See `docs/RESEARCH_ANALYSIS_IMPLEMENTATION.md`; the root OpenAPI contract still requires updating to cover opt-in research routes and must not be treated as a complete clinical API.

## Browser-facing protected BFF paths (Next.js)

- `POST /api/research` — one-image, origin-checked session proxy to the experimental backend (8MB maximum).
- `GET /api/research/{uuid}` — authenticated owner-only encrypted result fetch via BFF.
- `DELETE /api/research/{uuid}` — origin-checked result erasure.
- `GET /api/auth/session`, `GET /api/auth/login` and `POST /api/auth/logout` — pre-existing OIDC BFF from PR #29.

These are not public medical diagnosis interfaces; the research backend refuses activation in the production environment and defaults to disabled.
