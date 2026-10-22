# Protected experimental feedback

This is an implemented research-only workflow, not an approved medical feedback or diagnostic system. It requires verified OIDC sign-in, account consent and the existing authenticated analysis record. The production research-analysis feature remains disabled.

## Sequence

~~~mermaid
sequenceDiagram
    participant U as Browser
    participant B as Next.js BFF
    participant A as FastAPI
    participant D as PostgreSQL
    U->>B: Submit review choice for analysis UUID
    B->>B: Same-origin and session checks
    B->>A: POST /api/v1/analyses/{id}/feedback with OIDC JWT
    A->>D: Resolve actor ownership, consent, analysis completion
    A->>D: Insert once with pending human review status
    A-->>B: Feedback receipt
    B-->>U: Pending-review state
~~~

- apps/web/src/lib/research-feedback.ts defines an allowlist of the four supported review choices. They are opinions, not verified medical labels.
- apps/web/src/app/api/research/[[...action]]/route.ts allows only named methods and UUID paths, enforces same-origin mutation requests, bounds feedback JSON, and forwards verified bearer tokens from the server-side session.
- apps/web/src/app/history/page.tsx supports submitting, viewing and removing a private review from a retrieved research result.
- services/learning/feedback.py already enforces owning actor, consent and idempotence.
- services/learning/research_analysis.py now checks that encrypted result identifiers and model versions match their database row when decrypting it. Transplanted ciphertext is refused.
- tests/test_research_analysis_api.py includes ciphertext substitution regression; apps/web/src/lib/research-feedback.test.ts covers choice validation.

## Acceptance evidence still needed

Use a configured test OIDC provider, the expected research model artifacts and an isolated PostgreSQL database. Verify browser sign-in, owner vs nonowner access, consent revocation, feedback insert/duplicate/remove, expiry and encryption-key rotation. No real-user image or model output is suitable for clinical decisions yet.

References: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html ; https://www.rfc-editor.org/rfc/rfc9700.html ; https://www.gov.uk/government/publications/good-machine-learning-practice-for-medical-device-development-guiding-principles/good-machine-learning-practice-for-medical-device-development-guiding-principles .
