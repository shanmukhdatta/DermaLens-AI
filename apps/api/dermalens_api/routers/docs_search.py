"""Public, local-only documentation passage search; never asks a medical model.

This is citation-backed lookup, not semantic vector RAG or a chatbot.
Queries are never persisted or sent to external APIs.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query

from services.rag.index import DocumentationIndex

router = APIRouter(prefix="/docs", tags=["Project documentation"])


@lru_cache(maxsize=1)
def index() -> DocumentationIndex:
    return DocumentationIndex.from_repository(Path(__file__).resolve().parents[4])


@router.get("/search")
def search_documentation(
    q: Annotated[str, Query(min_length=4, max_length=180)],
) -> dict[str, object]:
    question = q.strip()
    if len(question) < 4:
        return {"status": "no_match", "matches": [], "notice": "Ask about project documentation."}
    results = index().search(question, limit=3)
    return {
        "status": "matches" if results else "no_match",
        "matches": [
            {
                "path": item.source.split("#", maxsplit=1)[0],
                "section": item.heading[:140],
                "excerpt": item.content[:650],
            }
            for item in results
        ],
        "notice": (
            "These are excerpts from public DermaLens project documentation, "
            "not medical advice or results from the skin classifier."
        ),
    }
