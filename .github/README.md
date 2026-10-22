# .github — module technical guide

## Purpose and scope

Repository automation definition. Status: **CI tests source integration, not clinical safety**. See root README and `docs/FINAL_FEATURE_AUDIT.md` for the release state.

## Direct file index

- This folder mainly groups nested packages; consult child README files.

## Architecture and internal workflow

Push/PR -> jobs -> status checks.

```mermaid
flowchart LR
    Entry[Entry point / caller] --> Validate[Validation or policy]
    Validate --> Module[github module]
    Module --> Outcome[Typed result / next layer]
```

## Public interfaces and integration

workflows. Consumers should use these boundaries rather than bypassing permissions, model integrity checks or consent.

## Dependencies and configuration

GitHub Actions settings. Do not commit secrets, patient photographs, model checkpoints or other sensitive artifacts.

## Verification

Run from repository root unless the command is an npm script (run npm scripts from `apps/web`):

```bash
Inspect workflow runs and required checks
```

These are **recommended commands**, not a claim they were executed during this documentation change. Record commit SHA, test output and independent integration evidence before changing audit state.
