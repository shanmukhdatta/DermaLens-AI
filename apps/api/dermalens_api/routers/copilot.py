"""Authenticated docs-only chatbot; no medical advice or diagnosis endpoints."""

from __future__ import annotations

import re
from typing import Annotated, Protocol

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, Field

from apps.api.dermalens_api.dependencies import require_verified_actor
from packages.common.errors import PUBLIC_MESSAGES, DomainError, ErrorCode
from packages.security.identity import Principal
from services.rag.grok import GrokProviderError
from services.rag.index import DocChunk, DocumentationIndex

router = APIRouter(prefix="/copilot", tags=["Documentation assistant"])

PERSONAL_MEDICAL = re.compile(
    r"\b(my skin|my face|i have a rash|what medicine|how to cure|treat my|diagnose me|"
    r"what disease do i have|which cream should i use)\b",
    re.IGNORECASE,
)


class DocsQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=4, max_length=300)


class AnswerProvider(Protocol):
    async def generate(self, question: str, excerpts: list[DocChunk]) -> str: ...


def get_docs_index(request: Request) -> DocumentationIndex:
    return request.app.state.docs_index  # type: ignore[no-any-return]


def get_docs_provider(request: Request) -> AnswerProvider:
    return request.app.state.docs_provider  # type: ignore[no-any-return]


@router.post("/query")
async def ask_project_docs(
    payload: DocsQuestion,
    actor: Annotated[Principal, Depends(require_verified_actor)],
    index: Annotated[DocumentationIndex, Depends(get_docs_index)],
    provider: Annotated[AnswerProvider, Depends(get_docs_provider)],
) -> dict[str, object]:
    del actor
    question = payload.question.strip()
    if PERSONAL_MEDICAL.search(question):
        return {
            "answer": (
                "This assistant only discusses DermaLens software, not personal skin concerns. "
                "Please speak with a qualified healthcare professional for medical questions."
            ),
            "sources": [],
        }
    matches = index.search(question)
    if not matches:
        return {
            "answer": (
                "I could not find relevant information in the approved project documentation."
            ),
            "sources": [],
        }
    try:
        answer = await provider.generate(question, matches)
    except GrokProviderError as exc:
        raise DomainError(
            ErrorCode.RAG_UNAVAILABLE, PUBLIC_MESSAGES[ErrorCode.RAG_UNAVAILABLE], 503
        ) from exc
    return {
        "answer": answer,
        "sources": [{"path": item.source, "heading": item.heading} for item in matches],
    }
