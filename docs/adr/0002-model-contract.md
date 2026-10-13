# ADR-002: Strict artifact preprocessing and verification

**Status:** Accepted (architecture), 2026-10-13.

**Context:** Research predictor expects RGB 224x224 float32 [0,255]; Keras custom layers perform model-specific normalization. The pretrained artifacts and actual label-map order are not present in Git.

**Decision:** Verified manifest + exact checkpoint/map SHA-256 and pinned compatible custom objects; Pillow bilinear resize; never externally normalize; reject missing/mismatched assets and prevent mock inference in real mode.

**Alternatives:** standardized external ImageNet normalization, hardcoded label order, silent fallback model.

**Consequences:** extra export/compatibility work in Phase 9, but reproducible and non-misleading predictions.
