"""Deliberately RED v2.3 contracts for the Creator Read Model."""
from __future__ import annotations

from dataclasses import fields, is_dataclass
import json
from pathlib import Path
import shutil

import pytest

import filmfoundry_v2

ROOT = Path(__file__).resolve().parents[1]
SMOKE_PROJECT = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "smoke-project"


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


def collect_snapshot(root: Path):
    discover = creator_api("discover_creator_sources")
    collect = creator_api("collect_creator_snapshot")
    return collect(root, discover(root))


def test_creator_catalog_rejects_multiple_current_authorities(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    duplicate = dict(catalog["sources"][0])
    duplicate["source_id"] = "SRC_WORKSPACE_DUPLICATE"
    catalog["sources"].append(duplicate)
    write_json(path, catalog)

    with pytest.raises(ValueError):
        creator_api("discover_creator_sources")(root)


def test_creator_catalog_rejects_workspace_path_escape(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["path"] = "../outside.json"
    write_json(path, catalog)

    with pytest.raises(ValueError):
        creator_api("discover_creator_sources")(root)


def test_creator_catalog_rejects_archive_as_active_source(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["path"] = "99_\u5f52\u6863/workspace-manifest.v2.json"
    write_json(path, catalog)

    with pytest.raises(ValueError):
        creator_api("discover_creator_sources")(root)


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

    with pytest.raises(ValueError):
        creator_api("discover_creator_sources")(root)


def test_creator_catalog_rejects_unknown_authority_enum(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["authority_role"] = "UNRECOGNIZED"
    write_json(path, catalog)

    with pytest.raises(ValueError):
        creator_api("discover_creator_sources")(root)


def test_creator_snapshot_dataclass_and_schema_stay_aligned():
    snapshot_type = getattr(filmfoundry_v2, "CreatorSnapshot", None)
    assert snapshot_type is not None, "FilmFoundry v2.3 public CreatorSnapshot dataclass is missing"
    assert is_dataclass(snapshot_type)

    schema_path = ROOT / "schemas" / "creator-snapshot.v1.json"
    assert schema_path.is_file(), "FilmFoundry v2.3 CreatorSnapshot schema is missing"
    schema = read_json(schema_path)
    assert set(schema["properties"]) == {field.name for field in fields(snapshot_type)}
