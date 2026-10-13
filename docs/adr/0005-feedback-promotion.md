# ADR-005: Feedback never updates deployed weights automatically

**Status:** Accepted (architecture), 2026-10-13.

**Context:** User votes can be mistaken or malicious; clinical ground truth is unavailable.

**Decision:** Store user feedback as unverified until review. Curate only consented validated examples, conduct offline experiments, compare with approved baseline, require human promotion and rollback.

**Alternatives:** online learning from votes, automatic retraining/deploy.

**Consequences:** slower model improvement with a defensible audit trail. Optional RL research does not gate production.
