"""Authenticated and moderated research feedback, never automatic training."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from apps.api.dermalens_api.dependencies import require_verified_actor
from apps.api.dermalens_api.routers.account import database_session
from packages.security.identity import Principal
from services.learning.feedback import delete_feedback, get_feedback, submit_feedback

router = APIRouter(prefix="/analyses", tags=["Research feedback"])


class FeedbackInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    choice: Literal["correct", "incorrect", "unsure", "quality_issue"]


def public_feedback(record: object) -> dict[str, str]:
    from services.persistence.models import FeedbackRecord

    if not isinstance(record, FeedbackRecord):
        raise TypeError("Expected stored feedback")
    return {
        "id": record.id,
        "choice": record.choice,
        "review_status": record.review_status,
    }


@router.post("/{analysis_id}/feedback", status_code=201)
def add_feedback(
    analysis_id: str,
    payload: FeedbackInput,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, str]:
    return public_feedback(submit_feedback(session, actor, analysis_id, payload.choice))


@router.get("/{analysis_id}/feedback")
def current_feedback(
    analysis_id: str,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, str]:
    return public_feedback(get_feedback(session, actor, analysis_id))


@router.delete("/{analysis_id}/feedback", status_code=204)
def remove_feedback(
    analysis_id: str,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> Response:
    delete_feedback(session, actor, analysis_id)
    return Response(status_code=204)
