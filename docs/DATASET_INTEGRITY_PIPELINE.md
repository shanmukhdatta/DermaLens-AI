# Research-data leakage audit (non-clinical)

`services/learning/leakage_audit.py` and `scripts/audit_dataset.py` implement bounded exact SHA256 matching, eight-orientation 64-bit dHash candidate detection, cross-split subject-group checks, path containment, and aggregate warning reports. A visual near-duplicate is a **review candidate**, not proof of a shared patient identity. Images remain on disk and are never uploaded.

Example schema for `manifest.csv`:

```csv
relative_path,split,label,source,subject_group
photos/001.png,train,Acne,real,pseudonym01
photos/002.png,calibration,Acne,real,pseudonym02
photos/003.png,test,Acne,real,pseudonym03
```

```bash
python -m scripts.audit_dataset --root /approved/research/images --manifest /approved/research/manifest.csv --output /private/review/leakage.json --threshold 5
```

CSV paths must be relative to the image root, and external source licenses and informed consent must be reviewed independently. The CLI returns exit code 1 for any caution flags; an empty warning list is **not** certification of patient-disjoint independence, clinical validity, unbiased labels or lawful data use.

Data sources for *research screening* (not automatically suitable six-class facial benchmarks):
- [Google SCIN data documentation](https://github.com/google-research-datasets/scin) — case-grouped donated images, dermatologist labels, SCIN-specific use license. Label and location filtering required.
- [ISIC challenge datasets](https://challenge.isic-archive.com/data/) — many dermoscopic / lesion crops, not interchangeable with facial clinical photography; per-challenge license and patient IDs vary.
- [Fitzpatrick17k](https://github.com/mattgroh/fitzpatrick17k) — broad clinical dermatology and skin-tone labels, noncommercial share-alike license; review original provenance and duplicates.

No model weights, case images or patient-identifying fields are bundled. Do not use synthetic images as independent clinical validation.
