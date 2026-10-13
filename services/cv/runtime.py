"""Fail-closed model adapter used in the foundation, never mock predictions."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from packages.common.errors import ModelNotReady
from services.cv.ports import RawPrediction


class UnavailableModelRuntime:
    """This is an intentionally unavailable runtime, NOT a trained model."""

    @property
    def ready(self) -> bool:
        return False

    def predict(self, rgb_float32_batch: NDArray[np.float32]) -> RawPrediction:
        del rgb_float32_batch
        raise ModelNotReady()
