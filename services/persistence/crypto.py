"""Authenticated encryption for owner-scoped research analysis metadata.

Keys are external deployment secrets. Never send key material to the browser
or log ciphertext, decrypted predictions or user identifiers.
"""

from __future__ import annotations

import json
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


def encrypt_result(payload: dict[str, Any], key: str) -> bytes:
    """Encrypt a small bounded JSON payload before database persistence."""
    raw = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(raw) > 16_384:
        raise ValueError("Result metadata exceeds safe persistence limit")
    return Fernet(key.encode("ascii")).encrypt(raw)


def decrypt_result(ciphertext: bytes, key: str) -> dict[str, Any]:
    """Decrypt and authenticate; never treat corrupted rows as valid predictions."""
    try:
        raw = Fernet(key.encode("ascii")).decrypt(ciphertext)
        result = json.loads(raw)
    except (InvalidToken, ValueError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Encrypted research result is invalid") from exc
    if not isinstance(result, dict):
        raise ValueError("Encrypted research result must be an object")
    return result
