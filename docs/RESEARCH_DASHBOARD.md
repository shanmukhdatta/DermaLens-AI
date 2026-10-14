# Private, browser-local research report viewer

`/research` accepts an **aggregate** JSON output from the existing `scripts.evaluate_predictions` CLI. It validates the source as a research-only report with `clinical_use_validated=false`, six trained classes, finite metrics, consistent test counts and bounded warnings. It renders aggregate test sample count, subject groups, accuracy, macro-F1, 10-bin exploratory calibration error and per-class support/precision/recall/F1.

The file is processed with the browser's local File API; there are no upload requests or hidden patient identifiers, and nothing is persisted across refresh. Malformed, large and unsupported reports are rejected. The dashboard itself does not verify dataset rights, quality of labels, real-model parity, or clinical applicability. Never treat artificial CI fixture scores as true model performance. Per-image predictions, photographs, medical identifiers and raw clinical data must not be opened in this viewer.
