# Phase 12 — Staging smoke tests and privacy-minimal monitoring

This PR implements **operational hardening components**, not a completed public rollout.

- Per-process aggregated route status/count/mean-latency metrics, using only registered route patterns. No image, message, bearer token, query parameter or per-person labels. Snapshot is an internal Python method, **not** a public metrics endpoint.
- Every API access log includes a bounded duration measurement; request IDs remain canonical.
- `python -m scripts.staging_smoke --api-base-url http://localhost:8000` asserts engineering liveness 200, *intentional* inference readiness 503, unauthorized model metadata 401 and unavailable analysis route 404, along with no-store/nosniff/request correlation. **Never** sends skin photos or personal data.
- Unit tests ensure the response contract, privacy-safe metric labels, and failure if unsupported clinical inference appears.

## Gates still open

This checks *engineering-disabled* mode only. Full container startup, user-browser E2E, live PostgreSQL/OIDC, rate limiting at ingress, real model artifact parity, clinician-supervised evaluation and performance, model confidence reliability, subgroup risks, rollback drill, and external security/privacy review are not performed by these tests. Public medical inference must remain disabled until those requirements have separate evidence.

To run after local Docker Compose startup:
```sh
python -m scripts.staging_smoke --api-base-url http://localhost:8000
```

A successful smoke test is evidence of correct **fail-closed wiring**, not that skin classification works or is safe.
