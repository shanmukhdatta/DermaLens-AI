"""Non-serving research face geometry to assess ROI and landmark alignment.

The deployed Keras input MUST remain the original full frame until held-out
model comparisons establish that a transformation is appropriate.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class FaceGeometry:
    box: tuple[int, int, int, int]
    left_eye: tuple[float, float] | None
    right_eye: tuple[float, float] | None
    rotation_degrees: float | None
    usable_landmarks: bool


def estimate_eye_alignment(
    rgb: np.ndarray, box: tuple[int, int, int, int],
    *, eye_detector: object | None = None,
) -> FaceGeometry:
    """Estimate head roll only; no inferred disease, color changes or silent crop."""
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise ValueError("Expected RGB uint8 image")
    x, y, width, height = box
    if min(x, y) < 0 or min(width, height) < 80:
        raise ValueError("Invalid face region")
    image_height, image_width = rgb.shape[:2]
    if x + width > image_width or y + height > image_height:
        raise ValueError("Face region outside image")
    gray = cv2.cvtColor(rgb[y : y + height // 2, x : x + width], cv2.COLOR_RGB2GRAY)
    if eye_detector is None:
        path = getattr(cv2, "data").haarcascades + "haarcascade_eye.xml"
        eye_detector = cv2.CascadeClassifier(path)
        if eye_detector.empty():
            raise RuntimeError("Eye landmark artifact unavailable")
    candidates = eye_detector.detectMultiScale(  # type: ignore[attr-defined]
        gray, scaleFactor=1.1, minNeighbors=5
    )
    eye_regions = sorted(candidates, key=lambda b: int(b[2] * b[3]), reverse=True)
    if len(eye_regions) < 2:
        return FaceGeometry(box, None, None, None, False)
    first, second = sorted(eye_regions[:2], key=lambda b: int(b[0]))
    left = (float(x + first[0] + first[2] / 2), float(y + first[1] + first[3] / 2))
    right = (float(x + second[0] + second[2] / 2), float(y + second[1] + second[3] / 2))
    dx = right[0] - left[0]
    dy = right[1] - left[1]
    if dx < max(20.0, width * 0.16):
        return FaceGeometry(box, left, right, None, False)
    angle = float(np.degrees(np.arctan2(dy, dx)))
    return FaceGeometry(box, left, right, round(angle, 2), abs(angle) <= 35)


def proposed_face_crop(
    rgb: np.ndarray, geometry: FaceGeometry, *, margin: float = 0.12
) -> np.ndarray:
    """Offline candidate ROI, never fed to the deployed research model by default."""
    if not 0 <= margin <= 0.35:
        raise ValueError("Unsupported ROI margin")
    x, y, w, h = geometry.box
    height, width = rgb.shape[:2]
    pad_x = int(round(w * margin))
    pad_y = int(round(h * margin))
    x0 = max(x - pad_x, 0)
    y0 = max(y - pad_y, 0)
    x1 = min(x + w + pad_x, width)
    y1 = min(y + h + pad_y, height)
    if x1 <= x0 or y1 <= y0:
        raise ValueError("Invalid proposed crop bounds")
    return np.asarray(rgb[y0:y1, x0:x1], dtype=np.uint8).copy()
