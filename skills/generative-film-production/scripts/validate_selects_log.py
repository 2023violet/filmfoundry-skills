#!/usr/bin/env python3
"""Validate FilmFoundry Selects log CSV, including v1.2 partial selections."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

ALLOWED_DISPOSITIONS = {"FULL_SELECT", "PARTIAL_SELECT"}
EPS = 1e-6


def _number(row: dict[str, str], key: str) -> tuple[float | None, str | None]:
    raw = (row.get(key) or "").strip()
    if not raw:
        return None, None
    try:
        return float(raw), None
    except ValueError:
        return None, f"{key}: must be numeric when present"


def validate_select_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    for i, row in enumerate(rows, start=2):
        prefix = f"row {i}"
        disposition = (row.get("disposition") or "").strip().upper()
        # Legacy v1.1 rows without disposition remain readable.
        if not disposition:
            continue
        if disposition not in ALLOWED_DISPOSITIONS:
            errors.append(f"{prefix}.disposition: must be one of {sorted(ALLOWED_DISPOSITIONS)}")
            continue

        values: dict[str, float | None] = {}
        for key in ("source_in_seconds", "source_out_seconds", "source_duration_seconds", "selected_duration_seconds"):
            value, error = _number(row, key)
            values[key] = value
            if error:
                errors.append(f"{prefix}.{error}")

        if disposition == "PARTIAL_SELECT":
            for key, value in values.items():
                if value is None:
                    errors.append(f"{prefix}.{key}: required for PARTIAL_SELECT")
            start = values["source_in_seconds"]
            end = values["source_out_seconds"]
            duration = values["source_duration_seconds"]
            selected = values["selected_duration_seconds"]
            if all(v is not None for v in (start, end, duration, selected)):
                assert start is not None and end is not None and duration is not None and selected is not None
                if start < 0:
                    errors.append(f"{prefix}.source_in_seconds: cannot be negative")
                if duration <= 0:
                    errors.append(f"{prefix}.source_duration_seconds: must be positive")
                if end <= start:
                    errors.append(f"{prefix}.source_out_seconds: must be greater than source_in_seconds")
                if end > duration + EPS:
                    errors.append(f"{prefix}.source_out_seconds: cannot exceed source duration")
                if abs(selected - (end - start)) > 1e-3:
                    errors.append(f"{prefix}.selected_duration_seconds: must equal source_out_seconds - source_in_seconds")
                if start <= EPS and abs(end - duration) <= 1e-3:
                    errors.append(f"{prefix}.disposition: PARTIAL_SELECT must exclude some source footage")
        else:
            # FULL_SELECT may omit timing for compatibility. If timing is supplied,
            # it must cover the entire source.
            supplied = [v is not None for v in values.values()]
            if any(supplied):
                if not all(supplied):
                    errors.append(f"{prefix}: FULL_SELECT timing must be complete when any timing field is supplied")
                else:
                    start = values["source_in_seconds"]
                    end = values["source_out_seconds"]
                    duration = values["source_duration_seconds"]
                    selected = values["selected_duration_seconds"]
                    assert start is not None and end is not None and duration is not None and selected is not None
                    if abs(start) > 1e-3 or abs(end - duration) > 1e-3 or abs(selected - duration) > 1e-3:
                        errors.append(f"{prefix}: FULL_SELECT timing must cover the whole source")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_selects_log.py <selects-log.csv>")
        return 2
    path = Path(argv[1])
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_select_rows(rows)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: selects log is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
