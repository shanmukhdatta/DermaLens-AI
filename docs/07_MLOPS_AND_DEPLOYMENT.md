# Operations, MLOps and deployment plan (planned)

Initial topology: Next.js web frontend + containerized FastAPI modular monolith + PostgreSQL/pgvector. Private S3-compatible storage only for consented optional artifacts. Version-controlled config and schema migrations; deploy behind HTTPS with secure secret injection. Grok API token stays server-side. No microservices until performance evidence.

CI pipeline stages: static security/lint + unit and schema validation -> integration/model smoke tests with private artifact in protected environment -> container build/scan -> staging smoke -> manual release gate. Model promotion independent of code; signed or digest-pinned artifact manifests, checksums and rollback to approved version. A missing or mismatched checkpoint makes readiness false and analysis unavailable.

Telemetry: counts, timing, error-code distribution, quality rejection, abstention, output drift, approved-feedback rates, model + document index versions. Do not log raw image, sensitive text prompts, bearer tokens, full probability vectors keyed to personal identity, or storage object URLs. Hash/aggregate metric dimensions to limit reidentification risk.

Backup and restore test for DB, retention/erasure job testing, secrets rotation, dependency scanning and emergency disable for analysis endpoint are release prerequisites. Real-device/browser and real-image validation required before deployment claims.

See [phase tracker](PHASE_TRACKER.md). There are no deployment success claims in Phase 0.
