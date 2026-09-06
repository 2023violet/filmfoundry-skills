"""Provider-neutral compilation of v2 Prompt Markdown."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import parse_prompt_metadata, validate_prompt_markdown


class PromptCompilationError(ValueError):
    """Raised when Prompt Markdown cannot be compiled."""


def compile_prompt(prompt_path: str | Path, provider: str) -> str:
    """Compile canonical prompt metadata into a deterministic provider payload.

    Provider clients remain outside FilmFoundry. The payload is intentionally
    plain text and contains the canonical facts in a stable order so adapters
    can translate it without mutating the source Markdown.
    """
    path = Path(prompt_path)
    text = path.read_text(encoding="utf-8")
    errors = validate_prompt_markdown(text)
    if errors:
        raise PromptCompilationError("; ".join(errors))
    metadata: dict[str, Any] = parse_prompt_metadata(text)
    lines = [
        "# FilmFoundry provider payload",
        f"provider: {provider}",
        "contract: prompt.v2",
        f"prompt_id: {metadata['prompt_id']}",
        f"prompt_type: {metadata['prompt_type']}",
        f"production_unit: {metadata['production_unit']}",
    ]
    ordered = (
        "visual_fact", "output_profile", "start_state", "end_state", "subjects",
        "dominant_action", "camera", "continuity_locks", "references", "forbidden", "acceptance",
    )
    for field in ordered:
        if field not in metadata:
            continue
        value = metadata[field]
        lines.append(f"\n[{field}]")
        if isinstance(value, (dict, list)):
            lines.append(json.dumps(value, ensure_ascii=False, sort_keys=True))
        else:
            lines.append(str(value))
    return "\n".join(lines) + "\n"


__all__ = ["PromptCompilationError", "compile_prompt"]
