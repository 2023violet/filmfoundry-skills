#!/usr/bin/env python3
"""Validate a FilmFoundry runtime state transition."""
from __future__ import annotations

import sys
from runtime_common import RUNTIME_STATES, STATE_RANK


def validate_state_transition(old: str, new: str) -> list[str]:
    old = old.strip().upper()
    new = new.strip().upper()
    if old not in STATE_RANK:
        return [f"unknown source runtime state: {old}"]
    if new not in STATE_RANK:
        return [f"unknown target runtime state: {new}"]
    if old == new:
        return []
    if STATE_RANK[new] != STATE_RANK[old] + 1:
        return [f"illegal runtime transition: {old} -> {new}; gates may not be skipped"]
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: validate_state_transition.py <old-state> <new-state>")
        return 2
    errors = validate_state_transition(argv[1], argv[2])
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: runtime state transition is legal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
