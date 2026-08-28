#!/usr/bin/env python3
"""Validate FilmFoundry Canonical Shot Spec JSON."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_TEXT = ("shot_id", "narrative_goal", "dominant_action", "initial_state", "end_state")
ALLOWED_GRANULARITY = {"none", "stages", "seconds"}
ALLOWED_TRANSITIONS = {"continuous", "hard_cut", "reverse_angle", "match_cut", "insert", "cutaway"}


def _missing_text(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    return not isinstance(value, str) or not value.strip()


def validate_shot_spec(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_TEXT:
        if _missing_text(data, key):
            errors.append(f"{key}: required non-empty string")

    dominant = data.get("dominant_action")
    if dominant is not None and not isinstance(dominant, str):
        errors.append("dominant_action: must be one concise string, not a list/object")

    granularity = data.get("timing_granularity", "stages")
    if granularity not in ALLOWED_GRANULARITY:
        errors.append(f"timing_granularity: must be one of {sorted(ALLOWED_GRANULARITY)}")
    if granularity == "seconds" and _missing_text(data, "timing_constraint"):
        errors.append("timing_constraint: required when timing_granularity is seconds")

    transition = data.get("transition_type")
    if transition is not None and transition not in ALLOWED_TRANSITIONS:
        errors.append(f"transition_type: unsupported value {transition!r}; must be one of {sorted(ALLOWED_TRANSITIONS)}")
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
