#!/usr/bin/env python3
"""Validate a FilmFoundry v1.1/v1.2 project runtime manifest and its components.

FilmFoundry v1.3 keeps the runtime schema backward-compatible while allowing an
optional capability-scoped model route registry. A broad model profile is still
accepted, but READY_FOR_VIDEO may also be authorized by a route-local evidence
gate when the manifest declares one explicitly.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

from runtime_common import STATE_RANK, load_json, nonempty
from validate_asset_registry import validate_rows as validate_asset_rows
from validate_axis_registry import validate_axis_registry
from validate_voice_registry import validate_voice_registry
from validate_model_profile import validate_model_profile
from validate_production_state import validate_production_state
from validate_dependencies import validate_dependencies
from validate_content_market_gate import validate_content_market_gate

V11_ASSET_COLUMNS = {
    "asset_id", "asset_type", "asset_class", "file_name", "canonical_descriptor",
    "state_variant", "parent_asset_id", "version", "sha256", "status",
    "reference_id", "reference_role", "does_not_control", "supersedes",
}

REQUIRED_PATHS = (
    "asset_registry",
    "axis_registry",
    "voice_registry",
    "production_state",
    "dependency_graph",
    "model_profile",
)


def _resolve(base_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base_dir / path


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def validate_project_runtime(manifest: dict[str, Any], *, base_dir: Path) -> list[str]:
    errors: list[str] = []
    if not nonempty(manifest.get("project_id")):
        errors.append("project_id: required")
    runtime_version = str(manifest.get("runtime_version", "")).strip()
    if runtime_version not in {"1.1", "1.2"}:
        errors.append("runtime_version: expected 1.1 or 1.2")

    project_goal = str(manifest.get("project_goal", "")).strip().upper()
    commercial_goals = {"AUDIENCE_GROWTH", "MONETIZATION", "SERIES_BUSINESS"}
    market_gate_path = manifest.get("content_market_gate")
    if runtime_version == "1.2" and not project_goal:
        errors.append("project_goal: required in v1.2 runtime")
    if runtime_version == "1.2" and project_goal in commercial_goals and not nonempty(market_gate_path):
        errors.append("content_market_gate: required path for commercial/series project_goal in v1.2")

    paths: dict[str, Path] = {}
    for field in REQUIRED_PATHS:
        value = manifest.get(field)
        if not nonempty(value):
            errors.append(f"{field}: required path")
            continue
        path = _resolve(base_dir, str(value))
        paths[field] = path
        if not path.is_file():
            errors.append(f"{field}: file not found: {path}")
    if nonempty(market_gate_path):
        market_path = _resolve(base_dir, str(market_gate_path))
        paths["content_market_gate"] = market_path
        if not market_path.is_file():
            errors.append(f"content_market_gate: file not found: {market_path}")

    route_registry_path = manifest.get("model_route_registry")
    if nonempty(route_registry_path):
        route_path = _resolve(base_dir, str(route_registry_path))
        paths["model_route_registry"] = route_path
        if not route_path.is_file():
            errors.append(f"model_route_registry: file not found: {route_path}")
    if errors:
        return errors

    try:
        with paths["asset_registry"].open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            asset_fields = set(reader.fieldnames or [])
            asset_rows = list(reader)
        missing_asset_columns = V11_ASSET_COLUMNS - asset_fields
        if missing_asset_columns:
            errors.append("v1.1 asset registry missing columns: " + ", ".join(sorted(missing_asset_columns)))
        axes = load_json(paths["axis_registry"])
        voices = load_json(paths["voice_registry"])
        state = load_json(paths["production_state"])
        deps = load_json(paths["dependency_graph"])
        profile = load_json(paths["model_profile"])
        market_gate = load_json(paths["content_market_gate"]) if "content_market_gate" in paths else None
        route_registry = load_json(paths["model_route_registry"]) if "model_route_registry" in paths else None
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"runtime component read error: {exc}"]

    errors.extend(f"asset_registry: {e}" for e in validate_asset_rows(asset_rows))
    errors.extend(f"axis_registry: {e}" for e in validate_axis_registry(axes if isinstance(axes, dict) else {}))
    errors.extend(f"voice_registry: {e}" for e in validate_voice_registry(voices if isinstance(voices, dict) else {}))
    errors.extend(f"production_state: {e}" for e in validate_production_state(state if isinstance(state, dict) else {}))
    errors.extend(f"model_profile: {e}" for e in validate_model_profile(profile if isinstance(profile, dict) else {}))
    if market_gate is not None:
        errors.extend(f"content_market_gate: {e}" for e in validate_content_market_gate(market_gate if isinstance(market_gate, dict) else {}))

    ready_assets = {
        (row.get("asset_id") or "").strip()
        for row in asset_rows
        if (row.get("status") or "PLANNED").strip().upper() == "LOCKED"
    }
    ready_axes = {
        str(axis.get("axis_id", "")).strip()
        for axis in (axes.get("axes", []) if isinstance(axes, dict) else [])
        if isinstance(axis, dict) and str(axis.get("status", "")).strip().upper() == "LOCKED"
    }
    ready_voices = {
        str(voice.get("voice_id", "")).strip()
        for voice in (voices.get("voices", []) if isinstance(voices, dict) else [])
        if isinstance(voice, dict) and str(voice.get("status", "")).strip().upper() == "LOCKED"
    }
    errors.extend(
        f"dependencies: {e}"
        for e in validate_dependencies(
            deps if isinstance(deps, dict) else {},
            state if isinstance(state, dict) else {},
            assets=ready_assets,
            axes=ready_axes,
            voices=ready_voices,
        )
    )

    # Market-gate decisions constrain expensive scale for v1.2 commercial projects.
    if runtime_version == "1.2" and project_goal in commercial_goals and isinstance(market_gate, dict):
        market_decision = str(market_gate.get("decision", "")).strip().upper()
        for unit_id, unit in (state.get("units", {}) if isinstance(state, dict) else {}).items():
            if not isinstance(unit, dict):
                continue
            runtime_status = str(unit.get("runtime_status", "")).strip().upper()
            if runtime_status not in STATE_RANK or STATE_RANK[runtime_status] < STATE_RANK["READY_FOR_KF"]:
                continue
            scope = str(unit.get("production_scope", "")).strip().upper()
            if scope not in {"MVP", "PRODUCTION"}:
                errors.append(f"market gate: {unit_id}.production_scope must be MVP or PRODUCTION before READY_FOR_KF in v1.2 commercial runtime")
                continue
            if market_decision == "NO_GO":
                errors.append(f"market gate NO_GO blocks {unit_id} from READY_FOR_KF or later")
            elif market_decision in {"TRAFFIC_EXPERIMENT", "MVP_ONLY"} and scope == "PRODUCTION":
                errors.append(f"market gate {market_decision} blocks PRODUCTION scope for {unit_id}; only MVP generation is allowed before PRODUCTION_APPROVED")

    # A project may initialize with an unverified broad model profile. v1.3 also
    # supports capability-scoped route evidence so unrelated provider tests do
    # not block a narrowly defined technical pilot. The route gate must be
    # explicit and machine-readable; absence of such evidence still blocks.
    verification = str(profile.get("verification_status", "")).strip().upper() if isinstance(profile, dict) else ""
    route_entries = route_registry.get("routes", {}) if isinstance(route_registry, dict) else {}
    allowed_scoped_release = {"PILOT_PASS", "REPEATED_LOCAL", "STRONG"}

    for unit_id, unit in (state.get("units", {}) if isinstance(state, dict) else {}).items():
        runtime_status = str((unit or {}).get("runtime_status", "")).strip().upper() if isinstance(unit, dict) else ""
        if runtime_status not in STATE_RANK or STATE_RANK[runtime_status] < STATE_RANK["READY_FOR_VIDEO"]:
            continue
        if verification == "MODEL_PROFILE_MINIMUM_PASS":
            continue

        gate_id = str((unit or {}).get("provider_route_gate", "")).strip() if isinstance(unit, dict) else ""
        route = route_entries.get(gate_id) if isinstance(route_entries, dict) and gate_id else None
        release_status = str((route or {}).get("release_status", "")).strip().upper() if isinstance(route, dict) else ""
        if release_status not in allowed_scoped_release:
            if gate_id:
                errors.append(
                    f"model evidence required before {unit_id} can reach READY_FOR_VIDEO or later: "
                    f"route gate {gate_id} is {release_status or 'UNVERIFIED'}"
                )
            else:
                errors.append(
                    f"model profile minimum evidence or an approved provider_route_gate required before "
                    f"{unit_id} can reach READY_FOR_VIDEO or later"
                )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_project_runtime.py <project-runtime.json>")
        return 2
    manifest_path = Path(argv[1])
    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    if not isinstance(manifest, dict):
        print("ERROR: top-level runtime manifest must be object")
        return 2
    errors = validate_project_runtime(manifest, base_dir=manifest_path.parent)
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("PASS: FilmFoundry project runtime is structurally valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
