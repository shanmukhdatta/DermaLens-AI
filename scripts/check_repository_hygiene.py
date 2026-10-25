"""Fail CI for accidentally tracked local secrets or private artifacts.

The intentionally public .env.example templates remain allowed.
"""

from __future__ import annotations

import subprocess
from pathlib import PurePosixPath

BLOCKED_DIRS = frozenset(
    {
        "__pycache__",
        "node_modules",
        "uploads",
        "datasets",
        "data",
        "storage",
        "artifacts",
        "outputs",
    }
)
BLOCKED_SUFFIXES = frozenset(
    {
        ".keras",
        ".h5",
        ".hdf5",
        ".pt",
        ".pth",
        ".pem",
        ".key",
        ".ckpt",
        ".onnx",
        ".tflite",
        ".safetensors",
    }
)
BLOCKED_NAMES = frozenset(
    {"id_rsa", "id_ed25519", ".env", ".env.local", ".env.production", ".env.test"}
)


def forbidden_tracked_path(relative_path: str) -> bool:
    """Recognize sensitive file paths, not safe configuration examples."""
    path = PurePosixPath(relative_path)
    # The MIT-licensed research snapshot contains actual Python source under src/data/.
    # Permit only direct .py source files there, never photographs or private data.
    is_original_data_module = (
        path.parts[:4] == ("research", "legacy", "src", "data")
        and len(path.parts) == 5
        and path.suffix == ".py"
    )
    if any(part in BLOCKED_DIRS for part in path.parts[:-1]) and not is_original_data_module:
        return True
    name = path.name.lower()
    if name == ".env.example":
        return False
    if name in BLOCKED_NAMES or name.startswith(".env."):
        return True
    return path.suffix.lower() in BLOCKED_SUFFIXES


def main() -> int:
    files = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    ).stdout.decode("utf-8")
    blocked = [path for path in files.split(chr(0)) if path and forbidden_tracked_path(path)]
    if blocked:
        print("FAIL: committed sensitive paths:", *blocked, sep="\n  ")
        return 1
    print("PASS: no tracked local secrets/model artifacts/private data paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
