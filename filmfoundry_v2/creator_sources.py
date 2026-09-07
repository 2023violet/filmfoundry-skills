"""Creator source catalog discovery and parser dispatch."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable, Mapping, Protocol

from .beat_map import parse_emotional_beat_map, validate_emotional_beat_map
from .contracts import (
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
_REPEATED_CURRENT_KINDS = {"shot_spec"}
_PATH_ESCAPE_ERROR = "CREATOR_SOURCE_PATH_ESCAPE: source path escapes workspace"
_ARCHIVE_ACTIVE_ERROR = "CREATOR_ARCHIVE_SOURCE_ACTIVE: active source is inside archive"
_MULTIPLE_CURRENT_ERROR = "CREATOR_MULTIPLE_CURRENT: multiple CURRENT sources for source_kind and scope"
_UNKNOWN_SCHEMA_ERROR = "CREATOR_UNKNOWN_SCHEMA: unsupported source schema"
_UNKNOWN_ENUM_ERROR = "CREATOR_UNKNOWN_ENUM: unknown authority_role"


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
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
    return data


def _parse_workspace_manifest(data: object) -> object:
    return _validated(validate_workspace_manifest(data) if isinstance(data, dict) else ["invalid"], data)


def _parse_asset_registry(data: object) -> object:
    return _validated(validate_asset_registry(data) if isinstance(data, list) else ["invalid"], data)


def _parse_production_state(data: object) -> object:
    return _validated(validate_production_state(data) if isinstance(data, dict) else ["invalid"], data)


def _parse_shot_spec(data: object) -> object:
    return _validated(validate_shot_spec(data) if isinstance(data, dict) else ["invalid"], data)


def _parse_dependency_graph(data: object) -> object:
    if not isinstance(data, Mapping):
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
    parsed = parse_dependency_graph(data)
    return _validated([issue.message for issue in validate_dependency_graph(parsed).errors], data)


def _parse_emotional_beat_map(data: object) -> object:
    if not isinstance(data, Mapping):
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
    parsed = parse_emotional_beat_map(data)
    return _validated([issue.message for issue in validate_emotional_beat_map(parsed).errors], data)


def _parse_narrative_index(data: object) -> object:
    if not isinstance(data, Mapping) or data.get("schema_version") != "narrative-index.v1":
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or any(not isinstance(node, Mapping) for node in nodes):
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
    return data


def _parse_continuity_chain(data: object) -> object:
    if not isinstance(data, Mapping) or data.get("schema_version") != "continuity-chain.v1":
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
    chains = data.get("chains")
    if not isinstance(chains, list) or any(not isinstance(chain, Mapping) for chain in chains):
        raise ValueError("CREATOR_SOURCE_INVALID: source validation failed")
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


def _normalize_path(value: str) -> Path:
    return Path(value.replace("\\", "/"))


def _resolve_workspace_path(root: Path, base: Path, value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(_PATH_ESCAPE_ERROR)
    relative = _normalize_path(value)
    if relative.is_absolute():
        raise ValueError(_PATH_ESCAPE_ERROR)
    resolved = (base / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(_PATH_ESCAPE_ERROR) from exc
    return resolved


def _archive_parts(root: Path) -> tuple[tuple[str, ...], ...]:
    manifest_path = root / "workspace-manifest.v2.json"
    if not manifest_path.is_file():
        return ()
    manifest = _load_json(manifest_path)
    if not isinstance(manifest, Mapping):
        return ()
    boundary = manifest.get("archive_boundary")
    archive_path = boundary.get("path") if isinstance(boundary, Mapping) else None
    if not isinstance(archive_path, str) or not archive_path:
        return ()
    normalized = _normalize_path(archive_path)
    return (tuple(part.casefold() for part in normalized.parts),)


def _is_active_archive_path(root: Path, path: Path, archive_parts: tuple[tuple[str, ...], ...]) -> bool:
    relative_parts = tuple(part.casefold() for part in path.relative_to(root).parts)
    if any(relative_parts[: len(parts)] == parts for parts in archive_parts):
        return True
    return any(part.startswith("99_") for part in relative_parts)


def _catalog_path(root: Path, adapter: CreatorProjectAdapter | None) -> Path:
    if adapter is None:
        return root / _CATALOG_FILE
    path = Path(adapter.locate_catalog(root)).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(_PATH_ESCAPE_ERROR) from exc
    return path


def discover_creator_sources(root: Path, adapter: CreatorProjectAdapter | None = None) -> CreatorSourceCatalog:
    workspace_root = Path(root).resolve()
    catalog_path = _catalog_path(workspace_root, adapter)
    catalog = _load_json(catalog_path)
    if not isinstance(catalog, Mapping) or catalog.get("schema_version") != _CATALOG_SCHEMA:
        raise ValueError(_UNKNOWN_SCHEMA_ERROR)

    project_id = catalog.get("project_id")
    if not isinstance(project_id, str) or not project_id:
        raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog")
    runtime_path = _resolve_workspace_path(workspace_root, workspace_root, catalog.get("runtime_path"))
    runtime_dir = runtime_path.parent
    sources = catalog.get("sources")
    if not isinstance(sources, list):
        raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog")

    current_keys: set[tuple[str, str]] = set()
    for source in sources:
        if not isinstance(source, Mapping):
            raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog source")
        role = source.get("authority_role")
        if role not in _AUTHORITY_ROLES:
            raise ValueError(_UNKNOWN_ENUM_ERROR)
        if role == "CURRENT":
            source_kind = str(source.get("source_kind", ""))
            key = (source_kind, str(source.get("scope", "")))
            if source_kind in _REPEATED_CURRENT_KINDS:
                key = (source_kind, f"{key[1]}:{source.get('path', '')}")
            if key in current_keys:
                raise ValueError(_MULTIPLE_CURRENT_ERROR)
            current_keys.add(key)

    archive_parts = _archive_parts(workspace_root)
    discovered: list[CreatorCatalogSource] = []
    gaps: list[CreatorSourceCoverageGap] = []
    for source in sources:
        assert isinstance(source, Mapping)
        path_base = source.get("path_base")
        if path_base not in _PATH_BASES:
            raise ValueError("CREATOR_SOURCE_INVALID: invalid path_base")
        base = workspace_root if path_base == "WORKSPACE_ROOT" else runtime_dir
        resolved_path = _resolve_workspace_path(workspace_root, base, source.get("path"))
        role = source["authority_role"]
        if role == "CURRENT" and _is_active_archive_path(workspace_root, resolved_path, archive_parts):
            raise ValueError(_ARCHIVE_ACTIVE_ERROR)

        source_id = source.get("source_id")
        source_kind = source.get("source_kind")
        parser_id = source.get("parser_id")
        schema_version = source.get("schema_version")
        scope = source.get("scope")
        required = source.get("required")
        fields = (source_id, source_kind, parser_id, schema_version, scope)
        if not all(isinstance(field, str) and field for field in fields) or not isinstance(required, bool):
            raise ValueError("CREATOR_SOURCE_INVALID: invalid catalog source")
        parser = _PARSERS.get((parser_id, schema_version))
        if parser is None:
            if required:
                raise ValueError(_UNKNOWN_SCHEMA_ERROR)
            gaps.append(CreatorSourceCoverageGap(source_id, source_kind, parser_id, schema_version, "unsupported source schema"))
            continue
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
