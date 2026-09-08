"""Scene-level topology and floor-plan facts."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Mapping

from .contracts import ID_RE
from .report import ValidationIssue, ValidationReport
from .script_analysis import _extensions, _load_mapping, _unknown

_ROOT = {"schema_version", "topology_id", "location_id", "nodes", "movement_paths", "review_status", "extensions"}
_NODE = {"node_id", "node_type", "adjacent_nodes", "entrances", "exits", "floor", "elevation", "orientation", "anchor_ids", "light_sources", "camera_side_regions", "extensions"}
_PATH = {"path_id", "subject_id", "node_ids", "anchor_ids", "screen_direction", "extensions"}

@dataclass(frozen=True)
class SceneTopology:
    topology_id: str
    location_id: str
    nodes: tuple[Mapping[str, Any], ...] = ()
    movement_paths: tuple[Mapping[str, Any], ...] = ()
    review_status: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)
    def to_dict(self) -> dict[str, Any]: return dict(self.raw)

def parse_scene_topology(value: str | Path | Mapping[str, Any]) -> SceneTopology:
    if isinstance(value, SceneTopology): return value
    payload = _load_mapping(value, "scene topology")
    return SceneTopology(str(payload.get("topology_id", "")), str(payload.get("location_id", "")), tuple(dict(x) for x in payload.get("nodes", ()) if isinstance(x, Mapping)), tuple(dict(x) for x in payload.get("movement_paths", ()) if isinstance(x, Mapping)), str(payload.get("review_status", "")), dict(payload))

def _issue(code: str, message: str, pointer: str, source: str) -> ValidationIssue: return ValidationIssue("ERROR", code, message, source=source, json_pointer=pointer)
def _required_id(value: Any, name: str, pointer: str, source: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value): issues.append(_issue("INVALID_ID", f"{pointer}/{name}: stable ASCII ID required", f"{pointer}/{name}", source))

def validate_scene_topology(value: SceneTopology | Mapping[str, Any], *, source: str = "") -> ValidationReport:
    data = value.to_dict() if isinstance(value, SceneTopology) else value
    if not isinstance(data, Mapping): return ValidationReport("scene_topology", [], [_issue("INVALID_TYPE", "scene topology: top-level object required", "", source)])
    issues = _unknown(data, _ROOT, "", source)
    if data.get("schema_version") != "scene-topology.v2": issues.append(_issue("INVALID_SCHEMA_VERSION", "schema_version: expected scene-topology.v2", "/schema_version", source))
    _required_id(data.get("topology_id"), "topology_id", "", source, issues); _required_id(data.get("location_id"), "location_id", "", source, issues)
    nodes = data.get("nodes")
    node_ids: set[str] = set()
    if not isinstance(nodes, list) or not nodes: issues.append(_issue("INVALID_TYPE", "nodes: non-empty list required", "/nodes", source)); nodes = []
    for i, node in enumerate(nodes):
        p = f"/nodes/{i}"
        if not isinstance(node, Mapping): issues.append(_issue("INVALID_TYPE", f"{p}: object required", p, source)); continue
        issues.extend(_unknown(node, _NODE, p, source)); nid = node.get("node_id"); _required_id(nid, "node_id", p, source, issues)
        if isinstance(nid, str) and nid in node_ids: issues.append(_issue("DUPLICATE_ID", f"{p}/node_id: duplicate {nid}", f"{p}/node_id", source))
        if isinstance(nid, str): node_ids.add(nid)
        for field_name in ("node_type", "floor", "elevation", "orientation"):
            if not isinstance(node.get(field_name), str) or not node[field_name].strip(): issues.append(_issue("REQUIRED_FIELD", f"{p}/{field_name}: non-empty string required", f"{p}/{field_name}", source))
        for field_name in ("adjacent_nodes", "entrances", "exits", "anchor_ids", "light_sources", "camera_side_regions"):
            if not isinstance(node.get(field_name), list): issues.append(_issue("INVALID_TYPE", f"{p}/{field_name}: list required", f"{p}/{field_name}", source))
        issues.extend(_extensions(node.get("extensions"), f"{p}/extensions", source))
    for i, path in enumerate(data.get("movement_paths", []) if isinstance(data.get("movement_paths"), list) else []):
        p = f"/movement_paths/{i}"
        if not isinstance(path, Mapping): issues.append(_issue("INVALID_TYPE", f"{p}: object required", p, source)); continue
        issues.extend(_unknown(path, _PATH, p, source)); _required_id(path.get("path_id"), "path_id", p, source, issues); _required_id(path.get("subject_id"), "subject_id", p, source, issues)
        if not isinstance(path.get("node_ids"), list) or len(path["node_ids"]) < 2: issues.append(_issue("INVALID_PATH", f"{p}/node_ids: at least two nodes required", f"{p}/node_ids", source))
        elif any(node not in node_ids for node in path["node_ids"]): issues.append(_issue("UNKNOWN_NODE", f"{p}/node_ids: every node must exist", f"{p}/node_ids", source))
        if not isinstance(path.get("screen_direction"), str) or not path["screen_direction"].strip(): issues.append(_issue("REQUIRED_FIELD", f"{p}/screen_direction: non-empty string required", f"{p}/screen_direction", source))
        issues.extend(_extensions(path.get("extensions"), f"{p}/extensions", source))
    if not isinstance(data.get("movement_paths"), list): issues.append(_issue("INVALID_TYPE", "movement_paths: list required", "/movement_paths", source))
    if not isinstance(data.get("review_status"), str) or not data["review_status"].strip(): issues.append(_issue("REQUIRED_FIELD", "review_status: non-empty string required", "/review_status", source))
    issues.extend(_extensions(data.get("extensions"), "/extensions", source))
    return ValidationReport("scene_topology", [source] if source else [], issues)

__all__ = ["SceneTopology", "parse_scene_topology", "validate_scene_topology"]
