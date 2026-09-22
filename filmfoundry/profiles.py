"""Small, explicit Project and Style Profile contracts.

Profiles are routing and compilation inputs.  They are deliberately separate
from Canon, Runtime, and provider adapters so a project or visual change does
not require a new Core branch.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Mapping


UNKNOWN = "UNKNOWN"

PROJECT_FIELDS = (
    "project_id",
    "medium",
    "audience",
    "target_duration",
    "production_scope",
    "continuity_level",
    "delivery_aspect",
    "profile_version",
    "source",
)
STYLE_FIELDS = (
    "visual_language",
    "palette",
    "texture",
    "lighting",
    "camera_behavior",
    "motion_density",
    "composition",
    "profile_version",
    "source",
)


def _value(mapping: Mapping[str, Any], field: str) -> str:
    value = mapping.get(field, UNKNOWN)
    if value is None or (isinstance(value, str) and not value.strip()):
        return UNKNOWN
    return str(value).strip()


@dataclass(frozen=True)
class ProjectProfile:
    project_id: str = UNKNOWN
    medium: str = UNKNOWN
    audience: str = UNKNOWN
    target_duration: str = UNKNOWN
    production_scope: str = UNKNOWN
    continuity_level: str = UNKNOWN
    delivery_aspect: str = UNKNOWN
    profile_version: str = UNKNOWN
    source: str = UNKNOWN

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "ProjectProfile":
        mapping = value or {}
        return cls(**{field: _value(mapping, field) for field in PROJECT_FIELDS})

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class StyleProfile:
    visual_language: str = UNKNOWN
    palette: str = UNKNOWN
    texture: str = UNKNOWN
    lighting: str = UNKNOWN
    camera_behavior: str = UNKNOWN
    motion_density: str = UNKNOWN
    composition: str = UNKNOWN
    profile_version: str = UNKNOWN
    source: str = UNKNOWN

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "StyleProfile":
        mapping = value or {}
        return cls(**{field: _value(mapping, field) for field in STYLE_FIELDS})

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _validate_profile(value: Mapping[str, Any], fields: tuple[str, ...], name: str) -> list[str]:
    if not isinstance(value, Mapping):
        return [f"{name}: object required"]
    errors: list[str] = []
    allowed = set(fields) | {"profile_version", "source", "extensions"}
    errors.extend(
        f"{name}.{key}: unsupported field; use extensions namespace"
        for key in sorted(set(value) - allowed)
    )
    for field in fields:
        if field in value and value[field] is not None and not isinstance(value[field], (str, int, float)):
            errors.append(f"{name}.{field}: scalar value required")
    if name == "project_profile" and "project_id" in value and _value(value, "project_id") == UNKNOWN:
        errors.append("project_profile.project_id: non-empty value required when supplied")
    return errors


def validate_project_profile(value: Mapping[str, Any]) -> list[str]:
    if isinstance(value, Mapping) and isinstance(value.get("project_profile"), Mapping):
        value = value["project_profile"]
    return _validate_profile(value, PROJECT_FIELDS, "project_profile")


def validate_style_profile(value: Mapping[str, Any]) -> list[str]:
    if isinstance(value, Mapping) and isinstance(value.get("style_profile"), Mapping):
        value = value["style_profile"]
    return _validate_profile(value, STYLE_FIELDS, "style_profile")


def load_profile(path: str | Path, *, kind: str) -> ProjectProfile | StyleProfile:
    """Load one JSON profile without guessing a missing value."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("profile document must be an object")
    if kind == "project":
        payload = payload.get("project_profile", payload)
        errors = validate_project_profile(payload)
        if errors:
            raise ValueError("; ".join(errors))
        return ProjectProfile.from_mapping(payload)
    if kind == "style":
        payload = payload.get("style_profile", payload)
        errors = validate_style_profile(payload)
        if errors:
            raise ValueError("; ".join(errors))
        return StyleProfile.from_mapping(payload)
    raise ValueError(f"unsupported profile kind: {kind}")


__all__ = [
    "PROJECT_FIELDS",
    "STYLE_FIELDS",
    "UNKNOWN",
    "ProjectProfile",
    "StyleProfile",
    "load_profile",
    "validate_project_profile",
    "validate_style_profile",
]
