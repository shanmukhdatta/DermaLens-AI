"""Stable error envelope aligned to the Phase 0 API contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class ErrorCode(StrEnum):
    """Public codes only. Never expose raw exception details to callers."""

    MODEL_NOT_READY = "MODEL_NOT_READY"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    RAG_UNAVAILABLE = "RAG_UNAVAILABLE"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass(eq=False)
class DomainError(Exception):
    code: ErrorCode
    message: str
    status_code: int
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def as_payload(self) -> dict[str, object]:
        return {
            "error": {"code": self.code.value, "message": self.message},
            "request_id": self.request_id,
        }


class ModelNotReady(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.MODEL_NOT_READY,
            message="Model inference is not available in this build.",
            status_code=503,
        )
