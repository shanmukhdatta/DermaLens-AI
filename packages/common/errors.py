"""Stable domain error codes; never include exception internals in HTTP errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class ErrorCode(StrEnum):
    """Public machine-readable codes. Error messages are fixed at the HTTP edge."""

    MODEL_NOT_READY = "MODEL_NOT_READY"
    NOT_AUTHORIZED = "NOT_AUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    INVALID_REQUEST = "INVALID_REQUEST"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    RAG_UNAVAILABLE = "RAG_UNAVAILABLE"
    INFERENCE_FAILED = "INFERENCE_FAILED"
    INVALID_IMAGE = "INVALID_IMAGE"
    IMAGE_TOO_LARGE = "IMAGE_TOO_LARGE"
    IMAGE_CHECK_UNAVAILABLE = "IMAGE_CHECK_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


PUBLIC_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.MODEL_NOT_READY: "Model inference is not available in this build.",
    ErrorCode.NOT_AUTHORIZED: "Authentication is required or unavailable.",
    ErrorCode.NOT_FOUND: "Resource not found.",
    ErrorCode.INVALID_REQUEST: "Request validation failed.",
    ErrorCode.METHOD_NOT_ALLOWED: "Method not allowed.",
    ErrorCode.RAG_UNAVAILABLE: "Documentation assistant is unavailable.",
    ErrorCode.INFERENCE_FAILED: "Inference is unavailable.",
    ErrorCode.INVALID_IMAGE: "The image could not be accepted.",
    ErrorCode.IMAGE_TOO_LARGE: "The uploaded image is too large.",
    ErrorCode.IMAGE_CHECK_UNAVAILABLE: "Image suitability checks are not available.",
    ErrorCode.INTERNAL_ERROR: "An internal error occurred.",
}


def safe_error_payload(code: ErrorCode, request_id: str) -> dict[str, object]:
    """Fixed-message response with server-validated correlation identifier."""
    return {
        "error": {"code": code.value, "message": PUBLIC_MESSAGES[code]},
        "request_id": request_id,
    }


@dataclass(eq=False)
class DomainError(Exception):
    code: ErrorCode
    message: str
    status_code: int
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def as_payload(self) -> dict[str, object]:
        """Legacy in-process representation; HTTP MUST use safe_error_payload."""
        return {
            "error": {"code": self.code.value, "message": self.message},
            "request_id": self.request_id,
        }


class ModelNotReady(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code=ErrorCode.MODEL_NOT_READY,
            message=PUBLIC_MESSAGES[ErrorCode.MODEL_NOT_READY],
            status_code=503,
        )
