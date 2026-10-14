# Master execution tracker — authoritative Phase 0–13 roadmap

Last updated: 2026-10-14 (post-merge audit). **Implementation PRs #1–#19 were merged where applicable; see docs/README_FEATURE_AUDIT.md for exact capabilities and release blockers.** Do not confuse this plan with the older Phase 0–12 conceptual sequence in the root README. Merging phase code does NOT mean a production-ready or clinically validated phase. A feature is accepted only after real external evidence and requirements verification.

| Phase | Scope | Dependency | Deliverable / acceptance gate | Status |
|---|---|---|---|---|
| 0 | Architecture finalization & baseline | both README audits | Signed-off docs, contracts, ADRs, phase tracking, lint/testable CI; model state honestly documented | Complete — PR #1 merged, CI passed |
| 1 | Repository engineering foundation | 0 | Python/Next.js workspace, lint/type/test harness, config loader, reproducible local commands, green CI | Merged — PR #2, CI green; external Windows startup not yet verified |
| 2 | FastAPI backend skeleton | 1 | App startup, dependency injection, request IDs, typed errors, liveness/readiness, auth boundary tests | Merged — PR #3 |
| 3 | Persistence and accounts | 2 | PostgreSQL, SQLAlchemy/Alembic, identity and owner guards, retention schema, migration and access tests | Implementation merged PR #4; external live OIDC/DB acceptance pending |
| 4 | CV image-processing gates | 2, 3 | Decode/quality/one-face/alignment/ROI; safe failure, reference fixture and parity tests (no real classifier required) | Merged PR #5; alignment/ROI and real-model parity still missing |
| 5 | Next.js user experience | 2, 4 | Accessible upload/notice, progress/rejections, results/abstentions, no unsafe medical copy; browser tests | Merged PR #6; basic pages/quality flow only; user result/feedback/history and browser QA pending |
| 6 | History and feedback | 3, 5 | Consent-respecting history, erasure, moderated feedback states, ownership checks, integration tests | Merged PR #7; backend feedback exists, verified user analysis path still missing |
| 7 | Documentation RAG | 2, docs | Curated markdown ingestion, embedding + pgvector, Grok adapter, citations, refusal, secret isolation | Merged PR #8; lexical docs and protected Grok adapter, vector indexing/provider E2E pending |
| 8 | Infrastructure & CI/CD foundation | 2, 3, 5, 7 | Reproducible Docker, staging configuration, secrets handling, migration/smoke CI, no public release | Merged PR #9; disposable Docker CI smoke PR #15 passed, production staging pending |
| 9 | Existing model integration | 1, 4, 8, private artifact | Verified .keras + exact label map and SHA256, compatible Keras custom objects, parity inference, no mocks | Merged PR #10 adapter; real trained .keras checkpoint, label mapping/parity blocked |
| 10 | Real-world evaluation and domain-shift audit | 9, approved evaluation data | Defined real-data split, subgroup/failure metrics, reliability benchmark; no unsupported performance claims | Pending acceptance: offline research tooling merged, requires private model/data and human review |
| 11 | Calibration, abstention, OOD and XAI | 9, 10 | Held-out threshold evaluation, safe abstention policy, Grad-CAM supported only, audited user interpretation | Not started |
| 12 | Integration hardening, deployment & monitoring | 5–11 | Unit/integration/E2E/security tests, deployable staging, alerting, rollback, privacy/legal/release gates | Not started |
| 13 | Controlled offline improvement | 6, 10–12 and validated feedback | Curated data, approved calibration/learning experiments, regression gate, manual promotion; optional RL research nonblocking | Not started |

### Gate policy

1. Implement code and tests before marking a phase done; CI alone does not replace runtime/manual proof.
2. Mark blocked phases `Blocked` with exact evidence and action. No completed claim without commit + passing checks.
3. Use branch/PR per phase, re-audit changed architecture, update this tracker, and supply a reproducible handoff.
4. Phase 9 model artifacts and Phase 10 real-world validation require user-provided private artifacts/data or approved external resources. Never pretend the Git repositories contain them.
5. Phase 0 is complete: merged PR #1, GitHub Actions verified. Phase 1 PR #2 was merged as `a54592fa950298dbe3732fe47b16b0db192a6228` after green PR CI. Local Windows/Antigravity smoke and visual checks remain unverified; do not treat those as passed.
