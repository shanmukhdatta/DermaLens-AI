"""Compare original research inference against the application Keras adapter.

Parity of tensors, class order and scores is a software equivalence check,
NOT a medical accuracy, clinical safety or deployment certification.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from services.cv.ports import RawPrediction


def verify_prediction_parity(
    reference: dict[str, Any],
    prediction: RawPrediction,
    *,
    image_sha256: str,
    checkpoint_sha256: str,
    source_commit: str,
    atol: float = 1e-5,
) -> dict[str, object]:
    """Reject any mismatched source, image, checkpoint, label index or numeric output."""
    if not 0 < atol <= 1e-3 or not np.isfinite(atol):
        raise ValueError("Unsupported parity tolerance")
    required = {
        "image_sha256": image_sha256,
        "checkpoint_sha256": checkpoint_sha256,
        "source_commit": source_commit,
    }
    if any(reference.get(key) != value for key, value in required.items()):
        raise ValueError("The reference was not made with this exact source, image and model")
    if reference.get("ordered_labels") != list(prediction.ordered_labels):
        raise ValueError("The research and service model label indices differ")
    raw = reference.get("probabilities")
    if not isinstance(raw, list) or len(raw) != 6:
        raise ValueError("Reference scores must contain exactly six classes")
    try:
        expected = np.asarray(raw, dtype=np.float64)
        actual = np.asarray(prediction.probabilities, dtype=np.float64)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid model scores") from exc
    if (
        expected.shape != (6,)
        or actual.shape != (6,)
        or not np.isfinite(expected).all()
        or not np.isfinite(actual).all()
        or np.any(expected < 0)
        or np.any(actual < 0)
        or np.any(expected > 1)
        or np.any(actual > 1)
        or not np.isclose(expected.sum(), 1.0, atol=1e-4)
        or not np.isclose(actual.sum(), 1.0, atol=1e-4)
    ):
        raise ValueError("Malformed probability output")
    absolute_error = np.abs(expected - actual)
    maximum = float(np.max(absolute_error))
    if maximum > atol or int(np.argmax(expected)) != int(np.argmax(actual)):
        raise ValueError("Inference parity failed")
    return {
        "software_parity_verified": True,
        "max_absolute_error": maximum,
        "tolerance": atol,
        "source_commit": source_commit,
        "model_id": prediction.model_id,
        "model_version": prediction.model_version,
        "clinical_accuracy_verified": False,
        "clinical_deployment_approved": False,
    }
