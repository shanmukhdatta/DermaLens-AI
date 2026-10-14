"""No-storage JPEG/PNG/WebP quality endpoint; never returns a medical prediction."""

from __future__ import annotations

from fastapi import APIRouter, Request

from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from services.cv.quality import MAX_IMAGE_BYTES, InvalidImage, inspect_image

router = APIRouter(prefix="/images", tags=["Image quality"])


@router.post("/check")
async def check_quality(request: Request) -> dict[str, object]:
    if not request.app.state.settings.enable_image_quality_checks:
        raise DomainError(
            ErrorCode.IMAGE_CHECK_UNAVAILABLE,
            PUBLIC_MESSAGES[ErrorCode.IMAGE_CHECK_UNAVAILABLE],
            503,
        )
    content_type = request.headers.get("content-type", "").split(";")[0].lower().strip()
    if content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise DomainError(ErrorCode.INVALID_IMAGE, PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE], 415)
    length = request.headers.get("content-length", "")
    if length.isascii() and length.isdecimal() and int(length) > MAX_IMAGE_BYTES:
        raise DomainError(
            ErrorCode.IMAGE_TOO_LARGE, PUBLIC_MESSAGES[ErrorCode.IMAGE_TOO_LARGE], 413
        )
    payload = bytearray()
    async for part in request.stream():
        if len(payload) + len(part) > MAX_IMAGE_BYTES:
            raise DomainError(
                ErrorCode.IMAGE_TOO_LARGE, PUBLIC_MESSAGES[ErrorCode.IMAGE_TOO_LARGE], 413
            )
        payload.extend(part)
    try:
        report = inspect_image(bytes(payload))
    except InvalidImage as exc:
        del exc
        raise DomainError(
            ErrorCode.INVALID_IMAGE, PUBLIC_MESSAGES[ErrorCode.INVALID_IMAGE], 422
        ) from None
    except RuntimeError:
        raise DomainError(
            ErrorCode.IMAGE_CHECK_UNAVAILABLE,
            PUBLIC_MESSAGES[ErrorCode.IMAGE_CHECK_UNAVAILABLE],
            503,
        ) from None
    return {
        **report.public_payload(),
        "medical_analysis_available": False,
        "notice": "Image checks do not diagnose or rule out skin conditions.",
    }
