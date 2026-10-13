# ADR-001: Modular monolith before service decomposition

**Status:** Accepted (architecture), 2026-10-13.

**Context:** CV, web, RAG, feedback and persistence need isolated interfaces without costly distributed orchestration.

**Decision:** FastAPI deploys as one modular monolith; web stays Next.js. Ports define CV runtime, repositories, LLM provider and storage. Explicit domain modules prevent accidental logic crossover.

**Alternatives:** independent inference/RAG microservices or all logic in API routes.

**Consequences:** simpler testing and operations; inference may block the API unless bounded concurrency is introduced. Split by profiling evidence, not by default.
