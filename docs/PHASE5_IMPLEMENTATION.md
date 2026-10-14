# Phase 5 — User-facing Next.js research experience

## Shipped pages
- `/`: home, responsible research framing, current capability status.
- `/check`: local file preview, opt-in acknowledgement, client-side type/size checks, actual bounded image-quality API call, accepted/rejected response guidance, honest 503/unavailable state; no stored image.
- `/how-it-works`: pipeline explainers and known limitations.
- `/privacy`: concise handling of photos, consent, history and data erasure.
- `/history`: explicit disabled state pending secure sign-in and approved history controls.
- `/assistant`: explicit disabled state pending audited documentation retrieval and LLM provider.
- Shared responsive header/footer, keyboard-focus styling and reduced-motion considerations.

`NEXT_PUBLIC_API_BASE_URL` controls API origin (default local). Only nonsensitive public URL configuration is passed to browser code; no private identity secrets or LLM keys. The backend's image-quality route must be explicitly enabled and protected by the deployment operator; disabling it is an expected and safely communicated response.

**Important:** This frontend does not render a fake disease category, fabricated confidence value, clinical reassurance or an unimplemented AI chatbot. Quality approval is not a diagnosis. Real model integration, feedback, OIDC UI and RAG will be connected in later reviewable phases.

## Validation
Existing Next.js npm lock and scripts continue to run ESLint, Vitest, Next production build, and TypeScript. Additional image-api pure-function tests cover accepted file types/size and error-code guidance. Browser review in Antigravity remains a mandatory external check, including mobile viewport, accessibility and API failure paths.
