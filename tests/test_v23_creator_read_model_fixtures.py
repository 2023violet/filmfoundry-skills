"""Fixture integrity checks for the additive v2.3 Creator Read Model."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from filmfoundry_v2 import (
    parse_emotional_beat_map,
    validate_dependency_graph,
    validate_asset_registry,
    validate_emotional_beat_map,
    validate_production_state,
    validate_shot_spec,
    validate_workspace_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model"
SOURCE_FIELDS = {
    "source_id",
    "source_kind",
    "path",
    "path_base",
    "parser_id",
    "schema_version",
    "authority_role",
    "scope",
    "required",
}
EXPECTED_FIXTURES = {
    "empty-project",
    "early-development",
    "asset-production",
    "shot-production",
    "blocked-dependency",
    "full-select",
    "partial-select",
    "continuity-conflict",
    "season-emotion",
    "episode-emotion",
    "chinese-project",
    "english-project",
    "smoke-project",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fixture_index() -> list[dict]:
    return read_json(FIXTURES / "fixture-index.json")


def source_path(project_root: Path, catalog: dict, source: dict) -> Path:
    runtime_path = project_root / catalog["runtime_path"]
    base = project_root if source["path_base"] == "WORKSPACE_ROOT" else runtime_path.parent
    resolved = (base / source["path"]).resolve()
    assert resolved.is_relative_to(project_root.resolve())
    return resolved


def fixture_counts(project_root: Path, catalog: dict) -> dict[str, int]:
    counts = {"seasons": 0, "episodes": 0, "assets": 0, "shots": 0, "continuity_chains": 0}
    for source in catalog["sources"]:
        data = read_json(source_path(project_root, catalog, source))
        if source["source_kind"] == "narrative_index":
            counts["seasons"] += sum(node["node_type"] == "SEASON" for node in data["nodes"])
            counts["episodes"] += sum(node["node_type"] == "EPISODE" for node in data["nodes"])
        elif source["source_kind"] == "asset_registry":
            counts["assets"] += len(data)
        elif source["source_kind"] == "shot_spec":
            counts["shots"] += 1
        elif source["source_kind"] == "continuity_chain":
            counts["continuity_chains"] += len(data["chains"])
    return counts


def test_fixture_inventory_is_complete_and_each_catalog_is_resolvable():
    entries = fixture_index()
    assert {entry["fixture_id"] for entry in entries} == EXPECTED_FIXTURES
    assert len(entries) == 13

    for entry in entries:
        project_root = FIXTURES / entry["path"]
        catalog = read_json(project_root / "creator-source-catalog.v1.json")
        runtime = read_json(project_root / catalog["runtime_path"])
        assert catalog["schema_version"] == "creator-source-catalog.v1"
        assert catalog["project_id"] == runtime["project_id"]
        assert len({source["source_id"] for source in catalog["sources"]}) == len(catalog["sources"])
        for source in catalog["sources"]:
            assert SOURCE_FIELDS <= set(source)
            assert source["path_base"] in {"WORKSPACE_ROOT", "RUNTIME_DIR"}
            assert source["authority_role"] in {"CURRENT", "HISTORICAL", "SUPPORTING"}
            assert isinstance(source["required"], bool)
            assert source_path(project_root, catalog, source).is_file()
        assert fixture_counts(project_root, catalog) == entry["expected"]


def test_existing_v2_sources_in_creator_fixtures_remain_valid():
    for entry in fixture_index():
        project_root = FIXTURES / entry["path"]
        catalog = read_json(project_root / "creator-source-catalog.v1.json")
        for source in catalog["sources"]:
            data = read_json(source_path(project_root, catalog, source))
            if source["source_kind"] == "workspace_manifest":
                assert validate_workspace_manifest(data) == []
            elif source["source_kind"] == "asset_registry":
                assert validate_asset_registry(data) == []
            elif source["source_kind"] == "production_state":
                assert validate_production_state(data) == []
            elif source["source_kind"] == "shot_spec":
                assert validate_shot_spec(data) == []
            elif source["source_kind"] == "dependency_graph":
                assert validate_dependency_graph(data).ok
            elif source["source_kind"] == "emotional_beat_map":
                assert validate_emotional_beat_map(parse_emotional_beat_map(data)).ok


def test_smoke_project_has_exact_generic_counts_and_verified_fixture_media():
    entry = next(entry for entry in fixture_index() if entry["fixture_id"] == "smoke-project")
    project_root = FIXTURES / entry["path"]
    catalog = read_json(project_root / "creator-source-catalog.v1.json")
    assert fixture_counts(project_root, catalog) == entry["expected"]
    assets = next(
        read_json(source_path(project_root, catalog, source))
        for source in catalog["sources"]
        if source["source_kind"] == "asset_registry"
    )

    for asset in assets:
        media = project_root / asset["path"]
        assert media.is_file()
        assert hashlib.sha256(media.read_bytes()).hexdigest() == asset["sha256"]

    for path in project_root.rglob("*"):
        assert "wucheng" not in path.name.lower()
    fixture_text = "\n".join(path.read_text(encoding="utf-8") for path in project_root.rglob("*.json"))
    assert "wucheng" not in fixture_text.lower()
