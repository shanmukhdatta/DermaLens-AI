# apps/web/src/app/privacy — module technical guide

## Purpose and scope

Public privacy and limitations notice screen. Status: **No claim that unimplemented retention paths are secure**. See root README and `docs/FINAL_FEATURE_AUDIT.md` for the release state.

## Direct file index

- `page.tsx` — React/Next.js component

## Architecture and internal workflow

Route -> visible privacy boundaries.

```mermaid
flowchart LR
    Entry[Entry point / caller] --> Validate[Validation or policy]
    Validate --> Module[privacy module]
    Module --> Outcome[Typed result / next layer]
```

## Public interfaces and integration

default export page component. Consumers should use these boundaries rather than bypassing permissions, model integrity checks or consent.

## Dependencies and configuration

None. Do not commit secrets, patient photographs, model checkpoints or other sensitive artifacts.

## Verification

Run from repository root unless the command is an npm script (run npm scripts from `apps/web`):

```bash
npm run build
```

These are **recommended commands**, not a claim they were executed during this documentation change. Record commit SHA, test output and independent integration evidence before changing audit state.
