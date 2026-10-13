# Target repository structure and Phase 0 contents

```text
DermaLens-AI/
  README.md                      # original master requirements, retained
  .editorconfig .gitignore .env.example
  pyproject.toml requirements-dev.txt
  .github/workflows/phase0.yml
  docs/
    01_SYSTEM_ARCHITECTURE.md
    02_COMPUTER_VISION_PIPELINE.md
    03_MODEL_AND_RESEARCH.md
    04_BACKEND_ARCHITECTURE.md
    05_RAG_ASSISTANT.md
    06_FEEDBACK_AND_CONTINUAL_LEARNING.md
    07_MLOPS_AND_DEPLOYMENT.md
    08_API_AND_DATA_FLOW.md
    09_PRIVACY_AND_SAFETY.md
    REPO_STRUCTURE.md PHASE_TRACKER.md
    adr/README.md, 0001..0006 decisions
  packages/contracts/openapi.v1.json
  models/README.md
  models/manifests/model-manifest.schema.json
  scripts/validate_phase0.py
  tests/test_phase0_contracts.py

  # Phase 1+ directories, not yet created:
  apps/api/  apps/web/
  services/cv/{quality,face_detection,alignment,preprocessing,inference,uncertainty,explainability}/
  services/rag/{ingestion,retrieval,embeddings,providers}/
  services/learning/{feedback,curation,calibration,evaluation,experiments}/
  packages/{security,telemetry,common}/
  infra/{database,docker,deployment,monitoring}/
  tests/{unit,integration,e2e,model_contract}/
```

Keep the API, CV and RAG as **separate Python modules** within one backend deployable; no independent service ports. Do not populate runtime modules with fake implementations during Phase 0. The root README's larger directory proposal remains aspirational. This document is the canonical directory rollout.
