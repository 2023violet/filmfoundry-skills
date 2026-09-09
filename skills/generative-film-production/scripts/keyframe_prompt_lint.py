#!/usr/bin/env python3
"""Structural linter for FilmFoundry keyframe-generation prompts."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = [
    "REFERENCE BINDING",
    "SHOT / UNIT",
    "VISUAL STYLE",
    "CHARACTER LOCK",
    "LOCATION LOCK",
    "PROP LOCK",
    "SHOT SIZE + PHYSICAL CAMERA",
    "COMPOSITION",
    "BLOCKING",
    "ACTION MOMENT",
    "ACTING",
    "LIGHTING",
    "CONTINUITY INPUT",
    "MUST PRESERVE",
    "FAILURE CONSTRAINTS",
]


def _section_pattern(section: str) -> str:
    return rf"(?:【|\[)\s*{re.escape(section)}\s*(?:】|\])"


def _body(text: str, section: str) -> str:
    m = re.search(
        _section_pattern(section) + r"\s*(.*?)(?=(?:【|\[)[A-Z /+]+(?:】|\])|\Z)",
        text,
        flags=re.I | re.S,
    )
    return m.group(1).strip() if m else ""


def lint_keyframe_prompt(text: str) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if not re.search(_section_pattern(section), text, flags=re.I):
            errors.append(f"Missing required keyframe section: {section}")

    moment = _body(text, "ACTION MOMENT")
    if re.search(_section_pattern("ACTION MOMENT"), text, flags=re.I) and not moment:
        errors.append("ACTION MOMENT: required single still moment")

    # A keyframe prompt may describe a moment that implies previous action, but
    # it must not contain a video timeline or multi-stage sequence to execute.
    stage_count = len(re.findall(r"\bstage\s*\d+|阶段\s*\d+", moment, flags=re.I))
    timestamp_count = len(re.findall(r"\d+(?:\.\d+)?\s*[-–—]\s*\d+(?:\.\d+)?\s*(?:s\b|秒)", moment, flags=re.I))
    if stage_count >= 2 or timestamp_count >= 2:
        errors.append("Keyframe sequence/timeline leak: ACTION MOMENT must describe one still image, not a video sequence")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: keyframe_prompt_lint.py <prompt.txt>")
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = lint_keyframe_prompt(text)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: keyframe prompt passes structural gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
