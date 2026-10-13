# Private model integration boundary

**Phase 0:** no checkpoints, model registry entries or authoritative label map have been checked into GitHub. Schema at [manifests/model-manifest.schema.json](manifests/model-manifest.schema.json) is the forward contract, not proof of any trained model.

Phase 9 handoff: export trusted `*_final.keras` with matching `label_map.json` from the **same** training run; copy to private model store. SHA-256 via `sha256sum model.keras label_map.json` (Linux/Kaggle) or `Get-FileHash -Algorithm SHA256 <file>` (PowerShell). The manifest must contain **real, verified hashes**; do not paste placeholders into approved manifests. Never commit `.keras`/weights or private images. Pin tested TensorFlow/Keras/Python versions and allowlisted custom layers from the research repository. Ensure label indices 0–5 map to exactly one each of `Acne`, `Fungal Infection`, `Hyperpigmentation`, `Normal Skin`, `Skin Cancer`, `Vitiligo` in the **actual saved order**, with no duplicate names.

Read [research provenance](../docs/03_MODEL_AND_RESEARCH.md) and [privacy](../docs/09_PRIVACY_AND_SAFETY.md). Production inference will refuse startup/readiness on checksum mismatch or absent checkpoint. Development tests may use an explicit fake adapter under `tests/`, never labeled as real inference.
