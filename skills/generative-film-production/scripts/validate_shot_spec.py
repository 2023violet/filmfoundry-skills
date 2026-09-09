#!/usr/bin/env python3
"""Validate FilmFoundry Canonical Shot Spec JSON.

The v1.1/v1.2 validator is adaptive: core fields always apply, while dialogue,
reverse-angle, eyeline-critical, prop-interaction, continuous-action, and hard-clock
fields are required only when the shot actually uses those routes. Legacy v1.0.1
and v1.1 specs remain accepted.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TEXT = ("shot_id", "narrative_goal", "dominant_action", "initial_state", "end_state")
V11_CORE_TEXT = ("generation_unit", "chapter", "duration_target", "shot_size", "composition", "camera_move", "quality_bar")
V12_CORE_TEXT = ("generation_unit", "chapter", "shot_size", "composition", "camera_move", "quality_bar")
ALLOWED_GRANULARITY = {"none", "stages", "seconds"}
ALLOWED_TRANSITIONS = {"continuous", "hard_cut", "reverse_angle", "match_cut", "insert", "cutaway"}
ALLOWED_DIALOGUE_ROUTES = {"H3_NATIVE_DIALOGUE", "EXTERNAL_VOICE_TIMING", "POST_VO_NO_LIPSYNC", "NATIVE", "EXTERNAL", "POST_VO"}


def _missing_text(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    return not isinstance(value, str) or not value.strip()


def _has_dialogue(data: dict[str, Any]) -> bool:
    value = data.get("dialogue")
    if not isinstance(value, str):
        return False
    return value.strip().lower() not in {"", "none", "n/a", "null"}


def _v12_mode(data: dict[str, Any]) -> bool:
    return str(data.get("schema_version", "")).strip() == "1.2"


def _v11_mode(data: dict[str, Any]) -> bool:
    return bool(data.get("generation_unit") or str(data.get("schema_version", "")).strip() in {"1.1", "1.2"})


def validate_shot_spec(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_TEXT:
        if _missing_text(data, key):
            errors.append(f"{key}: required non-empty string")

    if _v11_mode(data):
        core_fields = V12_CORE_TEXT if _v12_mode(data) else V11_CORE_TEXT
        version_label = "v1.2" if _v12_mode(data) else "v1.1"
        for key in core_fields:
            if _missing_text(data, key):
                errors.append(f"{key}: required non-empty string in {version_label} adaptive spec")
        location = data.get("location")
        if location is None or (isinstance(location, str) and not location.strip()) or (isinstance(location, dict) and not location):
            errors.append("location: required in v1.1 adaptive spec")
        if "transition_type" not in data or not isinstance(data.get("transition_type"), str) or not data.get("transition_type", "").strip():
            errors.append("transition_type: required in v1.1 adaptive spec")
        if "reference_bindings" not in data:
            errors.append("reference_bindings: explicit list required in v1.1 adaptive spec (may be empty for no-reference routes)")
        risks = data.get("failure_risks")
        if not isinstance(risks, list) or not risks:
            errors.append("failure_risks: at least one risk required in v1.1 adaptive spec")


    if _v12_mode(data):
        generation_duration = data.get("generation_duration_seconds")
        edit_duration = data.get("edit_target_duration_seconds")
        if not isinstance(generation_duration, (int, float)) or isinstance(generation_duration, bool) or generation_duration <= 0:
            errors.append("generation_duration_seconds: required positive number in v1.2")
        if not isinstance(edit_duration, (int, float)) or isinstance(edit_duration, bool) or edit_duration <= 0:
            errors.append("edit_target_duration_seconds: required positive number in v1.2")
        if (isinstance(generation_duration, (int, float)) and not isinstance(generation_duration, bool) and generation_duration > 0
                and isinstance(edit_duration, (int, float)) and not isinstance(edit_duration, bool) and edit_duration > generation_duration):
            errors.append("edit_target_duration_seconds: cannot exceed generation_duration_seconds")

    dominant = data.get("dominant_action")
    if dominant is not None and not isinstance(dominant, str):
        errors.append("dominant_action: must be one concise string, not a list/object")

    granularity = data.get("timing_granularity", "stages")
    if granularity not in ALLOWED_GRANULARITY:
        errors.append(f"timing_granularity: must be one of {sorted(ALLOWED_GRANULARITY)}")
    if granularity == "seconds":
        if _missing_text(data, "timing_constraint"):
            errors.append("timing_constraint: required when timing_granularity is seconds")
        if _v11_mode(data) and _missing_text(data, "timing_authority"):
            errors.append("timing_authority: required when timing_granularity is seconds")

    transition = data.get("transition_type")
    if transition is not None and transition not in ALLOWED_TRANSITIONS:
        errors.append(f"transition_type: unsupported value {transition!r}; must be one of {sorted(ALLOWED_TRANSITIONS)}")

    if data.get("eyeline_critical") is True:
        for field in ("eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
            if _missing_text(data, field):
                errors.append(f"{field}: required when eyeline_critical is true")
        direction = data.get("eyeline_screen_direction")
        if isinstance(direction, str) and direction.strip().lower() not in {"left", "right", "center"}:
            errors.append("eyeline_screen_direction: must be left, right, or center")

    if transition == "reverse_angle":
        for field in (
            "camera_axis",
            "screen_direction",
            "eyeline_subject",
            "eyeline_target",
            "eyeline_screen_direction",
        ):
            if _missing_text(data, field):
                errors.append(f"{field}: required for reverse_angle continuity")
        direction = data.get("eyeline_screen_direction")
        if isinstance(direction, str) and direction.strip().lower() not in {"left", "right", "center"}:
            errors.append("eyeline_screen_direction: must be left, right, or center")

    if transition == "continuous" and _v11_mode(data):
        for field in ("continuity_source", "previous_observed_state", "handoff_state"):
            if _missing_text(data, field):
                errors.append(f"{field}: required for continuous-action handoff")

    if _has_dialogue(data):
        for field in ("voice_id", "dialogue_route", "timing_authority", "speech_intent"):
            if _missing_text(data, field):
                errors.append(f"{field}: required when dialogue is present")
        route = data.get("dialogue_route")
        if isinstance(route, str) and route.strip() and route.strip().upper() not in ALLOWED_DIALOGUE_ROUTES:
            errors.append(f"dialogue_route: unsupported value {route!r}")

    if data.get("prop_interaction") is True:
        props = data.get("canonical_props")
        if not isinstance(props, list) or not props:
            errors.append("canonical_props: at least one canonical prop required when prop_interaction is true")
        for field in ("prop_initial_state", "prop_end_state", "prop_persistence"):
            if _missing_text(data, field):
                errors.append(f"{field}: required when prop_interaction is true")

    refs = data.get("reference_bindings", [])
    if refs is None:
        refs = []
    if not isinstance(refs, list):
        errors.append("reference_bindings: must be a list")
    else:
        seen_ref_ids: set[str] = set()
        for i, ref in enumerate(refs):
            if not isinstance(ref, dict):
                errors.append(f"reference_bindings[{i}]: must be an object")
                continue
            for key in ("ref_id", "controls", "does_not_control"):
                if _missing_text(ref, key):
                    errors.append(f"reference_bindings[{i}].{key}: required non-empty string")
            ref_id = ref.get("ref_id")
            if isinstance(ref_id, str) and ref_id.strip():
                normalized_ref_id = ref_id.strip()
                if normalized_ref_id in seen_ref_ids:
                    errors.append(f"reference_bindings[{i}].ref_id: duplicate ref_id {normalized_ref_id}")
                else:
                    seen_ref_ids.add(normalized_ref_id)

    stages = data.get("action_stages", [])
    if granularity == "stages":
        if not isinstance(stages, list) or not stages:
            errors.append("action_stages: at least one stage required for stages timing")
        else:
            for i, stage in enumerate(stages):
                if not isinstance(stage, dict):
                    errors.append(f"action_stages[{i}]: must be an object")
                    continue
                stage_number = stage.get("stage")
                if not isinstance(stage_number, int) or isinstance(stage_number, bool):
                    errors.append(f"action_stages[{i}].stage: required integer stage number")
                elif stage_number != i + 1:
                    errors.append(f"action_stages[{i}].stage: stages must be sequential starting at 1; expected {i + 1}, got {stage_number}")
                if _missing_text(stage, "action"):
                    errors.append(f"action_stages[{i}].action: required non-empty string")
                if _missing_text(stage, "end_state"):
                    errors.append(f"action_stages[{i}].end_state: required observable end state")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_shot_spec.py <shot-spec.json>")
        return 2
    path = Path(argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    if not isinstance(data, dict):
        print("ERROR: top-level JSON must be an object")
        return 2
    errors = validate_shot_spec(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: canonical shot spec is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
