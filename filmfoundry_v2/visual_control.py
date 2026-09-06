"""Provider-neutral visual-control contracts for FilmFoundry v2.1."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Mapping

from .contracts import ID_RE
from .report import ValidationIssue, ValidationReport


_ROOT_FIELDS = {
    "visual_control_id",
    "production_unit",
    "character_references",
    "location_reference",
    "spatial_map",
    "scale_references",
    "physics_cues",
    "previsualization",
    "lens_result",
    "review_status",
    "experiment_ids",
    "extensions",
}
_CHARACTER_FIELDS = {
    "asset_id",
    "reference_kind",
    "face_closeup_asset_id",
    "front_body_asset_id",
    "back_body_asset_id",
    "headless_body_strategy",
    "state_variant",
    "parent_asset_id",
    "mask_regions",
    "controls",
    "does_not_control",
    "qc_status",
    "extensions",
}
_LOCATION_FIELDS = {
    "location_id",
    "preferred_view",
    "anchor_objects",
    "camera_side",
    "light_sources",
    "geometry_controls",
    "does_not_control",
    "extensions",
}
_SPATIAL_FIELDS = {"relations", "extensions"}
_RELATION_FIELDS = {
    "subject_id",
    "anchor_id",
    "relation",
    "distance",
    "facing",
    "screen_direction",
    "camera_side",
    "light_direction",
    "extensions",
}
_SCALE_FIELDS = {
    "subject_id",
    "reference_object_id",
    "visible_relation",
    "intended_scale",
    "scale_confidence",
    "extensions",
}
_PHYSICS_FIELDS = {
    "material",
    "force",
    "weight",
    "inertia",
    "gravity",
    "observable_result",
    "extensions",
}
_PREVIS_FIELDS = {
    "duration_seconds",
    "state_alignment",
    "initial_state",
    "end_state",
    "asset_id",
    "route",
    "observable_result",
    "extensions",
}
_LENS_FIELDS = {
    "fov_degrees",
    "focal_length_mm",
    "observable_framing",
    "framing_result",
    "extensions",
}
_NAMESPACE_RE = re.compile(r"^(?:project|provider):[^\s:]+$")


@dataclass(frozen=True)
class VisualControlPlan:
    """Typed view of a visual-control JSON object.

    ``raw`` preserves the source mapping, including fields which validation
    reports as unsupported.  This keeps parse/validate useful together while
    still giving callers convenient typed access to the canonical fields.
    """

    visual_control_id: str
    production_unit: str
    character_references: tuple[Mapping[str, Any], ...] = ()
    location_reference: Mapping[str, Any] | None = None
    spatial_map: Mapping[str, Any] | None = None
    scale_references: tuple[Mapping[str, Any], ...] = ()
    physics_cues: tuple[Mapping[str, Any], ...] = ()
    previsualization: Mapping[str, Any] | None = None
    lens_result: Mapping[str, Any] | None = None
    review_status: str = ""
    experiment_ids: tuple[str, ...] = ()
    extensions: Mapping[str, Any] = field(default_factory=dict)
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "VisualControlPlan":
        return cls(
            visual_control_id=str(value.get("visual_control_id", "")),
            production_unit=str(value.get("production_unit", "")),
            character_references=tuple(value.get("character_references", ()) or ()),
            location_reference=value.get("location_reference"),
            spatial_map=value.get("spatial_map"),
            scale_references=tuple(value.get("scale_references", ()) or ()),
            physics_cues=tuple(value.get("physics_cues", ()) or ()),
            previsualization=value.get("previsualization"),
            lens_result=value.get("lens_result"),
            review_status=str(value.get("review_status", "")),
            experiment_ids=tuple(value.get("experiment_ids", ()) or ()),
            extensions=value.get("extensions", {}) or {},
            raw=dict(value),
        )

    def to_dict(self) -> dict[str, Any]:
        if self.raw:
            return dict(self.raw)
        value: dict[str, Any] = {
            "visual_control_id": self.visual_control_id,
            "production_unit": self.production_unit,
            "character_references": [dict(item) for item in self.character_references],
            "scale_references": [dict(item) for item in self.scale_references],
            "physics_cues": [dict(item) for item in self.physics_cues],
            "review_status": self.review_status,
            "experiment_ids": list(self.experiment_ids),
        }
        for key in ("location_reference", "spatial_map", "previsualization", "lens_result"):
            item = getattr(self, key)
            if item is not None:
                value[key] = dict(item)
        if self.extensions:
            value["extensions"] = dict(self.extensions)
        return value

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.to_dict().get(key, default)


def parse_visual_control(value: str | Path | Mapping[str, Any]) -> VisualControlPlan:
    """Parse a visual-control JSON document into a :class:`VisualControlPlan`.

    A mapping is copied without validation so callers can inspect all issues in
    one subsequent ``validate_visual_control`` call.  Strings are interpreted
    as a path when they identify an existing file, otherwise as JSON text.
    """

    if isinstance(value, VisualControlPlan):
        return value
    if isinstance(value, Mapping):
        payload: Any = value
    else:
        text: str
        is_path = isinstance(value, Path)
        if isinstance(value, str) and not is_path:
            try:
                is_path = Path(value).is_file()
            except OSError:
                is_path = False
        if is_path:
            text = Path(value).read_text(encoding="utf-8")
        else:
            text = str(value)
        try:
            payload = json.loads(text)
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError(f"visual control JSON: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError("visual control: top-level object required")
    return VisualControlPlan.from_mapping(payload)


def _as_mapping(value: VisualControlPlan | Mapping[str, Any]) -> Mapping[str, Any] | None:
    if isinstance(value, VisualControlPlan):
        return value.to_dict()
    return value if isinstance(value, Mapping) else None


def _direction_conflicts(left: Any, right: Any) -> bool:
    """Return true only when explicit directional tokens contradict."""

    if not left or not right:
        return False
    first = str(left).casefold()
    second = str(right).casefold()
    if first.strip() == second.strip():
        return False
    token_groups = (
        ("left", "right"),
        ("north", "south"),
        ("east", "west"),
        ("front", "back"),
    )
    for positive, negative in token_groups:
        first_positive = positive in first
        first_negative = negative in first
        second_positive = positive in second
        second_negative = negative in second
        if (first_positive and second_negative) or (first_negative and second_positive):
            return True
    return False


def _issue(
    severity: str,
    code: str,
    message: str,
    pointer: str = "",
    suggestion: str = "",
) -> ValidationIssue:
    return ValidationIssue(severity, code, message, json_pointer=pointer, suggestion=suggestion)


def _unknown(
    value: Mapping[str, Any],
    allowed: set[str],
    pointer: str,
    issues: list[ValidationIssue],
) -> None:
    for key in sorted(set(value) - allowed):
        issues.append(
            _issue(
                "ERROR",
                "UNKNOWN_FIELD",
                f"{pointer}{key}: unsupported field; use extensions namespace",
                f"{pointer}{key}",
            )
        )


def _extensions(value: Any, pointer: str, issues: list[ValidationIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer}extensions: object required", f"{pointer}extensions"))
        return
    for key in sorted(value):
        if not isinstance(key, str) or not _NAMESPACE_RE.fullmatch(key):
            issues.append(
                _issue(
                    "ERROR",
                    "INVALID_EXTENSION_NAMESPACE",
                    f"{pointer}extensions.{key}: use project:<name> or provider:<name>",
                    f"{pointer}extensions.{key}",
                )
            )


def _required_string(value: Mapping[str, Any], field: str, pointer: str, issues: list[ValidationIssue]) -> None:
    item = value.get(field)
    if not isinstance(item, str) or not item.strip():
        issues.append(_issue("ERROR", "REQUIRED_FIELD", f"{pointer}{field}: non-empty string required", f"{pointer}{field}"))


def _required_id(value: Mapping[str, Any], field: str, pointer: str, issues: list[ValidationIssue]) -> None:
    item = value.get(field)
    if not isinstance(item, str) or not ID_RE.fullmatch(item):
        issues.append(_issue("ERROR", "INVALID_ID", f"{pointer}{field}: must match ASCII stable ID pattern [A-Z][A-Z0-9_]{{2,63}}", f"{pointer}{field}"))


def _required_list(value: Mapping[str, Any], field: str, pointer: str, issues: list[ValidationIssue]) -> Any:
    item = value.get(field)
    if not isinstance(item, list):
        issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer}{field}: list required", f"{pointer}{field}"))
    return item


def _validate_character(value: Any, index: int, issues: list[ValidationIssue]) -> None:
    pointer = f"/character_references/{index}/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer[:-1]}: object required", pointer[:-1]))
        return
    _unknown(value, _CHARACTER_FIELDS, pointer, issues)
    _required_id(value, "asset_id", pointer, issues)
    for field in ("reference_kind", "face_closeup_asset_id", "front_body_asset_id", "back_body_asset_id", "state_variant", "controls", "does_not_control", "qc_status"):
        _required_string(value, field, pointer, issues)
    if value.get("headless_body_strategy") not in {"NONE", "OPTIONAL", "REQUIRED_BY_ADAPTER"}:
        issues.append(_issue("ERROR", "INVALID_ENUM", f"{pointer}headless_body_strategy: unsupported value", f"{pointer}headless_body_strategy"))
    for field in ("parent_asset_id",):
        if value.get(field) is not None and (not isinstance(value[field], str) or not ID_RE.fullmatch(value[field])):
            issues.append(_issue("ERROR", "INVALID_ID", f"{pointer}{field}: stable ID or null required", f"{pointer}{field}"))
    if "mask_regions" in value and not isinstance(value["mask_regions"], list):
        issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer}mask_regions: list required", f"{pointer}mask_regions"))
    _extensions(value.get("extensions"), pointer, issues)


def _validate_location(value: Any, issues: list[ValidationIssue]) -> None:
    pointer = "/location_reference/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", "/location_reference: object or null required", "/location_reference"))
        return
    _unknown(value, _LOCATION_FIELDS, pointer, issues)
    _required_id(value, "location_id", pointer, issues)
    for field in ("preferred_view", "camera_side", "geometry_controls", "does_not_control"):
        _required_string(value, field, pointer, issues)
    for field in ("anchor_objects", "light_sources"):
        item = value.get(field)
        if not isinstance(item, list) or any(not isinstance(entry, str) or not entry.strip() for entry in item):
            issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer}{field}: list of non-empty strings required", f"{pointer}{field}"))
    _extensions(value.get("extensions"), pointer, issues)


def _validate_spatial_map(value: Any, issues: list[ValidationIssue]) -> None:
    pointer = "/spatial_map/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", "/spatial_map: object or null required", "/spatial_map"))
        return
    _unknown(value, _SPATIAL_FIELDS, pointer, issues)
    relations = value.get("relations")
    if not isinstance(relations, list) or not relations:
        issues.append(_issue("ERROR", "REQUIRED_FIELD", "/spatial_map/relations: non-empty list required", "/spatial_map/relations"))
    else:
        seen: set[tuple[Any, ...]] = set()
        for index, relation in enumerate(relations):
            item_pointer = f"/spatial_map/relations/{index}/"
            if not isinstance(relation, Mapping):
                issues.append(_issue("ERROR", "INVALID_TYPE", f"{item_pointer[:-1]}: object required", item_pointer[:-1]))
                continue
            _unknown(relation, _RELATION_FIELDS, item_pointer, issues)
            for field in ("subject_id", "anchor_id", "relation", "distance", "facing", "screen_direction", "camera_side", "light_direction"):
                _required_string(relation, field, item_pointer, issues)
            key = tuple(relation.get(field) for field in ("subject_id", "anchor_id", "relation"))
            if key in seen:
                issues.append(_issue("ERROR", "DUPLICATE_RELATION", f"{item_pointer[:-1]}: duplicate spatial relation {key}", item_pointer[:-1]))
            seen.add(key)
            _extensions(relation.get("extensions"), item_pointer, issues)
    _extensions(value.get("extensions"), pointer, issues)


def _validate_scale(value: Any, index: int, issues: list[ValidationIssue]) -> None:
    pointer = f"/scale_references/{index}/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer[:-1]}: object required", pointer[:-1]))
        return
    _unknown(value, _SCALE_FIELDS, pointer, issues)
    for field in ("subject_id", "reference_object_id", "visible_relation", "intended_scale", "scale_confidence"):
        _required_string(value, field, pointer, issues)
    _extensions(value.get("extensions"), pointer, issues)


def _validate_physics(value: Any, index: int, issues: list[ValidationIssue]) -> None:
    pointer = f"/physics_cues/{index}/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", f"{pointer[:-1]}: object required", pointer[:-1]))
        return
    _unknown(value, _PHYSICS_FIELDS, pointer, issues)
    for field in ("material", "force", "weight", "inertia", "gravity", "observable_result"):
        _required_string(value, field, pointer, issues)
    _extensions(value.get("extensions"), pointer, issues)


def _validate_previsualization(value: Any, issues: list[ValidationIssue]) -> None:
    pointer = "/previsualization/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", "/previsualization: object or null required", "/previsualization"))
        return
    _unknown(value, _PREVIS_FIELDS, pointer, issues)
    duration = value.get("duration_seconds")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
        issues.append(_issue("ERROR", "INVALID_DURATION", "/previsualization/duration_seconds: positive number required", "/previsualization/duration_seconds"))
    alignment = value.get("state_alignment")
    if not isinstance(alignment, str) or not alignment.strip():
        issues.append(_issue("ERROR", "REQUIRED_FIELD", "/previsualization/state_alignment: non-empty string required", "/previsualization/state_alignment"))
    elif alignment.strip().upper() in {"FAIL", "FAILED", "MISMATCH", "UNALIGNED"}:
        issues.append(_issue("ERROR", "STATE_MISMATCH", f"/previsualization/state_alignment: {alignment} does not align shot state", "/previsualization/state_alignment"))
    _extensions(value.get("extensions"), pointer, issues)


def _validate_lens(value: Any, issues: list[ValidationIssue]) -> None:
    pointer = "/lens_result/"
    if not isinstance(value, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", "/lens_result: object or null required", "/lens_result"))
        return
    _unknown(value, _LENS_FIELDS, pointer, issues)
    for field in ("fov_degrees", "focal_length_mm"):
        if field in value and (not isinstance(value[field], (int, float)) or isinstance(value[field], bool) or value[field] <= 0):
            issues.append(_issue("ERROR", "INVALID_NUMBER", f"{pointer}{field}: positive number required", f"{pointer}{field}"))
    framing = value.get("observable_framing", value.get("framing_result"))
    if not isinstance(framing, str) or not framing.strip():
        issues.append(_issue("ERROR", "MISSING_OBSERVABLE_RESULT", f"{pointer}observable_framing: observable framing result required", f"{pointer}observable_framing"))
    _extensions(value.get("extensions"), pointer, issues)


def validate_visual_control(
    value: VisualControlPlan | Mapping[str, Any],
    source: str | Path = "",
) -> ValidationReport:
    """Validate a visual-control plan with structural errors and guidance warnings."""

    source = str(source) if source else ""
    payload = _as_mapping(value)
    issues: list[ValidationIssue] = []
    if payload is None:
        issues.append(_issue("ERROR", "INVALID_TYPE", "visual_control: top-level object required"))
        return ValidationReport("visual_control", [source] if source else [], issues)
    _unknown(payload, _ROOT_FIELDS, "/", issues)
    for field in ("visual_control_id", "production_unit", "review_status"):
        _required_string(payload, field, "/", issues)
    for field in ("visual_control_id", "production_unit"):
        _required_id(payload, field, "/", issues)
    for field in ("character_references", "scale_references", "physics_cues", "experiment_ids"):
        item = _required_list(payload, field, "/", issues)
        if isinstance(item, list):
            for index, entry in enumerate(item):
                if field == "character_references":
                    _validate_character(entry, index, issues)
                elif field == "scale_references":
                    _validate_scale(entry, index, issues)
                elif field == "physics_cues":
                    _validate_physics(entry, index, issues)
                elif not isinstance(entry, str) or not ID_RE.fullmatch(entry):
                    issues.append(_issue("ERROR", "INVALID_ID", f"/experiment_ids/{index}: stable ID required", f"/experiment_ids/{index}"))
    if "location_reference" in payload and payload["location_reference"] is not None:
        _validate_location(payload["location_reference"], issues)
    if "spatial_map" in payload and payload["spatial_map"] is not None:
        _validate_spatial_map(payload["spatial_map"], issues)
    if "previsualization" in payload and payload["previsualization"] is not None:
        _validate_previsualization(payload["previsualization"], issues)
    if "lens_result" in payload and payload["lens_result"] is not None:
        _validate_lens(payload["lens_result"], issues)
    _extensions(payload.get("extensions"), "/", issues)

    # The register marks neutral-gray identity backgrounds as an unverified
    # practice.  Keep its absence visible without blocking the structural gate.
    characters = payload.get("character_references")
    def _has_gray_note(item: Any) -> bool:
        if not isinstance(item, Mapping):
            return False
        extensions = item.get("extensions")
        if not isinstance(extensions, Mapping):
            return False
        return any("gray" in str(value).casefold() or "grey" in str(value).casefold() for value in extensions.values())

    if isinstance(characters, list) and characters and not any(_has_gray_note(item) for item in characters):
        issues.append(
            _issue(
                "WARNING",
                "MISSING_GRAY_BACKGROUND",
                "character identity reference has no neutral gray background; practice remains unverified",
                "/character_references",
                "record a controlled experiment before treating gray background as a default",
            )
        )
    if source:
        issues = [
            ValidationIssue(
                issue.severity,
                issue.code,
                issue.message,
                source=source,
                json_pointer=issue.json_pointer,
                related_ids=issue.related_ids,
                suggestion=issue.suggestion,
            )
            for issue in issues
        ]
    return ValidationReport("visual_control", [source] if source else [], issues)


def validate_visual_control_alignment(
    shot: Mapping[str, Any],
    plan: VisualControlPlan | Mapping[str, Any],
    source: str | Path = "",
) -> ValidationReport:
    """Check shot state, location and camera-side facts against a plan.

    This check deliberately does not mutate lifecycle state or inspect provider
    evidence; those gates remain owned by the runtime and adapter contracts.
    """

    source = str(source) if source else ""
    issues: list[ValidationIssue] = []
    if not isinstance(shot, Mapping):
        issues.append(_issue("ERROR", "INVALID_TYPE", "shot: top-level object required"))
        return ValidationReport("visual_control_alignment", [source] if source else [], issues)
    payload = _as_mapping(plan)
    if payload is None:
        issues.append(_issue("ERROR", "INVALID_TYPE", "visual_control: top-level object required"))
        return ValidationReport("visual_control_alignment", [source] if source else [], issues)

    control_report = validate_visual_control(payload, source=source)
    issues.extend(control_report.issues)

    shot_unit = shot.get("generation_unit_id", shot.get("generation_unit"))
    production_unit = payload.get("production_unit")
    if shot_unit and production_unit and str(shot_unit) != str(production_unit):
        issues.append(_issue("ERROR", "UNIT_MISMATCH", f"production_unit {production_unit!r} does not match shot unit {shot_unit!r}", "/production_unit"))

    previsualization = payload.get("previsualization")
    if isinstance(previsualization, Mapping):
        alignment = str(previsualization.get("state_alignment", "")).strip().upper()
        if alignment not in {"PASS", "MATCHED", "ALIGNED"}:
            issues.append(_issue("ERROR", "STATE_MISMATCH", "previsualization state alignment is not PASS", "/previsualization/state_alignment"))
        for field, shot_field in (("initial_state", "initial_state"), ("end_state", "end_state")):
            expected = previsualization.get(field)
            actual = shot.get(shot_field)
            if expected and actual and str(expected).strip().casefold() != str(actual).strip().casefold():
                issues.append(_issue("ERROR", "STATE_MISMATCH", f"previsualization {field} does not match shot {shot_field}", f"/previsualization/{field}"))

    location = payload.get("location_reference")
    shot_location = shot.get("location")
    if isinstance(location, Mapping) and isinstance(shot_location, Mapping):
        expected_id = location.get("location_id")
        actual_id = shot_location.get("asset_id", shot_location.get("location_id", shot_location.get("canonical")))
        if expected_id and actual_id and str(expected_id) != str(actual_id):
            issues.append(_issue("ERROR", "LOCATION_MISMATCH", f"location_reference {expected_id!r} does not match shot location {actual_id!r}", "/location_reference/location_id"))

    camera = shot.get("camera")
    camera_axis = shot.get("camera_axis")
    if isinstance(camera, Mapping):
        camera_axis = camera.get("axis", camera.get("camera_side", camera_axis))
    screen_direction = shot.get("screen_direction")
    spatial_map = payload.get("spatial_map")
    relations = spatial_map.get("relations", []) if isinstance(spatial_map, Mapping) else []
    if relations and (camera_axis or screen_direction):
        for index, relation in enumerate(relations):
            if not isinstance(relation, Mapping):
                continue
            relation_camera_side = relation.get("camera_side")
            relation_screen_direction = relation.get("screen_direction")
            if camera_axis and relation_camera_side and _direction_conflicts(camera_axis, relation_camera_side):
                issues.append(_issue("ERROR", "CAMERA_SIDE_MISMATCH", f"spatial relation camera side {relation_camera_side!r} conflicts with shot camera axis {camera_axis!r}", f"/spatial_map/relations/{index}/camera_side"))
            if screen_direction and relation_screen_direction and _direction_conflicts(screen_direction, relation_screen_direction):
                issues.append(_issue("ERROR", "SCREEN_DIRECTION_MISMATCH", f"spatial relation screen direction {relation_screen_direction!r} conflicts with shot screen direction {screen_direction!r}", f"/spatial_map/relations/{index}/screen_direction"))
    elif camera_axis or screen_direction:
        issues.append(_issue("WARNING", "MISSING_SPATIAL_AUTHORITY", "shot camera-side facts cannot be checked without spatial_map", "/spatial_map"))

    return ValidationReport("visual_control_alignment", [source] if source else [], issues)


__all__ = ["VisualControlPlan", "parse_visual_control", "validate_visual_control", "validate_visual_control_alignment"]
