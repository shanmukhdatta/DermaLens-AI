# Phase 13 — Controlled offline learning candidate review

This phase adds **offline gating**, not automatic retraining or model promotion.

## Curated feedback
`services.learning.curation.validate_training_manifest` checks an offline manifest of sample content hashes, private pseudonymous subject groups, a reviewed category, review-evidence hash, authorized research-training consent, rights confirmation and a clinician/researcher-verified provenance marker. No raw images or direct identifiers are included. This function verifies **manifest structure**, not signatures, actual consent grant validity or authenticity. Those require independent audit before any training is authorized.

User feedback marked `correct` or `incorrect` is never a trusted medical label. Account and history consent alone do **not** permit retraining.

## Candidate review
`python -m scripts.review_candidate --baseline /private/baseline.csv --candidate /private/candidate.csv --label-map /private/label_map.json --output /private/review.json`

This offline command takes the metadata/probability CSVs from Phase 10, audits splits and probabilities, requires the *same held-out real* examples for baseline and candidate, checks 30+ independent subject groups and distinct model versions, compares macro-F1, per-class recall and multiclass Brier score. Regressions reject a candidate from the engineering gate.

A passing candidate is marked `awaiting_independent_review`, **never** `approved_for_clinical_use` or deployed. Thresholds/margins must be designed and justified under a supervised evaluation protocol, not tuned repeatedly against the final held-out test. Actual training jobs, models, rights, real test data, safety claims, promotion registry and rollback are intentionally not fabricated.

## External acceptance blockers
- Certified patient-consent and licensing evidence for any new records.
- Clinician-backed label provenance for diagnostic conditions, independent test population and domain-shift studies.
- Actual verified checkpoint/label-map and secure artifact registry with signed approval.
- Validated uncertainty, OOD and explainability plus safety/legal review.
- Explicit, audited operator approval and production rollback drills.

No new weights are trained in this repository by this phase; the separate research workflow remains the training provenance.
