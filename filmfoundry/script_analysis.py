"""Sourced script facts that cannot silently become Canon."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Mapping

from .contracts import ID_RE, SHA256_RE
from .report import ValidationIssue, ValidationReport

_ROOT_FIELDS = {"schema_version", "script_analysis_id", "source_script", "facts", "unresolved_questions", "review_status", "extensions"}
_SOURCE_FIELDS = {"path", "sha256", "extensions"}
_FACT_FIELDS = {"fact_id", "category", "value", "source_span", "evidence_level", "confidence", "confirmed_by", "status", "extensions"}
_EVIDENCE = {"EXPLICIT_SCRIPT_FACT", "CREATOR_CONFIRMED", "INFERRED", "UNKNOWN", "CONFLICT"}
_STATUS = {"ACTIVE", "CANON", "REJECTED", "UNRESOLVED"}
_EXTENSION_RE = re.compile(r"^(?:project|provider):[^\s:]+$")


@dataclass(frozen=True)
class ScriptAnalysis:
    script_analysis_id: str
    source_path: str
    source_hash: str
    facts: tuple[Mapping[str, Any], ...] = ()
    unresolved_questions: tuple[str, ...] = ()
    review_status: str = ""
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return dict(self.raw)


def _load_mapping(value: str | Path | Mapping[str, Any], label: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        payload: Any = value
    else:
        text: str
        candidate = Path(value)
        try:
            is_path = candidate.is_file()
        except OSError:
            is_path = False
        text = candidate.read_text(encoding="utf-8") if is_path else str(value)
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{label} JSON: {exc}") from exc
    if not isinstance(payload, Mapping):
        raise ValueError(f"{label}: top-level object required")
    return payload


def parse_script_analysis(value: str | Path | Mapping[str, Any]) -> ScriptAnalysis:
    if isinstance(value, ScriptAnalysis):
        return value
    payload = _load_mapping(value, "script analysis")
    source = payload.get("source_script") if isinstance(payload.get("source_script"), Mapping) else {}
    return ScriptAnalysis(
        script_analysis_id=str(payload.get("script_analysis_id", "")),
        source_path=str(source.get("path", "")),
        source_hash=str(source.get("sha256", "")),
        facts=tuple(dict(item) for item in payload.get("facts", ()) if isinstance(item, Mapping)),
        unresolved_questions=tuple(str(item) for item in payload.get("unresolved_questions", ()) if isinstance(item, str)),
        review_status=str(payload.get("review_status", "")),
        raw=dict(payload),
    )


def _issue(code: str, message: str, pointer: str, source: str) -> ValidationIssue:
    return ValidationIssue("ERROR", code, message, source=source, json_pointer=pointer)


def _unknown(value: Mapping[str, Any], allowed: set[str], pointer: str, source: str) -> list[ValidationIssue]:
    return [_issue("UNKNOWN_FIELD", f"{pointer}/{key}: unsupported field", f"{pointer}/{key}", source) for key in sorted(set(value) - allowed)]


def _extensions(value: Any, pointer: str, source: str) -> list[ValidationIssue]:
    if value is None:
        return []
    if not isinstance(value, Mapping):
        return [_issue("INVALID_TYPE", f"{pointer}: object required", pointer, source)]
    return [_issue("INVALID_EXTENSION_NAMESPACE", f"{pointer}/{key}: invalid namespace", f"{pointer}/{key}", source) for key in sorted(value) if not isinstance(key, str) or not _EXTENSION_RE.fullmatch(key)]


def validate_script_analysis(value: ScriptAnalysis | Mapping[str, Any], *, source: str = "") -> ValidationReport:
    data = value.to_dict() if isinstance(value, ScriptAnalysis) else value
    if not isinstance(data, Mapping):
        return ValidationReport("script_analysis", [], [_issue("INVALID_TYPE", "script analysis: top-level object required", "", source)])
    issues = _unknown(data, _ROOT_FIELDS, "", source)
    if data.get("schema_version") != "script-analysis.v2":
        issues.append(_issue("INVALID_SCHEMA_VERSION", "schema_version: expected script-analysis.v2", "/schema_version", source))
    if not isinstance(data.get("script_analysis_id"), str) or not ID_RE.fullmatch(data["script_analysis_id"]):
        issues.append(_issue("INVALID_ID", "script_analysis_id: stable ASCII ID required", "/script_analysis_id", source))
    script = data.get("source_script")
    if not isinstance(script, Mapping):
        issues.append(_issue("INVALID_TYPE", "source_script: object required", "/source_script", source))
    else:
        issues.extend(_unknown(script, _SOURCE_FIELDS, "/source_script", source))
        if not isinstance(script.get("path"), str) or not script["path"].strip():
            issues.append(_issue("REQUIRED_FIELD", "source_script.path: non-empty string required", "/source_script/path", source))
        if not isinstance(script.get("sha256"), str) or not SHA256_RE.fullmatch(script["sha256"]):
            issues.append(_issue("INVALID_HASH", "source_script.sha256: SHA-256 required", "/source_script/sha256", source))
        issues.extend(_extensions(script.get("extensions"), "/source_script/extensions", source))
    facts = data.get("facts")
    if not isinstance(facts, list):
        issues.append(_issue("INVALID_TYPE", "facts: list required", "/facts", source))
    else:
        seen: set[str] = set()
        for index, fact in enumerate(facts):
            pointer = f"/facts/{index}"
            if not isinstance(fact, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer}: object required", pointer, source))
                continue
            issues.extend(_unknown(fact, _FACT_FIELDS, pointer, source))
            fact_id = fact.get("fact_id")
            if not isinstance(fact_id, str) or not ID_RE.fullmatch(fact_id):
                issues.append(_issue("INVALID_ID", f"{pointer}/fact_id: stable ASCII ID required", f"{pointer}/fact_id", source))
            elif fact_id in seen:
                issues.append(_issue("DUPLICATE_ID", f"{pointer}/fact_id: duplicate {fact_id}", f"{pointer}/fact_id", source))
            seen.add(fact_id) if isinstance(fact_id, str) else None
            for field_name in ("category", "value", "source_span"):
                if not isinstance(fact.get(field_name), str) or not fact[field_name].strip():
                    issues.append(_issue("REQUIRED_FIELD", f"{pointer}/{field_name}: non-empty string required", f"{pointer}/{field_name}", source))
            if fact.get("evidence_level") not in _EVIDENCE:
                issues.append(_issue("INVALID_ENUM", f"{pointer}/evidence_level: unsupported value", f"{pointer}/evidence_level", source))
            confidence = fact.get("confidence")
            if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                issues.append(_issue("INVALID_CONFIDENCE", f"{pointer}/confidence: number from 0 to 1 required", f"{pointer}/confidence", source))
            if fact.get("status") not in _STATUS:
                issues.append(_issue("INVALID_ENUM", f"{pointer}/status: unsupported value", f"{pointer}/status", source))
            if fact.get("status") == "CANON" and fact.get("evidence_level") == "INFERRED" and not fact.get("confirmed_by"):
                issues.append(_issue("UNCONFIRMED_CANON_FACT", f"{pointer}: inferred fact cannot become Canon without confirmation", pointer, source))
            issues.extend(_extensions(fact.get("extensions"), f"{pointer}/extensions", source))
    questions = data.get("unresolved_questions")
    if not isinstance(questions, list) or any(not isinstance(item, str) or not item.strip() for item in questions):
        issues.append(_issue("INVALID_TYPE", "unresolved_questions: list of non-empty strings required", "/unresolved_questions", source))
    if not isinstance(data.get("review_status"), str) or not data["review_status"].strip():
        issues.append(_issue("REQUIRED_FIELD", "review_status: non-empty string required", "/review_status", source))
    issues.extend(_extensions(data.get("extensions"), "/extensions", source))
    return ValidationReport("script_analysis", [source] if source else [], issues)


__all__ = ["ScriptAnalysis", "parse_script_analysis", "validate_script_analysis"]
