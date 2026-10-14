"""Image safety, ephemeral handling, metadata removal and quality gates."""

from __future__ import annotations

from io import BytesIO

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from apps.api.dermalens_api.config import Settings
from apps.api.dermalens_api.main import create_app
from services.cv.quality import InvalidImage, decode_image, inspect_image


def image_bytes(size: tuple[int, int] = (400, 400), fmt: str = "JPEG") -> bytes:
    with BytesIO() as output:
        Image.new("RGB", size, color=(130, 95, 80)).save(output, format=fmt)
        return output.getvalue()


class OneFace:
    def detect(self, rgb: np.ndarray) -> list[tuple[int, int, int, int]]:
        return [(70, 70, 180, 180)]


class TwoFaces:
    def detect(self, rgb: np.ndarray) -> list[tuple[int, int, int, int]]:
        return [(10, 10, 110, 110), (200, 200, 100, 100)]


class NoFaces:
    def detect(self, rgb: np.ndarray) -> list[tuple[int, int, int, int]]:
        return []


def test_valid_image_decode_and_baseline_quality() -> None:
    raw = image_bytes()
    decoded = decode_image(raw)
    assert decoded.shape == (400, 400, 3)
    assert decoded.dtype == np.uint8
    assert inspect_image(raw, OneFace()).accepted
    assert inspect_image(raw, NoFaces()).reasons == ("NO_FACE_DETECTED",)
    assert inspect_image(raw, TwoFaces()).reasons == ("MULTIPLE_FACES_DETECTED",)


@pytest.mark.parametrize("raw", [b"", b"invalid image bytes", image_bytes((10, 10))])
def test_invalid_bytes_rejected(raw: bytes) -> None:
    with pytest.raises(InvalidImage):
        decode_image(raw)


def test_animated_or_oversized_images_are_rejected() -> None:
    with BytesIO() as buffer:
        a = Image.new("RGB", (300, 300))
        b = Image.new("RGB", (300, 300))
        a.save(buffer, format="GIF", save_all=True, append_images=[b], duration=90)
        raw = buffer.getvalue()
    with pytest.raises(InvalidImage):
        decode_image(raw)
    with pytest.raises(InvalidImage):
        decode_image(b"\x00" * (8 * 1024 * 1024 + 1))


def test_quality_route_is_disabled_by_default() -> None:
    client = TestClient(create_app(Settings(env="test")), raise_server_exceptions=False)
    with client:
        response = client.post(
            "/api/v1/images/check", content=image_bytes(), headers={"Content-Type": "image/jpeg"}
        )
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "IMAGE_CHECK_UNAVAILABLE"


def test_quality_route_no_fake_predictions(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.cv.quality.HaarFaceDetector", OneFace)
    client = TestClient(
        create_app(Settings(env="test", enable_image_quality_checks=True)),
        raise_server_exceptions=False,
    )
    with client:
        response = client.post(
            "/api/v1/images/check", content=image_bytes(), headers={"Content-Type": "image/jpeg"}
        )
        assert response.status_code == 200
        report = response.json()
        assert report["accepted"] is True
        assert report["face_count"] == 1
        assert report["medical_analysis_available"] is False
        assert not any(key in report for key in ("prediction", "skin_cancer", "probabilities"))
        unsupported = client.post(
            "/api/v1/images/check", content=b"bad", headers={"Content-Type": "text/plain"}
        )
        assert unsupported.status_code == 415
        corrupt = client.post(
            "/api/v1/images/check", content=b"bad", headers={"Content-Type": "image/png"}
        )
        assert corrupt.status_code == 422
        huge = client.post(
            "/api/v1/images/check",
            content=b"x",
            headers={"Content-Type": "image/png", "Content-Length": "9000000"},
        )
        assert huge.status_code == 413
