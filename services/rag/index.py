"""Allowlisted project-document retrieval; no user data, source code or model artifacts."""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ALLOWED_DOCS = (
    "README.md",
    "docs/01_SYSTEM_ARCHITECTURE.md",
    "docs/02_COMPUTER_VISION_PIPELINE.md",
    "docs/03_MODEL_AND_RESEARCH.md",
    "docs/04_BACKEND_ARCHITECTURE.md",
    "docs/05_RAG_ASSISTANT.md",
    "docs/06_FEEDBACK_AND_CONTINUAL_LEARNING.md",
    "docs/07_MLOPS_AND_DEPLOYMENT.md",
    "docs/08_API_AND_DATA_FLOW.md",
    "docs/09_PRIVACY_AND_SAFETY.md",
)
STOP_WORDS = frozenset(
    {"the", "and", "for", "that", "this", "with", "how", "what", "why",
     "where", "from", "which", "does", "are", "can", "our", "their", "into"}
)


def terms(text: str) -> Counter[str]:
    return Counter(
        word for word in re.findall(r"[a-z0-9_]{3,}", text.lower())
        if word not in STOP_WORDS
    )


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:90]


@dataclass(frozen=True)
class DocChunk:
    source: str
    heading: str
    content: str


class DocumentationIndex:
    """Deterministic local lexical baseline; replaceable by embeddings + pgvector."""

    def __init__(self, chunks: list[DocChunk]) -> None:
        if not chunks:
            raise ValueError("No allowlisted documents could be indexed")
        self.chunks = tuple(chunks)
        self.term_counts = tuple(terms(chunk.heading + " " + chunk.content) for chunk in chunks)
        self.document_frequency: Counter[str] = Counter()
        for counter in self.term_counts:
            self.document_frequency.update(counter.keys())

    @classmethod
    def from_repository(cls, root: Path) -> DocumentationIndex:
        chunks: list[DocChunk] = []
        safe_root = root.resolve()
        for relative in ALLOWED_DOCS:
            source = (safe_root / relative).resolve()
            if not source.is_relative_to(safe_root) or not source.is_file():
                raise ValueError("Required documentation file missing or outside repository")
            text = source.read_text(encoding="utf-8")
            if len(text) > 160_000:
                raise ValueError("Documentation exceeds ingestion limit")
            heading = "Introduction"
            lines: list[str] = []
            def flush() -> None:
                block = "\n".join(lines).strip()
                if block:
                    for start in range(0, len(block), 1100):
                        excerpt = block[start:start + 1100].strip()
                        if excerpt:
                            chunks.append(DocChunk(relative + "#" + slug(heading), heading, excerpt))
            for line in text.splitlines():
                if line.startswith(("# ", "## ", "### ")):
                    flush()
                    lines = []
                    heading = line.lstrip("# ").strip()
                else:
                    lines.append(line)
            flush()
        return cls(chunks)

    def search(self, question: str, limit: int = 3) -> list[DocChunk]:
        query = terms(question)
        if not query:
            return []
        ranked: list[tuple[float, int]] = []
        count = len(self.chunks)
        for i, counter in enumerate(self.term_counts):
            score = 0.0
            for word in query:
                if word in counter:
                    idf = math.log(1 + (count - self.document_frequency[word] + 0.5) /
                                   (self.document_frequency[word] + 0.5))
                    score += idf * min(counter[word], 4)
            if score > 0:
                ranked.append((score, i))
        ranked.sort(key=lambda entry: (-entry[0], entry[1]))
        return [self.chunks[index] for _, index in ranked[:max(0, min(limit, 5))]]
