# ADR-004: Documentation-grounded RAG only

**Status:** Accepted (architecture), 2026-10-13.

**Context:** A chatbot explaining project architecture must not become an unverified medical assistant or leak personal face analyses.

**Decision:** Only approved markdown is indexed; hybrid retrieval with pgvector; source citations required; Grok provider behind a server-only interface; absent evidence or provider gives abstention.

**Alternatives:** general medical chatbot, whole-repo indexing, model output as RAG context.

**Consequences:** narrow but verifiable answers, token/provider cost, source-curation and prompt-injection defense requirements.
