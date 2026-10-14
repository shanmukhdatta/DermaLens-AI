"""Validate offline training-candidate manifests; unverified user feedback is excluded."""

from __future__ import annotations

from typing import Any

from services.cv.artifacts import EXPECTED_CATEGORIES

ALLOWED_KEYS = frozenset(
    {
        "sample_sha256",
        "subject_group",
        "verified_category",
        "review_state",
        "review_evidence_sha256",
        "consent_scope",
        "rights_verified",
        "label_source",
    }
)


def _sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_training_manifest(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Review manifest shape; evidence authenticity requires external verification.

    This never accesses or exports images. A valid manifest is not permission
    to train until the corresponding consent, label provenance and rights are audited.
    """
    if not records:
        raise ValueError("No curated examples")
    samples: set[str] = set()
    subjects: set[str] = set()
    for row in records:
        if set(row) != ALLOWED_KEYS:
            raise ValueError("Curation manifest has missing or forbidden fields")
        if (
            row["review_state"] != "validated"
            or row["consent_scope"] != "research_training"
            or row["rights_verified"] is not True
            or row["label_source"] not in {"clinician_verified", "researcher_verified"}
        ):
            raise ValueError("Unverified feedback or missing permission cannot enter training")
        if not _sha(row["sample_sha256"]) or not _sha(row["review_evidence_sha256"]):
            raise ValueError("Missing SHA256 image/evidence fingerprint")
        category = row["verified_category"]
        if (
            not isinstance(category, str)
            or " ".join(category.replace("_", " ").strip().lower().split())
            not in EXPECTED_CATEGORIES
        ):
            raise ValueError("Unsupported verified class")
        group = row["subject_group"]
        if not isinstance(group, str) or not group or len(group) > 128:
            raise ValueError("Invalid private subject group token")
        if row["sample_sha256"] in samples:
            raise ValueError("Duplicated curated sample")
        samples.add(row["sample_sha256"])
        subjects.add(group)
    return {
        "state": "manifest_structure_checked_external_approval_required",
        "validated_rows": len(records),
        "subject_groups": len(subjects),
        "image_bytes_included": False,
        "clinical_authorization": False,
    }
