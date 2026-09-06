#!/usr/bin/env python3
"""Validate FilmFoundry production-state JSON."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any
from runtime_common import RUNTIME_STATES, STATE_RANK, load_json, nonempty

SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def validate_production_state(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    units = data.get("units")
    if not isinstance(units, dict) or not units:
        return ["units: required non-empty object"]

    for unit_id, unit in units.items():
        prefix = f"units.{unit_id}"
        if not isinstance(unit, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        state = str(unit.get("runtime_status", "")).strip().upper()
        if state not in STATE_RANK:
            errors.append(f"{prefix}.runtime_status: must be one of {RUNTIME_STATES}")
            continue
        for field in ("spec_version", "asset_registry_version", "model_profile_version"):
            value = unit.get(field)
            if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
                errors.append(f"{prefix}.{field}: must be a positive integer when present")

        rank = STATE_RANK[state]
        keyframe = unit.get("keyframe") if isinstance(unit.get("keyframe"), dict) else {}
        video = unit.get("video") if isinstance(unit.get("video"), dict) else {}

        if rank >= STATE_RANK["KF_GENERATED"]:
            if not nonempty(keyframe.get("file")):
                errors.append(f"{prefix}.keyframe.file: required at KF_GENERATED or later")
        if rank >= STATE_RANK["KF_QC_PASS"]:
            if str(keyframe.get("qc", "")).strip().upper() != "PASS":
                errors.append(f"{prefix}.keyframe.qc: must be PASS at KF_QC_PASS or later")
            sha = str(keyframe.get("sha256", "")).strip()
            if sha and not SHA256_RE.fullmatch(sha):
                errors.append(f"{prefix}.keyframe.sha256: must be 64 hex characters when recorded")
        if rank >= STATE_RANK["VIDEO_GENERATED"]:
            if not nonempty(video.get("generation_id")) and not nonempty(video.get("file")):
                errors.append(f"{prefix}.video: generation_id or file required at VIDEO_GENERATED or later")
        if rank >= STATE_RANK["SELECT"]:
            selected = video.get("selected")
            if isinstance(selected, str):
                if not nonempty(selected):
                    errors.append(f"{prefix}.video.selected: required at SELECT or later")
            elif isinstance(selected, dict):
                if not nonempty(selected.get("file")):
                    errors.append(f"{prefix}.video.selected.file: required")
                disposition = str(selected.get("disposition", "")).strip().upper()
                if disposition not in {"FULL_SELECT", "PARTIAL_SELECT"}:
                    errors.append(f"{prefix}.video.selected.disposition: must be FULL_SELECT or PARTIAL_SELECT")
                source_duration = selected.get("source_duration_seconds")
                if not isinstance(source_duration, (int, float)) or isinstance(source_duration, bool) or source_duration <= 0:
                    errors.append(f"{prefix}.video.selected.source_duration_seconds: required positive number")
                if disposition == "PARTIAL_SELECT":
                    start = selected.get("in_seconds")
                    end = selected.get("out_seconds")
                    valid_numbers = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (start, end, source_duration))
                    if not valid_numbers or start < 0 or end <= start or end > source_duration:
                        errors.append(f"{prefix}.video.selected: PARTIAL_SELECT requires a valid contiguous range inside source duration")
                    elif start == 0 and abs(end - source_duration) <= 1e-6:
                        errors.append(f"{prefix}.video.selected: PARTIAL_SELECT range must exclude some source footage")
                elif disposition == "FULL_SELECT" and isinstance(source_duration, (int, float)) and not isinstance(source_duration, bool):
                    start = selected.get("in_seconds")
                    end = selected.get("out_seconds")
                    if start is not None or end is not None:
                        if not (isinstance(start, (int, float)) and not isinstance(start, bool) and isinstance(end, (int, float)) and not isinstance(end, bool)
                                and abs(start) <= 1e-6 and abs(end - source_duration) <= 1e-6):
                            errors.append(f"{prefix}.video.selected: FULL_SELECT range must cover the whole source when recorded")
            else:
                errors.append(f"{prefix}.video.selected: required at SELECT or later")
        if rank >= STATE_RANK["OBSERVED_STATE_RECORDED"]:
            if unit.get("observed_state_written") is not True:
                errors.append(f"{prefix}.observed_state_written: must be true at OBSERVED_STATE_RECORDED or later")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_production_state.py <production-state.json>")
        return 2
    try:
        data = load_json(Path(argv[1]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    if not isinstance(data, dict):
        print("ERROR: top-level JSON must be an object")
        return 2
    errors = validate_production_state(data)
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("PASS: production state is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
