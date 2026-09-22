"""Provider-neutral compilation of v3 Prompt Markdown."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from . import parse_prompt_metadata, validate_prompt_markdown
from .adapters import CompiledPayload, hash_text
from .handoff import build_provider_neutral_handoff
from .profiles import ProjectProfile, StyleProfile


class PromptCompilationError(ValueError):
    """Raised when Prompt Markdown cannot be compiled."""


def compile_prompt(
    prompt_path: str | Path,
    provider: str | None = None,
    *,
    project_profile: ProjectProfile | Mapping[str, Any] | None = None,
    style_profile: StyleProfile | Mapping[str, Any] | None = None,
    shot_spec: Mapping[str, Any] | None = None,
) -> str:
    """Compile Prompt Markdown into a deterministic Provider-neutral handoff.

    ``provider`` is retained as a deprecated compatibility argument for callers
    on the old CLI.  It is intentionally ignored: provider syntax belongs to an
    external adapter and never enters the Core handoff.
    """
    path = Path(prompt_path)
    text = path.read_text(encoding="utf-8")
    errors = validate_prompt_markdown(text)
    if errors:
        raise PromptCompilationError("; ".join(errors))
    metadata: dict[str, Any] = parse_prompt_metadata(text)
    return build_provider_neutral_handoff(
        metadata,
        project_profile=project_profile,
        style_profile=style_profile,
        shot_spec=shot_spec,
    ).to_markdown()


def compile_canonical(
    prompt_path: str | Path,
    provider: str | None = None,
    capability: dict[str, Any] | None = None,
    visual_control_path: str | Path | None = None,
    context_paths: Mapping[str, str | Path] | None = None,
    production_ledger_event_ids: tuple[str, ...] = (),
    requirement_report_path: str | Path | None = None,
    project_profile: ProjectProfile | Mapping[str, Any] | None = None,
    style_profile: StyleProfile | Mapping[str, Any] | None = None,
    shot_spec: Mapping[str, Any] | None = None,
) -> CompiledPayload:
    """Return the structured, Provider-neutral compilation contract.

    The legacy ``provider`` and ``capability`` parameters are accepted only to
    keep old integrations readable.  They no longer change the handoff body or
    authorize a provider call.
    """
    capability = capability or {}
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
    context_paths = dict(context_paths or {})
    context_sections: list[tuple[str, Any]] = []
    context_validators = {
        "script_analysis": ("script_analysis", "validate_script_analysis"),
        "look_bible": ("look_bible", "validate_look_bible"),
        "scene_topology": ("scene_topology", "validate_scene_topology"),
        "dependency_graph": ("dependency_graph", "validate_dependency_graph"),
    }
    input_hashes: dict[str, str] = {"prompt": hash_text(text)}
    for name in ("script_analysis", "look_bible", "scene_topology", "dependency_graph"):
        if name not in context_paths:
            continue
        context_path = Path(context_paths[name])
        context_text = context_path.read_text(encoding="utf-8")
        try:
            value = json.loads(context_text)
        except json.JSONDecodeError as exc:
            raise PromptCompilationError(f"{name} JSON: {exc}") from exc
        module_name, validator_name = context_validators[name]
        if name == "script_analysis":
            from .script_analysis import validate_script_analysis
            report = validate_script_analysis(value, source=str(context_path))
        elif name == "look_bible":
            from .look_bible import validate_look_bible
            report = validate_look_bible(value, source=str(context_path))
        elif name == "scene_topology":
            from .scene_topology import validate_scene_topology
            report = validate_scene_topology(value, source=str(context_path))
        else:
            from .dependency_graph import validate_dependency_graph
            report = validate_dependency_graph(value, source=str(context_path))
        if not report.ok:
            raise PromptCompilationError("; ".join(issue.message for issue in report.errors))
        context_sections.append((name, value))
        input_hashes[name] = hash_text(context_text)
    body = compile_prompt(
        path,
        project_profile=project_profile,
        style_profile=style_profile,
        shot_spec=shot_spec,
    )
    for name, value in context_sections:
        body += f"\n[{name}]\n{json.dumps(value, ensure_ascii=False, sort_keys=True)}\n"
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
        provider="provider-neutral",
        route="NEUTRAL_HANDOFF",
        parameters={},
        reference_slots=tuple(str(item["slot"]) for item in metadata.get("references", [])),
        capability_snapshot_id="NOT_APPLICABLE",
        body=body,
        input_hashes={**input_hashes, **({"visual_control": visual_control_hash} if visual_control_hash else {})},
        visual_control_id=visual_control_id,
        visual_control_hash=visual_control_hash,
        production_ledger_event_ids=tuple(production_ledger_event_ids),
        requirement_report_hash=(hash_text(Path(requirement_report_path).read_text(encoding="utf-8")) if requirement_report_path is not None else None),
    )


__all__ = ["PromptCompilationError", "compile_prompt", "compile_canonical"]
