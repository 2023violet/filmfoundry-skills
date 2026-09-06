"""Shared FilmFoundry runtime constants and JSON helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RUNTIME_STATES = [
    "DRAFT",
    "SPEC_RESOLVED",
    "PREFLIGHT_PASS",
    "READY_FOR_KF",
    "KF_GENERATED",
    "KF_QC_PASS",
    "READY_FOR_VIDEO",
    "VIDEO_GENERATED",
    "VIDEO_QC_PASS",
    "SELECT",
    "OBSERVED_STATE_RECORDED",
    "EDIT_READY",
]
STATE_RANK = {state: i for i, state in enumerate(RUNTIME_STATES)}
EVIDENCE_LEVELS = [
    "UNVERIFIED",
    "OBSERVED_ONCE",
    "REPEATED",
    "PROJECT_VERIFIED",
    "CROSS_PROJECT_VERIFIED",
]
EVIDENCE_RANK = {state: i for i, state in enumerate(EVIDENCE_LEVELS)}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())
