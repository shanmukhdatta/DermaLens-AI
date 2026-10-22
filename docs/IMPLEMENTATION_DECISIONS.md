# DermaLens AI — Implementation decisions, 2026-10-22

These reinforce existing ADRs; they do not override them.

1. **Public medical inference remains disabled.** No model checkpoint, independently verified real-world evaluation or approved calibrated abstention policy is available. Do not present image quality as a diagnosis.
2. **Reuse existing monorepo modules.** Do not create a duplicate FastAPI/Next.js application or overwrite research training provenance.
3. **Visual refresh is neutral to model availability.** Warm white `#FAF9F6`, terracotta `#D97757` and dark action color `#9F452F` replace green brand accents. Darker action shade is used for body-size text contrast against white; alerts retain semantic success/warning/error distinctions.
4. **Accessible navigation is real functionality.** Skip-to-content and `aria-current` route cues; keyboard-focus and reduced-motion styling retained.
5. **Requirements have independent state.** Module existence is not equivalent to build passing, clinical utility, privacy approval or deployed workflow acceptance.
6. **Local/CI checks remain mandatory.** No heavy clinical training is triggered by this UI/documentation commit.
