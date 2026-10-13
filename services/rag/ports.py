"""Provider-neutral, citation-aware document assistant contracts."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class DocumentChunk:
    content: str
    source_path: str
    heading: str
    chunk_id: str
    document_version: str


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    sources: tuple[DocumentChunk, ...]
    grounded: bool


class DocumentIndex(Protocol):
    async def search(self, question: str, *, limit: int) -> Sequence[DocumentChunk]: ...


class LLMProvider(Protocol):
    async def generate(self, question: str, context: Sequence[DocumentChunk]) -> str: ...


class RAGAssistant(Protocol):
    async def answer(self, question: str) -> GroundedAnswer: ...
