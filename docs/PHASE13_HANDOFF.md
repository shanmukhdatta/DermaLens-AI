# Phase 13 handoff — controlled offline improvement and model promotion

Implement offline candidate evaluation and registry transitions with signed/verified artifact manifest, baseline and candidate metric comparison, versioned approval, and rollback. Only reviewed real-world/clinician-verified feedback may enter model training; unverified user clicks must never become ground truth. Avoid changing model weights in the request path and keep raw images excluded by default. Test gate rejection and audit records. No automatic production deployment without independent clinical/regulatory review.
