# ADR-003: No image retention by default

**Status:** Accepted (architecture), 2026-10-13.

**Context:** Facial images and health-associated classifications are sensitive, and external RAG processing is unnecessary for CV.

**Decision:** Explicit pre-upload notice; default ephemeral image handling, no raw image persisted or logged. Only opt-in owner-scoped metadata history. Separate future reviewed research-image consent, not enabled by default.

**Alternatives:** always store photos; client-only inference.

**Consequences:** fewer debugging image artifacts; use synthetic/licensed test fixtures. Requires robust deletion, authorization and retention controls before release.
