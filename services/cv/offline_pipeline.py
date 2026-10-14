"""Offline-only image-to-model research pipeline, with a hard safety abstention gate.

No FastAPI endpoint imports this module. The original research full-frame RGB
preprocessing is preserved rather than feeding arbitrary face crops to the model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from io import BytesIO
from typing import Any

import numpy as np
from PIL import Image

from services.cv.artifacts import preprocess_compatible
from services.cv.ports import ModelRuntime, RawPrediction
from services.cv.quality import InvalidImage, QualityReport, inspect_image
from services.learning.calibration import ResearchCalibration, abstaining_decision

PIPELINE_VERSION = "research-offline-v1"


@dataclass(frozen=True)
class ResearchOutcome:
    status: str
    reason: str
    model_id: str | None
    model_version: str | None
    pipeline_version: str
    quality: dict[str, object] | None
    decision: dict[str, Any]
    raw_research_probabilities: tuple[float, ...] | None

    def payload(self) -> dict[str, Any]:
        return asdict(self)


def analyze_offline(
    image_bytes: bytes,
    runtime: ModelRuntime,
    *,
    detector: object | None = None,
    calibration: ResearchCalibration | None = None,
    include_private_research_scores: bool = False,
) -> ResearchOutcome:
    """Return abstention unless real model and independent approved policy are available.

    Raw model scores may be exported only by a caller executing this function
    offline with include_private_research_scores=True; they must not be exposed
    by an API or persisted in user history.
    """
    if not runtime.ready:
        return ResearchOutcome(
            "unavailable", "MODEL_NOT_READY", None, None, PIPELINE_VERSION, None,
            {"status": "abstained", "reason": "MODEL_NOT_READY", "medical_diagnosis": False},
            None,
        )
    try:
        report: QualityReport = inspect_image(image_bytes, detector=detector)
    except InvalidImage:
        return ResearchOutcome(
            "rejected", "INVALID_IMAGE", None, None, PIPELINE_VERSION, None,
            {"status": "abstained", "reason": "INVALID_IMAGE", "medical_diagnosis": False},
            None,
        )
    if not report.accepted:
        return ResearchOutcome(
            "rejected", report.reasons[0], None, None, PIPELINE_VERSION,
            report.public_payload(),
            {"status": "abstained", "reason": "IMAGE_QUALITY_GATE", "medical_diagnosis": False},
            None,
        )
    # This preserves the exact research preprocessing; face alignment is a
    # separate, not-yet-approved experiment and must not alter this input.
    with Image.open(BytesIO(image_bytes)) as image:
        original = preprocess_compatible(image)
    prediction: RawPrediction = runtime.predict(original)
    valid = (
        len(prediction.probabilities) == 6
        and len(prediction.ordered_labels) == 6
        and len(set(prediction.ordered_labels)) == 6
        and all(np.isfinite(v) and 0 <= v <= 1 for v in prediction.probabilities)
        and np.isclose(sum(prediction.probabilities), 1.0, atol=1e-3)
    )
    if not valid:
        raise ValueError("Research runtime violated the declared six-class output contract")
    decision = abstaining_decision(
        prediction.probabilities, prediction.model_version, calibration,
        offline_research_mode=False,
    )
    return ResearchOutcome(
        "abstained", "POLICY_NOT_VALIDATED", prediction.model_id,
        prediction.model_version, PIPELINE_VERSION, report.public_payload(),
        decision,
        prediction.probabilities if include_private_research_scores else None,
    )
