# Phase 6 — Feedback and consent-aware history integration

This feature introduces real, database-backed feedback records only for an actor with cryptographically verified identity and explicit active history consent, on a completed, owned, unexpired, versioned analysis. An unknown, other-user, uncompleted or expired analysis always appears nonexistent (404). Currently, no user-facing creation of real analysis records exists without model integration; automated tests generate **test fixtures only**.

Endpoint contract:
- `POST /api/v1/analyses/{analysis_id}/feedback` — accepted choices: correct, incorrect, unsure, quality_issue. Returns a single pending-review record (201).
- `GET /api/v1/analyses/{analysis_id}/feedback` — same actor only.
- `DELETE /api/v1/analyses/{analysis_id}/feedback` — retract user's submission.
- `GET /api/v1/account/export` — includes stored feedback for current actor.
- Existing history-consent revocation and account deletion cascade to analyses and feedback.

A DB unique constraint prevents conflicting duplicate submissions. An identical repeated submission is idempotent; a changed response yields 409 until user explicitly retracts it. No free-text medical narratives are stored. Never use user-generated feedback as automatic clinical truth, never update a model online, and never expose review claims as diagnoses.

**Validation:** backend migration and tenant-ownership tests, negative authentication tests and deletion tests in CI. Production PostgreSQL migration, concurrency and provider integration must still be exercised against disposable infrastructure before enabling accounts publicly. No trained checkpoint or clinician review is implied by this PR.
