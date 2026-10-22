# Technical Research Decisions — October 22, 2026

## 1. Upload handling
**Problem:** Photo uploads must reject large, invalid and multi-frame files without accidental storage. **Selected:** reuse the existing validated `inspect_image` boundary and bounded streaming `Request.stream()` with strict 8 MB cutoff. **Rejected:** unrestricted `UploadFile.read()` or filesystem copies. **Evidence:** [Starlette Request streaming](https://starlette.dev/requests/) and [FastAPI upload guidance](https://fastapi.tiangolo.com/tutorial/request-files/). User media-type declarations remain untrusted; decoder validates actual image formats.

## 2. Model compatibility
**Problem:** A pretrained 22-class dermatology network cannot be silently relabeled to DermaLens's six-class head. **Selected:** reuse SHA256-verified research `.keras` checkpoint with exact six-class index mapping and 224x224 full-frame RGB contract, refusing incompatible outputs. **Evidence:** existing repository `services/cv/artifacts.py`, `services/cv/keras_runtime.py`; compatibility is established by model-specific evidence, not by model family names. **Status:** actual weights/label-map and model parity fixtures are still absent.

## 3. Protecting experimental result metadata
**Problem:** Facial disease-like inferences are sensitive. **Selected:** no raw-photo retention, explicit history consent, owner guards, key-managed Fernet authenticated encryption for small structured result metadata, 30-day expiry by default, and bounded erasure tooling. **Rejected:** returning a bare account ID or storing plain predicted labels. **Reference:** [cryptography Fernet documentation](https://cryptography.io/en/latest/fernet/). This is an engineering control, not proof of full compliance or formal security certification.

## 4. Identity
**Problem:** Authenticated history must prevent cross-user record leakage. **Selected:** preserve existing OIDC RS256/JWKS verification and issuer + subject owner mapping, rather than invent a password scheme. An OIDC browser-to-backend-for-frontend workflow merged in PR #29. Production identity-provider configuration and security verification are still outstanding. **Reject:** hand-written password hashing, pasted credentials or unsigned JWT claims.

## 5. Independent image evaluation
**Problem:** Real-world datasets have duplicate subjects, edited photos and modality mismatch. **Selected:** local manifest with explicit splits and subject groups, exact SHA256, rotation/mirroring-canonical dHash and cross-split review flags; no imaginary patient identity. **Sources to assess, not automatically ingest:**
- [Google SCIN](https://github.com/google-research-datasets/scin): 10k+ clinical photos grouped by contribution, dermatologist annotation, SCIN-specific data-use license; check facial location/target class support.
- [ISIC challenge data](https://challenge.isic-archive.com/data/): multiple skin-lesion datasets, many dermoscopic with mixed licenses; lesion crops are not direct facial-image evaluation substitutes.
- [Fitzpatrick17k](https://github.com/mattgroh/fitzpatrick17k): broad clinical photos, skin tone and CC BY-NC-SA license; verify provenance and permitted research use.

No automatic license clearance or diagnostic-label mapping is claimed.

## 6. Indian privacy requirements
For deployment in India, assess the [MeitY DPDP Rules 2025](https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025) and their phased commencement with qualified counsel. Do not assert complete legal compliance based only on consent toggles. Health-related facial photos deserve conservative safeguards and age-appropriate consent handling.

## 7. Explicitly rejected shortcuts
No random/synthetic inference substituted for a real model; no medical validation claimed from CI; no automated online retraining from raw feedback; no external API key in browser; no automatic cloud deployment or clinical-facing classification.
