from __future__ import annotations

import hashlib
import json
from pathlib import Path

from filmfoundry_v2 import (
    ArtifactRequirement,
    RequirementReport,
    evaluate_requirements,
    validate_production_ledger,
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
