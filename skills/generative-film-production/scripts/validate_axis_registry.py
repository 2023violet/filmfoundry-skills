#!/usr/bin/env python3
"""Validate FilmFoundry camera-axis registry JSON."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from runtime_common import load_json, nonempty

ALLOWED_SIDE = {"left", "right", "center"}
ALLOWED_STATUS = {"PLANNED", "LOCKED", "RETIRED"}


def validate_axis_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    axes = data.get("axes")
    if not isinstance(axes, list):
        return ["axes: required list"]
    seen: set[str] = set()
    for i, axis in enumerate(axes):
        prefix = f"axes[{i}]"
        if not isinstance(axis, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        axis_id = str(axis.get("axis_id", "")).strip()
        if not axis_id:
            errors.append(f"{prefix}.axis_id: required")
        elif axis_id in seen:
            errors.append(f"{prefix}.axis_id: duplicate {axis_id}")
        seen.add(axis_id)
        for field in ("location_id", "subject_a", "subject_b"):
            if not nonempty(axis.get(field)):
                errors.append(f"{prefix}.{field}: required")
        status = str(axis.get("status", "PLANNED")).strip().upper()
        if status not in ALLOWED_STATUS:
            errors.append(f"{prefix}.status: unsupported {status}")

        subject_a = str(axis.get("subject_a", "")).strip()
        subject_b = str(axis.get("subject_b", "")).strip()
        side = axis.get("screen_side")
        eye = axis.get("eyeline")
        if not isinstance(side, dict):
            errors.append(f"{prefix}.screen_side: required object")
        elif subject_a and subject_b:
            a = str(side.get(subject_a, "")).lower()
            b = str(side.get(subject_b, "")).lower()
            if a not in ALLOWED_SIDE or b not in ALLOWED_SIDE:
                errors.append(f"{prefix}.screen_side: both subjects require left/right/center values")
            elif a == b and a != "center":
                errors.append(f"{prefix}.screen_side: two subjects cannot occupy the same canonical side")
        if not isinstance(eye, dict):
            errors.append(f"{prefix}.eyeline: required object")
        elif subject_a and subject_b:
            a = str(eye.get(subject_a, "")).lower()
            b = str(eye.get(subject_b, "")).lower()
            if a not in ALLOWED_SIDE or b not in ALLOWED_SIDE:
                errors.append(f"{prefix}.eyeline: both subjects require left/right/center values")
            elif (a, b) not in {("left", "right"), ("right", "left"), ("center", "center")}:
                errors.append(f"{prefix}.eyeline: subject directions must be reciprocal")
        if not isinstance(axis.get("crossing_allowed"), bool):
            errors.append(f"{prefix}.crossing_allowed: required boolean")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_axis_registry.py <axis-registry.json>")
        return 2
    try:
        data = load_json(Path(argv[1]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_axis_registry(data if isinstance(data, dict) else {})
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("PASS: axis registry is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
