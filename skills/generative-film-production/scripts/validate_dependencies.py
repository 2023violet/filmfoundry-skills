#!/usr/bin/env python3
"""Validate FilmFoundry generation-unit dependency readiness."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from runtime_common import STATE_RANK, load_json


def validate_dependencies(
    graph: dict[str, Any],
    state: dict[str, Any],
    *,
    assets: set[str],
    axes: set[str],
    voices: set[str],
) -> list[str]:
    errors: list[str] = []
    units = graph.get("units")
    state_units = state.get("units") if isinstance(state.get("units"), dict) else {}
    if not isinstance(units, dict):
        return ["units: dependency graph requires object"]
    for unit_id, deps in units.items():
        if not isinstance(deps, dict):
            errors.append(f"units.{unit_id}: dependency entry must be object")
            continue
        hard = deps.get("hard", [])
        if not isinstance(hard, list):
            errors.append(f"units.{unit_id}.hard: must be list")
            continue
        for i, dep in enumerate(hard):
            prefix = f"units.{unit_id}.hard[{i}]"
            if not isinstance(dep, dict):
                errors.append(f"{prefix}: must be object")
                continue
            kind = dep.get("type")
            ident = str(dep.get("id", "")).strip()
            if kind == "unit_state":
                minimum = str(dep.get("at_least", "")).strip().upper()
                current = str((state_units.get(ident) or {}).get("runtime_status", "")).strip().upper()
                if minimum not in STATE_RANK:
                    errors.append(f"{prefix}.at_least: unknown state {minimum}")
                elif current not in STATE_RANK or STATE_RANK[current] < STATE_RANK[minimum]:
                    errors.append(f"{prefix}: {ident} must reach {minimum}; current={current or 'MISSING'}")
            elif kind == "asset":
                if ident not in assets:
                    errors.append(f"{prefix}: required asset {ident} is not ready")
            elif kind == "axis":
                if ident not in axes:
                    errors.append(f"{prefix}: required axis {ident} is not ready")
            elif kind == "voice":
                if ident not in voices:
                    errors.append(f"{prefix}: required voice {ident} is not ready")
            else:
                errors.append(f"{prefix}.type: unsupported dependency type {kind!r}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 7 or argv[1] != "--graph" or argv[3] != "--state" or argv[5] != "--ready":
        print("usage: validate_dependencies.py --graph dependency.json --state production-state.json --ready ready.json")
        return 2
    try:
        graph = load_json(Path(argv[2]))
        state = load_json(Path(argv[4]))
        ready = load_json(Path(argv[6]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_dependencies(
        graph,
        state,
        assets=set(ready.get("assets", [])),
        axes=set(ready.get("axes", [])),
        voices=set(ready.get("voices", [])),
    )
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("PASS: hard dependencies are ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
