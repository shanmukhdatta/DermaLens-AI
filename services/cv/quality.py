"""Ephemeral image quality signals and single-face gate; never diagnostic inference."""

from __future__ import annotations

import io
import warnings
from dataclasses import asdict, dataclass

import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MIN_SIDE = 224
MAX_SIDE = 4096
ALLOW_FORMATS = {"JPEG", "PNG", "WEBP"}


class InvalidImage(ValueError):
    """Invalid or unsupported image; never return the uploaded bytes in errors."""


@dataclass(frozen=True)
class QualityReport:
    accepted: bool
    reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    width: int | None
    height: int | None
    face_count: int | None
    blur_signal: float | None
    brightness_signal: float | None

    def public_payload(self) -> dict[str, object]:
        return asdict(self)


class HaarFaceDetector:
    """Replaceable baseline detector, not a validated lesion/skin detector."""

    def __init__(self) -> None:
        path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._cascade = cv2.CascadeClassifier(path)
        if self._cascade.empty():
            raise RuntimeError("Face detector artifact unavailable")

    def detect(self, rgb: np.ndarray) -> list[tuple[int, int, int, int]]:
        # Downscale only for detection; do not modify or persist the uploaded image.
        width = rgb.shape[1]
        scale = min(1.0, 720.0 / float(width))
        smaller = cv2.resize(rgb, (0, 0), fx=scale, fy=scale) if scale < 1 else rgb
        gray = cv2.cvtColor(smaller, cv2.COLOR_RGB2GRAY)
        boxes = self._cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        return [
            (int(x / scale), int(y / scale), int(w / scale), int(h / scale)) for x, y, w, h in boxes
        ]


def decode_image(payload: bytes) -> np.ndarray:
    if not payload or len(payload) > MAX_IMAGE_BYTES:
        raise InvalidImage("INVALID_IMAGE_SIZE")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(payload)) as uploaded:
                if uploaded.format not in ALLOW_FORMATS:
                    raise InvalidImage("UNSUPPORTED_FORMAT")
                if getattr(uploaded, "n_frames", 1) != 1:
                    raise InvalidImage("ANIMATED_IMAGE")
                w, h = uploaded.size
                if min(w, h) < MIN_SIDE or max(w, h) > MAX_SIDE:
                    raise InvalidImage("IMAGE_DIMENSIONS_UNSUPPORTED")
                uploaded.load()
                normalized = ImageOps.exif_transpose(uploaded)
                rgb = normalized.convert("RGB")
                result = np.asarray(rgb, dtype=np.uint8).copy()
        return result
    except (
        OSError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise InvalidImage("IMAGE_DECODE_FAILED") from exc


def inspect_image(payload: bytes, detector: object | None = None) -> QualityReport:
    rgb = decode_image(payload)
    height, width = rgb.shape[:2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    # Uncalibrated diagnostic signals. Threshold warnings are not medical claims.
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    warnings_list: list[str] = []
    if blur < 70:
        warnings_list.append("POSSIBLY_BLURRY")
    if brightness < 45:
        warnings_list.append("POSSIBLY_DARK")
    if brightness > 225:
        warnings_list.append("POSSIBLY_OVEREXPOSED")
    detector_instance = detector if detector is not None else HaarFaceDetector()
    boxes = detector_instance.detect(rgb)  # type: ignore[attr-defined]
    reasons: list[str] = []
    if not boxes:
        reasons.append("NO_FACE_DETECTED")
    elif len(boxes) != 1:
        reasons.append("MULTIPLE_FACES_DETECTED")
    else:
        _, _, face_width, face_height = boxes[0]
        if min(face_width, face_height) < 80:
            reasons.append("FACE_TOO_SMALL")
    return QualityReport(
        accepted=not reasons,
        reasons=tuple(reasons),
        warnings=tuple(warnings_list),
        width=width,
        height=height,
        face_count=len(boxes),
        blur_signal=round(blur, 2),
        brightness_signal=round(brightness, 2),
    )
