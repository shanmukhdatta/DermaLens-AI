# Privacy, security and medical-safety policy

**Use boundary:** research/educational prototype only. No clinical diagnosis, screening, treatment, severity or subtype claims. An image cannot rule out a serious condition; label `Skin Cancer` is an unvalidated model class and must never be framed as confirmed cancer. Provide a prompt to contact a qualified clinician for concerning or changing symptoms; do not rely on the app for urgent decisions. Do not advertise clinical accuracy without relevant prospective evidence/regulatory review.

## Sensitive facial images

Default: explicit pre-upload notice, `ephemeral` processing, transient memory only, no retained raw face, no request-body logging, EXIF stripped for processing, bounded resource usage, immediate cleanup including errors. Optional `history_metadata` stores derived metadata, **not images**. Future separate, explicit `research_image_opt_in` mode may use encrypted restricted object store only after implementation of purpose notice, age/guardian rules as applicable, retention duration, revoke/delete flow, access logs, legal review, and encryption. This mode is NOT available in Phase 0.

Minimize collection of directly identifying data. Consent record covers purpose, time, version, choice; withdrawal affects future processing. Authenticate owner-scoped history/feedback, authorize each access; audit privacy-affecting operations without storing face content. All application secrets via secret manager/environment; never commit local .env, model weights or private datasets. HTTPS, CSP, CSRF/session protection (if cookies), secure OIDC, origin allowlist, upload limits, antivirus/decoder-hardening controls, rate limits and encrypted backup procedures are gates before public release.

## Provider / AI separation

Grok bot receives only safe, sanitized documentation question + approved public project document chunks, **never** face images, predictions, medical history or metadata. Bot is NOT a healthcare assistant. Defend against untrusted-document prompt injection, hallucinated citations and unsafe medical guidance. Model uncertainty and OOD thresholds must be evaluated on appropriate data; if policy or model unavailable, abstain. Explainability maps are visual attribution only.

## Retention, rights, risk gates

Define data retention durations per data type before enabling storage; TTL workers, deletion, export, backup aging and log redaction must be tested. Do not retain images for dataset improvements without separate valid consent and licensed, representative data. Underage users require an age-appropriate deployment policy and applicable consent requirements; avoid public collection until this is implemented. Security/privacy review, independent expert evaluation and incident response remain future release gates, not Phase 0 accomplishments.
