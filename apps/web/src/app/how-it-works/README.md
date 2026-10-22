# apps/web/src/app/how-it-works — module technical guide

## Purpose and scope

Read-only architecture explainer screen. Status: **Content is explanatory, not patient-specific**. See root README and `docs/FINAL_FEATURE_AUDIT.md` for the release state.

## Direct file index

- `page.tsx` — React/Next.js component

## Architecture and internal workflow

Route -> rendered explanatory content.

```mermaid
flowchart LR
    Entry[Entry point / caller] --> Validate[Validation or policy]
    Validate --> Module[howitworks module]
    Module --> Outcome[Typed result / next layer]
```

## Public interfaces and integration

default export HowItWorksPage or page default. Consumers should use these boundaries rather than bypassing permissions, model integrity checks or consent.

## Dependencies and configuration

None. Do not commit secrets, patient photographs, model checkpoints or other sensitive artifacts.

## Verification

Run from repository root unless the command is an npm script (run npm scripts from `apps/web`):

```bash
npm run build
```

These are **recommended commands**, not a claim they were executed during this documentation change. Record commit SHA, test output and independent integration evidence before changing audit state.
