# ADR-006: Python/FastAPI, Next.js, PostgreSQL/pgvector

**Status:** Accepted (architecture), 2026-10-13.

**Context:** One Python inference runtime, modern web UX, modest project infrastructure.

**Decision:** Python 3.11+ / FastAPI / Pydantic v2 / SQLAlchemy 2 / Alembic; TensorFlow/Keras pinned to artifact when available; Next.js + TypeScript; PostgreSQL with pgvector; S3-compatible storage opt-in; Docker + GitHub Actions; Grok through provider adapter. Start with manifest registry; defer MLflow, distributed workers, Redis and external vector DB until justified.

**Alternatives:** Django monolith, separate model microservice, MongoDB, dedicated vector DB, all-in-one Next.js server.

**Consequences:** clean Python ML integration and relational ownership; app and web have separate build/deployment lifecycles; exact runtime versions finalized after checkpoint compatibility validation.
