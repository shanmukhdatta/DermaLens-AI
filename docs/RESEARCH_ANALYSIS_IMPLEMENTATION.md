# Gated experimental analysis architecture

**Status:** Source-code functionality wired; no real checkpoint, independent clinical evaluation, approved confidence calibration or public diagnostic deployment is included.

```mermaid
sequenceDiagram
    participant U as Verified research participant
    participant API as FastAPI
    participant DB as Relational store
    participant M as Local verified Keras model
    U->>API: POST /api/v1/analyses (consented, authorized, one image)
    API->>DB: Verify issuer+subject history opt-in
    API->>API: Bounded decode and one-face quality check
    API->>M: Full-frame 224x224 RGB, same as research predictor
    M-->>API: Six ordered probabilities
    API->>API: Check class/probability contract; label research-only
    API->>DB: Encrypt only metadata with Fernet and expiry (no photo)
    API-->>U: Nonclinical research-only response with warning
    U->>API: GET/DELETE by UUID with auth
    API->>DB: Enforce account ownership and expiry
    API-->>U: Decrypted owner result / deletion
```

## Enable only for isolated research environments

Requirements: installed `requirements-cv.txt` and `requirements-persistence.txt`, migrated PostgreSQL (`alembic upgrade head`), configured OIDC issuer/audience/JWKS, verified research manifest and exact local checkpoint and label-map paths, and deployment-managed Fernet key.

```bash
# Examples are variable names, not credentials.
DERMALENS_ENABLE_RESEARCH_ANALYSES=true
DERMALENS_MODEL_MANIFEST_PATH=/private/model/manifest.json
DERMALENS_MODEL_CHECKPOINT_PATH=/private/model/classifier.keras
DERMALENS_MODEL_LABEL_MAP_PATH=/private/model/label_map.json
DERMALENS_RESULT_ENCRYPTION_KEY=<generated-private-Fernet-key>
DERMALENS_RESEARCH_HISTORY_DAYS=30
```

The application refuses research analyses in `production`. Unconfigured research endpoints reject before inference. The model is loaded exclusively from local SHA256-verified files, not dynamically downloaded. It uses full-frame research preprocessing, **not** experimentally aligned face crops. The result is `RESEARCH_ONLY_UNCALIBRATED`, with raw score clearly distinct from clinical confidence. Do not convert the score into a diagnosis.

## Privacy boundaries

- Authentication uses existing OIDC JWT verification; no password database is introduced.
- Requires explicit history-metadata consent before any stored prediction.
- Uses Fernet authenticated encryption for stored result metadata. The encryption key is an external secret, not a committed file.
- Raw photographs remain ephemeral; result encryption does **not** equal complete database encryption, backups encryption or certification.
- Real endpoints are POST /api/v1/analyses, GET/DELETE /api/v1/analyses/{uuid}; existing GET /api/v1/account/analyses lists owner-scoped metadata.
- Expiring results are excluded from reads; run the operator-only bounded sweep described in `docs/RETENTION_OPERATIONS.md` for physical deletion.

## Verification

```bash
python -m pytest -q tests/test_research_analysis_api.py
python -m pytest -q tests/test_phase3_persistence.py
```

The above tests use a fixture model in test code only. Passing them cannot establish real model fitness, production authentication, clinical safety, anti-abuse scalability, regulatory approval or full browser usability. External checkpoint and independent validation are still necessary.
