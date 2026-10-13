"""Validate Phase 0 architecture files, links, schemas, and Markdown fence integrity.

This validates structural contracts, not live inference or runtime services.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
API = ROOT / "packages/contracts/openapi.v1.json"
MODEL_SCHEMA = ROOT / "models/manifests/model-manifest.schema.json"

EXPECTED = [
    *[DOCS / f"{i:02d}_{name}.md" for i, name in enumerate(
        (
            "SYSTEM_ARCHITECTURE",
            "COMPUTER_VISION_PIPELINE",
            "MODEL_AND_RESEARCH",
            "BACKEND_ARCHITECTURE",
            "RAG_ASSISTANT",
            "FEEDBACK_AND_CONTINUAL_LEARNING",
            "MLOPS_AND_DEPLOYMENT",
            "API_AND_DATA_FLOW",
            "PRIVACY_AND_SAFETY",
        ), start=1
    )],
    DOCS / "PHASE_TRACKER.md",
    DOCS / "REPO_STRUCTURE.md",
    DOCS / "PHASE0_VALIDATION.md",
    DOCS / "PHASE1_HANDOFF.md",
    DOCS / "adr/README.md",
    *[DOCS / f"adr/{i:04d}-{name}.md" for i, name in enumerate(
        ("modular-monolith", "model-contract", "image-privacy",
         "docs-only-rag", "feedback-promotion", "stack"), start=1
    )],
    ROOT / "models/README.md",
    API,
    MODEL_SCHEMA,
]

LINK = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
FENCE = re.compile(r"^\s*```(.*)$")


def check_markdown(path: Path) -> list[str]:
    """Check every opening fence closes and all local links resolve."""
    problems = []
    current_fence = None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        fence = FENCE.match(line)
        if fence:
            lang = fence.group(1).strip()
            if current_fence is None:
                current_fence = (n, lang)
                if lang == "mermaid":
                    pass
            else:
                if lang:
                    problems.append(f"{path}:{n}: closing fence has a language")
                current_fence = None
            continue
        if current_fence:
            continue
        for link in LINK.findall(line):
            target = link.split("#", maxsplit=1)[0].strip()
            if not target or target.startswith(("#", "mailto:")):
                continue
            if urlparse(target).scheme or target.startswith("//"):
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
                problems.append(f"{path}:{n}: broken local link {link}")
    if current_fence:
        problems.append(f"{path}:{current_fence[0]}: unterminated code fence")
    return problems


def validate_all() -> list[str]:
    problems = [f"Missing file: {path}" for path in EXPECTED if not path.is_file()]
    if problems:
        return problems
    for path in [p for p in EXPECTED if p.suffix == ".md"]:
        problems.extend(check_markdown(path))
    try:
        schema = json.loads(MODEL_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["properties"]["input"]["properties"]["normalization"]["const"] == (
            "model_internal"
        )
        assert schema["properties"]["input"]["properties"]["shape"]["const"] == [
            None, 224, 224, 3
        ]
    except (ValueError, KeyError, AssertionError, TypeError) as error:
        problems.append(f"Model manifest schema: {error}")
    try:
        api = json.loads(API.read_text(encoding="utf-8"))
        validate(api)
        assert api["info"]["version"] == "1.0.0"
        for endpoint in (
            "/api/v1/analyses", "/api/v1/analyses/{analysis_id}",
            "/api/v1/analyses/{analysis_id}/feedback", "/api/v1/copilot/query",
            "/api/v1/models/current", "/api/v1/health", "/api/v1/readiness",
        ):
            assert endpoint in api["paths"], endpoint
    except (ValueError, KeyError, AssertionError, TypeError) as error:
        problems.append(f"OpenAPI contract: {error}")
    # Detect intentional placeholder file-type violations in the repo index during CI.
    return problems


if __name__ == "__main__":
    errors = validate_all()
    if errors:
        for item in errors:
            print("FAIL:", item)
        raise SystemExit(1)
    print("PASS: file inventory, relative links, Markdown fences, model JSON Schema, OpenAPI")
