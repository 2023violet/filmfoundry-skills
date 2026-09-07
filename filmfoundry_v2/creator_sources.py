"""Creator source catalog discovery and parser dispatch."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Callable, Mapping, Protocol

from .beat_map import parse_emotional_beat_map, validate_emotional_beat_map
from .contracts import (
    ID_RE,
    validate_asset_registry,
    validate_production_state,
    validate_shot_spec,
    validate_workspace_manifest,
)
from .dependency_graph import parse_dependency_graph, validate_dependency_graph


_CATALOG_FILE = "creator-source-catalog.v1.json"
_CATALOG_SCHEMA = "creator-source-catalog.v1"
_PATH_BASES = {"WORKSPACE_ROOT", "RUNTIME_DIR"}
_AUTHORITY_ROLES = {"CURRENT", "HISTORICAL", "SUPPORTING"}
_PATH_ESCAPE_ERROR = "CREATOR_SOURCE_PATH_ESCAPE: source path escapes workspace"
_ARCHIVE_ACTIVE_ERROR = "CREATOR_ARCHIVE_SOURCE_ACTIVE: active source is inside archive"
_MULTIPLE_CURRENT_ERROR = "CREATOR_MULTIPLE_CURRENT: multiple CURRENT sources for source_kind and scope"
_UNKNOWN_SCHEMA_ERROR = "CREATOR_UNKNOWN_SCHEMA: unsupported source schema"
_UNKNOWN_ENUM_ERROR = "CREATOR_UNKNOWN_ENUM: unknown authority_role"
_INVALID_ID_ERROR = "CREATOR_INVALID_ID: invalid stable ASCII ID"
_DUPLICATE_SOURCE_ID_ERROR = "CREATOR_DUPLICATE_SOURCE_ID: duplicate source_id"
_SOURCE_INVALID_ERROR = "CREATOR_SOURCE_INVALID: source validation failed"
_SCOPE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,63}$")
_NARRATIVE_NODE_FIELDS = {
    "node_id",
    "node_type",
    "display_name",
    "narrative_responsibility",
    "parent_id",
    "canon_source",
}
_NARRATIVE_NODE_TYPES = {"SEASON", "ARC", "EPISODE", "SEQUENCE", "SCENE", "BEAT"}
_CONTINUITY_CHAIN_FIELDS = {"chain_id", "entity_id", "edges"}
_CONTINUITY_EDGE_FIELDS = {"from_shot_id", "to_shot_id", "field", "from_value", "to_value"}


@dataclass(frozen=True)
class CreatorCatalogSource:
    source_id: str
    source_kind: str
    path: Path
    parser_id: str
    schema_version: str
    authority_role: str
    scope: str
    required: bool
    data: object


@dataclass(frozen=True)
class CreatorSourceCoverageGap:
    source_id: str
    source_kind: str
    parser_id: str
    schema_version: str
    reason: str


@dataclass(frozen=True)
class CreatorSourceCatalog:
    root: Path
    project_id: str
    runtime_path: Path
    sources: tuple[CreatorCatalogSource, ...]
    coverage_gaps: tuple[CreatorSourceCoverageGap, ...]


class CreatorProjectAdapter(Protocol):
    def locate_catalog(self, root: Path) -> Path:
        """Return the project-specific source catalog path."""


Parser = Callable[[object], object]


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"CREATOR_SOURCE_INVALID: unable to read source: {path}") from exc


def _validated(errors: list[str], data: object) -> object:
    if errors:
        raise ValueError(_SOURCE_INVALID_ERROR)
    return data


def _parse_workspace_manifest(data: object) -> object:
    return _validated(validate_workspace_manifest(data) if isinstance(data, dict) else ["invalid"], data)


def _parse_asset_registry(data: object) -> object:
    return _validated(
        validate_asset_registry(data) if isinstance(data, (dict, list)) else ["invalid"],
        data,
    )


def _parse_production_state(data: object) -> object:
    return _validated(validate_production_state(data) if isinstance(data, dict) else ["invalid"], data)


def _parse_shot_spec(data: object) -> object:
    return _validated(validate_shot_spec(data) if isinstance(data, dict) else ["invalid"], data)


def _parse_dependency_graph(data: object) -> object:
    if not isinstance(data, Mapping):
        raise ValueError(_SOURCE_INVALID_ERROR)
    parsed = parse_dependency_graph(data)
    return _validated([issue.message for issue in validate_dependency_graph(parsed).errors], data)


def _parse_emotional_beat_map(data: object) -> object:
    if not isinstance(data, Mapping):
        raise ValueError(_SOURCE_INVALID_ERROR)
    parsed = parse_emotional_beat_map(data)
    return _validated([issue.message for issue in validate_emotional_beat_map(parsed).errors], data)


def _parse_narrative_index(data: object) -> object:
    if (
        not isinstance(data, Mapping)
        or set(data) != {"schema_version", "nodes"}
        or data.get("schema_version") != "narrative-index.v1"
    ):
        raise ValueError(_SOURCE_INVALID_ERROR)
    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError(_SOURCE_INVALID_ERROR)
    parents: dict[str, str | None] = {}
    for node in nodes:
        if not isinstance(node, Mapping) or set(node) != _NARRATIVE_NODE_FIELDS:
            raise ValueError(_SOURCE_INVALID_ERROR)
        node_id = node.get("node_id")
        parent_id = node.get("parent_id")
        if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id) or node_id in parents:
            raise ValueError(_SOURCE_INVALID_ERROR)
        if node.get("node_type") not in _NARRATIVE_NODE_TYPES:
            raise ValueError(_SOURCE_INVALID_ERROR)
        if any(
            not isinstance(node.get(field), str) or not node[field]
            for field in ("display_name", "narrative_responsibility", "canon_source")
        ):
            raise ValueError(_SOURCE_INVALID_ERROR)
        if parent_id is not None and (not isinstance(parent_id, str) or not ID_RE.fullmatch(parent_id)):
            raise ValueError(_SOURCE_INVALID_ERROR)
        parents[node_id] = parent_id
    for node_id, parent_id in parents.items():
        visited = {node_id}
        while parent_id is not None:
            if parent_id not in parents or parent_id in visited:
                raise ValueError(_SOURCE_INVALID_ERROR)
            visited.add(parent_id)
            parent_id = parents[parent_id]
    return data


def _parse_continuity_chain(data: object) -> object:
    if (
        not isinstance(data, Mapping)
        or set(data) != {"schema_version", "chains"}
        or data.get("schema_version") != "continuity-chain.v1"
    ):
        raise ValueError(_SOURCE_INVALID_ERROR)
    chains = data.get("chains")
    if not isinstance(chains, list):
        raise ValueError(_SOURCE_INVALID_ERROR)
    chain_ids: set[str] = set()
    for chain in chains:
        if not isinstance(chain, Mapping) or set(chain) != _CONTINUITY_CHAIN_FIELDS:
            raise ValueError(_SOURCE_INVALID_ERROR)
        chain_id = chain.get("chain_id")
        entity_id = chain.get("entity_id")
        edges = chain.get("edges")
        if (
            not isinstance(chain_id, str)
            or not ID_RE.fullmatch(chain_id)
            or chain_id in chain_ids
            or not isinstance(entity_id, str)
            or not ID_RE.fullmatch(entity_id)
            or not isinstance(edges, list)
        ):
            raise ValueError(_SOURCE_INVALID_ERROR)
        chain_ids.add(chain_id)
        edge_keys: set[tuple[str, str, str]] = set()
        for edge in edges:
            if not isinstance(edge, Mapping) or set(edge) != _CONTINUITY_EDGE_FIELDS:
                raise ValueError(_SOURCE_INVALID_ERROR)
            from_shot = edge.get("from_shot_id")
            to_shot = edge.get("to_shot_id")
            field = edge.get("field")
            if (
                not isinstance(from_shot, str)
                or not ID_RE.fullmatch(from_shot)
                or not isinstance(to_shot, str)
                or not ID_RE.fullmatch(to_shot)
                or from_shot == to_shot
                or not isinstance(field, str)
                or not field
                or any(not isinstance(edge.get(name), str) or not edge[name] for name in ("from_value", "to_value"))
            ):
                raise ValueError(_SOURCE_INVALID_ERROR)
            key = (from_shot, to_shot, field)
            if key in edge_keys:
                raise ValueError(_SOURCE_INVALID_ERROR)
            edge_keys.add(key)
    return data


_PARSERS: dict[tuple[str, str], Parser] = {
    ("workspace-manifest-json", "workspace-manifest.v2"): _parse_workspace_manifest,
    ("asset-registry-json", "asset-registry.v2"): _parse_asset_registry,
    ("production-state-json", "production-state.v2"): _parse_production_state,
    ("shot-spec-json", "shot-spec.v2"): _parse_shot_spec,
    ("dependency-graph-json", "asset-dependency-graph.v2"): _parse_dependency_graph,
    ("emotional-beat-map-json", "emotional-beat-map.v2"): _parse_emotional_beat_map,
    ("narrative-index-json", "narrative-index.v1"): _parse_narrative_index,
    ("continuity-chain-json", "continuity-chain.v1"): _parse_continuity_chain,
}


def _normalized_relative_path(value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(_PATH_ESCAPE_ERROR)
    normalized = value.replace("\\", "/")
    windows = PureWindowsPath(value)
    posix = PurePosixPath(normalized)
    if windows.drive or windows.is_absolute() or posix.is_absolute():
        raise ValueError(_PATH_ESCAPE_ERROR)
    return Path(normalized)


def _resolve_workspace_path(root: Path, base: Path, value: object) -> Path:
    relative = _normalized_relative_path(value)
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(_PATH_ESCAPE_ERROR) from exc
    return resolved


def _is_active_archive_path(path: Path, archive_paths: tuple[Path, ...]) -> bool:
    for archive_path in archive_paths:
        try:
            path.relative_to(archive_path)
        except ValueError:
            continue
        return True
    return False


def _catalog_path(root: Path, adapter: CreatorProjectAdapter | None) -> Path:
    if adapter is None:
        return root / _CATALOG_FILE
    value = str(adapter.locate_catalog(root))
    normalized = value.replace("\\", "/")
    windows = PureWindowsPath(value)
    posix = PurePosixPath(normalized)
    if windows.drive and not windows.is_absolute():
        raise ValueError(_PATH_ESCAPE_ERROR)
    if windows.is_absolute() or posix.is_absolute():
        path = Path(normalized)
        if not path.is_absolute():
            raise ValueError(_PATH_ESCAPE_ERROR)
        path = path.resolve()
    else:
        path = (root / Path(normalized)).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(_PATH_ESCAPE_ERROR) from exc
    return path


def _validate_catalog_source(source: object) -> Mapping[str, object]:
    if not isinstance(source, Mapping):
        raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog source")
    role = source.get("authority_role")
    if role not in _AUTHORITY_ROLES:
        raise ValueError(_UNKNOWN_ENUM_ERROR)
    source_id = source.get("source_id")
    scope = source.get("scope")
    if (
        not isinstance(source_id, str)
        or not ID_RE.fullmatch(source_id)
        or not isinstance(scope, str)
        or not _SCOPE_RE.fullmatch(scope)
    ):
        raise ValueError(_INVALID_ID_ERROR)
    required_fields = ("source_kind", "path", "parser_id", "schema_version")
    if (
        any(not isinstance(source.get(field), str) or not source[field] for field in required_fields)
        or source.get("path_base") not in _PATH_BASES
        or not isinstance(source.get("required"), bool)
    ):
        raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog source")
    return source


def discover_creator_sources(root: Path, adapter: CreatorProjectAdapter | None = None) -> CreatorSourceCatalog:
    workspace_root = Path(root).resolve()
    catalog_path = _catalog_path(workspace_root, adapter)
    catalog = _load_json(catalog_path)
    if not isinstance(catalog, Mapping) or catalog.get("schema_version") != _CATALOG_SCHEMA:
        raise ValueError(_UNKNOWN_SCHEMA_ERROR)

    project_id = catalog.get("project_id")
    if not isinstance(project_id, str) or not ID_RE.fullmatch(project_id):
        raise ValueError(_INVALID_ID_ERROR)
    sources = catalog.get("sources")
    if not isinstance(sources, list):
        raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog")

    declared_sources = tuple(_validate_catalog_source(source) for source in sources)
    source_ids: set[str] = set()
    current_keys: set[tuple[str, str]] = set()
    for source in declared_sources:
        source_id = source["source_id"]
        assert isinstance(source_id, str)
        if source_id in source_ids:
            raise ValueError(_DUPLICATE_SOURCE_ID_ERROR)
        source_ids.add(source_id)
        role = source["authority_role"]
        if role == "CURRENT":
            source_kind = source["source_kind"]
            scope = source["scope"]
            assert isinstance(source_kind, str) and isinstance(scope, str)
            key = (source_kind, scope)
            if key in current_keys:
                raise ValueError(_MULTIPLE_CURRENT_ERROR)
            current_keys.add(key)

    runtime_path = _resolve_workspace_path(workspace_root, workspace_root, catalog.get("runtime_path"))
    runtime_dir = runtime_path.parent
    resolved_sources: list[tuple[Mapping[str, object], Path]] = []
    for source in declared_sources:
        base = workspace_root if source["path_base"] == "WORKSPACE_ROOT" else runtime_dir
        resolved_sources.append((source, _resolve_workspace_path(workspace_root, base, source["path"])))

    discovered: list[CreatorCatalogSource] = []
    gaps: list[CreatorSourceCoverageGap] = []
    parsed_data: dict[str, object] = {}
    archive_paths: list[Path] = []
    for source, resolved_path in resolved_sources:
        if source["source_kind"] != "workspace_manifest":
            continue
        source_id = source["source_id"]
        parser_id = source["parser_id"]
        schema_version = source["schema_version"]
        required = source["required"]
        assert isinstance(source_id, str) and isinstance(parser_id, str) and isinstance(schema_version, str) and isinstance(required, bool)
        parser = _PARSERS.get((parser_id, schema_version))
        if parser is None:
            if required:
                raise ValueError(_UNKNOWN_SCHEMA_ERROR)
            continue
        data = parser(_load_json(resolved_path))
        parsed_data[source_id] = data
        assert isinstance(data, Mapping)
        boundary = data["archive_boundary"]
        assert isinstance(boundary, Mapping)
        archive_paths.append(_resolve_workspace_path(workspace_root, workspace_root, boundary["path"]))

    for source, resolved_path in resolved_sources:
        source_id = source["source_id"]
        source_kind = source["source_kind"]
        parser_id = source["parser_id"]
        schema_version = source["schema_version"]
        role = source["authority_role"]
        scope = source["scope"]
        required = source["required"]
        assert all(isinstance(field, str) for field in (source_id, source_kind, parser_id, schema_version, role, scope))
        assert isinstance(required, bool)
        if role == "CURRENT" and _is_active_archive_path(resolved_path, tuple(archive_paths)):
            raise ValueError(_ARCHIVE_ACTIVE_ERROR)
        parser = _PARSERS.get((parser_id, schema_version))
        if parser is None:
            if required:
                raise ValueError(_UNKNOWN_SCHEMA_ERROR)
            gaps.append(CreatorSourceCoverageGap(source_id, source_kind, parser_id, schema_version, "unsupported source schema"))
            continue
        data = parsed_data.get(source_id)
        if data is None:
            data = parser(_load_json(resolved_path))
        discovered.append(
            CreatorCatalogSource(source_id, source_kind, resolved_path, parser_id, schema_version, role, scope, required, data)
        )

    return CreatorSourceCatalog(workspace_root, project_id, runtime_path, tuple(discovered), tuple(gaps))


__all__ = [
    "CreatorCatalogSource",
    "CreatorProjectAdapter",
    "CreatorSourceCatalog",
    "CreatorSourceCoverageGap",
    "discover_creator_sources",
]
