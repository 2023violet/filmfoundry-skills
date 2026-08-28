#!/usr/bin/env python3
"""Heuristic linter for compiled AI-video prompts.

The linter intentionally reports explainable warnings rather than pretending to
understand visual quality. It catches structural smells that FilmFoundry asks an
agent to resolve before expensive generation.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

UNVERIFIABLE = (
    "keep it consistent",
    "keep consistent",
    "保持一致",
    "保持人物一致",
    "cinematic throughout",
)
SOUP_TERMS = (
    "cinematic",
    "epic",
    "masterpiece",
    "ultra detailed",
    "award winning",
    "stunning",
    "dramatic",
    "beautiful",
    "8k",
    "best quality",
)

CAMERA_MOVE_PATTERNS = {
    "push_in": r"\b(?:push[- ]?in|dolly in|camera pushes? in)\b|缓慢前推|镜头前推|推镜",
    "pull_back": r"\b(?:pull[- ]?back|pulls? back|pull out|dolly out|camera pulls? back)\b|缓慢拉远|镜头拉远|拉镜",
    "orbit": r"\b(?:orbits?|orbiting|arc around|circle around)\b|环绕|刷锅",
    "pan": r"\bpan(?:s|ning)?\b|横摇",
    "tilt": r"\btilt(?:s|ing)?\b|俯仰摇",
    "track": r"\b(?:track|tracking|truck|follow shot)\b|跟拍|横移",
    "crane": r"\b(?:crane|jib)\b|升降",
}

HARD_CLOCK_TERMS = (
    "lip sync",
    "voiceover",
    "voice-over",
    "supplied audio",
    "music beat",
    "beat sync",
    "fixed reveal",
    "brand reveal",
    "对白同步",
    "口型",
    "配音",
    "音乐节拍",
)


def lint_prompt(text: str, route: str = "generic") -> list[str]:
    findings: list[str] = []
    lower = text.lower()
    route = route.strip().lower()

    hits = [phrase for phrase in UNVERIFIABLE if phrase.lower() in lower]
    if hits:
        findings.append(
            "Unverifiable intent: replace generic consistency/quality language with visible locks or observable end states: "
            + ", ".join(hits)
        )

    reference_mentions = re.findall(r"(?:reference image|参考图)\s*\d+", lower, flags=re.I)
    has_role_binding = "controls" in lower or "控制" in text
    if reference_mentions and not has_role_binding:
        findings.append("Reference role missing: bind each referenced image to what it controls and what it does not control")

    pointer_ids = sorted(set(re.findall(r"\bref_[a-z0-9_]+\b", lower, flags=re.I)))
    unbound_pointers: list[str] = []
    unbounded_pointers: list[str] = []
    for pointer in pointer_ids:
        binding_pattern = re.compile(
            rf"\b{re.escape(pointer)}\b[^\n]{{0,200}}(?:\bcontrols?\b|控制)",
            flags=re.I,
        )
        boundary_pattern = re.compile(
            rf"\b{re.escape(pointer)}\b[^\n]{{0,200}}(?:does_not_control|does\s+not\s+control|不控制)",
            flags=re.I,
        )
        if not binding_pattern.search(text):
            unbound_pointers.append(pointer.upper())
        elif not boundary_pattern.search(text):
            unbounded_pointers.append(pointer.upper())
    if unbound_pointers:
        findings.append(
            "Reference role missing: explicit pointer bindings required for " + ", ".join(unbound_pointers)
        )
    if unbounded_pointers:
        findings.append(
            "Reference boundary missing: does_not_control is required for " + ", ".join(unbounded_pointers)
        )

    stages = len(re.findall(r"\bstage\s*\d+|阶段\s*\d+", lower, flags=re.I))
    end_states = len(re.findall(r"end state\s*:|结束状态\s*[：:]", lower, flags=re.I))
    if stages and end_states < stages:
        findings.append(f"End state coverage: {stages} stages found but only {end_states} explicit end state markers")

    timestamp_count = len(
        re.findall(r"(?<!\w)\d+(?:\.\d+)?\s*[-–—]\s*\d+(?:\.\d+)?\s*(?:s\b|秒)", lower)
    )
    hard_clock = any(term in lower for term in HARD_CLOCK_TERMS)
    if timestamp_count >= 4 and not hard_clock:
        findings.append(
            "Timestamp density: dense second-level timing has no named hard-clock reason; prefer event order or stages + end states"
        )

    camera_scan = lower
    for negation in (
        r"\bno\s+(?:orbit|pan|tilt|tracking|push[- ]?in|pull[- ]?back)\b",
        r"\bdo not\s+(?:orbit|pan|tilt|track|push|pull)\b",
        r"\bdon't\s+(?:orbit|pan|tilt|track|push|pull)\b",
        r"不要(?:环绕|刷锅|横摇|俯仰摇|跟拍|前推|拉远)",
    ):
        camera_scan = re.sub(negation, "", camera_scan, flags=re.I)
    camera_moves = [
        name for name, pattern in CAMERA_MOVE_PATTERNS.items()
        if re.search(pattern, camera_scan, flags=re.I)
    ]
    if len(camera_moves) >= 3:
        findings.append(
            "Camera move conflict: too many distinct camera moves in one clip ("
            + ", ".join(camera_moves)
            + "); use one coherent physically explainable camera path or split the clip"
        )

    soup_hits = [term for term in SOUP_TERMS if term in lower]
    comma_like = len(re.findall(r"[,，]", text))
    if len(set(soup_hits)) >= 6 and comma_like >= 5:
        findings.append(
            "Keyword soup: replace stacked quality adjectives with observable composition, lighting, camera, texture, and motion decisions"
        )

    if route == "i2v" and len(text.split()) > 350 and not any(k in lower for k in ("preserve", "must preserve", "锁定")):
        findings.append("I2V over-description: long prompt lacks explicit must-preserve locks; let the start image own stable appearance")

    return findings


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print("usage: prompt_lint.py <prompt.txt> [route]")
        return 2
    path = Path(argv[1])
    route = argv[2] if len(argv) == 3 else "generic"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2
    findings = lint_prompt(text, route=route)
    if findings:
        for finding in findings:
            print(f"FAIL: {finding}")
        return 1
    print("PASS: no structural prompt lint findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
