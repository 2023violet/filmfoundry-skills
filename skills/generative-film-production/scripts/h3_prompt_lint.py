#!/usr/bin/env python3
"""MiniMax H3 compiled-prompt gate for FilmFoundry v1.1.

This linter validates FilmFoundry structure. It deliberately does not claim
that MiniMax H3 obeys semantic reference roles; R1 is allowed only when the
project Model Profile has repeated-or-stronger evidence for that behavior.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from runtime_common import EVIDENCE_RANK
from prompt_lint import lint_prompt

REQUIRED_SECTIONS = [
    "REFERENCE BINDING",
    "GLOBAL SHOT",
    "LOCKS",
    "CAMERA",
    "ACTING",
    "PHYSICS / PERSISTENCE",
    "AUDIO",
    "FAILURE CONSTRAINTS",
]

POINTER_RE = re.compile(r"@图\s*\d+|\{\{[^{}\n]+\}\}|\bREF_[A-Z0-9_]+\b", re.I)


def _has_section(text: str, section: str) -> bool:
    return bool(re.search(rf"(?:【|\[)\s*{re.escape(section)}\s*(?:】|\])", text, flags=re.I))


def _section_body(text: str, section: str) -> str:
    match = re.search(
        rf"(?:【|\[)\s*{re.escape(section)}\s*(?:】|\])\s*(.*?)(?=(?:【|\[)[A-Z /+]+(?:】|\])|\Z)",
        text,
        flags=re.I | re.S,
    )
    return match.group(1).strip() if match else ""


def lint_h3_prompt(text: str, *, adapter_mode: str = "R2", role_binding_status: str = "UNVERIFIED") -> list[str]:
    errors: list[str] = []
    adapter_mode = adapter_mode.strip().upper()
    role_binding_status = role_binding_status.strip().upper()

    for section in REQUIRED_SECTIONS:
        if not _has_section(text, section):
            errors.append(f"Missing required H3 section: {section}")

    has_stages = _has_section(text, "ACTION STAGES + END STATES")
    has_timing = _has_section(text, "TIMING")
    if not has_stages and not has_timing:
        errors.append("Missing required H3 section: ACTION STAGES + END STATES or TIMING")
    if has_stages and has_timing:
        errors.append("Timing grammar conflict: use ACTION STAGES + END STATES or TIMING, not both")

    if adapter_mode not in {"R1", "R2", "R3"}:
        errors.append("adapter_mode: must be R1, R2, or R3")
    if adapter_mode == "R1":
        if role_binding_status not in EVIDENCE_RANK or EVIDENCE_RANK[role_binding_status] < EVIDENCE_RANK["REPEATED"]:
            errors.append("R1 semantic reference role binding requires VERIFIED evidence at REPEATED or stronger level in the Model Profile")

    ref_body = _section_body(text, "REFERENCE BINDING")
    pointer_matches = list(POINTER_RE.finditer(ref_body))
    pointers = {match.group(0) for match in pointer_matches}

    if adapter_mode == "R1" and pointer_matches:
        # Semantic role binding is meaningful only when every submitted visual
        # reference has both an explicit positive role and an explicit boundary.
        # Evaluate the text local to each pointer (up to the next pointer), so a
        # well-specified reference cannot accidentally make an adjacent bare
        # reference look valid.
        for index, match in enumerate(pointer_matches):
            start = match.start()
            end = pointer_matches[index + 1].start() if index + 1 < len(pointer_matches) else len(ref_body)
            segment = ref_body[start:end]
            pointer = match.group(0)
            if not re.search(r"\bcontrols?\b|控制", segment, flags=re.I):
                errors.append(f"R1 reference {pointer} missing explicit controls role")
            if not re.search(r"does[_ -]?not[_ -]?control|不控制|不得继承|不要继承", segment, flags=re.I):
                errors.append(f"R1 reference {pointer} missing explicit does_not_control boundary")

    if adapter_mode == "R3" and len(pointers) > 1:
        errors.append("R3 precomposed-keyframe mode allows only one visual reference pointer; move identity/style locking upstream into the keyframe")

    # One submitted prompt must have one execution duration. Alternative
    # 6-second/10-second branches are planning notes, not compiled output.
    duration_alternatives = set(re.findall(r"(?:\bif\b|如果|若)\s*(?:是\s*)?(?:平台固定生成\s*)?(\d+(?:\.\d+)?)\s*(?:seconds?|s|秒)", text, flags=re.I))
    if len(duration_alternatives) >= 2:
        errors.append("Duration ambiguity: compiled H3 prompt contains multiple alternative duration plans; compile exactly one actual duration")

    timing = _section_body(text, "ACTION STAGES + END STATES") if has_stages else _section_body(text, "TIMING")
    if timing:
        uses_stages = bool(re.search(r"\bstage\s*\d+|阶段\s*\d+", timing, flags=re.I))
        uses_hard_timing = has_timing
        if (uses_stages or uses_hard_timing) and not re.search(r"final\s+end\s+state|最终(?:可见)?结束状态|最终状态", timing, flags=re.I):
            errors.append("FINAL END STATE is required when stage or hard timing is used")

    # Audio must be explicitly owned even when silent/post-only.
    audio = _section_body(text, "AUDIO")
    if _has_section(text, "AUDIO") and not audio:
        errors.append("AUDIO section must explicitly state dialogue/music/ambience ownership or none")

    # Reuse the provider-agnostic structural smells too (camera conflicts,
    # keyword soup, unjustified dense timestamps, I2V over-description).
    for finding in lint_prompt(text, route="i2v"):
        if finding not in errors:
            errors.append(finding)

    return errors


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3, 4}:
        print("usage: h3_prompt_lint.py <prompt.txt> [R1|R2|R3] [role-binding-evidence]")
        return 2
    try:
        text = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2
    mode = argv[2] if len(argv) >= 3 else "R2"
    evidence = argv[3] if len(argv) >= 4 else "UNVERIFIED"
    errors = lint_h3_prompt(text, adapter_mode=mode, role_binding_status=evidence)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: MiniMax H3 compiled prompt passes structural gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
