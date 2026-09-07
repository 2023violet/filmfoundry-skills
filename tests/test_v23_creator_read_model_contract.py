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
    archive_path = root / "99_\u5f52\u6863" / "workspace-manifest.v2.json"
    archive_path.parent.mkdir()
    shutil.copy2(root / "workspace-manifest.v2.json", archive_path)
    catalog["sources"][0]["path"] = "99_\u5f52\u6863/workspace-manifest.v2.json"
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
