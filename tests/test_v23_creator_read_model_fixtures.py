"""Fixture integrity checks for the additive v2.3 Creator Read Model."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from filmfoundry import (
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
    "wucheng-frozen",
}
SUPPORTED_SOURCE_KINDS = {
    "workspace_manifest",
    "narrative_index",
    "asset_registry",
    "production_state",
    "shot_spec",
    "continuity_chain",
    "dependency_graph",
    "emotional_beat_map",
}
NARRATIVE_NODE_FIELDS = {
    "node_id",
    "node_type",
    "display_name",
    "narrative_responsibility",
    "parent_id",
    "canon_source",
}
CONTINUITY_CHAIN_FIELDS = {"chain_id", "entity_id", "edges"}
CONTINUITY_EDGE_FIELDS = {"from_shot_id", "to_shot_id", "field", "from_value", "to_value"}


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


def validate_runtime_shape(runtime: dict, project_id: str) -> None:
    assert isinstance(runtime, dict)
    assert runtime.get("schema_version") == "project-runtime.v1"
    assert runtime.get("project_id") == project_id
    assert isinstance(runtime.get("phase"), str) and runtime["phase"]


def validate_catalog_shape(catalog: dict) -> None:
    assert isinstance(catalog, dict)
    assert {"schema_version", "project_id", "runtime_path", "sources"} <= set(catalog)
    assert catalog["schema_version"] == "creator-source-catalog.v1"
    assert isinstance(catalog["project_id"], str) and catalog["project_id"]
    assert isinstance(catalog["runtime_path"], str) and catalog["runtime_path"]
    assert isinstance(catalog["sources"], list)


def validate_catalog_source_shape(source: dict) -> None:
    assert SOURCE_FIELDS <= set(source)
    for field in SOURCE_FIELDS - {"required"}:
        assert isinstance(source[field], str) and source[field]
    assert isinstance(source["required"], bool)
    assert source["source_kind"] in SUPPORTED_SOURCE_KINDS


def validate_narrative_index_shape(data: dict) -> None:
    assert isinstance(data, dict)
    assert data.get("schema_version") == "narrative-index.v1"
    assert isinstance(data.get("nodes"), list)
    for node in data["nodes"]:
        assert isinstance(node, dict)
        assert NARRATIVE_NODE_FIELDS <= set(node)
        for field in NARRATIVE_NODE_FIELDS - {"parent_id"}:
            assert isinstance(node[field], str) and node[field]
        assert node["parent_id"] is None or (
            isinstance(node["parent_id"], str) and node["parent_id"]
        )


def validate_continuity_chain_shape(data: dict) -> None:
    assert isinstance(data, dict)
    assert data.get("schema_version") == "continuity-chain.v1"
    assert isinstance(data.get("chains"), list)
    for chain in data["chains"]:
        assert isinstance(chain, dict)
        assert CONTINUITY_CHAIN_FIELDS <= set(chain)
        for field in CONTINUITY_CHAIN_FIELDS - {"edges"}:
            assert isinstance(chain[field], str) and chain[field]
        assert isinstance(chain["edges"], list)
        for edge in chain["edges"]:
            assert isinstance(edge, dict)
            assert CONTINUITY_EDGE_FIELDS <= set(edge)
            assert all(isinstance(edge[field], str) and edge[field] for field in CONTINUITY_EDGE_FIELDS)


def validate_declared_source_shape(source: dict, data: object) -> None:
    if source["source_kind"] == "narrative_index":
        validate_narrative_index_shape(data)
    elif source["source_kind"] == "continuity_chain":
        validate_continuity_chain_shape(data)
    elif source["source_kind"] not in SUPPORTED_SOURCE_KINDS:
        raise AssertionError(f"unsupported fixture source_kind: {source['source_kind']}")


def fixture_counts(project_root: Path, catalog: dict) -> dict[str, int]:
    counts = {"seasons": 0, "episodes": 0, "assets": 0, "shots": 0, "continuity_chains": 0}
    for source in catalog["sources"]:
        if source["source_kind"] not in SUPPORTED_SOURCE_KINDS:
            raise AssertionError(f"unsupported fixture source_kind: {source['source_kind']}")
        data = read_json(source_path(project_root, catalog, source))
        validate_declared_source_shape(source, data)
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
    assert len(entries) == 14

    for entry in entries:
        project_root = FIXTURES / entry["path"]
        catalog = read_json(project_root / "creator-source-catalog.v1.json")
        validate_catalog_shape(catalog)
        runtime = read_json(project_root / catalog["runtime_path"])
        validate_runtime_shape(runtime, catalog["project_id"])
        assert catalog["schema_version"] == "creator-source-catalog.v1"
        assert catalog["project_id"] == runtime["project_id"]
        assert len({source["source_id"] for source in catalog["sources"]}) == len(catalog["sources"])
        for source in catalog["sources"]:
            validate_catalog_source_shape(source)
            assert source["path_base"] in {"WORKSPACE_ROOT", "RUNTIME_DIR"}
            assert source["authority_role"] in {"CURRENT", "HISTORICAL", "SUPPORTING"}
            assert isinstance(source["required"], bool)
            source_file = source_path(project_root, catalog, source)
            assert source_file.is_file()
            validate_declared_source_shape(source, read_json(source_file))
        assert fixture_counts(project_root, catalog) == entry["expected"]


def test_existing_v2_sources_in_creator_fixtures_remain_valid():
    for entry in fixture_index():
        project_root = FIXTURES / entry["path"]
        catalog = read_json(project_root / "creator-source-catalog.v1.json")
        for source in catalog["sources"]:
            data = read_json(source_path(project_root, catalog, source))
            validate_declared_source_shape(source, data)
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
            elif source["source_kind"] not in {"narrative_index", "continuity_chain"}:
                raise AssertionError(f"unsupported fixture source_kind: {source['source_kind']}")


def test_fixture_shot_sources_use_their_stable_shot_ids_as_scopes():
    for entry in fixture_index():
        project_root = FIXTURES / entry["path"]
        catalog = read_json(project_root / "creator-source-catalog.v1.json")
        for source in catalog["sources"]:
            if source["source_kind"] == "shot_spec":
                assert source["scope"] == read_json(source_path(project_root, catalog, source))["shot_id"]


def test_fixture_integrity_rejects_unknown_source_kind():
    entry = next(entry for entry in fixture_index() if entry["fixture_id"] == "smoke-project")
    project_root = FIXTURES / entry["path"]
    catalog = read_json(project_root / "creator-source-catalog.v1.json")
    unknown = dict(catalog["sources"][0])
    unknown["source_id"] = "SRC_UNKNOWN"
    unknown["source_kind"] = "unknown_source_kind"
    catalog["sources"] = [*catalog["sources"], unknown]

    try:
        fixture_counts(project_root, catalog)
    except AssertionError as exc:
        assert str(exc) == "unsupported fixture source_kind: unknown_source_kind"
    else:
        raise AssertionError("unknown fixture source_kind was silently ignored")


def test_smoke_project_has_exact_generic_counts_and_verified_fixture_media():
    entry = next(entry for entry in fixture_index() if entry["fixture_id"] == "smoke-project")
    project_root = FIXTURES / entry["path"]
    catalog = read_json(project_root / "creator-source-catalog.v1.json")
    assert fixture_counts(project_root, catalog) == entry["expected"]
    shot_scopes = {
        source["source_id"]: source["scope"]
        for source in catalog["sources"]
        if source["source_kind"] == "shot_spec"
    }
    assert shot_scopes == {
        "SRC_SHOT_ONE": "EP01_SH001",
        "SRC_SHOT_TWO": "EP01_SH002",
        "SRC_SHOT_THREE": "EP02_SH001",
        "SRC_SHOT_FOUR": "EP02_SH002",
    }
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
    media_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (project_root / "media").rglob("*")
        if path.is_file()
    )
    assert "wucheng" not in media_text.lower()
