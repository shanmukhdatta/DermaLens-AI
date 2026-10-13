"""Consent labels describe future service contracts, not active persistence."""
from enum import StrEnum


class ConsentMode(StrEnum):
    EPHEMERAL = "ephemeral"
    HISTORY_METADATA = "history_metadata"
