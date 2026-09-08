"""Location view coverage sets used as candidates before promotion."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
from .contracts import ID_RE
from .report import ValidationIssue, ValidationReport
from .script_analysis import _extensions, _load_mapping, _unknown

_ROOT = {"schema_version", "coverage_id", "location_id", "views", "review_status", "extensions"}
_VIEW = {"view_id", "node_id", "camera_side", "screen_direction", "visible_anchor_ids", "occluded_anchor_ids", "framing_result", "source_asset_id", "qc_status", "extensions"}
@dataclass(frozen=True)
class LocationCoverageSet:
    coverage_id: str; location_id: str; views: tuple[Mapping[str, Any], ...] = (); review_status: str = ""; raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)
    def to_dict(self) -> dict[str, Any]: return dict(self.raw)
def parse_location_coverage(value: str | Path | Mapping[str, Any]) -> LocationCoverageSet:
    if isinstance(value, LocationCoverageSet): return value
    payload = _load_mapping(value, "location coverage"); return LocationCoverageSet(str(payload.get("coverage_id", "")), str(payload.get("location_id", "")), tuple(dict(x) for x in payload.get("views", ()) if isinstance(x, Mapping)), str(payload.get("review_status", "")), dict(payload))
def validate_location_coverage(value: LocationCoverageSet | Mapping[str, Any], *, source: str = "") -> ValidationReport:
    data = value.to_dict() if isinstance(value, LocationCoverageSet) else value
    issue = lambda c,m,p: ValidationIssue("ERROR", c, m, source=source, json_pointer=p)
    if not isinstance(data, Mapping): return ValidationReport("location_coverage", [], [issue("INVALID_TYPE", "location coverage: top-level object required", "")])
    issues = _unknown(data, _ROOT, "", source)
    if data.get("schema_version") != "location-coverage-set.v2": issues.append(issue("INVALID_SCHEMA_VERSION", "schema_version: expected location-coverage-set.v2", "/schema_version"))
    for name in ("coverage_id", "location_id"):
        if not isinstance(data.get(name), str) or not ID_RE.fullmatch(data[name]): issues.append(issue("INVALID_ID", f"/{name}: stable ASCII ID required", f"/{name}"))
    views = data.get("views")
    if not isinstance(views, list) or not views: issues.append(issue("INVALID_TYPE", "/views: non-empty list required", "/views")); views = []
    seen: set[str] = set()
    for i, view in enumerate(views):
        p = f"/views/{i}"
        if not isinstance(view, Mapping): issues.append(issue("INVALID_TYPE", f"{p}: object required", p)); continue
        issues.extend(_unknown(view, _VIEW, p, source)); vid = view.get("view_id")
        if not isinstance(vid, str) or not ID_RE.fullmatch(vid): issues.append(issue("INVALID_ID", f"{p}/view_id: stable ASCII ID required", f"{p}/view_id"))
        elif vid in seen: issues.append(issue("DUPLICATE_ID", f"{p}/view_id: duplicate {vid}", f"{p}/view_id"))
        else: seen.add(vid)
        for name in ("node_id", "camera_side", "screen_direction", "framing_result", "source_asset_id", "qc_status"):
            if not isinstance(view.get(name), str) or not view[name].strip(): issues.append(issue("REQUIRED_FIELD", f"{p}/{name}: non-empty string required", f"{p}/{name}"))
        for name in ("visible_anchor_ids", "occluded_anchor_ids"):
            if not isinstance(view.get(name), list): issues.append(issue("INVALID_TYPE", f"{p}/{name}: list required", f"{p}/{name}"))
        issues.extend(_extensions(view.get("extensions"), f"{p}/extensions", source))
    if not isinstance(data.get("review_status"), str) or not data["review_status"].strip(): issues.append(issue("REQUIRED_FIELD", "/review_status: non-empty string required", "/review_status"))
    issues.extend(_extensions(data.get("extensions"), "/extensions", source))
    return ValidationReport("location_coverage", [source] if source else [], issues)
__all__ = ["LocationCoverageSet", "parse_location_coverage", "validate_location_coverage"]
