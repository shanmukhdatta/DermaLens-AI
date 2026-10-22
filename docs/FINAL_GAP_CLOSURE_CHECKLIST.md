# DermaLens AI — Integrated Gap Closure Checklist

**Updated 2026-10-22.** This inventory distinguishes source implementation, CI verification,
independent external validation, and permission to deploy. The README-derived 144-row
`docs/IMPLEMENTATION_CHECKLIST.md` is a historical requirements inventory; its older aggregate
statuses have **not** been reclassified as 100% complete.

| Gap | Implemented source and integration | Still required for genuine completion |
|---|---|---|
| A — Trained model and label order | VerifiedKerasModel, SHA256 and model manifest; PR #35 adds candidate-only manifest creation and original DiseasePredictor parity CLIs | Actual trained and licensed 6-class `.keras` checkpoint, matching exact `label_map.json`, real training environment/source SHA, private golden image outputs, real parity execution |
| B — Independent clinical validation | Private model-backed evaluation, label-map integrity, subject leakage checks, dHash and pHash near-duplicate audit, confusion matrix, sensitivity/specificity, calibration research helpers (PR #31 and #34) | Rights-cleared, independently labeled clinical photos; verified subject independence; robust subgroup and site/device evaluation; domain expert review; measured calibration/OOD/unknown-class behavior |
| C — Protected analysis and results | Explicit nonproduction feature flag, image constraints, authenticated POST/GET/DELETE analyses, owner-scoped encrypted metadata, TTL and result-row identity checks (PR #32 and #33) | End-to-end execution with real validated model/clinical safeguards; approved result semantics and explainability; production medical release remains disabled |
| D — Authentication and history | Existing backend OIDC/JWKS verification; Next.js BFF PKCE with encrypted session; account consent, history, export, account deletion, private results and moderated feedback UX (PR #29, #32 and #33) | Real configured OIDC provider, safe role/application settings, browser/session/expiration/cross-origin E2E, security review |
| E — Privacy and security | No raw uploaded-image persistence, bounded decoding, owner access checks, authenticated encryption, explicit consent, offline expiry pruner, safe logging and CI tests | Independent threat model and penetration assessment; real-host secrets/TLS/backup/incident/erasure/key-rotation testing; region-appropriate privacy/legal review |
| F — Documentation retrieval | Lexical citations and optional protected Grok documentation client | Semantic embedding/indexing and provider validation if README scope requires them |
| G — Uncertainty and explainability | Offline exploratory calibration and Grad-CAM modules | Real independent OOD, calibration, expert explanation review; validated release policy, with abstention for unknown cases |
| H — Operations | Next.js/FastAPI, SQLAlchemy/Alembic, Docker Compose, CI checks and disposable staging smoke | Real target deployment with durable telemetry, production TLS, rate-limit coordination, backups, recovery and rollback exercises |

## Actual engineering evidence

- PR #29: Next.js OIDC BFF and owner history; merged after CI.
- PR #31: private model-backed evaluation pipeline; merged after CI.
- PR #32: nonproduction protected experimental analysis and encrypted results; merged after CI.
- PR #33: feedback UI/API integration and ciphertext row-binding checks; merged after CI.
- PR #34: independent evaluation metrics and near-duplicate research checks; merged after CI.
- PR #35: candidate model manifest and original research inference parity tools; merged after CI.
- Latest PR #35 verification ran Ruff, mypy, Python tests (**132 passed, 68 warnings**),
  frontend lint/build/typecheck/Vitest, model contracts and Docker smoke. These prove
  source engineering checks, not a live medical product or independent security certification.

## External acceptance gates — do not bypass

1. Obtain the actual authorized checkpoint, original label map and training provenance from the research/Kaggle artifacts. No model weight files were located in the checked GitHub repository.
2. In a private environment execute `docs/MODEL_ARTIFACT_PARITY_RUNBOOK.md`; confirm serialization and original predictor output parity on multiple permitted images.
3. Evaluate subject-disjoint, legally usable real clinical samples, document errors, confidence intervals, subgroup, site/device and OOD reliability, and review with qualified experts. Do not use synthetic fixtures as clinical evidence.
4. Configure an actual OIDC identity provider and test registered redirect, PKCE, issuer, audience, session expiry, CSRF, account ownership, consent, deletion and feedback from real browsers.
5. Perform privacy, security and operational tests with the intended deployment architecture; document and remediate findings. Retention CLI cannot substitute for image/object-storage deletion if that future feature is enabled.
6. Obtain any relevant clinical/regulatory approvals **before** enabling public diagnostic use. A passing unit test, scientific paper or CI build cannot grant these.

**Hard safeguard:** production configuration rejects the experimental research-analysis mode; no diagnosis or skin-cancer rule-out is authorized. Do not remove this gate to inflate completion percentages.

See `docs/FINAL_ENGINEERING_HANDOFF.md`, `docs/FINAL_FEATURE_AUDIT.md`,
`docs/MODEL_ARTIFACT_PARITY_RUNBOOK.md` and
`docs/RESEARCH_FEEDBACK_INTEGRATION.md`.
