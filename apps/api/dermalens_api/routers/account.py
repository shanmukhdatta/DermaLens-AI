"""Phase 3 owner-scoped account and consent endpoints; no unverified medical history."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, ConfigDict, StrictBool
from sqlalchemy.orm import Session

from apps.api.dermalens_api.dependencies import require_verified_actor
from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal
from services.persistence.repository import (
    change_history_consent,
    erase_account,
    find_account,
    history_consent,
    owned_history,
)

router = APIRouter(prefix="/account", tags=["Account"])


class ConsentChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: StrictBool


def database_session(request: Request) -> Iterator[Session]:
    factory = getattr(request.app.state, "db_session_factory", None)
    if factory is None:
        raise DomainError(ErrorCode.INTERNAL_ERROR, PUBLIC_MESSAGES[ErrorCode.INTERNAL_ERROR], 503)
    with factory() as session:
        yield session


@router.get("")
def account_status(
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, bool]:
    account = find_account(session, actor)
    return {"history_enabled": history_consent(session, account)}


@router.put("/history-consent")
def update_history_consent(
    payload: ConsentChange,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, bool]:
    return {"history_enabled": change_history_consent(session, actor, payload.enabled)}


@router.get("/analyses")
def list_history(
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, object]:
    records = owned_history(session, actor)
    return {
        "items": [
            {
                "id": record.id,
                "status": record.status,
                "model_version": record.model_version,
                "pipeline_version": record.pipeline_version,
                "created_at": record.created_at.isoformat(),
            }
            for record in records
        ]
    }


@router.get("/export")
def export_data(
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> dict[str, object]:
    account = find_account(session, actor)
    items = owned_history(session, actor)
    return {
        "history_enabled": history_consent(session, account),
        "analyses": [
            {
                "id": item.id,
                "created_at": item.created_at.isoformat(),
                "model_version": item.model_version,
                "status": item.status,
            }
            for item in items
        ],
    }


@router.delete("", status_code=204)
def delete_account(
    actor: Annotated[Principal, Depends(require_verified_actor)],
    session: Annotated[Session, Depends(database_session)],
) -> Response:
    erase_account(session, actor)
    return Response(status_code=204)
