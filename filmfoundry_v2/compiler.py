"""Provider-neutral compilation of v2 Prompt Markdown."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import parse_prompt_metadata, validate_prompt_markdown
from .adapters import CompiledPayload, hash_text


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


def compile_canonical(
    prompt_path: str | Path,
    provider: str,
    capability: dict[str, Any],
    visual_control_path: str | Path | None = None,
) -> CompiledPayload:
    """Return the structured, provider-neutral compilation contract."""
    path = Path(prompt_path)
    text = path.read_text(encoding="utf-8")
    errors = validate_prompt_markdown(text)
    if errors:
        raise PromptCompilationError("; ".join(errors))
    metadata = parse_prompt_metadata(text)
    visual_control: dict[str, Any] | None = None
    visual_control_hash: str | None = None
    visual_control_id: str | None = None
    if visual_control_path is not None:
        visual_path = Path(visual_control_path)
        visual_text = visual_path.read_text(encoding="utf-8")
        try:
            visual_control = json.loads(visual_text)
        except json.JSONDecodeError as exc:
            raise PromptCompilationError(f"visual control JSON: {exc}") from exc
        from .visual_control import validate_visual_control

        report = validate_visual_control(visual_control, source=str(visual_path))
        if not report.ok:
            raise PromptCompilationError("; ".join(issue.message for issue in report.errors))
        visual_control_hash = hash_text(visual_text)
        visual_control_id = str(visual_control["visual_control_id"])
    body = compile_prompt(path, provider)
    if visual_control is not None:
        # Keep the control sections deterministic so provider adapters can map
        # them without changing the authoring artifact.
        for field in (
            "visual_control_id", "character_references", "location_reference",
            "spatial_map", "scale_references", "physics_cues", "previsualization",
            "lens_result",
        ):
            if field in visual_control and visual_control[field] not in (None, [], {}):
                body += f"\n[{field}]\n{json.dumps(visual_control[field], ensure_ascii=False, sort_keys=True)}\n"
        body += "[visual_control_hash]\n" + str(visual_control_hash) + "\n"
    return CompiledPayload(
        provider=provider,
        route=str(capability.get("route", "UNSPECIFIED")),
        parameters=dict(capability.get("parameters", {})),
        reference_slots=tuple(str(item["slot"]) for item in metadata.get("references", [])),
        capability_snapshot_id=str(capability.get("snapshot_id", "UNVERIFIED")),
        body=body,
        input_hashes={
            "prompt": hash_text(text),
            **({"visual_control": visual_control_hash} if visual_control_hash else {}),
        },
        visual_control_id=visual_control_id,
        visual_control_hash=visual_control_hash,
    )


__all__ = ["PromptCompilationError", "compile_prompt", "compile_canonical"]
