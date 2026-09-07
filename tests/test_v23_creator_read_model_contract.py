"""Deliberately RED v2.3 contracts for the Creator Read Model."""
from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
import json
from pathlib import Path
import shutil
import types
from typing import Literal, Union, get_args, get_origin, get_type_hints

import pytest

import filmfoundry_v2

ROOT = Path(__file__).resolve().parents[1]
SMOKE_PROJECT = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "smoke-project"
PATH_ESCAPE_ERROR = "CREATOR_SOURCE_PATH_ESCAPE: source path escapes workspace"
ARCHIVE_ACTIVE_ERROR = "CREATOR_ARCHIVE_SOURCE_ACTIVE: active source is inside archive"
MULTIPLE_CURRENT_ERROR = "CREATOR_MULTIPLE_CURRENT: multiple CURRENT sources for source_kind and scope"
UNKNOWN_SCHEMA_ERROR = "CREATOR_UNKNOWN_SCHEMA: unsupported source schema"
UNKNOWN_ENUM_ERROR = "CREATOR_UNKNOWN_ENUM: unknown authority_role"
INVALID_ID_ERROR = "CREATOR_INVALID_ID: invalid stable ASCII ID"
DUPLICATE_SOURCE_ID_ERROR = "CREATOR_DUPLICATE_SOURCE_ID: duplicate source_id"
INVALID_SOURCE_ERROR = "CREATOR_SOURCE_INVALID: source validation failed"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copied_smoke_project(tmp_path: Path) -> Path:
    root = tmp_path / "smoke-project"
    shutil.copytree(SMOKE_PROJECT, root)
    return root


def source_catalog(root: Path) -> tuple[Path, dict]:
    path = root / "creator-source-catalog.v1.json"
    return path, read_json(path)


def creator_api(name: str):
    value = getattr(filmfoundry_v2, name, None)
    assert callable(value), f"FilmFoundry v2.3 public API {name} is missing"
    return value


def assert_creator_error(exc_info: pytest.ExceptionInfo[ValueError], expected: str) -> None:
    assert str(exc_info.value) == expected


def collect_snapshot(root: Path):
    discover = creator_api("discover_creator_sources")
    collect = creator_api("collect_creator_snapshot")
    return collect(root, discover(root))


def test_creator_catalog_rejects_multiple_current_authorities(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    current = catalog["sources"][0]
    current_key = (current["source_kind"], current["scope"])
    assert sum(
        (source["source_kind"], source["scope"]) == current_key
        for source in catalog["sources"]
        if source["authority_role"] == "CURRENT"
    ) == 1
    duplicate = dict(current)
    duplicate["source_id"] = "SRC_WORKSPACE_DUPLICATE"
    duplicate["source_kind"] = current_key[0]
    duplicate["scope"] = current_key[1]
    catalog["sources"].append(duplicate)
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, MULTIPLE_CURRENT_ERROR)


def test_creator_catalog_rejects_workspace_path_escape(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    shutil.copy2(root / "workspace-manifest.v2.json", tmp_path / "outside.json")
    catalog["sources"][0]["path"] = "../outside.json"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, PATH_ESCAPE_ERROR)


def test_creator_catalog_rejects_archive_as_active_source(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    archive_path = root / "archive" / "workspace-manifest.v2.json"
    archive_path.parent.mkdir()
    shutil.copy2(root / "workspace-manifest.v2.json", archive_path)
    catalog["sources"][0]["path"] = "archive/workspace-manifest.v2.json"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, ARCHIVE_ACTIVE_ERROR)


