#!/usr/bin/env python3
"""Transition-aware continuity checks for adjacent shot ledger entries."""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any


def _text(d: dict[str, Any], key: str) -> str:
    value = d.get(key, "")
    return value.strip() if isinstance(value, str) else ""


def validate_transition(prev: dict[str, Any], nxt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    out_type = _text(prev, "transition_out") or "hard_cut"
    in_type = _text(nxt, "transition_in") or out_type
    if out_type != in_type:
        errors.append(f"transition mismatch: previous={out_type}, next={in_type}")
        return errors

    kind = out_type
    if kind == "continuous":
        tail = _text(prev, "tail_frame_id")
        source = _text(nxt, "start_frame_source")
        if not tail or source != tail:
            errors.append("continuous transition: next start_frame_source must relay previous tail_frame_id")
        if _text(prev, "end_state") != _text(nxt, "initial_state"):
            errors.append("continuous transition: next initial_state must match previous end_state")
        for field in ("asset_state", "wardrobe_state", "light_state", "time_state"):
            prev_value = _text(prev, field)
            next_value = _text(nxt, field)
            if not prev_value or not next_value:
                errors.append(f"continuous transition: {field} is required on both shots")
            elif prev_value != next_value:
                errors.append(f"continuous transition: {field} continuity mismatch")

    elif kind == "reverse_angle":
        for field in (
            "camera_axis",
            "screen_direction",
            "prop_state",
            "asset_state",
            "wardrobe_state",
            "light_state",
            "time_state",
        ):
            prev_value = _text(prev, field)
            next_value = _text(nxt, field)
            if not prev_value or not next_value:
                errors.append(f"reverse_angle: {field} is required on both shots")
            elif prev_value != next_value:
                errors.append(f"reverse_angle: {field} continuity mismatch")

        eyeline_fields = ("eyeline_subject", "eyeline_target", "eyeline_screen_direction")
        missing_eyeline = [field for field in eyeline_fields if not _text(prev, field) or not _text(nxt, field)]
        if missing_eyeline:
            errors.append(
                "reverse_angle: structured eyeline fields are required on both shots: "
                + ", ".join(missing_eyeline)
            )
        else:
            prev_subject = _text(prev, "eyeline_subject")
            prev_target = _text(prev, "eyeline_target")
            next_subject = _text(nxt, "eyeline_subject")
            next_target = _text(nxt, "eyeline_target")
            if prev_subject != next_target or prev_target != next_subject:
                errors.append("reverse_angle: eyeline subject/target must be reciprocal across the cut")

            prev_dir = _text(prev, "eyeline_screen_direction").lower()
            next_dir = _text(nxt, "eyeline_screen_direction").lower()
            opposite = {("left", "right"), ("right", "left"), ("center", "center")}
            if (prev_dir, next_dir) not in opposite:
                errors.append("reverse_angle: eyeline screen directions must be opposite across the cut")

    elif kind == "match_cut":
        prev_feature = _text(prev, "match_feature")
        next_feature = _text(nxt, "match_feature")
        if not prev_feature or not next_feature:
            errors.append("match_cut: match_feature is required on both shots")
        elif prev_feature != next_feature:
            errors.append("match_cut: match_feature must describe the same intended match")

    elif kind in {"hard_cut", "insert", "cutaway"}:
        # No tail-frame requirement. State differences may be intentional and are
        # reviewed at the story/ledger layer rather than forced as pixel continuity.
        pass
    else:
        errors.append(f"unsupported transition type: {kind}")

    return errors


def _read_two_rows(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if len(rows) != 2:
        raise ValueError("continuity CLI expects exactly two adjacent ledger rows")
    return rows[0], rows[1]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: continuity_lint.py <two-row-continuity.csv>")
        return 2
    try:
        prev, nxt = _read_two_rows(Path(argv[1]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_transition(prev, nxt)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: transition continuity checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
