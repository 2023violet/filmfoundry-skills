"""Strict, provider-neutral FilmFoundry v3 contracts."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,63}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
LIFECYCLE_STATES = (
    "DRAFT", "SPEC_RESOLVED", "PREFLIGHT_PASS", "READY_FOR_KF", "KF_GENERATED",
    "KF_QC_PASS", "READY_FOR_VIDEO", "VIDEO_GENERATED", "VIDEO_QC_PASS", "SELECT",
    "OBSERVED_STATE_RECORDED", "EDIT_READY",
)
STATE_RANK = {state: i for i, state in enumerate(LIFECYCLE_STATES)}
EVIDENCE_LEVELS = {"UNVERIFIED", "OBSERVED_ONCE", "REPEATED", "PROJECT_VERIFIED", "CROSS_PROJECT_VERIFIED"}
ASSET_STATES = {"PLANNED", "CANDIDATE", "LOCKED", "RETIRED", "MISSING", "LEGACY_FORMAT"}
ASSET_PROFILES = {
    "CHARACTER_REFERENCE", "LOCATION_REFERENCE_WIDE", "PROP_REFERENCE", "VISUAL_CONTROL",
    "DELIVERY_VERTICAL", "VIDEO_SOURCE_NATIVE",
}
SHOT_CORE = {
    "shot_id", "generation_unit_id", "edit_unit_ids", "generation_duration_seconds",
    "edit_target_duration_seconds", "narrative_goal", "dominant_action", "location",
    "initial_state", "end_state", "shot_size", "composition", "camera", "transition_type",
    "reference_bindings", "failure_risks", "quality_bar",
}
PROMPT_CORE = {
    "prompt_id", "prompt_type", "production_unit", "visual_fact", "output_profile",
    "start_state", "end_state", "subjects", "dominant_action", "camera", "continuity_locks",
    "references", "forbidden", "acceptance",
}
MANIFEST_CORE = {
    "workspace_version", "project_id", "top_level", "authorities", "archive_boundary",
    "id_policy", "adapter_compatibility", "required_tools",
}
EVIDENCE_CORE = {
    "evidence_id", "provider", "provider_surface", "provider_version", "capability", "route",
    "result", "evidence_level", "generation_ids", "scope", "observed_at", "review_due",
}


def _unknown(data: dict[str, Any], allowed: set[str]) -> list[str]:
    return [f"{key}: unsupported field; use extensions namespace" for key in sorted(set(data) - allowed - {"extensions"})]


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _id(value: Any, field: str) -> list[str]:
    if not isinstance(value, str) or not ID_RE.fullmatch(value):
        return [f"{field}: must match ASCII stable ID pattern [A-Z][A-Z0-9_]{{2,63}}"]
    return []


def validate_workspace_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest: top-level object required"]
    errors.extend(_unknown(data, MANIFEST_CORE))
    if data.get("workspace_version") != "3.0.0":
        errors.append("workspace_version: unsupported; expected 3.0.0")
    errors.extend(_id(data.get("project_id"), "project_id"))
    if not isinstance(data.get("top_level"), dict) or not data["top_level"]:
        errors.append("top_level: non-empty object required")
    authorities = data.get("authorities")
    if not isinstance(authorities, dict):
        errors.append("authorities: object required")
    else:
        if authorities.get("human") != "markdown":
            errors.append("authorities.human: must be markdown")
        if not isinstance(authorities.get("machine"), list) or not {"json", "csv"}.issubset(set(authorities.get("machine", []))):
            errors.append("authorities.machine: must include json and csv")
    boundary = data.get("archive_boundary")
    if not isinstance(boundary, dict) or not _nonempty(boundary.get("path")) or boundary.get("mode") != "read_only":
        errors.append("archive_boundary: path and read_only mode required")
    policy = data.get("id_policy")
    if not isinstance(policy, dict) or policy.get("charset") != "ASCII":
        errors.append("id_policy: ASCII charset required")
    if not isinstance(data.get("adapter_compatibility"), dict) or not data["adapter_compatibility"]:
        errors.append("adapter_compatibility: non-empty object required")
    if not isinstance(data.get("required_tools"), list) or not data["required_tools"]:
        errors.append("required_tools: non-empty list required")
    return errors


def resolve_manifest_path(root: Path, value: str) -> Path:
    """Resolve a manifest-relative path and reject traversal outside root."""
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError("manifest paths must be relative")
    root = root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes manifest root: {value}") from exc
    return resolved


def validate_asset_registry(rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if isinstance(rows, dict):
        rows = rows.get("assets", [])
    if not isinstance(rows, list):
        return ["asset_registry: list or object with assets list required"]
    seen: set[str] = set()
    required = {
        "asset_id", "asset_type", "asset_class", "display_name", "path", "sha256", "width", "height",
        "aspect_ratio", "mode", "alpha", "profile", "state", "canonical_level", "reference_role",
        "does_not_control", "source", "episode_scope",
    }
    for i, row in enumerate(rows, 1):
        errors.extend(_unknown(row, required))
        aid = row.get("asset_id")
        errors.extend(_id(aid, f"row {i} asset_id"))
        if aid in seen:
            errors.append(f"row {i}: duplicate asset_id {aid}")
        seen.add(aid)
        for field in required - {"asset_id", "width", "height", "aspect_ratio", "alpha", "episode_scope"}:
            if not _nonempty(row.get(field)):
                errors.append(f"row {i} {field}: required")
        if not isinstance(row.get("width"), int) or row["width"] <= 0:
            errors.append(f"row {i} width: positive integer required")
        if not isinstance(row.get("height"), int) or row["height"] <= 0:
            errors.append(f"row {i} height: positive integer required")
        if not isinstance(row.get("aspect_ratio"), (int, float)) or isinstance(row.get("aspect_ratio"), bool) or row["aspect_ratio"] <= 0:
            errors.append(f"row {i} aspect_ratio: positive number required")
        if not SHA256_RE.fullmatch(str(row.get("sha256", ""))):
            errors.append(f"row {i} sha256: 64-character hexadecimal digest required")
        if row.get("state") not in ASSET_STATES:
            errors.append(f"row {i} state: unsupported value {row.get('state')!r}")
        if row.get("profile") not in ASSET_PROFILES:
            errors.append(f"row {i} profile: unsupported value {row.get('profile')!r}")
        if row.get("profile") == "DELIVERY_VERTICAL" and row.get("height", 0) <= row.get("width", 0):
            errors.append(f"row {i} DELIVERY_VERTICAL: height must exceed width")
        if row.get("profile") == "LOCATION_REFERENCE_WIDE" and row.get("width", 0) <= row.get("height", 0):
            errors.append(f"row {i} LOCATION_REFERENCE_WIDE: width must exceed height")
        if not isinstance(row.get("episode_scope"), list):
            errors.append(f"row {i} episode_scope: list required")
    return errors


def validate_shot_spec(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["shot: top-level object required"]
    errors.extend(_unknown(data, SHOT_CORE | {"schema_version", "dialogue", "voice_id", "dialogue_route", "timing_authority", "speech_intent", "camera_axis", "screen_direction", "eyeline_critical", "eyeline_subject", "eyeline_target", "eyeline_screen_direction", "prop_interaction", "canonical_props", "prop_initial_state", "prop_end_state", "prop_persistence", "continuity_source", "previous_observed_state", "handoff_state", "timing_granularity", "timing_constraint", "action_stages"}))
    for field in SHOT_CORE:
        if field not in data or data[field] in (None, "", []):
            errors.append(f"{field}: required")
    for field in ("narrative_goal", "dominant_action", "initial_state", "end_state", "shot_size", "composition", "quality_bar", "transition_type"):
        if field in data and not _nonempty(data[field]):
            errors.append(f"{field}: non-empty string required")
    for field in ("shot_id", "generation_unit_id"):
        errors.extend(_id(data.get(field), field))
    if not isinstance(data.get("edit_unit_ids"), list) or not data["edit_unit_ids"]:
        errors.append("edit_unit_ids: non-empty list required")
    for field in ("generation_duration_seconds", "edit_target_duration_seconds"):
        if not isinstance(data.get(field), (int, float)) or isinstance(data.get(field), bool) or data[field] <= 0:
            errors.append(f"{field}: positive number required")
    if isinstance(data.get("generation_duration_seconds"), (int, float)) and isinstance(data.get("edit_target_duration_seconds"), (int, float)) and data["edit_target_duration_seconds"] > data["generation_duration_seconds"]:
        errors.append("edit_target_duration_seconds: cannot exceed generation_duration_seconds")
    refs = data.get("reference_bindings")
    if not isinstance(refs, list):
        errors.append("reference_bindings: list required")
    else:
        slots: set[str] = set()
        for i, ref in enumerate(refs):
            if not isinstance(ref, dict):
                errors.append(f"reference_bindings[{i}]: object required")
                continue
            errors.extend(
                f"reference_bindings[{i}].{error}"
                for error in _unknown(ref, {"slot", "asset_id", "role", "controls", "does_not_control"})
            )
            for field in ("slot", "asset_id", "role", "controls", "does_not_control"):
                if not _nonempty(ref.get(field)):
                    errors.append(f"reference_bindings[{i}].{field}: required")
            if ref.get("slot") in slots:
                errors.append(f"reference_bindings[{i}]: duplicate reference slot {ref.get('slot')}")
            slots.add(ref.get("slot"))
    transition = data.get("transition_type")
    if transition == "reverse_angle":
        for field in ("camera_axis", "screen_direction", "eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
            if not _nonempty(data.get(field)):
                errors.append(f"{field}: required for reverse_angle")
    if data.get("eyeline_critical") is True:
        for field in ("eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
            if not _nonempty(data.get(field)):
                errors.append(f"{field}: required when eyeline_critical is true")
    if data.get("dialogue") not in (None, "", "none", "None"):
        for field in ("voice_id", "dialogue_route", "timing_authority", "speech_intent"):
            if not _nonempty(data.get(field)):
                errors.append(f"{field}: required when dialogue exists")
    if data.get("prop_interaction") is True:
        if not isinstance(data.get("canonical_props"), list) or not data["canonical_props"]:
            errors.append("canonical_props: required when prop_interaction is true")
        for field in ("prop_initial_state", "prop_end_state", "prop_persistence"):
            if not _nonempty(data.get(field)):
                errors.append(f"{field}: required when prop_interaction is true")
    if transition == "continuous":
        for field in ("continuity_source", "previous_observed_state", "handoff_state"):
            if not _nonempty(data.get(field)):
                errors.append(f"{field}: required for continuous transition")
    return errors


def parse_prompt_metadata(text: str) -> dict[str, Any]:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    if not match:
        raise ValueError("prompt requires a JSON metadata fence")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("prompt metadata must be an object")
    return value


def validate_prompt_markdown(text: str) -> list[str]:
    try:
        data = parse_prompt_metadata(text)
    except (ValueError, json.JSONDecodeError) as exc:
        return [f"metadata: {exc}"]
    errors = _unknown(data, PROMPT_CORE)
    for field in PROMPT_CORE:
        if field not in data or data[field] in (None, "", []):
            errors.append(f"{field}: required")
    for field in ("prompt_type", "production_unit", "visual_fact", "output_profile", "start_state", "end_state", "dominant_action", "camera"):
        if field in data and not _nonempty(data[field]):
            errors.append(f"{field}: non-empty string required")
    for field in ("subjects", "continuity_locks", "forbidden", "acceptance"):
        if field in data and not isinstance(data[field], list):
            errors.append(f"{field}: list required")
    errors.extend(_id(data.get("prompt_id"), "prompt_id"))
    refs = data.get("references")
    if not isinstance(refs, list):
        errors.append("references: list required")
    else:
        slots: set[str] = set()
        for i, ref in enumerate(refs):
            if not isinstance(ref, dict):
                errors.append(f"references[{i}]: object required")
                continue
            errors.extend(
                f"references[{i}].{error}"
                for error in _unknown(ref, {"slot", "asset_id", "role", "controls", "does_not_control"})
            )
            for field in ("slot", "asset_id", "role", "controls", "does_not_control"):
                if not _nonempty(ref.get(field)):
                    errors.append(f"references[{i}].{field}: required")
            if ref.get("slot") in slots:
                errors.append(f"references[{i}]: duplicate reference slot {ref.get('slot')}")
            slots.add(ref.get("slot"))
    for heading in ("visual_fact", "output_profile", "start_state", "end_state", "subjects", "dominant_action", "camera", "continuity_locks", "references", "forbidden", "acceptance"):
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", text, flags=re.M):
            errors.append(f"section {heading}: required Markdown heading")
    return errors


def validate_state_transition(old: str, new: str) -> list[str]:
    old, new = old.strip().upper(), new.strip().upper()
    if old not in STATE_RANK:
        return [f"unknown source runtime state: {old}"]
    if new not in STATE_RANK:
        return [f"unknown target runtime state: {new}"]
    if old != new and STATE_RANK[new] != STATE_RANK[old] + 1:
        return [f"illegal runtime transition: {old} -> {new}; gates may not be skipped"]
    return []


def validate_production_state(data: dict[str, Any]) -> list[str]:
    errors: list[str] = _unknown(data, {"schema_version", "units"}) if isinstance(data, dict) else []
    if isinstance(data, dict) and data.get("schema_version") != "3.0.0":
        errors.append("schema_version: unsupported; expected 3.0.0")
    units = data.get("units") if isinstance(data, dict) else None
    if not isinstance(units, dict):
        return ["units: object required"]
    for uid, unit in units.items():
        if not isinstance(unit, dict):
            errors.append(f"units.{uid}: object required")
            continue
        errors.extend(
            f"units.{uid}.{error}"
            for error in _unknown(
                unit,
                {
                    "runtime_status", "design_status", "visual_control_state_alignment",
                    "provider_route", "provider_evidence_id", "select_type", "source_in",
                    "source_out", "observed_state", "history",
                },
            )
        )
        status = str(unit.get("runtime_status", "")).upper()
        if status not in STATE_RANK:
            errors.append(f"units.{uid}.runtime_status: unknown state")
            continue
        if status in {"READY_FOR_VIDEO", "VIDEO_GENERATED", "VIDEO_QC_PASS", "SELECT", "OBSERVED_STATE_RECORDED", "EDIT_READY"}:
            if str(unit.get("visual_control_state_alignment", "")).upper() != "PASS":
                errors.append(f"units.{uid}: visual control state alignment must PASS before video")
            if not unit.get("provider_evidence_id"):
                errors.append(f"units.{uid}: provider evidence required before video")
        if status == "SELECT" and str(unit.get("select_type", "FULL")).upper() == "PARTIAL_SELECT":
            if not isinstance(unit.get("source_in"), (int, float)) or not isinstance(unit.get("source_out"), (int, float)) or unit["source_out"] <= unit["source_in"]:
                errors.append(f"units.{uid}: PARTIAL_SELECT source_in/source_out contiguous range required")
            if not unit.get("observed_state"):
                errors.append(f"units.{uid}: PARTIAL_SELECT observed_state required")
    return errors


def validate_evidence(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_unknown(data, EVIDENCE_CORE | {"default_behavior"}))
    for field in EVIDENCE_CORE:
        if field not in data or data[field] in (None, "", []):
            errors.append(f"{field}: required")
    errors.extend(_id(data.get("evidence_id"), "evidence_id"))
    if data.get("evidence_level") not in EVIDENCE_LEVELS:
        errors.append("evidence_level: unsupported value")
    if data.get("default_behavior") is True and data.get("evidence_level") == "OBSERVED_ONCE":
        errors.append("OBSERVED_ONCE evidence cannot establish default behavior")
    if not isinstance(data.get("generation_ids"), list) or not data["generation_ids"]:
        errors.append("generation_ids: non-empty list required")
    return errors


def validate_reference_graph(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = _unknown(graph, {"nodes", "edges"}) if isinstance(graph, dict) else []
    nodes = graph.get("nodes") if isinstance(graph, dict) else None
    edges = graph.get("edges") if isinstance(graph, dict) else None
    if not isinstance(nodes, list):
        return ["nodes: list required"]
    if not isinstance(edges, list):
        return ["edges: list required"]
    known = set(nodes)
    seen: set[tuple[Any, Any, Any]] = set()
    for i, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edges[{i}]: object required")
            continue
        errors.extend(
            f"edges[{i}].{error}"
            for error in _unknown(edge, {"source", "target", "relation"})
        )
        key = (edge.get("source"), edge.get("target"), edge.get("relation"))
        if key in seen:
            errors.append(f"edges[{i}]: duplicate edge {key}")
        seen.add(key)
        for endpoint in ("source", "target"):
            if edge.get(endpoint) not in known:
                errors.append(f"edges[{i}].{endpoint}: unknown node {edge.get(endpoint)!r}")
    return errors
