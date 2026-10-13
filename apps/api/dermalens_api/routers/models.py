"""Model metadata endpoint protected by a verified-actor dependency."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from apps.api.dermalens_api.dependencies import require_verified_actor

router = APIRouter(
    prefix="/models",
    tags=["Models"],
    dependencies=[Depends(require_verified_actor)],
)


@router.get("/current")
def current_model() -> dict[str, bool | str | None]:
    """No trusted registered model or label map exists in this build."""
    return {"ready": False, "model_id": None, "model_version": None}
