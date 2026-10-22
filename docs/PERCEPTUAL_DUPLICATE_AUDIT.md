# Independent near-duplicate audit (dHash + pHash)

`scripts/audit_dataset.py` uses two **complementary** 64-bit perceptual image hashes:

- dHash: local luminance-gradient comparisons, canonicalized across the eight rotations/reflections.
- pHash: median-thresholded 8×8 low-frequency DCT coefficients after 32×32 grayscale resizing, also canonicalized over eight orientations.
- Exact SHA-256 detects byte-for-byte duplicates even if perceptual hashing fails.

Each hash separately checks approximate matches across **different train/calibration/validation/test splits**. For Hamming distance ≤7, exact candidate generation uses eight 8-bit buckets; any match within seven differing bits must share at least one chunk. A match from **either** hash generates a human-review candidate. `possible_phash_cross_split_pairs` counts matches from pHash; `possible_near_cross_split_pairs` is the **union**, avoiding double-counting between methods. The report returns bounded nonreversible pair tokens rather than patient names or original image paths.

This process is not person recognition and does not establish independence. A hash can confuse unrelated patterns or miss crop/overlay transformations. No patient identifiers implies the test population is **not patient independent**, even when hashes show no matches. An operator must independently investigate candidate pairs under approved access controls. Outputs are **not clinical validation**.

Run with previously acquired, permitted images:

```bash
python scripts/audit_dataset.py --manifest PRIVATE_MANIFEST.csv --root /private/dataset \
  --output /private/audit.json --threshold 5
```

The audit caps review pairs to bound memory; huge repeated-picture datasets are refused rather than silently declared clean. Continue to assess legal rights, independently assigned labels, and patient-level grouping. No actual photos are stored in the report.
