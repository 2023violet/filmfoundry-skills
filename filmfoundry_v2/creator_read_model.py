"""Typed, read-only Creator Snapshot collection."""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from .creator_sources import CreatorCatalogSource, CreatorSourceCatalog, CreatorSourceCoverageGap


Derivation = Literal["DIRECT", "VALIDATED", "AGGREGATED"]
DataStatus = Literal["KNOWN", "UNKNOWN", "INVALID"]
ObservedReadiness = Literal[
    "PRESENT_HASH_OK",
    "PRESENT_HASH_UNVERIFIED",
    "PRESENT_HASH_MISMATCH",
    "MISSING",
    "NOT_APPLICABLE",
    "UNKNOWN",
]


@dataclass(frozen=True)
class CreatorSourceRef:
    source_id: str
    source_kind: str
    path: str
    pointer: str
    sha256: str
    authority_role: str
    version: str | None


@dataclass(frozen=True)
class CreatorProvenance:
    source_refs: tuple[CreatorSourceRef, ...]
    derivation: Derivation
    rule_id: str | None


@dataclass(frozen=True)
class CreatorMetric:
    metric_id: str
    value: int | float | str | None
    data_status: DataStatus
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorOverview:
    project_id: str
    phase: str
    current_authority: str
    historical_authority: str | None
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorNarrativeNode:
    node_id: str
    node_type: str
    display_name: str
    narrative_responsibility: str
    parent_id: str | None
    canon_source: str
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorEmotionPoint:
    beat_id: str
    production_unit: str
    sequence: int
    narrative_function: str
    primary_emotion: str
    tension_level: int
    direction: str
    turning_point: bool
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorAsset:
    asset_id: str
    asset_type: str
    display_name: str
    path: str
    declared_state: str
    observed_readiness: ObservedReadiness
    declared_sha256: str | None
    observed_sha256: str | None
    provenance: CreatorProvenance

    @property
    def sha256(self) -> str | None:
        """Compatibility alias for the declared media digest."""
        return self.declared_sha256


@dataclass(frozen=True)
class CreatorShot:
    shot_id: str
    generation_unit_id: str
    runtime_status: str | None
    select_type: str | None
    observed_state: str | None
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorContinuityEdge:
    chain_id: str
    entity_id: str
    from_shot_id: str
    to_shot_id: str
    field: str
    from_value: str
    to_value: str
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorBlocker:
    blocker_id: str
    severity: str
    entity_id: str | None
    rule_id: str | None
    reason: str
    support_boundary: str
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorConflict:
    conflict_id: str
    conflict_type: str
    entity_id: str | None
    reason: str
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorCoverage:
    coverage_id: str
    source_kind: str
    data_status: DataStatus
    successful_sources: int
    declared_sources: int
    reason: str | None
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorAction:
    action_id: str
    entity_id: str | None
    priority: int
    severity: str
    reason: str
    rule_id: str | None
    prerequisites: tuple[str, ...]
    support_boundary: str
    provenance: CreatorProvenance


@dataclass(frozen=True)
class CreatorSnapshot:
    schema_version: Literal["creator-snapshot.v1"]
    project_id: str
    overview: CreatorOverview
    metrics: tuple[CreatorMetric, ...]
    narrative_nodes: tuple[CreatorNarrativeNode, ...]
    emotion_points: tuple[CreatorEmotionPoint, ...]
    assets: tuple[CreatorAsset, ...]
    shots: tuple[CreatorShot, ...]
    continuity_edges: tuple[CreatorContinuityEdge, ...]
    blockers: tuple[CreatorBlocker, ...]
    conflicts: tuple[CreatorConflict, ...]
    coverage: tuple[CreatorCoverage, ...]

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _json_pointer(value: str) -> str:
    return "/" + value.replace("~", "~0").replace("/", "~1")


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def _source_ref(root: Path, source: CreatorCatalogSource, pointer: str = "/") -> CreatorSourceRef:
    return CreatorSourceRef(
        source_id=source.source_id,
        source_kind=source.source_kind,
        path=_relative_path(root, source.path),
        pointer=pointer,
        sha256=_sha256(source.path),
        authority_role=source.authority_role,
        version=source.schema_version,
    )


def _gap_ref(root: Path, gap: CreatorSourceCoverageGap) -> CreatorSourceRef:
    return CreatorSourceRef(
        source_id=gap.source_id,
        source_kind=gap.source_kind,
        path=_relative_path(root, gap.path),
        pointer="/",
        sha256=_sha256(gap.path),
        authority_role=gap.authority_role,
        version=gap.schema_version,
    )


def _provenance(refs: tuple[CreatorSourceRef, ...], derivation: Derivation, rule_id: str | None = None) -> CreatorProvenance:
    return CreatorProvenance(refs, derivation, rule_id)


