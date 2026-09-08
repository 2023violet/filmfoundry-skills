"""Typed, read-only Creator Snapshot collection."""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
import hashlib
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Literal, Mapping

from .creator_sources import CreatorCatalogSource, CreatorSourceCatalog, CreatorSourceCoverageGap
from .contracts import LIFECYCLE_STATES, STATE_RANK


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


TERMINOLOGY_SCHEMA_VERSION = "creator-terminology.v1"


def _freeze_mapping(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType({
        key: _freeze_mapping(item) if isinstance(item, Mapping) else item
        for key, item in value.items()
    })


_TERMINOLOGY: Mapping[str, Mapping[str, Mapping[str, str]]] = _freeze_mapping({
    "lifecycle": {
        "DRAFT": {"zh-CN": "草稿", "en": "Draft"},
        "SPEC_RESOLVED": {"zh-CN": "规格已解析", "en": "Specification resolved"},
        "PREFLIGHT_PASS": {"zh-CN": "预检通过", "en": "Preflight passed"},
        "READY_FOR_KF": {"zh-CN": "待生成关键帧", "en": "Ready for keyframe"},
        "KF_GENERATED": {"zh-CN": "关键帧已生成", "en": "Keyframe generated"},
        "KF_QC_PASS": {"zh-CN": "关键帧质检通过", "en": "Keyframe QC passed"},
        "READY_FOR_VIDEO": {"zh-CN": "待生成视频", "en": "Ready for video"},
        "VIDEO_GENERATED": {"zh-CN": "视频已生成", "en": "Video generated"},
        "VIDEO_QC_PASS": {"zh-CN": "视频质检通过", "en": "Video QC passed"},
        "SELECT": {"zh-CN": "已选片", "en": "Selected"},
        "OBSERVED_STATE_RECORDED": {"zh-CN": "已记录观察状态", "en": "Observed State recorded"},
        "EDIT_READY": {"zh-CN": "可剪辑", "en": "Ready for edit"},
    },
    "asset_state": {
        "PLANNED": {"zh-CN": "已规划", "en": "Planned"},
        "CANDIDATE": {"zh-CN": "候选", "en": "Candidate"},
        "LOCKED": {"zh-CN": "已锁定", "en": "Locked"},
        "RETIRED": {"zh-CN": "已退役", "en": "Retired"},
        "MISSING": {"zh-CN": "缺失", "en": "Missing"},
        "LEGACY_FORMAT": {"zh-CN": "旧格式", "en": "Legacy format"},
    },
    "evidence_level": {
        "UNVERIFIED": {"zh-CN": "未验证", "en": "Unverified"},
        "OBSERVED_ONCE": {"zh-CN": "观察一次", "en": "Observed once"},
        "REPEATED": {"zh-CN": "重复验证", "en": "Repeated"},
        "PROJECT_VERIFIED": {"zh-CN": "项目内验证", "en": "Project verified"},
        "CROSS_PROJECT_VERIFIED": {"zh-CN": "跨项目验证", "en": "Cross-project verified"},
    },
    "select_type": {
        "FULL": {"zh-CN": "完整选片", "en": "Full select"},
        "FULL_SELECT": {"zh-CN": "完整选片", "en": "Full select"},
        "PARTIAL_SELECT": {"zh-CN": "部分选片", "en": "Partial select"},
    },
    "authority": {
        "CURRENT": {"zh-CN": "当前权威", "en": "Current authority"},
        "HISTORICAL": {"zh-CN": "历史参考", "en": "Historical reference"},
        "SUPPORTING": {"zh-CN": "辅助来源", "en": "Supporting source"},
    },
    "severity": {
        "CRITICAL": {"zh-CN": "严重", "en": "Critical"},
        "ERROR": {"zh-CN": "错误", "en": "Error"},
        "BLOCKER": {"zh-CN": "阻塞", "en": "Blocker"},
        "WARNING": {"zh-CN": "警告", "en": "Warning"},
        "INFO": {"zh-CN": "信息", "en": "Info"},
        "ADVISORY": {"zh-CN": "建议", "en": "Advisory"},
    },
    "support_boundary": {
        "SOURCE_VALIDATION": {"zh-CN": "来源校验；Creator Layer 不修复来源", "en": "Source validation; Creator Layer does not repair sources"},
        "AUTHORITY_REVIEW": {"zh-CN": "权威来源复核；Creator Layer 不选择权威", "en": "Authority review; Creator Layer does not choose authority"},
        "HARD_BLOCKER_REVIEW": {"zh-CN": "硬阻塞复核；由来源所有者解决", "en": "Hard-blocker review; source owners resolve it"},
        "MISSING_ARTIFACT": {"zh-CN": "缺失制品复核；Creator Layer 不生成制品", "en": "Missing-artifact review; Creator Layer does not create artifacts"},
        "OBSERVED_STATE_HANDOFF": {"zh-CN": "观察状态交接；Creator Layer 不推测状态", "en": "Observed State handoff; Creator Layer does not infer state"},
        "LIFECYCLE_GUIDANCE": {"zh-CN": "生命周期指引；Creator Layer 不变更状态", "en": "Lifecycle guidance; Creator Layer does not change state"},
        "ASSET_INTEGRITY": {"zh-CN": "资产完整性复核；Creator Layer 不改写声明", "en": "Asset integrity review; Creator Layer does not rewrite declarations"},
        "NON_BLOCKING_ADVICE": {"zh-CN": "非阻塞建议；Creator Layer 仅报告", "en": "Non-blocking advice; Creator Layer only reports"},
    },
    "observed_readiness": {
        "PRESENT_HASH_OK": {"zh-CN": "文件存在且哈希匹配", "en": "Present, hash verified"},
        "PRESENT_HASH_UNVERIFIED": {"zh-CN": "文件存在但哈希未验证", "en": "Present, hash unverified"},
        "PRESENT_HASH_MISMATCH": {"zh-CN": "文件存在但哈希不匹配", "en": "Present, hash mismatch"},
        "MISSING": {"zh-CN": "文件缺失", "en": "Missing"},
        "NOT_APPLICABLE": {"zh-CN": "不适用", "en": "Not applicable"},
        "UNKNOWN": {"zh-CN": "未知", "en": "Unknown"},
    },
})

_TERM_CATEGORY_ALIASES = {
    "asset": "asset_state",
    "assetstate": "asset_state",
    "asset_state": "asset_state",
    "evidence": "evidence_level",
    "evidencelevel": "evidence_level",
    "observed": "observed_readiness",
    "observedreadiness": "observed_readiness",
    "readiness": "observed_readiness",
    "select": "select_type",
    "selecttype": "select_type",
    "support": "support_boundary",
    "supportboundary": "support_boundary",
}


def _term_category(category: object) -> str:
    normalized = str(category).strip().lower().replace("-", "_").replace(" ", "_")
    return _TERM_CATEGORY_ALIASES.get(normalized, normalized)


def _unknown_term(value: object, language: str) -> str:
    raw = "UNKNOWN" if value is None else str(value)
    if language == "zh-CN":
        return f"{raw}（无解释）"
    return f"{raw} (no explanation)"


@dataclass(frozen=True)
class CreatorTerminologyRegistry:
    """Versioned labels shared by Creator views and navigation."""

    schema_version: Literal["creator-terminology.v1"] = TERMINOLOGY_SCHEMA_VERSION
    terms: Mapping[str, Mapping[str, Mapping[str, str]]] = field(default_factory=lambda: _TERMINOLOGY)

    def __post_init__(self) -> None:
        object.__setattr__(self, "terms", _freeze_mapping(self.terms))

    @property
    def version(self) -> str:
        return self.schema_version

    @property
    def registry(self) -> Mapping[str, Mapping[str, Mapping[str, str]]]:
        return self.terms

    def label(self, category: str, value: object, *, language: str = "zh-CN") -> str:
        category_terms = self.terms.get(_term_category(category), {})
        value_terms = category_terms.get(str(value))
        if not isinstance(value_terms, Mapping):
            return _unknown_term(value, language if language == "zh-CN" else "en")
        requested = language if isinstance(language, str) and language else "zh-CN"
        candidates = (requested, "zh-CN", "en") if requested in {"zh-CN", "en"} else (requested, "en")
        for candidate in candidates:
            label = value_terms.get(candidate)
            if isinstance(label, str) and label:
                return label
        return _unknown_term(value, requested if requested == "zh-CN" else "en")

    def lookup(self, category: str, value: object, *, language: str = "zh-CN") -> str:
        return self.label(category, value, language=language)

    def translate(self, category: str, value: object, *, language: str = "zh-CN") -> str:
        return self.label(category, value, language=language)

    def __getitem__(self, category: str) -> Mapping[str, Mapping[str, str]]:
        return self.terms[_term_category(category)]


TERMINOLOGY_REGISTRY = CreatorTerminologyRegistry()


def get_creator_terminology(language: str = "zh-CN") -> CreatorTerminologyRegistry:
    """Return the immutable-versioned registry; language is selected at lookup time."""
    del language
    return TERMINOLOGY_REGISTRY


def terminology_label(category: str, value: object, *, language: str = "zh-CN") -> str:
    return TERMINOLOGY_REGISTRY.label(category, value, language=language)


def translate_creator_term(category: str, value: object, *, language: str = "zh-CN") -> str:
    return terminology_label(category, value, language=language)


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
    rule_id: str
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


@dataclass(frozen=True)
class CreatorNavigation:
    """Deterministic, read-only actions derived from a CreatorSnapshot."""

    actions: tuple[CreatorAction, ...]
    primary_action: CreatorAction | None
    parallel_actions: tuple[CreatorAction, ...]
    terminology_version: Literal["creator-terminology.v1"] = TERMINOLOGY_SCHEMA_VERSION
    schema_version: Literal["creator-navigation.v1"] = "creator-navigation.v1"

    @property
    def primary(self) -> CreatorAction | None:
        return self.primary_action

    @property
    def parallel(self) -> tuple[CreatorAction, ...]:
        return self.parallel_actions

    @property
    def primary_action_id(self) -> str | None:
        return self.primary_action.action_id if self.primary_action else None

    @property
    def parallel_action_ids(self) -> tuple[str, ...]:
        return tuple(action.action_id for action in self.parallel_actions)

    @property
    def terminology(self) -> CreatorTerminologyRegistry:
        return TERMINOLOGY_REGISTRY

    @property
    def same_priority_actions(self) -> tuple[CreatorAction, ...]:
        if self.primary_action is None:
            return ()
        return (self.primary_action, *self.parallel_actions)

    def to_dict(self) -> dict[str, Any]:
        return _jsonable(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class CreatorReadModel:
    """Composition of immutable snapshot facts and derived navigation."""

    snapshot: CreatorSnapshot
    navigation: CreatorNavigation
    schema_version: Literal["creator-read-model.v1"] = "creator-read-model.v1"

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
    selected_production_gaps: list[CreatorSourceCoverageGap] = []
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
            selected_production_gaps.extend(
                gap for gap in scope_gaps if gap.authority_role == "CURRENT"
            )
        elif any(gap.authority_role == "CURRENT" for gap in scope_gaps):
            selected_production_gaps.extend(
                gap for gap in scope_gaps if gap.authority_role == "CURRENT"
            )
            continue
        elif len(historical) == 1 and not any(gap.authority_role == "HISTORICAL" for gap in scope_gaps):
            production_sources.extend(historical)
        else:
            selected_production_gaps.extend(
                gap for gap in scope_gaps if gap.authority_role == "HISTORICAL"
            )

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
    production_gaps = selected_production_gaps
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


_NAV_PRIORITY_SOURCE = 1
_NAV_PRIORITY_HARD_BLOCKER = 2
_NAV_PRIORITY_MISSING_ARTIFACT = 3
_NAV_PRIORITY_OBSERVED_STATE = 4
_NAV_PRIORITY_LIFECYCLE = 5
_NAV_PRIORITY_ADVICE = 6
_SUPPORT_SOURCE_VALIDATION = "SOURCE_VALIDATION"
_SUPPORT_AUTHORITY_REVIEW = "AUTHORITY_REVIEW"
_SUPPORT_HARD_BLOCKER_REVIEW = "HARD_BLOCKER_REVIEW"
_SUPPORT_MISSING_ARTIFACT = "MISSING_ARTIFACT"
_SUPPORT_OBSERVED_STATE_HANDOFF = "OBSERVED_STATE_HANDOFF"
_SUPPORT_LIFECYCLE_GUIDANCE = "LIFECYCLE_GUIDANCE"
_SUPPORT_ASSET_INTEGRITY = "ASSET_INTEGRITY"
_SUPPORT_NON_BLOCKING_ADVICE = "NON_BLOCKING_ADVICE"
_HARD_SEVERITIES = {"CRITICAL", "ERROR", "BLOCKER"}
_SEVERITY_ORDER = {
    "CRITICAL": 0,
    "ERROR": 1,
    "BLOCKER": 1,
    "WARNING": 2,
    "INFO": 3,
    "ADVISORY": 4,
}


def _severity_key(value: object) -> tuple[int, str]:
    normalized = str(value).upper()
    return (_SEVERITY_ORDER.get(normalized, len(_SEVERITY_ORDER)), normalized)


def _nonempty_rule(value: object, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback


def _nonempty_reason(value: object, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback


def _nonempty_boundary(value: object, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback


def _support_boundary(value: object, fallback: str) -> str:
    if isinstance(value, str) and value in TERMINOLOGY_REGISTRY.registry.get("support_boundary", {}):
        return value
    return fallback


def _refs(*provenances: CreatorProvenance) -> tuple[CreatorSourceRef, ...]:
    result: list[CreatorSourceRef] = []
    for provenance in provenances:
        for source_ref in provenance.source_refs:
            if source_ref not in result:
                result.append(source_ref)
    return tuple(result)


def _action(
    action_id: str,
    entity_id: str | None,
    priority: int,
    severity: str,
    reason: str,
    rule_id: str,
    prerequisites: tuple[str, ...],
    support_boundary: str,
    provenance: CreatorProvenance,
) -> CreatorAction:
    if not provenance.source_refs:
        raise ValueError("CREATOR_NAVIGATION_PROVENANCE: derived action requires non-empty provenance")
    action_provenance = CreatorProvenance(
        provenance.source_refs,
        "AGGREGATED" if len(provenance.source_refs) > 1 else "VALIDATED",
        rule_id,
    )
    return CreatorAction(
        action_id,
        entity_id,
        priority,
        severity,
        reason,
        rule_id,
        prerequisites or ("source facts must remain available",),
        support_boundary or "Creator Layer reports facts; it does not mutate source authorities",
        action_provenance,
    )


def _blocker_priority(blocker: CreatorBlocker) -> int:
    rule = str(blocker.rule_id or "").lower()
    reason = str(blocker.reason or "").lower()
    if str(blocker.severity).upper() in _HARD_SEVERITIES:
        return _NAV_PRIORITY_HARD_BLOCKER
    if "observed_state" in rule or "previous" in rule:
        return _NAV_PRIORITY_OBSERVED_STATE
    if "missing" in rule or "missing" in reason or "missing" in blocker.blocker_id.lower():
        return _NAV_PRIORITY_MISSING_ARTIFACT
    return _NAV_PRIORITY_ADVICE


def _missing_observed_state_actions(snapshot: CreatorSnapshot) -> list[CreatorAction]:
    actions: list[CreatorAction] = []
    shot_by_id = {shot.shot_id: shot for shot in snapshot.shots}
    handoff_predecessors = {
        edge.from_shot_id
        for edge in snapshot.continuity_edges
        if edge.to_shot_id in shot_by_id
    }
    for shot in sorted(snapshot.shots, key=lambda item: item.shot_id):
        status = str(shot.runtime_status or "").upper()
        if (
            shot.shot_id not in handoff_predecessors
            and shot.observed_state in (None, "")
            and status in STATE_RANK
            and STATE_RANK[status] >= STATE_RANK["SELECT"]
        ):
            action_id = f"OBSERVED_STATE_{shot.shot_id}"
            actions.append(
                _action(
                    action_id,
                    shot.shot_id,
                    _NAV_PRIORITY_OBSERVED_STATE,
                    "WARNING",
                    f"shot {shot.shot_id} has no Observed State",
                    "creator.navigation.previous_observed_state",
                    ("record the shot's Observed State before continuing",),
                    _SUPPORT_OBSERVED_STATE_HANDOFF,
                    shot.provenance,
                )
            )
    for edge in sorted(snapshot.continuity_edges, key=lambda item: (item.from_shot_id, item.to_shot_id, item.field, item.chain_id)):
        source_shot = shot_by_id.get(edge.from_shot_id)
        successor = shot_by_id.get(edge.to_shot_id)
        source_status = str(source_shot.runtime_status or "").upper() if source_shot else ""
        successor_status = str(successor.runtime_status or "").upper() if successor else ""
        if (
            source_shot is None
            or successor is None
            or source_shot.observed_state not in (None, "")
            or source_status not in STATE_RANK
            or STATE_RANK[source_status] < STATE_RANK["SELECT"]
        ):
            continue
        action_id = f"OBSERVED_STATE_{edge.from_shot_id}_BEFORE_{edge.to_shot_id}"
        actions.append(
            _action(
                action_id,
                edge.from_shot_id,
                _NAV_PRIORITY_OBSERVED_STATE,
                "WARNING",
                f"previous shot {edge.from_shot_id} has no Observed State before {edge.to_shot_id}",
                "creator.navigation.previous_observed_state",
                ("record the predecessor Observed State for the continuity handoff",),
                _SUPPORT_OBSERVED_STATE_HANDOFF,
                CreatorProvenance(_refs(edge.provenance, source_shot.provenance), "AGGREGATED", "creator.navigation.previous_observed_state"),
            )
        )
    return actions


def _lifecycle_actions(snapshot: CreatorSnapshot) -> list[CreatorAction]:
    actions: list[CreatorAction] = []
    for shot in sorted(snapshot.shots, key=lambda item: item.shot_id):
        status = str(shot.runtime_status or "").upper()
        if status not in STATE_RANK or status == LIFECYCLE_STATES[-1]:
            continue
        next_state = LIFECYCLE_STATES[STATE_RANK[status] + 1]
        actions.append(
            _action(
                f"LIFECYCLE_{shot.shot_id}_{next_state}",
                shot.shot_id,
                _NAV_PRIORITY_LIFECYCLE,
                "INFO",
                f"advance {shot.shot_id} from {status} to {next_state}",
                "creator.navigation.lifecycle.next",
                (f"complete the prerequisites for {next_state}",),
                _SUPPORT_LIFECYCLE_GUIDANCE,
                shot.provenance,
            )
        )
    return actions


def _advice_actions(snapshot: CreatorSnapshot) -> list[CreatorAction]:
    actions: list[CreatorAction] = []
    for asset in sorted(snapshot.assets, key=lambda item: item.asset_id):
        if asset.observed_readiness != "PRESENT_HASH_UNVERIFIED":
            continue
        actions.append(
            _action(
                f"ADVICE_ASSET_{asset.asset_id}",
                asset.asset_id,
                _NAV_PRIORITY_ADVICE,
                "INFO",
                f"verify the observed media hash for {asset.asset_id}",
                "creator.navigation.asset.hash",
                ("compute and compare the declared media hash",),
                _SUPPORT_NON_BLOCKING_ADVICE,
                asset.provenance,
            )
        )
    return actions


def _asset_integrity_actions(snapshot: CreatorSnapshot) -> list[CreatorAction]:
    actions: list[CreatorAction] = []
    for asset in sorted(snapshot.assets, key=lambda item: item.asset_id):
        if asset.observed_readiness != "PRESENT_HASH_MISMATCH":
            continue
        actions.append(
            _action(
                f"INTEGRITY_ASSET_{asset.asset_id}",
                asset.asset_id,
                _NAV_PRIORITY_HARD_BLOCKER,
                "ERROR",
                f"observed media hash does not match the declaration for {asset.asset_id}",
                "creator.navigation.asset.integrity",
                ("inspect the media and reconcile its declared hash",),
                _SUPPORT_ASSET_INTEGRITY,
                asset.provenance,
            )
        )
    return actions


def derive_creator_navigation(snapshot: CreatorSnapshot) -> CreatorNavigation:
    """Derive deterministic actions from Snapshot facts without source access."""
    actions: list[CreatorAction] = []

    for coverage in snapshot.coverage:
        if coverage.data_status not in {"UNKNOWN", "INVALID"}:
            continue
        severity = "ERROR" if coverage.data_status == "INVALID" else "WARNING"
        actions.append(
            _action(
                f"SOURCE_{coverage.coverage_id}",
                coverage.coverage_id,
                _NAV_PRIORITY_SOURCE,
                severity,
                _nonempty_reason(coverage.reason, "source is unavailable"),
                _nonempty_rule(coverage.provenance.rule_id, "creator.navigation.source_coverage"),
                ("make the declared source readable and parseable",),
                _SUPPORT_SOURCE_VALIDATION,
                coverage.provenance,
            )
        )

    for conflict in snapshot.conflicts:
        actions.append(
            _action(
                f"CONFLICT_{conflict.conflict_id}",
                conflict.entity_id,
                _NAV_PRIORITY_SOURCE,
                "ERROR",
                _nonempty_reason(conflict.reason, "authority conflict requires review"),
                _nonempty_rule(conflict.provenance.rule_id, "creator.navigation.authority_conflict"),
                ("review the competing source authorities",),
                _SUPPORT_AUTHORITY_REVIEW,
                conflict.provenance,
            )
        )

    for blocker in snapshot.blockers:
        priority = _blocker_priority(blocker)
        actions.append(
            _action(
                f"BLOCKER_{blocker.blocker_id}",
                blocker.entity_id,
                priority,
                str(blocker.severity),
                _nonempty_reason(blocker.reason, "production blocker requires review"),
                _nonempty_rule(blocker.rule_id, "creator.navigation.blocker"),
                (f"resolve blocker {blocker.blocker_id}",),
                _support_boundary(blocker.support_boundary, _SUPPORT_HARD_BLOCKER_REVIEW),
                blocker.provenance,
            )
        )

    actions.extend(_missing_observed_state_actions(snapshot))
    actions.extend(_lifecycle_actions(snapshot))
    actions.extend(_asset_integrity_actions(snapshot))
    actions.extend(_advice_actions(snapshot))

    actions.sort(key=lambda item: (item.priority, _severity_key(item.severity), item.entity_id or "", item.action_id))
    ordered = tuple(actions)
    primary = ordered[0] if ordered else None
    parallel = tuple(action for action in ordered[1:] if primary is not None and action.priority == primary.priority)
    return CreatorNavigation(ordered, primary, parallel)


def build_creator_read_model(root: Path, catalog: CreatorSourceCatalog) -> CreatorReadModel:
    snapshot = collect_creator_snapshot(root, catalog)
    return CreatorReadModel(snapshot, derive_creator_navigation(snapshot))


__all__ = [
    "CreatorAction", "CreatorAsset", "CreatorBlocker", "CreatorConflict", "CreatorContinuityEdge", "CreatorCoverage",
    "CreatorEmotionPoint", "CreatorMetric", "CreatorNarrativeNode", "CreatorNavigation", "CreatorOverview",
    "CreatorProvenance", "CreatorReadModel", "CreatorShot", "CreatorSnapshot", "CreatorSourceRef",
    "CreatorTerminologyRegistry", "TERMINOLOGY_REGISTRY", "TERMINOLOGY_SCHEMA_VERSION",
    "build_creator_read_model", "collect_creator_snapshot", "derive_creator_navigation", "get_creator_terminology",
    "terminology_label", "translate_creator_term",
]
