"""Deliberately RED v2.3 contracts for the Creator Read Model."""
from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
import json
from pathlib import Path
import shutil
import types
from typing import Literal, Union, get_args, get_origin, get_type_hints

import pytest

import filmfoundry

ROOT = Path(__file__).resolve().parents[1]
SMOKE_PROJECT = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "smoke-project"
FROZEN_WUCHENG_PROJECT = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "projects" / "wucheng-frozen"
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
    value = getattr(filmfoundry, name, None)
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
    shutil.copy2(root / "workspace-manifest.v3.json", tmp_path / "outside.json")
    catalog["sources"][0]["path"] = "../outside.json"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, PATH_ESCAPE_ERROR)


def test_creator_catalog_rejects_archive_as_active_source(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    archive_path = root / "archive" / "workspace-manifest.v3.json"
    archive_path.parent.mkdir()
    shutil.copy2(root / "workspace-manifest.v3.json", archive_path)
    catalog["sources"][0]["path"] = "archive/workspace-manifest.v3.json"
    write_json(path, catalog)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, ARCHIVE_ACTIVE_ERROR)


def test_creator_snapshot_keeps_locked_asset_when_media_is_missing(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v3.json"
    registry = read_json(registry_path)
    registry[0]["state"] = "LOCKED"
    registry[0]["path"] = "media/missing-reference.txt"
    write_json(registry_path, registry)

    snapshot = collect_snapshot(root)
    asset = next(asset for asset in snapshot.assets if asset.asset_id == "CHAR_RIVER")
    assert asset.declared_state == "LOCKED"
    assert asset.observed_readiness == "MISSING"
    blocker = next(blocker for blocker in snapshot.blockers if blocker.entity_id == "CHAR_RIVER")
    assert blocker.provenance.derivation == "VALIDATED"
    assert blocker.provenance.rule_id == "creator.asset.media"
    assert [ref.source_id for ref in blocker.provenance.source_refs] == ["SRC_ASSETS"]


def test_creator_snapshot_reports_present_media_hash_mismatch(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v3.json"
    registry = read_json(registry_path)
    registry[0]["sha256"] = "a" * 64
    write_json(registry_path, registry)

    snapshot = collect_snapshot(root)
    asset = next(asset for asset in snapshot.assets if asset.asset_id == "CHAR_RIVER")
    assert asset.observed_readiness == "PRESENT_HASH_MISMATCH"


def test_creator_snapshot_serialization_is_deterministic_and_workspace_relative():
    snapshot = collect_snapshot(SMOKE_PROJECT)

    first = snapshot.to_json()
    second = snapshot.to_json()

    assert first == second
    payload = json.loads(first)
    assert payload["schema_version"] == "creator-snapshot.v1"
    assert "actions" not in payload
    assert "navigation" not in payload
    asset = next(asset for asset in snapshot.assets if asset.asset_id == "CHAR_RIVER")
    source_ref = asset.provenance.source_refs[0]
    assert source_ref.path == "runtime/sources/asset-registry.v3.json"
    assert source_ref.pointer == "/0"
    assert len(source_ref.sha256) == 64


def test_creator_snapshot_preserves_current_and_historical_authority_mismatch(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    historical = root / "historical-production-state.v3.json"
    historical_data = read_json(root / "runtime" / "sources" / "production-state.v3.json")
    for unit in historical_data["units"].values():
        unit.update(
            runtime_status="SELECT",
            visual_control_state_alignment="PASS",
            provider_evidence_id="EVIDENCE_HISTORICAL",
        )
    write_json(historical, historical_data)
    historical_source = dict(next(source for source in catalog["sources"] if source["source_id"] == "SRC_STATE"))
    historical_source.update(
        source_id="SRC_HISTORICAL_PRODUCTION",
        source_kind="production_state",
        path="historical-production-state.v3.json",
        path_base="WORKSPACE_ROOT",
        authority_role="HISTORICAL",
    )
    current_index = next(
        index for index, source in enumerate(catalog["sources"])
        if source["source_id"] == "SRC_STATE"
    )
    catalog["sources"].insert(current_index, historical_source)
    write_json(path, catalog)

    snapshot = collect_snapshot(root)

    conflict = next(conflict for conflict in snapshot.conflicts if conflict.conflict_type == "AUTHORITY_MISMATCH")
    assert {ref.source_id for ref in conflict.provenance.source_refs} == {
        "SRC_NARRATIVE",
        "SRC_HISTORICAL_PRODUCTION",
    }
    assert snapshot.overview.current_authority == "CURRENT"
    assert snapshot.overview.historical_authority == "HISTORICAL"
    metrics = {metric.metric_id: metric for metric in snapshot.metrics}
    assert {metric_id: metric.value for metric_id, metric in metrics.items()} == {
        "assets.total": 5,
        "production_units.total": 4,
        "character_media.missing": 0,
        "generation.total": 0,
        "select.total": 0,
    }
    assert [ref.source_kind for ref in metrics["assets.total"].provenance.source_refs] == ["asset_registry"]
    assert [ref.source_id for ref in metrics["production_units.total"].provenance.source_refs] == ["SRC_STATE"]
    shot = next(shot for shot in snapshot.shots if shot.shot_id == "EP01_SH001")
    assert shot.runtime_status == "DRAFT"
    assert [ref.source_id for ref in shot.provenance.source_refs] == ["SRC_SHOT_ONE", "SRC_STATE"]
    assert shot.provenance.source_refs[1].pointer == "/units/EP01_SH001_G01"


def test_creator_snapshot_ignores_unrelated_authority_scopes(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    historical = root / "historical-production-state.v3.json"
    shutil.copy2(root / "runtime" / "sources" / "production-state.v3.json", historical)
    historical_source = dict(next(source for source in catalog["sources"] if source["source_id"] == "SRC_STATE"))
    historical_source.update(
        source_id="SRC_OTHER_STORY_PRODUCTION",
        path="historical-production-state.v3.json",
        path_base="WORKSPACE_ROOT",
        authority_role="HISTORICAL",
        scope="OTHER_STORY",
    )
    catalog["sources"].append(historical_source)
    write_json(path, catalog)

    snapshot = collect_snapshot(root)

    assert not any(conflict.conflict_type == "AUTHORITY_MISMATCH" for conflict in snapshot.conflicts)


def test_frozen_wucheng_snapshot_keeps_exact_boundary_facts():
    snapshot = collect_snapshot(FROZEN_WUCHENG_PROJECT)
    metrics = {metric.metric_id: metric for metric in snapshot.metrics}

    assert {metric_id: metric.value for metric_id, metric in metrics.items()} == {
        "assets.total": 75,
        "production_units.total": 19,
        "character_media.missing": 21,
        "generation.total": 0,
        "select.total": 0,
    }
    assert snapshot.overview.current_authority == "CURRENT"
    assert snapshot.overview.historical_authority == "HISTORICAL"
    assert any(conflict.conflict_type == "AUTHORITY_MISMATCH" for conflict in snapshot.conflicts)
    for metric_id in ("production_units.total", "generation.total", "select.total"):
        metric = metrics[metric_id]
        assert metric.data_status == "KNOWN"
        assert [ref.source_id for ref in metric.provenance.source_refs] == ["SRC_PRODUCTION_HISTORICAL"]
        assert [ref.authority_role for ref in metric.provenance.source_refs] == ["HISTORICAL"]
    for metric_id in ("assets.total", "character_media.missing"):
        assert [ref.source_id for ref in metrics[metric_id].provenance.source_refs] == ["SRC_ASSETS"]


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
    assert source.path == SMOKE_PROJECT / "runtime" / "sources" / "shots" / "EP01_SH001.v3.json"
    assert source.data["shot_id"] == "EP01_SH001"


def test_creator_catalog_resolves_windows_syntax_from_a_chinese_workspace(tmp_path: Path):
    root = tmp_path / "项目"
    shutil.copytree(SMOKE_PROJECT, root)
    path, catalog = source_catalog(root)
    catalog["runtime_path"] = "runtime\\project-runtime.json"
    source = next(source for source in catalog["sources"] if source["source_id"] == "SRC_ASSETS")
    source["path"] = "sources\\asset-registry.v3.json"
    write_json(path, catalog)

    discovered = creator_api("discover_creator_sources")(root)

    asset_source = next(source for source in discovered.sources if source.source_id == "SRC_ASSETS")
    assert asset_source.path == root / "runtime" / "sources" / "asset-registry.v3.json"


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
    assert [(gap.source_id, gap.data_status, gap.reason) for gap in discovered.coverage_gaps] == [
        ("SRC_OPTIONAL_FUTURE", "UNKNOWN", "unsupported source schema")
    ]
    snapshot = creator_api("collect_creator_snapshot")(root, discovered)
    gap = next(item for item in snapshot.coverage if item.coverage_id == "SRC_OPTIONAL_FUTURE")
    assert gap.data_status == "UNKNOWN"
    assert [ref.source_id for ref in gap.provenance.source_refs] == ["SRC_OPTIONAL_FUTURE"]


@pytest.mark.parametrize("failure", ["malformed_json", "invalid_records"])
def test_creator_snapshot_marks_optional_invalid_source_and_metrics_invalid(tmp_path: Path, failure: str):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    asset_source = next(source for source in catalog["sources"] if source["source_id"] == "SRC_ASSETS")
    asset_source["required"] = False
    write_json(path, catalog)
    registry_path = root / "runtime" / "sources" / "asset-registry.v3.json"
    if failure == "malformed_json":
        registry_path.write_text("{", encoding="utf-8")
    else:
        write_json(registry_path, {})

    discovered = creator_api("discover_creator_sources")(root)
    snapshot = creator_api("collect_creator_snapshot")(root, discovered)

    assert all(source.source_id != "SRC_ASSETS" for source in discovered.sources)
    source_gap = next(gap for gap in discovered.coverage_gaps if gap.source_id == "SRC_ASSETS")
    assert source_gap.data_status == "INVALID"
    assert source_gap.path == registry_path
    assert source_gap.authority_role == "CURRENT"
    assert source_gap.scope == "project"
    invalid = next(item for item in snapshot.coverage if item.coverage_id == "SRC_ASSETS")
    assert invalid.data_status == "INVALID"
    assert invalid.successful_sources == 0
    assert [ref.source_id for ref in invalid.provenance.source_refs] == ["SRC_ASSETS"]
    metrics = {metric.metric_id: metric for metric in snapshot.metrics}
    for metric_id in ("assets.total", "character_media.missing"):
        assert metrics[metric_id].value is None
        assert metrics[metric_id].data_status == "INVALID"
        assert [ref.source_id for ref in metrics[metric_id].provenance.source_refs] == ["SRC_ASSETS"]


def test_creator_snapshot_marks_optional_missing_source_and_metrics_unknown(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    asset_source = next(source for source in catalog["sources"] if source["source_id"] == "SRC_ASSETS")
    asset_source["required"] = False
    write_json(path, catalog)
    registry_path = root / "runtime" / "sources" / "asset-registry.v3.json"
    registry_path.unlink()

    discovered = creator_api("discover_creator_sources")(root)
    snapshot = creator_api("collect_creator_snapshot")(root, discovered)

    source_gap = next(gap for gap in discovered.coverage_gaps if gap.source_id == "SRC_ASSETS")
    assert source_gap.data_status == "UNKNOWN"
    assert source_gap.reason == "source file missing"
    metrics = {metric.metric_id: metric for metric in snapshot.metrics}
    for metric_id in ("assets.total", "character_media.missing"):
        assert metrics[metric_id].value is None
        assert metrics[metric_id].data_status == "UNKNOWN"
        assert [ref.source_id for ref in metrics[metric_id].provenance.source_refs] == ["SRC_ASSETS"]


def test_creator_snapshot_does_not_fall_back_to_historical_when_current_scope_is_invalid(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    current_source = next(source for source in catalog["sources"] if source["source_id"] == "SRC_STATE")
    current_source["required"] = False
    historical_path = root / "historical-production-state.v3.json"
    shutil.copy2(root / "runtime" / "sources" / "production-state.v3.json", historical_path)
    historical_source = dict(current_source)
    historical_source.update(
        source_id="SRC_HISTORICAL_PRODUCTION",
        path="historical-production-state.v3.json",
        path_base="WORKSPACE_ROOT",
        authority_role="HISTORICAL",
    )
    catalog["sources"].append(historical_source)
    write_json(path, catalog)
    write_json(root / "runtime" / "sources" / "production-state.v3.json", {})

    snapshot = collect_snapshot(root)

    shot = next(shot for shot in snapshot.shots if shot.shot_id == "EP01_SH001")
    assert shot.runtime_status is None
    metrics = {metric.metric_id: metric for metric in snapshot.metrics}
    for metric_id in ("production_units.total", "generation.total", "select.total"):
        assert metrics[metric_id].value is None
        assert metrics[metric_id].data_status == "INVALID"
        assert [ref.source_id for ref in metrics[metric_id].provenance.source_refs] == ["SRC_STATE"]


def test_creator_snapshot_keeps_current_metrics_known_when_historical_source_is_invalid(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    historical_path = root / "historical-production-state.v3.json"
    historical_path.write_text("{", encoding="utf-8")
    historical_source = dict(next(source for source in catalog["sources"] if source["source_id"] == "SRC_STATE"))
    historical_source.update(
        source_id="SRC_HISTORICAL_PRODUCTION_INVALID",
        path="historical-production-state.v3.json",
        path_base="WORKSPACE_ROOT",
        authority_role="HISTORICAL",
        required=False,
    )
    catalog["sources"].append(historical_source)
    write_json(path, catalog)

    discovered = creator_api("discover_creator_sources")(root)
    snapshot = creator_api("collect_creator_snapshot")(root, discovered)

    historical_gap = next(
        gap for gap in discovered.coverage_gaps
        if gap.source_id == "SRC_HISTORICAL_PRODUCTION_INVALID"
    )
    assert historical_gap.data_status == "INVALID"
    coverage = next(item for item in snapshot.coverage if item.coverage_id == historical_gap.source_id)
    assert coverage.data_status == "INVALID"
    metrics = {metric.metric_id: metric for metric in snapshot.metrics}
    for metric_id, value in {
        "production_units.total": 4,
        "generation.total": 0,
        "select.total": 0,
    }.items():
        assert metrics[metric_id].value == value
        assert metrics[metric_id].data_status == "KNOWN"
        assert [ref.source_id for ref in metrics[metric_id].provenance.source_refs] == ["SRC_STATE"]


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
        path="sources/shots/../shots/EP01_SH001.v3.json",
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
    manifest = root / "workspace-manifest.v3.json"
    declared_manifest = root / "manifest" / manifest.name
    declared_manifest.parent.mkdir()
    shutil.copy2(manifest, declared_manifest)
    manifest.unlink()
    catalog["sources"][0]["path"] = "manifest/workspace-manifest.v3.json"
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
    catalog_path, catalog = source_catalog(root)
    continuity_source = next(source for source in catalog["sources"] if source["source_id"] == "SRC_CONTINUITY")
    continuity_source["required"] = True
    write_json(catalog_path, catalog)
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
    registry_path = root / "runtime" / "sources" / "asset-registry.v3.json"
    write_json(registry_path, {"assets": read_json(registry_path)})

    discovered = creator_api("discover_creator_sources")(root)

    assets = next(source for source in discovered.sources if source.source_id == "SRC_ASSETS")
    assert assets.data["assets"][0]["asset_id"] == "CHAR_RIVER"


@pytest.mark.parametrize("registry", [{}, {"assets": {}}, {"unexpected": []}])
def test_creator_catalog_rejects_invalid_object_form_asset_registry(tmp_path: Path, registry: dict):
    root = copied_smoke_project(tmp_path)
    registry_path = root / "runtime" / "sources" / "asset-registry.v3.json"
    write_json(registry_path, registry)

    with pytest.raises(ValueError) as exc_info:
        creator_api("discover_creator_sources")(root)
    assert_creator_error(exc_info, INVALID_SOURCE_ERROR)


def test_creator_catalog_rejects_drive_qualified_source_path(tmp_path: Path):
    root = copied_smoke_project(tmp_path)
    path, catalog = source_catalog(root)
    catalog["sources"][0]["path"] = "C:workspace-manifest.v3.json"
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
    snapshot_type = getattr(filmfoundry, "CreatorSnapshot", None)
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
    assert type_hints["schema_version"] == Literal["creator-snapshot.v1"]
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
        annotation_origins.update(
            type(value)
            for option in annotation_options
            if get_origin(option) is Literal
            for value in get_args(option)
        )
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

    dataclass_definitions = {
        "source_ref": filmfoundry.CreatorSourceRef,
        "provenance": filmfoundry.CreatorProvenance,
        "overview": filmfoundry.CreatorOverview,
        "metric": filmfoundry.CreatorMetric,
        "narrative_node": filmfoundry.CreatorNarrativeNode,
        "emotion_point": filmfoundry.CreatorEmotionPoint,
        "asset": filmfoundry.CreatorAsset,
        "shot": filmfoundry.CreatorShot,
        "continuity_edge": filmfoundry.CreatorContinuityEdge,
        "blocker": filmfoundry.CreatorBlocker,
        "conflict": filmfoundry.CreatorConflict,
        "coverage": filmfoundry.CreatorCoverage,
    }
    for definition_name, dataclass_type in dataclass_definitions.items():
        definition = schema["$defs"][definition_name]
        dataclass_field_names = {field.name for field in fields(dataclass_type)}
        assert set(definition["properties"]) == dataclass_field_names
        assert set(definition["required"]) == dataclass_field_names

    enum_fields = {
        ("provenance", "derivation"): (filmfoundry.CreatorProvenance, "derivation"),
        ("metric", "data_status"): (filmfoundry.CreatorMetric, "data_status"),
        ("asset", "observed_readiness"): (filmfoundry.CreatorAsset, "observed_readiness"),
        ("coverage", "data_status"): (filmfoundry.CreatorCoverage, "data_status"),
    }
    for (definition_name, property_name), (dataclass_type, field_name) in enum_fields.items():
        annotation = get_type_hints(dataclass_type)[field_name]
        assert get_origin(annotation) is Literal
        assert set(get_args(annotation)) == set(schema["$defs"][definition_name]["properties"][property_name]["enum"])

    for definition_name, dataclass_type in dataclass_definitions.items():
        definition = schema["$defs"][definition_name]
        hints = get_type_hints(dataclass_type)
        for field_name, property_definition in definition["properties"].items():
            annotation = hints[field_name]
            options = get_args(annotation) if get_origin(annotation) in {Union, types.UnionType} else (annotation,)
            options = tuple(option for option in options if option is not type(None))
            if "$ref" in property_definition:
                expected_type = dataclass_definitions[property_definition["$ref"].rsplit("/", 1)[-1]]
                assert expected_type in options
            items = property_definition.get("items", {})
            if "$ref" in items:
                expected_type = dataclass_definitions[items["$ref"].rsplit("/", 1)[-1]]
                assert any(expected_type in get_args(option) for option in options)
