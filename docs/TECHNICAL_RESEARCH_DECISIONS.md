# DermaLens — technical research decisions and verified sources

The research/engineering decisions below were made for the current six-class dermatology research system; the user-supplied master prompt is not itself a clinical release approval.

## 1. Model serving and label integrity

**Compared:** generic off-the-shelf dermatology checkpoint, unknown labels from internet model; verified project-trained `.keras` artifact + exact producer index map. **Decision:** retain `VerifiedKerasModel` with SHA-256, source-commit, tensor/preprocess shape, serialized custom-object allowlist. Start only if manifest, checkpoint and label map are all provided and compatible. Never silently recode acne/fungal/hyperpigmentation/normal/skin cancer/vitiligo ordering or claim BCC/SCC/melanoma subtype unless actual head predicts it.

**Integration:** `Settings.model_manifest_path`, `model_checkpoint_path`, `model_label_map_path` → `create_app` → `VerifiedKerasModel`. Even real weights only produce abstaining research decisions until independent calibration/domain-shift/unknown-class tests justify release. No trained checkpoint was found in the tracked production repository.

## 2. Auth and protected private workflows

**Compared:** bespoke password hashing/login/session system, raw access-token storage in browser; standards-based external OIDC + Auth.js server-session bridge. **Decision:** delegate sign-in/password reset/registration to an operator-selected OIDC provider, let `Auth.js` hold the access token in its encrypted server-session JWT, and use Next route handlers as a same-origin authenticated proxy to existing FastAPI cryptographically verified RS256 JWT auth. Do not copy bearer token into the browser's session object, client-side localStorage, React state or URLs. Enforce same-origin mutation, bounded upload, fixed route allowlist and short expiry; requests remain unavailable without real issuer/credentials.

**Sources:**
- Auth.js installation and App Router integration: https://authjs.dev/reference/nextjs
- Auth.js generic OIDC provider setup: https://authjs.dev/guides/configuring-oauth-providers
- Auth.js JWT and protected API routes: https://authjs.dev/getting-started/session-management/protecting

**Integration:** `apps/web/src/auth.ts`, `app/api/auth/[...nextauth]`, `app/api/private/[...path]`, `app/history`; backend `packages/security/oidc.py`, `require_verified_actor`. Real provider access token **must be a JWT with configured backend audience**, not just an ID token or opaque access token. CSRF, issuer, JWT algorithm, subject and audience checks are not optional.

## 3. Consent and database persistence

**Compared:** storing raw photographs by default, in-memory result cache; persisting only consented non-diagnostic metadata linked to a cryptographically verified account. **Decision:** never store image bytes in DB/object storage, and do not auto-enroll the user in history. Reject unconsented research uploads before reading photo. Save status, reason, quality, pipeline/model version and creation/expiry only. Thirty-day expiry, explicit per-record delete and revocation-wide deletion; no class probabilities are saved or exposed.

**Source:** SQLAlchemy documented transaction framing and ORM Unit of Work: https://docs.sqlalchemy.org/en/20/orm/session_basics.html

**Integration:** Alembic revision `0004_result`, `services/persistence/models.py`, `routers/analyses.py`, existing `repository.py` and `retention.py`. API never accepts client-specified account_id, issuer or owner; all ownership comes from verified OIDC principal.

## 4. Privacy in India and risk of children's data

Images of faces and medical context can be sensitive. Indian Digital Personal Data Protection Rules were notified in 2025 with staged commencement, including provisions for verifiable parental consent where applicable. This app is not deemed compliant by writing consent checkbox code. Do not enable deployment to children or claim compliance until legal policy and verifiable parental/guardian consent flow are reviewed; the prototype has **no age verification**.

**Official source:** MeitY Gazette DPDP Rules 2025: https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf

## 5. Clinical validation and data leakage

An evaluation is independent only when real licensed cohort, patient-group separation, exact/near-duplicate audit, strict test/calibration splits, subgroup confounding checks and error analysis are documented. The existing offline `services/learning/evaluation.py` computes per-class precision/recall/F1, Brier/NLL/ECE and subgroup summaries, but these are not clinical performance estimates until run with independent approved data. Synthetic and training images are excluded from claims of clinical validation.

**Integration:** `scripts/evaluate_predictions.py`, `services/learning/evaluation.py`, `models/manifests` and QA. OOD, alignment, uncertainty, Grad-CAM fidelity and actual deployment population acceptance require independent data and review.

## Explicit no-claim statement

CI, migrations, image quality checks, passing small fixtures, checkpoint tensor compatibility and warm orange/white pages verify engineering behavior only. They **do not establish diagnosis, sensitivity/specificity in patients, legal compliance or production safety**.
