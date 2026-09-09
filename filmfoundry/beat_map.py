"""Beat-level emotional and sonic intent."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from .contracts import ID_RE
from .report import ValidationIssue, ValidationReport
from .script_analysis import ScriptAnalysis, _extensions, _load_mapping, _unknown

_ROOT_FIELDS = {"schema_version", "beat_map_id", "production_unit", "beats", "review_status", "extensions"}
_BEAT_FIELDS = {"beat_id", "sequence", "narrative_function", "primary_emotion", "tension_level", "direction", "turning_point", "rationale", "music_state", "silence_required", "dialogue_density", "timing_authority", "review_status", "extensions"}


@dataclass(frozen=True)
class EmotionalBeatMap:
    beat_map_id: str
    production_unit: str
    beats: tuple[Mapping[str, Any], ...] = ()
    review_status: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)


def parse_emotional_beat_map(value: str | Path | Mapping[str, Any]) -> EmotionalBeatMap:
    if isinstance(value, EmotionalBeatMap):
        return value
    payload = _load_mapping(value, "emotional beat map")
    return EmotionalBeatMap(str(payload.get("beat_map_id", "")), str(payload.get("production_unit", "")), tuple(dict(item) for item in payload.get("beats", ()) if isinstance(item, Mapping)), str(payload.get("review_status", "")), dict(payload))


def _issue(code: str, message: str, pointer: str, source: str) -> ValidationIssue:
    return ValidationIssue("ERROR", code, message, source=source, json_pointer=pointer)


def validate_emotional_beat_map(value: EmotionalBeatMap | Mapping[str, Any], *, source: str = "") -> ValidationReport:
    data = value.to_dict() if isinstance(value, EmotionalBeatMap) else value
    if not isinstance(data, Mapping):
        return ValidationReport("emotional_beat_map", [], [_issue("INVALID_TYPE", "emotional beat map: top-level object required", "", source)])
    issues = _unknown(data, _ROOT_FIELDS, "", source)
    if data.get("schema_version") != "emotional-beat-map.v3":
        issues.append(_issue("INVALID_SCHEMA_VERSION", "schema_version: expected emotional-beat-map.v3", "/schema_version", source))
    for name in ("beat_map_id", "production_unit"):
        if not isinstance(data.get(name), str) or not ID_RE.fullmatch(data[name]):
            issues.append(_issue("INVALID_ID", f"{name}: stable ASCII ID required", f"/{name}", source))
    beats = data.get("beats")
    if not isinstance(beats, list) or not beats:
        issues.append(_issue("INVALID_TYPE", "beats: non-empty list required", "/beats", source))
    else:
        seen_ids: set[str] = set()
        seen_sequences: set[int] = set()
        for index, beat in enumerate(beats):
            pointer = f"/beats/{index}"
            if not isinstance(beat, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer}: object required", pointer, source))
                continue
            issues.extend(_unknown(beat, _BEAT_FIELDS, pointer, source))
            beat_id = beat.get("beat_id")
            if not isinstance(beat_id, str) or not ID_RE.fullmatch(beat_id):
                issues.append(_issue("INVALID_ID", f"{pointer}/beat_id: stable ASCII ID required", f"{pointer}/beat_id", source))
            elif beat_id in seen_ids:
                issues.append(_issue("DUPLICATE_ID", f"{pointer}/beat_id: duplicate {beat_id}", f"{pointer}/beat_id", source))
            else:
                seen_ids.add(beat_id)
            sequence = beat.get("sequence")
            if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1 or sequence in seen_sequences:
                issues.append(_issue("INVALID_SEQUENCE", f"{pointer}/sequence: unique positive integer required", f"{pointer}/sequence", source))
            else:
                seen_sequences.add(sequence)
            for name in ("narrative_function", "primary_emotion", "rationale", "music_state", "dialogue_density", "timing_authority", "review_status"):
                if not isinstance(beat.get(name), str) or not beat[name].strip():
                    issues.append(_issue("REQUIRED_FIELD", f"{pointer}/{name}: non-empty string required", f"{pointer}/{name}", source))
            tension = beat.get("tension_level")
            if isinstance(tension, bool) or not isinstance(tension, int) or not 0 <= tension <= 10:
                issues.append(_issue("INVALID_TENSION", f"{pointer}/tension_level: creator annotation from 0 to 10 required", f"{pointer}/tension_level", source))
            if beat.get("direction") not in {"RISING", "FALLING", "STEADY"}:
                issues.append(_issue("INVALID_ENUM", f"{pointer}/direction: unsupported value", f"{pointer}/direction", source))
            for name in ("turning_point", "silence_required"):
                if not isinstance(beat.get(name), bool):
                    issues.append(_issue("INVALID_TYPE", f"{pointer}/{name}: boolean required", f"{pointer}/{name}", source))
            issues.extend(_extensions(beat.get("extensions"), f"{pointer}/extensions", source))
    if not isinstance(data.get("review_status"), str) or not data["review_status"].strip():
        issues.append(_issue("REQUIRED_FIELD", "review_status: non-empty string required", "/review_status", source))
    issues.extend(_extensions(data.get("extensions"), "/extensions", source))
    return ValidationReport("emotional_beat_map", [source] if source else [], issues)


def production_requirement_facts(script_analysis: ScriptAnalysis | Mapping[str, Any], beat_map: EmotionalBeatMap | Mapping[str, Any] | None = None) -> dict[str, bool]:
    analysis = script_analysis.to_dict() if isinstance(script_analysis, ScriptAnalysis) else script_analysis
    beat_data = beat_map.to_dict() if isinstance(beat_map, EmotionalBeatMap) else beat_map
    facts = analysis.get("facts", []) if isinstance(analysis, Mapping) else []
    categories = {str(item.get("category", "")).upper() for item in facts if isinstance(item, Mapping)}
    beats = beat_data.get("beats", []) if isinstance(beat_data, Mapping) else []
    has_dialogue = "DIALOGUE" in categories or "VOICE" in categories or any(isinstance(item, Mapping) and str(item.get("dialogue_density", "")).upper() not in {"", "NONE"} for item in beats)
    has_music = any(isinstance(item, Mapping) and str(item.get("music_state", "")).upper() not in {"", "NONE", "SILENCE"} for item in beats)
    multiple = len(beats) > 1
    return {"has_multiple_beats": multiple, "has_dialogue_or_voice": has_dialogue, "has_music": has_music, "requires_emotional_beat_map": multiple or has_dialogue or has_music}


__all__ = ["EmotionalBeatMap", "parse_emotional_beat_map", "validate_emotional_beat_map", "production_requirement_facts"]
