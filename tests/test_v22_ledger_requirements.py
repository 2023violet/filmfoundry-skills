from __future__ import annotations

import hashlib
import json
from pathlib import Path

from filmfoundry_v2 import (
    ArtifactRequirement,
    RequirementReport,
    evaluate_requirements,
    validate_production_ledger,
    validate_production_policy,
)
from test_v2_cli import run_ff


def _event_hash(event: dict) -> str:
    value = {key: item for key, item in event.items() if key != "event_hash"}
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def valid_ledger() -> dict:
    first = {
        "event_id": "EVENT_001",
        "sequence": 1,
        "occurred_at": "2026-09-07T00:00:00Z",
        "event_type": "ATTEMPT_RECORDED",
        "entity_id": "UNIT_TEST",
        "actor": "HUMAN",
        "parameters": {"seed": 1, "duration_seconds": 4},
        "previous_event_hash": None,
    }
    first["event_hash"] = _event_hash(first)
    return {
        "schema_version": "production-ledger.v2",
        "ledger_id": "LEDGER_TEST",
        "entities": [
            {"entity_id": "SCRIPT_TEST", "entity_type": "SCRIPT"},
            {
                "entity_id": "UNIT_TEST",
                "entity_type": "PRODUCTION_UNIT",
                "references": {"script": "SCRIPT_TEST"},
            },
        ],
        "events": [first],
    }


def test_ledger_accepts_hash_chained_events_and_entity_references():
    report = validate_production_ledger(valid_ledger())
    assert report.ok
    assert report.checked == ["LEDGER_TEST"]


def test_ledger_rejects_tampered_event_and_unknown_entity_reference():
    payload = valid_ledger()
    payload["events"][0]["actor"] = "AUTOMATION"
    payload["entities"][1]["references"]["script"] = "SCRIPT_MISSING"

    report = validate_production_ledger(payload)

    assert not report.ok
    assert {issue.code for issue in report.errors} >= {"INVALID_EVENT_HASH", "UNKNOWN_ENTITY_REFERENCE"}


def test_ledger_retry_can_change_only_declared_variables():
    payload = valid_ledger()
    first = payload["events"][0]
    first["retry_policy"] = {"variable_fields": ["seed"]}
    first["event_hash"] = _event_hash(first)
    retry = {
        "event_id": "EVENT_002",
        "sequence": 2,
        "occurred_at": "2026-09-07T00:01:00Z",
        "event_type": "ATTEMPT_RECORDED",
        "entity_id": "UNIT_TEST",
        "actor": "HUMAN",
        "parameters": {"seed": 2, "duration_seconds": 5},
        "retry_of": "EVENT_001",
        "previous_event_hash": first["event_hash"],
    }
    retry["event_hash"] = _event_hash(retry)
    payload["events"].append(retry)

    report = validate_production_ledger(payload)

    assert not report.ok
    assert any(issue.code == "RETRY_VARIABLE_NOT_ALLOWED" for issue in report.errors)


def test_requirement_evaluation_keeps_optional_creative_artifacts_as_warnings():
    policy = {
        "schema_version": "production-policy.v2",
        "policy_id": "POLICY_TEST",
        "requirements": [
            {
                "requirement_id": "REQ_SCRIPT_FACTS",
                "artifact_type": "SCRIPT_FACTS",
                "description": "sourced script facts",
            },
            {
                "requirement_id": "REQ_MUSIC_INTENT",
                "artifact_type": "MUSIC_INTENT",
                "description": "music intent",
                "severity": "WARNING",
                "required_when": {"has_music": True},
            },
        ],
    }

    report = evaluate_requirements(policy, {"has_music": True}, [{"artifact_type": "SCRIPT_FACTS"}])

    assert isinstance(report, RequirementReport)
    assert report.exit_code == 0
    assert [item.requirement_id for item in report.required] == ["REQ_MUSIC_INTENT", "REQ_SCRIPT_FACTS"]
    assert [issue.code for issue in report.warnings] == ["MISSING_REQUIRED_ARTIFACT"]
    assert ArtifactRequirement.from_mapping(policy["requirements"][0]).artifact_type == "SCRIPT_FACTS"


def test_requirement_evaluation_reports_missing_foundation_artifact_as_error():
    policy = {
        "schema_version": "production-policy.v2",
        "policy_id": "POLICY_TEST",
        "requirements": [{"requirement_id": "REQ_SCRIPT_FACTS", "artifact_type": "SCRIPT_FACTS", "description": "sourced script facts"}],
    }

    report = evaluate_requirements(policy, {}, [])

    assert report.exit_code == 1
    assert [issue.code for issue in report.errors] == ["MISSING_REQUIRED_ARTIFACT"]


def test_cli_ledger_and_requirements_commands_preserve_error_only_exit_semantics(tmp_path: Path):
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(valid_ledger()), encoding="utf-8")
    validate = run_ff("ledger", "validate", "--ledger", str(ledger_path), "--format", "json")
    assert validate.returncode == 0, validate.stderr
    assert json.loads(validate.stdout)["ok"] is True

    report = run_ff("ledger", "report", "--ledger", str(ledger_path), "--format", "json")
    assert report.returncode == 0, report.stderr
    assert json.loads(report.stdout)["event_count"] == 1

    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps({
        "schema_version": "production-policy.v2",
        "policy_id": "POLICY_TEST",
        "requirements": [{"requirement_id": "REQ_MUSIC", "artifact_type": "MUSIC_INTENT", "description": "music", "severity": "WARNING"}],
    }), encoding="utf-8")
    facts_path = tmp_path / "facts.json"
    facts_path.write_text("{}", encoding="utf-8")
    artifacts_path = tmp_path / "artifacts.json"
    artifacts_path.write_text("[]", encoding="utf-8")
    requirements = run_ff(
        "requirements", "--policy", str(policy_path), "--facts", str(facts_path),
        "--artifacts", str(artifacts_path), "--format", "json",
    )
    assert requirements.returncode == 0, requirements.stderr
    payload = json.loads(requirements.stdout)
    assert payload["ok"] is True
    assert payload["warnings"]


