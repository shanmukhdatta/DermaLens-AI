"""Feedback contracts only; no storage or learning in Phase 1."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class ReviewState(StrEnum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VALIDATED = "validated"
    REJECTED = "rejected"


class FeedbackRating(StrEnum):
    CORRECT = "correct"
    INCORRECT = "incorrect"
    UNSURE = "unsure"


@dataclass(frozen=True)
class FeedbackSubmission:
    analysis_id: UUID
    owner_id: UUID
    rating: FeedbackRating
    proposed_category: str | None


class FeedbackRepository(Protocol):
    async def record_unverified(self, feedback: FeedbackSubmission) -> UUID: ...
