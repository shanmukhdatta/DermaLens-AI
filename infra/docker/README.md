# Local DermaLens container stack

Only local loopback ports are published; this configuration is for Antigravity or an internal research environment, **not** direct internet exposure. No face images are persisted. The image quality endpoint is available; the skin classifier remains unavailable and readiness returns 503 until an approved model is integrated.

## Start

1. Install Docker Engine/Desktop with Compose v2.
2. In repository root, create an untracked `.env` with `DERMALENS_POSTGRES_PASSWORD=<strong-random-local-only-password>`. Keep this file untracked.
3. Run `docker compose config -q` to confirm interpolation.
4. Build and start with `docker compose up --build -d`.
5. Explicitly apply reviewed migrations: `docker compose run --rm api /opt/dermalens/.venv/bin/alembic upgrade head`.
6. Open http://localhost:3000 and run a quality check. API liveness is http://localhost:8000/api/v1/health and reports `{"status":"ok"}`; readiness intentionally returns HTTP 503. If image quality is not ready, do not substitute fake inference.
7. Stop with `docker compose down`. Avoid `--volumes` unless you intentionally want to permanently delete local account data.

External database/postgres and OIDC integration require additional security validation before enabling real accounts. Never put the model checkpoint, private facial photos or credentials in the repository or image build context. Production must provide trusted TLS termination, rate limits, DDoS protections, security and legal review, incident response, backups and retention/deletion jobs.

## What this proves

Successful Docker startup is an engineering packaging milestone, not proof of diagnostic accuracy or model readiness. Test model artifacts and real-world generalization separately.