def _source_rows(source: CreatorCatalogSource, key: str) -> tuple[tuple[str, Any], ...]:
    data = source.data
    if isinstance(data, list):
        return tuple((f"/{index}", row) for index, row in enumerate(data))
    if isinstance(data, dict) and isinstance(data.get(key), list):
        return tuple((f"/{key}/{index}", row) for index, row in enumerate(data[key]))
    return ()


def _media_path(root: Path, source: CreatorCatalogSource, value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidates = (root / value, source.path.parent / value)
    fallback: Path | None = None
    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            continue
        if fallback is None:
            fallback = resolved
        if resolved.is_file():
            return resolved
    return fallback


def _asset_readiness(root: Path, source: CreatorCatalogSource, row: dict[str, Any]) -> tuple[ObservedReadiness, str | None]:
    path = _media_path(root, source, row.get("path"))
    if path is None:
        return ("NOT_APPLICABLE", None) if not row.get("path") else ("UNKNOWN", None)
    if not path.is_file():
        return "MISSING", None
    observed = _sha256(path)
    declared = row.get("sha256")
    if not isinstance(declared, str) or not declared:
        return "PRESENT_HASH_UNVERIFIED", observed
    if observed.lower() == declared.lower():
        return "PRESENT_HASH_OK", observed
    return "PRESENT_HASH_MISMATCH", observed


def _runtime_ref(root: Path, catalog: CreatorSourceCatalog) -> CreatorSourceRef | None:
    path = catalog.runtime_path
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    version = data.get("schema_version") if isinstance(data, dict) else None
    return CreatorSourceRef("RUNTIME", "runtime", _relative_path(root, path), "/", _sha256(path), "CURRENT", version if isinstance(version, str) else None)


def _metric(metric_id: str, value: int | float | str | None, status: DataStatus, refs: tuple[CreatorSourceRef, ...], rule: str) -> CreatorMetric:
    return CreatorMetric(metric_id, value, status, _provenance(refs, "AGGREGATED", rule))


def _aggregate_status(
    successful_sources: list[CreatorCatalogSource],
    gaps: list[CreatorSourceCoverageGap],
) -> DataStatus:
    if any(gap.data_status == "INVALID" for gap in gaps):
        return "INVALID"
    if gaps or not successful_sources:
        return "UNKNOWN"
    return "KNOWN"


def collect_creator_snapshot(root: Path, catalog: CreatorSourceCatalog) -> CreatorSnapshot:
    workspace_root = Path(root).resolve()
    assets: list[CreatorAsset] = []
    narrative_nodes: list[CreatorNarrativeNode] = []
    emotion_points: list[CreatorEmotionPoint] = []
    shots: list[CreatorShot] = []
    continuity_edges: list[CreatorContinuityEdge] = []
    coverage: list[CreatorCoverage] = []
    source_by_kind: dict[str, list[CreatorCatalogSource]] = {}
    gaps_by_kind: dict[str, list[CreatorSourceCoverageGap]] = {}

    for source in catalog.sources:
        source_by_kind.setdefault(source.source_kind, []).append(source)
        ref = _source_ref(workspace_root, source)
        coverage.append(CreatorCoverage(source.source_id, source.source_kind, "KNOWN", 1, 1, None, _provenance((ref,), "VALIDATED")))
        if source.source_kind == "asset_registry":
            for pointer, row in _source_rows(source, "assets"):
                if not isinstance(row, dict):
                    continue
                readiness, observed_sha = _asset_readiness(workspace_root, source, row)
                assets.append(
                    CreatorAsset(
                        str(row.get("asset_id", "")),
                        str(row.get("asset_type", "")),
                        str(row.get("display_name", "")),
                        str(row.get("path", "")),
                        str(row.get("state", "")),
                        readiness,
                        row.get("sha256") if isinstance(row.get("sha256"), str) else None,
                        observed_sha,
                        _provenance((CreatorSourceRef(ref.source_id, ref.source_kind, ref.path, pointer, ref.sha256, ref.authority_role, ref.version),), "DIRECT"),
                    )
                )
        elif source.source_kind == "narrative_index":
            for pointer, row in _source_rows(source, "nodes"):
                if isinstance(row, dict):
                    node_ref = CreatorSourceRef(ref.source_id, ref.source_kind, ref.path, pointer, ref.sha256, ref.authority_role, ref.version)
                    narrative_nodes.append(CreatorNarrativeNode(*(row.get(name) for name in ("node_id", "node_type", "display_name", "narrative_responsibility", "parent_id", "canon_source")), _provenance((node_ref,), "DIRECT")))
        elif source.source_kind == "emotional_beat_map":
            data = source.data if isinstance(source.data, dict) else {}
            production_unit = str(data.get("production_unit", ""))
            for pointer, row in _source_rows(source, "beats"):
                if isinstance(row, dict):
                    point_ref = CreatorSourceRef(ref.source_id, ref.source_kind, ref.path, pointer, ref.sha256, ref.authority_role, ref.version)
                    emotion_points.append(CreatorEmotionPoint(*(row.get(name) for name in ("beat_id",)), production_unit, *(row.get(name) for name in ("sequence", "narrative_function", "primary_emotion", "tension_level", "direction", "turning_point")), _provenance((point_ref,), "DIRECT")))
        elif source.source_kind == "shot_spec" and isinstance(source.data, dict):
            shot_id = str(source.data.get("shot_id", ""))
            generation_unit_id = str(source.data.get("generation_unit_id", ""))
            shots.append(CreatorShot(shot_id, generation_unit_id, None, None, None, _provenance((ref,), "DIRECT")))
        elif source.source_kind == "continuity_chain" and isinstance(source.data, dict):
            for chain in source.data.get("chains", []):
                if not isinstance(chain, dict):
                    continue
                for edge in chain.get("edges", []):
                    if isinstance(edge, dict):
                        continuity_edges.append(CreatorContinuityEdge(str(chain.get("chain_id", "")), str(chain.get("entity_id", "")), *(str(edge.get(name, "")) for name in ("from_shot_id", "to_shot_id", "field", "from_value", "to_value")), _provenance((ref,), "DIRECT")))

    for gap in catalog.coverage_gaps:
        gaps_by_kind.setdefault(gap.source_kind, []).append(gap)
        gap_ref = _gap_ref(workspace_root, gap)
        coverage.append(
            CreatorCoverage(
                gap.source_id,
                gap.source_kind,
                gap.data_status,
                0,
                1,
                gap.reason,
                _provenance((gap_ref,), "VALIDATED", "creator.coverage.gap"),
            )
        )

    runtime_data: dict[str, Any] = {}
    try:
        loaded = json.loads(catalog.runtime_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            runtime_data = loaded
    except (OSError, json.JSONDecodeError):
        runtime_data = {}
    runtime_ref = _runtime_ref(workspace_root, catalog)
    all_refs = tuple(_source_ref(workspace_root, source) for source in catalog.sources)
    overview_refs = all_refs + ((runtime_ref,) if runtime_ref else ())
    current_sources = [source for source in catalog.sources if source.authority_role == "CURRENT"]
    historical_sources = [source for source in catalog.sources if source.authority_role == "HISTORICAL"]
    overview = CreatorOverview(catalog.project_id, str(runtime_data.get("phase", "UNKNOWN")), "CURRENT" if current_sources else "UNKNOWN", "HISTORICAL" if historical_sources else None, _provenance(overview_refs, "AGGREGATED", "creator.overview"))

    declared_production_sources = source_by_kind.get("production_state", [])
    production_sources: list[CreatorCatalogSource] = []
    production_by_scope: dict[str, list[CreatorCatalogSource]] = {}
    production_gaps_by_scope: dict[str, list[CreatorSourceCoverageGap]] = {}
    for source in declared_production_sources:
        production_by_scope.setdefault(source.scope, []).append(source)
    for gap in gaps_by_kind.get("production_state", []):
        production_gaps_by_scope.setdefault(gap.scope, []).append(gap)
    production_scopes = list(production_by_scope)
    production_scopes.extend(
        gap.scope
        for gap in gaps_by_kind.get("production_state", [])
        if gap.scope not in production_by_scope and gap.scope not in production_scopes
    )
    for scope in production_scopes:
        sources = production_by_scope.get(scope, [])
        scope_gaps = production_gaps_by_scope.get(scope, [])
        current = [source for source in sources if source.authority_role == "CURRENT"]
        historical = [source for source in sources if source.authority_role == "HISTORICAL"]
        if current:
            production_sources.extend(current)
        elif any(gap.authority_role == "CURRENT" for gap in scope_gaps):
            continue
        elif len(historical) == 1 and not any(gap.authority_role == "HISTORICAL" for gap in scope_gaps):
            production_sources.extend(historical)

    state_rows: list[tuple[str, dict[str, Any], CreatorSourceRef]] = []
    for source in production_sources:
        ref = _source_ref(workspace_root, source)
        data = source.data if isinstance(source.data, dict) else {}
        units = data.get("units", {})
        if isinstance(units, dict):
            for unit_id, unit in units.items():
                if isinstance(unit, dict):
                    pointer = "/units" + _json_pointer(str(unit_id))
                    state_rows.append((str(unit_id), unit, CreatorSourceRef(ref.source_id, ref.source_kind, ref.path, pointer, ref.sha256, ref.authority_role, ref.version)))
    for index, shot in enumerate(shots):
        matching = next(((row, ref) for unit_id, row, ref in state_rows if shot.generation_unit_id == unit_id), None)
        if matching:
            row, ref = matching
            shots[index] = CreatorShot(shot.shot_id, shot.generation_unit_id, row.get("runtime_status"), row.get("select_type"), row.get("observed_state"), _provenance((shot.provenance.source_refs[0], ref), "VALIDATED"))

    asset_sources = source_by_kind.get("asset_registry", [])
    asset_gaps = gaps_by_kind.get("asset_registry", [])
    production_gaps = gaps_by_kind.get("production_state", [])
    asset_status = _aggregate_status(asset_sources, asset_gaps)
    production_status = _aggregate_status(production_sources, production_gaps)
    asset_refs = tuple(_source_ref(workspace_root, source) for source in asset_sources) + tuple(
        _gap_ref(workspace_root, gap) for gap in asset_gaps
    )
    production_refs = tuple(_source_ref(workspace_root, source) for source in production_sources) + tuple(
        _gap_ref(workspace_root, gap) for gap in production_gaps
    )
    generated_statuses = {"KF_GENERATED", "KF_QC_PASS", "READY_FOR_VIDEO", "VIDEO_GENERATED", "VIDEO_QC_PASS", "SELECT", "OBSERVED_STATE_RECORDED", "EDIT_READY"}
    selected_count = sum(str(row.get("runtime_status", "")).upper() == "SELECT" for _, row, _ in state_rows)
    generated_count = sum(str(row.get("runtime_status", "")).upper() in generated_statuses for _, row, _ in state_rows)
    missing_characters = sum(asset.asset_type.lower() == "character" and asset.observed_readiness == "MISSING" for asset in assets)
    metrics = (
        _metric("assets.total", len(assets) if asset_status == "KNOWN" else None, asset_status, asset_refs, "creator.assets.total"),
        _metric("production_units.total", len(state_rows) if production_status == "KNOWN" else None, production_status, production_refs, "creator.production.total"),
        _metric("character_media.missing", missing_characters if asset_status == "KNOWN" else None, asset_status, asset_refs, "creator.media.missing"),
        _metric("generation.total", generated_count if production_status == "KNOWN" else None, production_status, production_refs, "creator.generation.total"),
        _metric("select.total", selected_count if production_status == "KNOWN" else None, production_status, production_refs, "creator.select.total"),
    )

    conflicts: list[CreatorConflict] = []
    current_narrative_scopes = {
        source.scope
        for source in catalog.sources
        if source.source_kind == "narrative_index" and source.authority_role == "CURRENT"
    }
    mismatch_sources = [
        source
        for source in catalog.sources
        if (
            source.source_kind == "narrative_index"
            and source.authority_role == "CURRENT"
            and source.scope in {
                production.scope
                for production in catalog.sources
                if production.source_kind == "production_state" and production.authority_role == "HISTORICAL"
            }
        )
        or (
            source.source_kind == "production_state"
            and source.authority_role == "HISTORICAL"
            and source.scope in current_narrative_scopes
        )
    ]
    if mismatch_sources:
        refs = tuple(_source_ref(workspace_root, source) for source in mismatch_sources)
        conflicts.append(CreatorConflict("AUTHORITY_MISMATCH", "AUTHORITY_MISMATCH", None, "current story authority conflicts with historical production mapping", _provenance(refs, "VALIDATED", "creator.authority.mismatch")))

    blockers = tuple(
        CreatorBlocker(f"MISSING_{asset.asset_id}", "WARNING", asset.asset_id, "creator.asset.media", f"media is {asset.observed_readiness}", "filesystem observation", _provenance(asset.provenance.source_refs, "VALIDATED", "creator.asset.media"))
        for asset in assets
        if asset.observed_readiness == "MISSING"
    )
    return CreatorSnapshot("creator-snapshot.v1", catalog.project_id, overview, metrics, tuple(narrative_nodes), tuple(emotion_points), tuple(sorted(assets, key=lambda item: item.asset_id)), tuple(sorted(shots, key=lambda item: item.shot_id)), tuple(continuity_edges), blockers, tuple(conflicts), tuple(sorted(coverage, key=lambda item: item.coverage_id)))


__all__ = [
    "CreatorAction", "CreatorAsset", "CreatorBlocker", "CreatorConflict", "CreatorContinuityEdge", "CreatorCoverage",
    "CreatorEmotionPoint", "CreatorMetric", "CreatorNarrativeNode", "CreatorOverview", "CreatorProvenance",
    "CreatorShot", "CreatorSnapshot", "CreatorSourceRef", "collect_creator_snapshot",
]
