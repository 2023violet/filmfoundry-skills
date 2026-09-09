"""Append-only production-ledger and conditional artifact policy contracts."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Mapping

from .contracts import ID_RE, SHA256_RE
from .report import ValidationIssue, ValidationReport


_LEDGER_FIELDS = {"schema_version", "ledger_id", "entities", "events", "extensions"}
_ENTITY_FIELDS = {"entity_id", "entity_type", "references", "extensions"}
_EVENT_FIELDS = {
    "event_id", "sequence", "occurred_at", "event_type", "entity_id", "actor",
    "artifact_id", "parameters", "retry_of", "retry_policy", "previous_event_hash",
    "event_hash", "correction_of", "extensions",
}
_POLICY_FIELDS = {"schema_version", "policy_id", "requirements", "extensions"}
_REQUIREMENT_FIELDS = {"requirement_id", "artifact_type", "description", "severity", "required_when", "extensions"}
_EXTENSION_RE = re.compile(r"^(?:project|provider):[^\s:]+$")
_MISSING = object()


def _issue(code: str, message: str, pointer: str = "", severity: str = "ERROR") -> ValidationIssue:
    return ValidationIssue(severity, code, message, json_pointer=pointer)


def _unknown(value: Mapping[str, Any], allowed: set[str], pointer: str, issues: list[ValidationIssue]) -> None:
    for key in sorted(set(value) - allowed):
        issues.append(_issue("UNKNOWN_FIELD", f"{pointer}{key}: unsupported field; use extensions namespace", f"{pointer}{key}"))


def _extensions(value: Any, pointer: str, issues: list[ValidationIssue]) -> None:
    if value is None:
        return
    if not isinstance(value, Mapping):
        issues.append(_issue("INVALID_TYPE", f"{pointer}extensions: object required", f"{pointer}extensions"))
        return
    for key in sorted(value):
        if not isinstance(key, str) or not _EXTENSION_RE.fullmatch(key):
            issues.append(_issue("INVALID_EXTENSION_NAMESPACE", f"{pointer}extensions.{key}: use project:<name> or provider:<name>", f"{pointer}extensions.{key}"))


def _valid_id(value: Any) -> bool:
    return isinstance(value, str) and bool(ID_RE.fullmatch(value))


def _canonical_event_hash(event: Mapping[str, Any]) -> str:
    body = {key: value for key, value in event.items() if key != "event_hash"}
    encoded = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False


def validate_production_ledger(value: Mapping[str, Any]) -> ValidationReport:
    """Validate entities and an append-only, hash-chained event sequence."""

    issues: list[ValidationIssue] = []
    if not isinstance(value, Mapping):
        return ValidationReport("production_ledger", [], [_issue("INVALID_TYPE", "production ledger: top-level object required")])
    ledger_id = value.get("ledger_id")
    checked = [str(ledger_id)] if isinstance(ledger_id, str) else []
    _unknown(value, _LEDGER_FIELDS, "/", issues)
    if value.get("schema_version") != "production-ledger.v3":
        issues.append(_issue("INVALID_SCHEMA_VERSION", "/schema_version: expected production-ledger.v3", "/schema_version"))
    if not _valid_id(ledger_id):
        issues.append(_issue("INVALID_ID", "/ledger_id: stable ID required", "/ledger_id"))
    entities = value.get("entities")
    entity_ids: set[str] = set()
    entity_rows: list[tuple[int, Mapping[str, Any]]] = []
    if not isinstance(entities, list):
        issues.append(_issue("INVALID_TYPE", "/entities: list required", "/entities"))
    else:
        for index, entity in enumerate(entities):
            pointer = f"/entities/{index}/"
            if not isinstance(entity, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer[:-1]}: object required", pointer[:-1]))
                continue
            entity_rows.append((index, entity))
            _unknown(entity, _ENTITY_FIELDS, pointer, issues)
            entity_id = entity.get("entity_id")
            if not _valid_id(entity_id):
                issues.append(_issue("INVALID_ID", f"{pointer}entity_id: stable ID required", f"{pointer}entity_id"))
            elif entity_id in entity_ids:
                issues.append(_issue("DUPLICATE_ENTITY_ID", f"{pointer}entity_id: duplicate {entity_id}", f"{pointer}entity_id"))
            else:
                entity_ids.add(entity_id)
            if not isinstance(entity.get("entity_type"), str) or not entity["entity_type"].strip():
                issues.append(_issue("REQUIRED_FIELD", f"{pointer}entity_type: non-empty string required", f"{pointer}entity_type"))
            references = entity.get("references", {})
            if not isinstance(references, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer}references: object required", f"{pointer}references"))
            _extensions(entity.get("extensions"), pointer, issues)
    for index, entity in entity_rows:
        references = entity.get("references", {})
        if not isinstance(references, Mapping):
            continue
        for relation, target in references.items():
            pointer = f"/entities/{index}/references/{relation}"
            if not isinstance(relation, str) or not relation.strip() or not _valid_id(target):
                issues.append(_issue("INVALID_ENTITY_REFERENCE", f"{pointer}: relation and stable entity ID required", pointer))
            elif target not in entity_ids:
                issues.append(_issue("UNKNOWN_ENTITY_REFERENCE", f"{pointer}: unknown entity {target}", pointer))

    events = value.get("events")
    previous_hash: str | None = None
    event_by_id: dict[str, Mapping[str, Any]] = {}
    if not isinstance(events, list):
        issues.append(_issue("INVALID_TYPE", "/events: list required", "/events"))
    else:
        for index, event in enumerate(events):
            pointer = f"/events/{index}/"
            if not isinstance(event, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer[:-1]}: object required", pointer[:-1]))
                continue
            _unknown(event, _EVENT_FIELDS, pointer, issues)
            event_id = event.get("event_id")
            if not _valid_id(event_id):
                issues.append(_issue("INVALID_ID", f"{pointer}event_id: stable ID required", f"{pointer}event_id"))
            elif event_id in event_by_id:
                issues.append(_issue("DUPLICATE_EVENT_ID", f"{pointer}event_id: duplicate {event_id}", f"{pointer}event_id"))
            sequence = event.get("sequence")
            if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence != index + 1:
                issues.append(_issue("INVALID_EVENT_SEQUENCE", f"{pointer}sequence: expected {index + 1} for append-only order", f"{pointer}sequence"))
            if not _valid_timestamp(event.get("occurred_at")):
                issues.append(_issue("INVALID_TIMESTAMP", f"{pointer}occurred_at: timezone-aware ISO-8601 timestamp required", f"{pointer}occurred_at"))
            if not isinstance(event.get("event_type"), str) or not event["event_type"].strip():
                issues.append(_issue("REQUIRED_FIELD", f"{pointer}event_type: non-empty string required", f"{pointer}event_type"))
            entity_id = event.get("entity_id")
            if not _valid_id(entity_id):
                issues.append(_issue("INVALID_REFERENCE", f"{pointer}entity_id: stable entity ID required", f"{pointer}entity_id"))
            elif entity_id not in entity_ids:
                issues.append(_issue("UNKNOWN_EVENT_ENTITY", f"{pointer}entity_id: unknown entity {event.get('entity_id')!r}", f"{pointer}entity_id"))
            if not isinstance(event.get("actor"), str) or not event["actor"].strip():
                issues.append(_issue("REQUIRED_FIELD", f"{pointer}actor: non-empty string required", f"{pointer}actor"))
            if "artifact_id" in event and not _valid_id(event["artifact_id"]):
                issues.append(_issue("INVALID_ID", f"{pointer}artifact_id: stable ID required", f"{pointer}artifact_id"))
            parameters = event.get("parameters", {})
            if not isinstance(parameters, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer}parameters: object required", f"{pointer}parameters"))
                parameters = {}
            expected_previous = None if index == 0 else previous_hash
            if "previous_event_hash" not in event:
                issues.append(_issue("REQUIRED_FIELD", f"{pointer}previous_event_hash: required", f"{pointer}previous_event_hash"))
            elif event["previous_event_hash"] != expected_previous:
                issues.append(_issue("INVALID_EVENT_CHAIN", f"{pointer}previous_event_hash: does not match preceding event", f"{pointer}previous_event_hash"))
            supplied_hash = event.get("event_hash")
            if not isinstance(supplied_hash, str) or not SHA256_RE.fullmatch(supplied_hash) or supplied_hash.lower() != _canonical_event_hash(event):
                issues.append(_issue("INVALID_EVENT_HASH", f"{pointer}event_hash: does not match immutable event content", f"{pointer}event_hash"))
            previous_hash = supplied_hash if isinstance(supplied_hash, str) else None

            if "retry_of" in event:
                retry_of = event["retry_of"]
                if not _valid_id(retry_of):
                    issues.append(_issue("INVALID_REFERENCE", f"{pointer}retry_of: stable earlier event ID required", f"{pointer}retry_of"))
                    retry_of = None
                original = event_by_id.get(retry_of) if retry_of is not None else None
                if original is None:
                    issues.append(_issue("UNKNOWN_RETRY_EVENT", f"{pointer}retry_of: must refer to an earlier event", f"{pointer}retry_of"))
                else:
                    policy = original.get("retry_policy")
                    variables = policy.get("variable_fields") if isinstance(policy, Mapping) else None
                    if not isinstance(variables, list) or any(not isinstance(item, str) or not item for item in variables):
                        issues.append(_issue("RETRY_POLICY_MISSING", f"{pointer}retry_of: original event must declare retry_policy.variable_fields", f"{pointer}retry_of"))
                    else:
                        original_parameters = original.get("parameters", {})
                        if not isinstance(original_parameters, Mapping):
                            original_parameters = {}
                        for field in sorted(set(original_parameters) | set(parameters)):
                            original_value = original_parameters.get(field, _MISSING)
                            retry_value = parameters.get(field, _MISSING)
                            if original_value is _MISSING or retry_value is _MISSING:
                                changed = original_value is not retry_value
                            else:
                                changed = original_value != retry_value
                            if changed and field not in variables:
                                issues.append(_issue("RETRY_VARIABLE_NOT_ALLOWED", f"{pointer}parameters.{field}: retry may change only declared variables", f"{pointer}parameters.{field}"))
            retry_policy = event.get("retry_policy")
            if retry_policy is not None:
                variables = retry_policy.get("variable_fields") if isinstance(retry_policy, Mapping) else None
                if isinstance(retry_policy, Mapping):
                    _unknown(retry_policy, {"variable_fields"}, f"{pointer}retry_policy/", issues)
                if not isinstance(variables, list) or any(not isinstance(item, str) or not item for item in variables):
                    issues.append(_issue("INVALID_RETRY_POLICY", f"{pointer}retry_policy.variable_fields: list of non-empty strings required", f"{pointer}retry_policy"))
            if "correction_of" in event:
                correction_of = event["correction_of"]
                if not _valid_id(correction_of):
                    issues.append(_issue("INVALID_REFERENCE", f"{pointer}correction_of: stable earlier event ID required", f"{pointer}correction_of"))
                    correction_of = None
                if correction_of is None or correction_of not in event_by_id:
                    issues.append(_issue("UNKNOWN_CORRECTION_EVENT", f"{pointer}correction_of: must refer to an earlier event", f"{pointer}correction_of"))
                if event.get("event_type") != "CORRECTION_RECORDED":
                    issues.append(_issue("INVALID_CORRECTION_EVENT", f"{pointer}event_type: corrections use CORRECTION_RECORDED compensating events", f"{pointer}event_type"))
            _extensions(event.get("extensions"), pointer, issues)
            if isinstance(event_id, str) and event_id not in event_by_id:
                event_by_id[event_id] = event
    _extensions(value.get("extensions"), "/", issues)
    return ValidationReport("production_ledger", checked, issues)


@dataclass(frozen=True)
class ArtifactRequirement:
    requirement_id: str
    artifact_type: str
    description: str
    severity: str = "ERROR"
    required_when: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ArtifactRequirement":
        return cls(
            requirement_id=str(value.get("requirement_id", "")),
            artifact_type=str(value.get("artifact_type", "")),
            description=str(value.get("description", "")),
            severity=str(value.get("severity", "ERROR")),
            required_when=dict(value.get("required_when", {}) or {}),
        )

    def applies_to(self, facts: Mapping[str, Any]) -> bool:
        return all(_fact_value(facts, key) == expected for key, expected in self.required_when.items())


def _fact_value(facts: Mapping[str, Any], path: str) -> Any:
    value: Any = facts
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return None
        value = value[part]
    return value


def validate_production_policy(value: Mapping[str, Any]) -> ValidationReport:
    """Validate a strict, provider-neutral artifact requirement policy."""

    issues: list[ValidationIssue] = []
    if not isinstance(value, Mapping):
        return ValidationReport("production_policy", [], [_issue("INVALID_TYPE", "production policy: top-level object required")])
    policy_id = value.get("policy_id")
    checked = [str(policy_id)] if isinstance(policy_id, str) else []
    _unknown(value, _POLICY_FIELDS, "/", issues)
    if value.get("schema_version") != "production-policy.v3":
        issues.append(_issue("INVALID_SCHEMA_VERSION", "/schema_version: expected production-policy.v3", "/schema_version"))
    if not _valid_id(policy_id):
        issues.append(_issue("INVALID_ID", "/policy_id: stable ID required", "/policy_id"))
    requirements = value.get("requirements")
    seen: set[str] = set()
    if not isinstance(requirements, list):
        issues.append(_issue("INVALID_TYPE", "/requirements: list required", "/requirements"))
    else:
        for index, requirement in enumerate(requirements):
            pointer = f"/requirements/{index}/"
            if not isinstance(requirement, Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer[:-1]}: object required", pointer[:-1]))
                continue
            _unknown(requirement, _REQUIREMENT_FIELDS, pointer, issues)
            for field in ("requirement_id", "artifact_type"):
                item = requirement.get(field)
                if not _valid_id(item):
                    issues.append(_issue("INVALID_ID", f"{pointer}{field}: stable ID required", f"{pointer}{field}"))
            requirement_id = requirement.get("requirement_id")
            if isinstance(requirement_id, str):
                if requirement_id in seen:
                    issues.append(_issue("DUPLICATE_REQUIREMENT_ID", f"{pointer}requirement_id: duplicate {requirement_id}", f"{pointer}requirement_id"))
                seen.add(requirement_id)
            if not isinstance(requirement.get("description"), str) or not requirement["description"].strip():
                issues.append(_issue("REQUIRED_FIELD", f"{pointer}description: non-empty string required", f"{pointer}description"))
            severity = requirement.get("severity", "ERROR")
            if not isinstance(severity, str) or severity not in {"ERROR", "WARNING"}:
                issues.append(_issue("INVALID_SEVERITY", f"{pointer}severity: ERROR or WARNING required", f"{pointer}severity"))
            if "required_when" in requirement and not isinstance(requirement["required_when"], Mapping):
                issues.append(_issue("INVALID_TYPE", f"{pointer}required_when: object required", f"{pointer}required_when"))
            _extensions(requirement.get("extensions"), pointer, issues)
    _extensions(value.get("extensions"), "/", issues)
    return ValidationReport("production_policy", checked, issues)


@dataclass
class RequirementReport:
    policy_id: str
    required: list[ArtifactRequirement] = field(default_factory=list)
    satisfied: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.required = sorted(self.required, key=lambda item: item.requirement_id)
        self.satisfied = sorted(set(self.satisfied))
        self.issues = sorted(self.issues, key=lambda item: item.sort_key)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "ERROR"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "WARNING"]

    @property
    def ok(self) -> bool:
        return not self.errors

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": "requirements",
            "policy_id": self.policy_id,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "required": [
                {"requirement_id": item.requirement_id, "artifact_type": item.artifact_type,
                 "description": item.description, "severity": item.severity,
                 "required_when": dict(item.required_when)}
                for item in self.required
            ],
            "satisfied": list(self.satisfied),
            "issues": [issue.to_dict() for issue in self.issues],
            "errors": [issue.message for issue in self.errors],
            "warnings": [issue.message for issue in self.warnings],
        }


def _artifact_types(value: Any) -> tuple[set[str], str | None]:
    if isinstance(value, Mapping):
        value = value.get("artifacts", [])
    if not isinstance(value, list):
        return set(), "artifact inventory: list or object with artifacts list required"
    result: set[str] = set()
    for item in value:
        if isinstance(item, str):
            result.add(item)
        elif isinstance(item, Mapping) and isinstance(item.get("artifact_type"), str):
            result.add(item["artifact_type"])
    return result, None


def evaluate_requirements(
    policy: Mapping[str, Any],
    facts: Mapping[str, Any],
    artifacts: Any,
) -> RequirementReport:
    """Evaluate policy requirements against generic facts and artifact inventory."""

    validation = validate_production_policy(policy)
    policy_id = str(policy.get("policy_id", "")) if isinstance(policy, Mapping) else ""
    issues = list(validation.issues)
    required: list[ArtifactRequirement] = []
    satisfied: list[str] = []
    if validation.ok and isinstance(policy.get("requirements"), list) and isinstance(facts, Mapping):
        artifact_types, inventory_error = _artifact_types(artifacts)
        if inventory_error:
            issues.append(_issue("INVALID_ARTIFACT_INVENTORY", inventory_error))
        for raw in policy["requirements"]:
            if not isinstance(raw, Mapping):
                continue
            requirement = ArtifactRequirement.from_mapping(raw)
            if not requirement.applies_to(facts):
                continue
            required.append(requirement)
            if requirement.artifact_type in artifact_types:
                satisfied.append(requirement.requirement_id)
            else:
                issues.append(_issue(
                    "MISSING_REQUIRED_ARTIFACT",
                    f"{requirement.requirement_id}: missing required artifact type {requirement.artifact_type}",
                    f"/requirements/{requirement.requirement_id}",
                    requirement.severity,
                ))
    elif not isinstance(facts, Mapping):
        issues.append(_issue("INVALID_TYPE", "facts: object required"))
    return RequirementReport(policy_id, required, satisfied, issues)


def production_ledger_report(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact ledger report without changing its event history."""

    report = validate_production_ledger(value)
    payload = report.to_dict()
    payload.update({
        "ledger_id": value.get("ledger_id") if isinstance(value, Mapping) else None,
        "entity_count": len(value.get("entities", [])) if isinstance(value, Mapping) and isinstance(value.get("entities"), list) else 0,
        "event_count": len(value.get("events", [])) if isinstance(value, Mapping) and isinstance(value.get("events"), list) else 0,
    })
    return payload


__all__ = [
    "ArtifactRequirement", "RequirementReport", "evaluate_requirements",
    "production_ledger_report", "validate_production_ledger", "validate_production_policy",
]
