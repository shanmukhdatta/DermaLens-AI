# Phase 7 — Documentation grounded assistant (gated)

The backend can load **only** the original README and nine approved architecture/privacy Markdown files. Each section is broken into bounded excerpts retaining path and heading provenance. A deterministic lexical retriever ranks excerpts. It does NOT currently implement semantic embeddings or persistent pgvector; those remain an explicitly tracked completion gap rather than a hidden fake feature.

The Grok provider uses xAI's documented `POST https://api.x.ai/v1/responses`, with `store:false`, no tools, strict instructions, 25s timeout and bounded output. API keys are server-only and must never be exposed in `NEXT_PUBLIC_*`. Images, model artifacts, medical history, database records, chats and source code are excluded from retrieval. Sources returned in the API are exact retrieved document references; they are retrieval provenance, **not** independent fact verification.

Feature remains disabled unless all server settings `DERMALENS_ENABLE_RAG_ASSISTANT=true`, `DERMALENS_GROK_API_KEY=...` are set. Even then, the query endpoint requires cryptographically verified identity; no anonymous provider spending. Default application continues returning 404 for the unshipped assistant. The consumer UI will be activated only after account sign-in, rate limits and provider configuration are tested.

The assistant answers documentation questions, never interprets facial images or recommends medical treatment. Private questions are blocked from the provider with a local refusal. Inadequate retrieval returns a fixed no-evidence message. API errors are redacted to `RAG_UNAVAILABLE`. No provider credentials are committed.

Reference: https://docs.x.ai/developers/rest-api-reference/inference/responses (checked 2026-10-14).

**Tests:** deterministic allowlist and retrieval, verified actor enforcement, personal medical refusal, source provenance, and a fake provider confirming `store:false`. Live xAI calls were NOT executed. Add a vector index, provider rate-limiting, monitoring and prompt-injection/red-team evaluation before public release.
