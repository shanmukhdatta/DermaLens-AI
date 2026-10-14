# Phase 3: Persistence and verified accounts — implementation notes

This phase implements a *minimal*, owner-scoped persistence substrate. No upload or analysis endpoint is enabled; no facial images, clinical labels, logits, explanations or chat messages are persisted.

## Authentication

If and only if all `DERMALENS_OIDC_ISSUER`, `DERMALENS_OIDC_AUDIENCE` and `DERMALENS_OIDC_JWKS_URL` are configured, the API uses the OIDC verifier. It validates RS256 signatures with issuer-associated JWKS, issuer/audience/expiry/issued-at/subject, and rejects other algorithms. The JWKS hostname must match issuer. With no OIDC configuration, **all** bearer tokens continue to be rejected. CORS alone is not authentication.

## Storage

`DERMALENS_DATABASE_URL` points to PostgreSQL using `postgresql+psycopg://`. SQLite is allowed only for local test/development. Install the extension with `uv pip install --python .venv/bin/python -r requirements-persistence.txt`. Run `uv run --no-sync alembic upgrade head` before enabling accounts. Migrations must be an explicit, reviewed operation, not executed on service startup.

Data model: `accounts` (issuer, subject), `consents` (purpose and granted), `analyses` (metadata-only future table) and `feedback` (future verified review). Foreign keys cascade through account deletion. A revoked history consent deletes associated analyses. Default consent is **false**; reading without consent returns an empty history. Stored raw facial images are forbidden.

## Active endpoints

- `GET /api/v1/account`: current verified user's history consent state.
- `PUT /api/v1/account/history-consent`: `{\"enabled\":true|false}`.
- `GET /api/v1/account/analyses`: owner-scoped metadata, max 100, excludes expired records.
- `GET /api/v1/account/export`: export available metadata.
- `DELETE /api/v1/account`: idempotent erasure, HTTP 204.

No caller can specify account ID, subject, or issuer through request body. Requests require verified JWT identity and configured persistence; otherwise fail closed. No fake inference.

## Gates and limitations

Automated SQLite migration, authorization, consent and JWT cryptography tests exercise the implementation. Before production exposure, additionally run real disposable PostgreSQL migration/concurrency tests, verify identity provider integration and issuer/JWKS rotation, ensure encrypted managed storage and retention jobs, and perform external privacy/security review. The API readiness endpoint remains 503 until verified inference and safety policy are available. **No public clinical service is authorized by this phase.**
