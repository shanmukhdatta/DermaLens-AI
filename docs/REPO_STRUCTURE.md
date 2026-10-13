# Repository structure — implemented vs planned

Status as of Phase 1 pull request #2. This is the **actual tracked engineering workspace** in the branch, not a promise that future features are active.

```text
DermaLens-AI/
├── README.md
├── pyproject.toml               # Python dependencies, Ruff, mypy, pytest
├── uv.lock                      # resolved Python dependency graph
├── requirements-dev.txt         # original Phase 0 standalone tooling
├── .env.example, .gitignore, .editorconfig
├── .github/workflows/
│   ├── phase0.yml               # Phase 0 schema/document checks
│   └── phase1.yml               # Python + web tests, lint, type and builds
├── apps/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── dermalens_api/
│   │       ├── __init__.py
│   │       ├── config.py       # DERMALENS_ typed fail-closed settings
│   │       └── main.py         # health 200, readiness 503, no inference
│   └── web/
│       ├── package.json, package-lock.json
│       ├── tsconfig.json, next.config.ts, next-env.d.ts
│       ├── eslint.config.mjs, .env.example, .gitignore
│       └── src/
│           ├── app/layout.tsx, page.tsx, globals.css
│           └── lib/platform-status.ts, platform-status.test.ts
├── services/                    # ONLY domain protocols/types
│   ├── cv/ports.py, runtime.py   # missing-model runtime throws error
│   ├── rag/ports.py             # no live docs index or Grok provider
│   └── learning/ports.py        # no live feedback storage
├── packages/
│   ├── common/errors.py
│   ├── security/consent.py
│   ├── telemetry/__init__.py
│   └── contracts/openapi.v1.json, README.md
├── models/README.md, manifests/model-manifest.schema.json
├── scripts/
│   ├── validate_phase0.py
│   └── check_repository_hygiene.py
├── tests/
│   ├── test_phase0_contracts.py
│   ├── test_api_foundation.py
│   └── test_repository_hygiene.py
└── docs/
    ├── 01_SYSTEM_ARCHITECTURE.md ... 09_PRIVACY_AND_SAFETY.md
    ├── PHASE_TRACKER.md, REPO_STRUCTURE.md
    ├── PHASE0_VALIDATION.md, PHASE1_HANDOFF.md
    ├── PHASE1_IMPLEMENTATION.md, PHASE1_VALIDATION.md
    ├── PHASE2_HANDOFF.md
    └── adr/
```

**Not yet created/implemented:** `infra/database/`, `infra/docker/`, `infra/deployment/`, `infra/monitoring/`, additional `services/cv` image-quality/face/preprocessing/model inference modules, RAG indexing and provider adapters, offline learning/evaluation, and the dedicated integration/E2E test suites.

No trained `.keras` model or sensitive images are committed. Phase 0's conceptual repository layout was a target; this file records what exists today.
