"""Model metadata endpoint protected by a verified-actor dependency."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from apps.api.dermalens_api.dependencies import require_verified_actor

router = APIRouter(
    prefix="/models",
    tags=["Models"],
    dependencies=[Depends(require_verified_actor)],
)


@router.get("/current")
def current_model(request: Request) -> dict[str, bool | str | None]:
    """Research model identity is visible only to a verified actor."""
    runtime = request.app.state.model_runtime
    if not request.app.state.settings.enable_research_analyses or not runtime.ready:
        return {"ready": False, "model_id": None, "model_version": None}
    artifacts = getattr(runtime, "artifacts", None)
    return {
        "ready": False,  # no clinical clearance
        "model_id": getattr(artifacts, "model_id", None),
        "model_version": getattr(artifacts, "version", None),
    }
