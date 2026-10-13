# Master execution tracker — authoritative Phase 0–13 roadmap

Last updated: 2026-10-13. **Only Phase 0 is being implemented in this branch.** Do not confuse this plan with the older Phase 0–12 conceptual sequence in the root README. A phase is complete only with code/config committed, test evidence, documented limitations, and explicit handoff.

| Phase | Scope | Dependency | Deliverable / acceptance gate | Status |
|---|---|---|---|---|
| 0 | Architecture finalization & baseline | both README audits | Signed-off docs, contracts, ADRs, phase tracking, lint/testable CI; model state honestly documented | In review |
| 1 | Repository engineering foundation | 0 | Python/Next.js workspace, lint/type/test harness, config loader, reproducible local commands, green CI | Not started |
| 2 | FastAPI backend skeleton | 1 | App startup, dependency injection, request IDs, typed errors, liveness/readiness, auth boundary tests | Not started |
| 3 | Persistence and accounts | 2 | PostgreSQL, SQLAlchemy/Alembic, identity and owner guards, retention schema, migration and access tests | Not started |
| 4 | CV image-processing gates | 2, 3 | Decode/quality/one-face/alignment/ROI; safe failure, reference fixture and parity tests (no real classifier required) | Not started |
| 5 | Next.js user experience | 2, 4 | Accessible upload/notice, progress/rejections, results/abstentions, no unsafe medical copy; browser tests | Not started |
| 6 | History and feedback | 3, 5 | Consent-respecting history, erasure, moderated feedback states, ownership checks, integration tests | Not started |
| 7 | Documentation RAG | 2, docs | Curated markdown ingestion, embedding + pgvector, Grok adapter, citations, refusal, secret isolation | Not started |
| 8 | Infrastructure & CI/CD foundation | 2, 3, 5, 7 | Reproducible Docker, staging configuration, secrets handling, migration/smoke CI, no public release | Not started |
| 9 | Existing model integration | 1, 4, 8, private artifact | Verified .keras + exact label map and SHA256, compatible Keras custom objects, parity inference, no mocks | Not started; artifact required |
| 10 | Real-world evaluation and domain-shift audit | 9, approved evaluation data | Defined real-data split, subgroup/failure metrics, reliability benchmark; no unsupported performance claims | Not started |
| 11 | Calibration, abstention, OOD and XAI | 9, 10 | Held-out threshold evaluation, safe abstention policy, Grad-CAM supported only, audited user interpretation | Not started |
| 12 | Integration hardening, deployment & monitoring | 5–11 | Unit/integration/E2E/security tests, deployable staging, alerting, rollback, privacy/legal/release gates | Not started |
| 13 | Controlled offline improvement | 6, 10–12 and validated feedback | Curated data, approved calibration/learning experiments, regression gate, manual promotion; optional RL research nonblocking | Not started |

### Gate policy

1. Implement code and tests before marking a phase done; CI alone does not replace runtime/manual proof.
2. Mark blocked phases `Blocked` with exact evidence and action. No completed claim without commit + passing checks.
3. Use branch/PR per phase, re-audit changed architecture, update this tracker, and supply a reproducible handoff.
4. Phase 9 model artifacts and Phase 10 real-world validation require user-provided private artifacts/data or approved external resources. Never pretend the Git repositories contain them.
5. `Phase 0 = In review` until validation and PR checks pass and acceptance is confirmed. After acceptance, change to `Complete` with commit/PR evidence.