def _report_or_none(validator, value):
    try:
        return validator(value)
    except TypeError:
        return None


def test_malformed_reference_and_severity_containers_return_structural_reports():
    malformed_entity = valid_ledger()
    malformed_entity["events"][0]["entity_id"] = []
    malformed_entity["events"][0]["event_hash"] = _event_hash(malformed_entity["events"][0])
    entity_report = _report_or_none(validate_production_ledger, malformed_entity)

    malformed_correction = valid_ledger()
    correction = {
        "event_id": "EVENT_002",
        "sequence": 2,
        "occurred_at": "2026-09-07T00:01:00Z",
        "event_type": "CORRECTION_RECORDED",
        "entity_id": "UNIT_TEST",
        "actor": "HUMAN",
        "correction_of": [],
        "previous_event_hash": malformed_correction["events"][0]["event_hash"],
    }
    correction["event_hash"] = _event_hash(correction)
    malformed_correction["events"].append(correction)
    correction_report = _report_or_none(validate_production_ledger, malformed_correction)

    malformed_severity = {
        "schema_version": "production-policy.v2",
        "policy_id": "POLICY_TEST",
        "requirements": [{"requirement_id": "REQ_TEST", "artifact_type": "SCRIPT_FACTS", "description": "facts", "severity": []}],
    }
    severity_report = _report_or_none(validate_production_policy, malformed_severity)

    assert entity_report is not None
    assert correction_report is not None
    assert severity_report is not None
    assert any(issue.code == "INVALID_REFERENCE" for issue in entity_report.errors)
    assert any(issue.code == "INVALID_REFERENCE" for issue in correction_report.errors)
    assert any(issue.code == "INVALID_SEVERITY" for issue in severity_report.errors)


def test_runtime_ledger_validation_matches_strict_nested_schema_rules():
    payload = valid_ledger()
    event = payload["events"][0]
    event["sequence"] = True
    event.pop("previous_event_hash")
    event["retry_of"] = None
    event["correction_of"] = None
    event["retry_policy"] = {"variable_fields": ["seed"], "unexpected": True}
    event["event_hash"] = _event_hash(event)

    report = validate_production_ledger(payload)

    assert not report.ok
    codes = {issue.code for issue in report.errors}
    assert {"INVALID_EVENT_SEQUENCE", "REQUIRED_FIELD", "INVALID_REFERENCE", "UNKNOWN_FIELD"} <= codes


def test_malformed_artifact_inventory_is_an_error_not_a_warning_only_report(tmp_path: Path):
    policy = {
        "schema_version": "production-policy.v2",
        "policy_id": "POLICY_TEST",
        "requirements": [{"requirement_id": "REQ_MUSIC", "artifact_type": "MUSIC_INTENT", "description": "music", "severity": "WARNING"}],
    }
    report = evaluate_requirements(policy, {}, 42)
    assert report.exit_code == 1
    assert any(issue.code == "INVALID_ARTIFACT_INVENTORY" for issue in report.errors)

    policy_path = tmp_path / "policy.json"
    facts_path = tmp_path / "facts.json"
    artifacts_path = tmp_path / "artifacts.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    facts_path.write_text("{}", encoding="utf-8")
    artifacts_path.write_text("42", encoding="utf-8")
    result = run_ff(
        "requirements", "--policy", str(policy_path), "--facts", str(facts_path),
        "--artifacts", str(artifacts_path), "--format", "json",
    )
    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any("artifact inventory" in error for error in payload["errors"])


def test_retry_comparison_detects_missing_and_explicit_null_parameters():
    for original_parameters, retry_parameters in (
        ({"seed": 1, "optional": None}, {"seed": 2}),
        ({"seed": 1}, {"seed": 2, "optional": None}),
    ):
        payload = valid_ledger()
        first = payload["events"][0]
        first["parameters"] = original_parameters
        first["retry_policy"] = {"variable_fields": ["seed"]}
        first["event_hash"] = _event_hash(first)
        retry = {
            "event_id": "EVENT_002",
            "sequence": 2,
            "occurred_at": "2026-09-07T00:01:00Z",
            "event_type": "ATTEMPT_RECORDED",
            "entity_id": "UNIT_TEST",
            "actor": "HUMAN",
            "parameters": retry_parameters,
            "retry_of": "EVENT_001",
            "previous_event_hash": first["event_hash"],
        }
        retry["event_hash"] = _event_hash(retry)
        payload["events"].append(retry)

        report = validate_production_ledger(payload)

        assert any(issue.code == "RETRY_VARIABLE_NOT_ALLOWED" for issue in report.errors)


def test_entity_reference_issues_keep_their_original_array_indexes():
    payload = valid_ledger()
    payload["entities"].insert(0, "invalid")
    payload["entities"][2]["references"]["script"] = "SCRIPT_MISSING"

    report = validate_production_ledger(payload)

    assert any(issue.json_pointer == "/entities/2/references/script" for issue in report.errors)
