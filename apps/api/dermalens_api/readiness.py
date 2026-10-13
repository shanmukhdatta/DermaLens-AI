"""Explicit capability gates. Optional dependencies are never presumed healthy."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from services.cv.ports import ModelRuntime


@dataclass(frozen=True)
class ReadinessGates:
    """Dependency-injected checks; no storage, network calls or model loading in Phase 2."""

    model_runtime: ModelRuntime
    policy_validated: bool = False
    required_checks: tuple[Callable[[], bool], ...] = ()

    def ready(self) -> bool:
        """Fail closed if model, safety policy or any configured required probe fails."""
        try:
            # Evaluate each gate explicitly, even if one is already unavailable.
            model_ok = self.model_runtime.ready
            checks_ok = all(check() for check in self.required_checks)
            return bool(model_ok and self.policy_validated and checks_ok)
        except Exception:
            return False
