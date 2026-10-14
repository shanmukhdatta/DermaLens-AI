# Phase 8: Reproducible local infrastructure shell

Included: Python 3.11 API Dockerfile with explicit locked `uv` installation and runtime extension dependencies, Node 22 Next.js multi-stage Dockerfile, PostgreSQL 17 container with health check, Docker Compose loopback-only bindings, explicit separate Alembic migration command, rootless app containers and privacy-focused build ignore rules. CI validates Compose configuration.

**Not yet validated:** actual Docker image builds and startup against this runner environment, disposable PostgreSQL transaction/concurrency tests, TLS ingress, production sign-in, image detection across real devices, cloud secret management, rate limits and hosted public deployment. This Compose file is strictly for local, nonclinical engineering evaluation.

The app's public liveness may report 200 with no classifier; readiness deliberately reports 503 until a verified model and safety policy are ready.