def test_creator_snapshot_keeps_locked_asset_when_media_is_missing(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v2.json"
    registry = read_json(registry_path)
    registry[0]["state"] = "LOCKED"
    registry[0]["path"] = "media/missing-reference.txt"
    write_json(registry_path, registry)

    snapshot = collect_snapshot(root)
    asset = next(asset for asset in snapshot.assets if asset.asset_id == "CHAR_RIVER")
    assert asset.declared_state == "LOCKED"
    assert asset.observed_readiness == "MISSING"


def test_creator_snapshot_reports_present_media_hash_mismatch(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v2.json"
    registry = read_json(registry_path)
    registry[0]["sha256"] = "a" * 64
    write_json(registry_path, registry)

    snapshot = collect_snapshot(root)
    asset = next(asset for asset in snapshot.assets if asset.asset_id == "CHAR_RIVER")
    assert asset.observed_readiness == "PRESENT_HASH_MISMATCH"


def test_creator_catalog_rejects_required_unknown_schema(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["schema_version"] = "workspace-manifest.v999"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, UNKNOWN_SCHEMA_ERROR)


def test_creator_catalog_rejects_unknown_authority_enum(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["authority_role"] = "UNRECOGNIZED"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, UNKNOWN_ENUM_ERROR)


def test_creator_catalog_discovers_supported_sources_with_parsed_records():
    catalog = creator_api("discover_creator_sources")(SMOKE_PROJECT)

    assert catalog.project_id == "SMOKE_PROJECT"
    assert catalog.runtime_path == SMOKE_PROJECT / "runtime" / "project-runtime.json"
    assert catalog.coverage_gaps == ()
    assert len(catalog.sources) == 9
    source = next(source for source in catalog.sources if source.source_id == "SRC_SHOT_ONE")
    assert source.path == SMOKE_PROJECT / "runtime" / "sources" / "shots" / "EP01_SH001.v2.json"
    assert source.data["shot_id"] == "EP01_SH001"


def test_creator_catalog_resolves_windows_syntax_from_a_chinese_workspace(tmp_path: Path):
    root = tmp_path / "项目"
    shutil.copytree(SMOKE_PROJECT, root)
    path, catalog = source_catalog(root)
    catalog["runtime_path"] = "runtime\\project-runtime.json"
    source = next(source for source in catalog["sources"] if source["source_id"] == "SRC_ASSETS")
    source["path"] = "sources\\asset-registry.v2.json"
    write_json(path, catalog)

    discovered = creator_api("discover_creator_sources")(root)

    asset_source = next(source for source in discovered.sources if source.source_id == "SRC_ASSETS")
    assert asset_source.path == root / "runtime" / "sources" / "asset-registry.v2.json"


def test_creator_catalog_reports_optional_unsupported_source_as_coverage_gap(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    optional = dict(catalog["sources"][0])
    optional.update(
        source_id="SRC_OPTIONAL_FUTURE",
        source_kind="future_source",
        parser_id="future-json",
        schema_version="future-source.v1",
        authority_role="SUPPORTING",
        required=False,
    )
    catalog["sources"].append(optional)
    write_json(path, catalog)

    discovered = creator_api("discover_creator_sources")(root)

    assert all(source.source_id != "SRC_OPTIONAL_FUTURE" for source in discovered.sources)
    assert [(gap.source_id, gap.reason) for gap in discovered.coverage_gaps] == [
        ("SRC_OPTIONAL_FUTURE", "unsupported source schema")
    ]


def test_creator_catalog_uses_an_adapter_catalog_path(tmp_path: Path):
    root = copied_smoke_project(tmp_path)

    class Adapter:
        def locate_catalog(self, workspace_root: Path) -> Path:
            return workspace_root / "creator-source-catalog.v1.json"

    discovered = creator_api("discover_creator_sources")(root, Adapter())

    assert discovered.project_id == "SMOKE_PROJECT"


def test_creator_catalog_rejects_duplicate_current_shot_with_equivalent_path(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    shot = next(source for source in catalog["sources"] if source["source_id"] == "SRC_SHOT_ONE")
    duplicate = dict(shot)
    duplicate.update(
        source_id="SRC_SHOT_ONE_DUPLICATE",
        path="sources/shots/../shots/EP01_SH001.v2.json",
    )
    catalog["sources"].append(duplicate)
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, MULTIPLE_CURRENT_ERROR)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("project_id", "project-id"),
        ("source_id", "source-id"),
        ("scope", "scope-id"),
    ],
)
def test_creator_catalog_rejects_non_stable_ascii_ids(tmp_path: Path, field: str, value: str):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    if field == "project_id":
        catalog[field] = value
    else:
        catalog["sources"][0][field] = value
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, INVALID_ID_ERROR)


def test_creator_catalog_rejects_duplicate_source_id(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][1]["source_id"] = catalog["sources"][0]["source_id"]
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, DUPLICATE_SOURCE_ID_ERROR)


def test_creator_catalog_uses_a_declared_manifest_for_archive_boundary(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    manifest = root / "workspace-manifest.v2.json"
    declared_manifest = root / "manifest" / manifest.name
    declared_manifest.parent.mkdir()
    shutil.copy2(manifest, declared_manifest)
    manifest.unlink()
    catalog["sources"][0]["path"] = "manifest/workspace-manifest.v2.json"
    archive_path = root / "archive" / "narrative-index.v1.json"
    archive_path.parent.mkdir()
    shutil.copy2(root / "narrative-index.v1.json", archive_path)
    catalog["sources"][1]["path"] = "archive/narrative-index.v1.json"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, ARCHIVE_ACTIVE_ERROR)


