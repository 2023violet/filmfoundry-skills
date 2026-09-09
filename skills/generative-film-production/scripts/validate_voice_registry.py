#!/usr/bin/env python3
"""Validate FilmFoundry voice registry JSON."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from runtime_common import load_json, nonempty

ALLOWED_STATUS = {"PLANNED", "DRAFT", "LOCKED", "RETIRED"}


def validate_voice_registry(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    voices = data.get("voices")
    if not isinstance(voices, list):
        return ["voices: required list"]
    seen: set[str] = set()
    for i, voice in enumerate(voices):
        prefix = f"voices[{i}]"
        if not isinstance(voice, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        voice_id = str(voice.get("voice_id", "")).strip()
        if not voice_id:
            errors.append(f"{prefix}.voice_id: required")
        elif voice_id in seen:
            errors.append(f"{prefix}.voice_id: duplicate {voice_id}")
        seen.add(voice_id)
        if not nonempty(voice.get("character_id")):
            errors.append(f"{prefix}.character_id: required")
        status = str(voice.get("status", "PLANNED")).strip().upper()
        if status not in ALLOWED_STATUS:
            errors.append(f"{prefix}.status: unsupported {status}")
        if status == "LOCKED":
            for field in ("provider", "voice_model", "voice_reference"):
                if not nonempty(voice.get(field)):
                    errors.append(f"{prefix}.{field}: required for LOCKED voice")
            rates = voice.get("speech_rate")
            if not isinstance(rates, dict) or not rates:
                errors.append(f"{prefix}.speech_rate: measured speech-rate map required for LOCKED voice")
            else:
                for label, value in rates.items():
                    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
                        errors.append(f"{prefix}.speech_rate.{label}: must be positive measured numeric rate")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_voice_registry.py <voice-registry.json>")
        return 2
    try:
        data = load_json(Path(argv[1]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_voice_registry(data if isinstance(data, dict) else {})
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("PASS: voice registry is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
