# Phase 12 — Integration smoke and privacy-minimal staging telemetry

**Implementation status:** Runtime metrics code and automated container smoke are implemented; deployed clinical inference, private OIDC integration, real checkpoint evaluation, monitoring durability, disaster recovery and public release authorization remain pending.

## Operational metrics

`RuntimeTelemetry` accumulates per-route request counts, HTTP status families and coarse latency buckets with a fixed registered route-template allowlist. Unknown paths are labeled `<unmatched>`; no query strings, user-supplied identifiers, headers, uploaded images, facial details, IP addresses or chat text are metrics labels. Internal snapshot is accessible only within the application process (`app.state.telemetry.snapshot()`). No public metrics endpoint is enabled. Metrics are **in-memory developer telemetry** and must eventually be replaced or supplemented by a secure durable operator observability backend.

## Disposable container integration

GitHub workflow `.github/workflows/phase12-staging-smoke.yml` builds the existing Docker Compose API, Next.js and PostgreSQL services with synthetic CI-only credentials, starts them together, applies the actual Alembic migration, checks HTTP liveness and explicit fail-closed 503 readiness, verifies anonymous account/model metadata denial, confirms RAG is unavailable without API keys, checks the landing page, then deletes its disposable volume. This is an engineering smoke test, **not** independent medical evaluation.

On Antigravity/local machine:
```powershell
$env:DERMALENS_POSTGRES_PASSWORD="local-only-long-unique-password"
docker compose up --build -d --wait
docker compose exec -T api /opt/dermalens/.venv/bin/alembic upgrade head
python -m scripts.operational_smoke --api-origin http://127.0.0.1:8000 --web-origin http://127.0.0.1:3000
docker compose down
```

**Never run `docker compose down --volumes` on a machine with important persistent records.** CI uses disposable data only.

## Mandatory release gates not satisfied here

- Real verified OIDC/JWKS issuer, rotated signing keys, token scope/audience and ownership reviews.
- Live PostgreSQL concurrency, retention and deletion audits, including user export.
- Model checkpoint parity to original research and independent real-image evaluation.
- Calibrated, independently evaluated abstention/OOD and explainability behavior.
- API authentication, input rate limits, upload throttling, abuse handling and persistent observability.
- Clinical, privacy, legal and deployment approvals for any public diagnostic or skin-cancer use.

All inference-dependent endpoints remain unavailable until separately evaluated and explicitly authorized.
