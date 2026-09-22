"""Provider-neutral Prompt handoff between FilmFoundry and external tools."""
from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping

from .profiles import ProjectProfile, StyleProfile, UNKNOWN


HANDOFF_STATUSES = (
    "DRAFT",
    "SPEC_RESOLVED",
    "EXTERNAL_ADAPTER_REQUIRED",
    "HUMAN_REVIEW",
    "READY_FOR_EXTERNAL_TOOL",
)

HANDOFF_SECTIONS = (
    "REFERENCE BINDING",
    "PROJECT / STYLE PROFILE",
    "SHOT / GENERATION UNIT",
    "SUBJECTS AND IDENTITY LOCKS",
    "LOCATION AND SPATIAL LOCKS",
    "PROP / STATE LOCKS",
    "DOMINANT ACTION",
    "CAMERA AND COMPOSITION",
    "LIGHTING AND PHYSICAL CUES",
    "CONTINUITY INPUT",
    "OBSERVABLE END STATE",
    "MUST PRESERVE",
    "FAILURE CONSTRAINTS",
    "ACCEPTANCE CHECKS",
)

_SECTION_KEYS = tuple(heading.lower().replace(" / ", "_").replace(" ", "_") for heading in HANDOFF_SECTIONS)


def _text(value: Any, default: str = UNKNOWN) -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip() or default
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _json_value(value: Any) -> Any:
    return value if value not in (None, "") else UNKNOWN


@dataclass(frozen=True)
class ProviderNeutralHandoff:
    handoff_id: str
    status: str
    sections: dict[str, Any]
    provenance: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "provider-neutral-handoff.v1",
            "handoff_id": self.handoff_id,
            "status": self.status,
            "sections": self.sections,
            "provenance": self.provenance,
        }

    def to_markdown(self) -> str:
        metadata = json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, indent=2)
        lines = [
            "# FilmFoundry provider-neutral handoff",
            "",
            "```json",
            metadata,
            "```",
        ]
        for heading in HANDOFF_SECTIONS:
            lines.extend(("", f"## {heading}", ""))
            key = heading.lower().replace(" / ", "_").replace(" ", "_")
            value = self.sections.get(key, UNKNOWN)
            if isinstance(value, (dict, list)):
                lines.append(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2))
            else:
                lines.append(str(value))
        return "\n".join(lines) + "\n"


def validate_provider_neutral_handoff(value: Mapping[str, Any]) -> list[str]:
    """Validate the handoff envelope without validating any external tool."""
    if not isinstance(value, Mapping):
        return ["handoff: object required"]
    errors: list[str] = []
    if value.get("schema_version") != "provider-neutral-handoff.v1":
        errors.append("schema_version: expected provider-neutral-handoff.v1")
    if not isinstance(value.get("handoff_id"), str) or not value["handoff_id"].strip():
        errors.append("handoff_id: non-empty value required")
    if value.get("status") not in HANDOFF_STATUSES:
        errors.append(f"status: unsupported value {value.get('status')!r}")
    sections = value.get("sections")
    if not isinstance(sections, Mapping):
        errors.append("sections: object required")
    else:
        errors.extend(f"sections.{key}: required" for key in _SECTION_KEYS if key not in sections)
    if not isinstance(value.get("provenance"), Mapping):
        errors.append("provenance: object required")
    return errors


def build_provider_neutral_handoff(
    prompt: Mapping[str, Any],
    *,
    project_profile: ProjectProfile | Mapping[str, Any] | None = None,
    style_profile: StyleProfile | Mapping[str, Any] | None = None,
    shot_spec: Mapping[str, Any] | None = None,
    status: str = "SPEC_RESOLVED",
) -> ProviderNeutralHandoff:
    """Map canonical Prompt metadata into a stable, provider-free handoff.

    The function only copies declared facts.  It never adds provider syntax,
    capabilities, duration folklore, or a call instruction.
    """
    if status not in HANDOFF_STATUSES:
        raise ValueError(f"unsupported handoff status: {status}")
    project = project_profile if isinstance(project_profile, ProjectProfile) else ProjectProfile.from_mapping(project_profile)
    style = style_profile if isinstance(style_profile, StyleProfile) else StyleProfile.from_mapping(style_profile)
    shot = shot_spec or {}
    refs = prompt.get("references", shot.get("reference_bindings", []))
    handoff_id = _text(prompt.get("prompt_id", shot.get("shot_id", "HANDOFF_UNKNOWN")))
    sections: dict[str, Any] = {
        "reference_binding": _json_value(refs),
        "project_style_profile": {"project_profile": project.to_dict(), "style_profile": style.to_dict()},
        "shot_generation_unit": {
            "shot_id": _json_value(shot.get("shot_id")),
            "generation_unit_id": _json_value(shot.get("generation_unit_id", prompt.get("production_unit"))),
            "generation_duration_seconds": _json_value(shot.get("generation_duration_seconds")),
            "edit_target_duration_seconds": _json_value(shot.get("edit_target_duration_seconds")),
            "prompt_type": _json_value(prompt.get("prompt_type")),
        },
        "subjects_and_identity_locks": _json_value(prompt.get("subjects")),
        "location_and_spatial_locks": _json_value(shot.get("location", prompt.get("visual_fact"))),
        "prop_state_locks": {
            "initial_state": _json_value(shot.get("prop_initial_state", prompt.get("start_state"))),
            "end_state": _json_value(shot.get("prop_end_state", prompt.get("end_state"))),
            "persistence": _json_value(shot.get("prop_persistence")),
        },
        "dominant_action": _json_value(shot.get("dominant_action", prompt.get("dominant_action"))),
        "camera_and_composition": {
            "shot_size": _json_value(shot.get("shot_size")),
            "composition": _json_value(shot.get("composition")),
            "camera": _json_value(shot.get("camera", prompt.get("camera"))),
        },
        "lighting_and_physical_cues": _json_value(prompt.get("lighting", style.lighting)),
        "continuity_input": _json_value(shot.get("previous_observed_state", prompt.get("continuity_locks"))),
        "observable_end_state": _json_value(shot.get("end_state", prompt.get("end_state"))),
        "must_preserve": _json_value(prompt.get("continuity_locks")),
        "failure_constraints": _json_value(shot.get("failure_risks", prompt.get("forbidden"))),
        "acceptance_checks": _json_value(shot.get("quality_bar", prompt.get("acceptance"))),
    }
    provenance = {
        "prompt": _text(prompt.get("prompt_id", "PROMPT_UNKNOWN")),
        "project_profile": "declared" if project_profile is not None else "UNKNOWN",
        "style_profile": "declared" if style_profile is not None else "UNKNOWN",
        "shot_spec": "declared" if shot_spec is not None else "UNKNOWN",
    }
    return ProviderNeutralHandoff(handoff_id=handoff_id, status=status, sections=sections, provenance=provenance)


__all__ = [
    "HANDOFF_SECTIONS",
    "HANDOFF_STATUSES",
    "ProviderNeutralHandoff",
    "build_provider_neutral_handoff",
    "validate_provider_neutral_handoff",
]
