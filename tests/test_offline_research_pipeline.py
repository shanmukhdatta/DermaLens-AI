"""Test only engineering control flow; fixture predictions are NOT real performance."""
from __future__ import annotations

from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from services.cv.face_geometry import FaceGeometry, estimate_eye_alignment, proposed_face_crop
from services.cv.offline_pipeline import analyze_offline
from services.cv.ports import RawPrediction
from services.cv.runtime import UnavailableModelRuntime


class FixtureDetector:
    def __init__(self, count: int = 1) -> None:
        self.count = count

    def detect(self, rgb: np.ndarray) -> list[tuple[int, int, int, int]]:
        return [(60 + i * 30, 60, 140, 150) for i in range(self.count)]


class FixtureRuntime:
    ready = True

    def predict(self, batch: np.ndarray) -> RawPrediction:
        assert batch.shape == (1, 224, 224, 3)
        assert batch.dtype == np.float32
        assert batch.min() >= 0 and batch.max() <= 255
        return RawPrediction(
            "fixture-not-a-model", "fixture", tuple(f"Research-{i}" for i in range(6)),
            (0.9, 0.02, 0.02, 0.02, 0.02, 0.02),
        )


def photo() -> bytes:
    with BytesIO() as output:
        Image.new("RGB", (400, 400), color=(110, 90, 140)).save(output, format="JPEG")
        return output.getvalue()


def test_offline_pipeline_always_abstains_without_approved_medical_policy() -> None:
    result = analyze_offline(photo(), FixtureRuntime(), detector=FixtureDetector())
    assert result.status == "abstained"
    assert result.model_version == "fixture"
    assert result.decision["medical_diagnosis"] is False
    assert result.raw_research_probabilities is None
    private = analyze_offline(
        photo(), FixtureRuntime(), detector=FixtureDetector(),
        include_private_research_scores=True,
    )
    assert len(private.raw_research_probabilities or ()) == 6


def test_missing_model_never_decodes_or_classifies() -> None:
    result = analyze_offline(b"bad", UnavailableModelRuntime())
    assert result.status == "unavailable"
    assert result.model_id is None
    assert result.raw_research_probabilities is None


def test_rejects_no_face_multiple_faces_and_corrupt_images() -> None:
    for count in (0, 2):
        rejected = analyze_offline(photo(), FixtureRuntime(), detector=FixtureDetector(count))
        assert rejected.status == "rejected"
        assert rejected.raw_research_probabilities is None
    assert analyze_offline(b"invalid", FixtureRuntime()).status == "rejected"


def test_face_geometry_is_research_only_and_clips_roi() -> None:
    rgb = np.zeros((300, 300, 3), dtype=np.uint8)
    class Eyes:
        def detectMultiScale(
            self, gray: np.ndarray, **kwargs: object
        ) -> list[tuple[int, int, int, int]]:
            del gray, kwargs
            return [(15, 10, 30, 25), (95, 12, 29, 26)]

    geom = estimate_eye_alignment(rgb, (20, 20, 180, 180), eye_detector=Eyes())
    assert geom.usable_landmarks
    assert geom.rotation_degrees is not None
    crop = proposed_face_crop(rgb, geom)
    assert 180 <= crop.shape[0] <= 300
    assert isinstance(geom, FaceGeometry)
    with pytest.raises(ValueError):
        estimate_eye_alignment(rgb, (-1, 0, 120, 120), eye_detector=Eyes())
    with pytest.raises(ValueError):
        proposed_face_crop(rgb, geom, margin=0.8)