def test_creator_catalog_allows_archive_named_path_without_declared_manifest(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"] = catalog["sources"][1:]
    archive_path = root / "99_\u5f52\u6863" / "narrative-index.v1.json"
    archive_path.parent.mkdir()
    shutil.copy2(root / "narrative-index.v1.json", archive_path)
    catalog["sources"][0]["path"] = "99_\u5f52\u6863/narrative-index.v1.json"
    write_json(path, catalog)

    discovered = creator_api("discover_creator_sources")(root)

    assert discovered.sources[0].path == archive_path


@pytest.mark.parametrize("mutation", ["unknown_field", "missing_field", "invalid_id", "unknown_parent"])
def test_creator_catalog_rejects_invalid_narrative_index_records(tmp_path: Path, mutation: str):
    root = copied_smoke_project(tmp_path)
    narrative_path = root / "narrative-index.v1.json"
    narrative = read_json(narrative_path)
    if mutation == "unknown_field":
        narrative["nodes"][0]["unexpected"] = "value"
    elif mutation == "missing_field":
        del narrative["nodes"][0]["display_name"]
    elif mutation == "invalid_id":
        narrative["nodes"][0]["node_id"] = "season-one"
    else:
        narrative["nodes"][1]["parent_id"] = "MISSING_PARENT"
    write_json(narrative_path, narrative)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, INVALID_SOURCE_ERROR)


@pytest.mark.parametrize("mutation", ["unknown_field", "missing_field", "invalid_id", "self_edge"])
def test_creator_catalog_rejects_invalid_continuity_records(tmp_path: Path, mutation: str):
    root = copied_smoke_project(tmp_path)
    continuity_path = root / "continuity-chain.v1.json"
    continuity = read_json(continuity_path)
    edge = continuity["chains"][0]["edges"][0]
    if mutation == "unknown_field":
        edge["unexpected"] = "value"
    elif mutation == "missing_field":
        del edge["field"]
    elif mutation == "invalid_id":
        continuity["chains"][0]["chain_id"] = "chain-lamp"
    else:
        edge["to_shot_id"] = edge["from_shot_id"]
    write_json(continuity_path, continuity)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, INVALID_SOURCE_ERROR)


def test_creator_catalog_accepts_object_form_asset_registry(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v2.json"
    write_json(registry_path, {"assets": read_json(registry_path)})

    discovered = creator_api("discover_creator_sources")(root)

    assets = next(source for source in discovered.sources if source.source_id == "SRC_ASSETS")
    assert assets.data["assets"][0]["asset_id"] == "CHAR_RIVER"


@pytest.mark.parametrize("registry", [{}, {"assets": {}}, {"unexpected": []}])
def test_creator_catalog_rejects_invalid_object_form_asset_registry(tmp_path: Path, registry: dict):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v2.json"
    write_json(registry_path, registry)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, INVALID_SOURCE_ERROR)


def test_creator_catalog_rejects_drive_qualified_source_path(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["path"] = "C:workspace-manifest.v2.json"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, PATH_ESCAPE_ERROR)


def test_creator_catalog_resolves_relative_adapter_path_from_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    root = copied_smoke_project(tmp_path)
    monkeypatch.chdir(tmp_path)

    class Adapter:
        def locate_catalog(self, workspace_root: Path) -> Path:
            return Path("creator-source-catalog.v1.json")

    discovered = creator_api("discover_creator_sources")(root, Adapter())

    assert discovered.project_id == "SMOKE_PROJECT"


def test_creator_snapshot_dataclass_and_schema_stay_aligned():
    snapshot_type = getattr(filmfoundry_v2, "CreatorSnapshot", None)
    assert snapshot_type is not None, "FilmFoundry v2.3 public CreatorSnapshot dataclass is missing"
    assert is_dataclass(snapshot_type)

    schema_path = ROOT / "schemas" / "creator-snapshot.v1.json"
    assert schema_path.is_file(), "FilmFoundry v2.3 CreatorSnapshot schema is missing"
    schema = read_json(schema_path)
    dataclass_fields = {field.name: field for field in fields(snapshot_type)}
    schema_properties = schema["properties"]
    assert set(schema_properties) == set(dataclass_fields)

    required = schema.get("required")
    assert isinstance(required, list) and required
    for name in required:
        assert name in dataclass_fields
        field = dataclass_fields[name]
        assert field.default is MISSING
        assert field.default_factory is MISSING

    type_hints = get_type_hints(snapshot_type)
    json_types = {
        "string": {str},
        "integer": {int},
        "number": {int, float},
        "boolean": {bool},
        "array": {list, tuple},
        "object": {dict},
    }
    for name, definition in schema_properties.items():
        annotation = type_hints[name]
        annotation_options = get_args(annotation)
        if get_origin(annotation) in {Union, types.UnionType}:
            annotation_options = tuple(option for option in annotation_options if option is not type(None))
        else:
            annotation_options = (annotation,)
        annotation_origins = {
            get_origin(option) or option
            for option in annotation_options
            if option is not type(None)
        }
        schema_types = definition.get("type", [])
        if isinstance(schema_types, str):
            schema_types = [schema_types]
        for schema_type in schema_types:
            if schema_type in json_types:
                assert annotation_origins & json_types[schema_type]
        if "enum" in definition:
            literal_values = {
                value
                for option in annotation_options
                if get_origin(option) is Literal
                for value in get_args(option)
            }
            assert literal_values == set(definition["enum"])
