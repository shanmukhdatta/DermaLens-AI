"""Stable interfaces; implementations arrive in Phases 4 and 9."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class RawPrediction:
    """Model probability outputs, not clinical confidence."""

    model_id: str
    model_version: str
    ordered_labels: tuple[str, ...]
    probabilities: tuple[float, ...]


@dataclass(frozen=True)
class CVOutcome:
    """No classifier state is inferred from the existence of these types."""

    status: Literal["completed", "abstained", "rejected", "failed"]
    reason_code: str | None
    prediction: RawPrediction | None


class ModelRuntime(Protocol):
    @property
    def ready(self) -> bool: ...

    def predict(self, rgb_float32_batch: NDArray[np.float32]) -> RawPrediction: ...


class CVPipeline(Protocol):
    def evaluate(self, image_bytes: bytes, model: ModelRuntime) -> CVOutcome: ...
