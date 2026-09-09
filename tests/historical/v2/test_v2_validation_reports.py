from __future__ import annotations

import json
from pathlib import Path

import pytest

from filmfoundry import ValidationIssue, ValidationReport


def test_validation_issue_rejects_unknown_severity():
    with pytest.raises(ValueError, match="ERROR or WARNING"):
        ValidationIssue("INFO", "X", "not supported")


def test_validation_report_sorts_errors_then_warnings_stably_and_deduplicates_checked():
    report = ValidationReport(
        stage="higgsfield",
        checked=["b.json", "a.json", "a.json"],
        issues=[
            ValidationIssue("WARNING", "W2", "warning two", source="z.json"),
            ValidationIssue("ERROR", "E2", "error two", source="z.json"),
            ValidationIssue("ERROR", "E1", "error one", source="a.json"),
            ValidationIssue("WARNING", "W1", "warning one", source="a.json"),
        ],
    )

    assert report.checked == ["a.json", "b.json"]
    assert [(issue.severity, issue.source, issue.code) for issue in report.issues] == [
        ("ERROR", "a.json", "E1"),
        ("ERROR", "z.json", "E2"),
        ("WARNING", "a.json", "W1"),
        ("WARNING", "z.json", "W2"),
    ]


def test_warning_only_report_is_ok_and_has_zero_exit_code():
    report = ValidationReport.from_messages(
        "higgsfield",
        checked=["register.json"],
        errors=[],
        warnings=["capability has no observed generation yet"],
    )

    assert report.ok is True
    assert report.exit_code == 0
    assert report.errors == []
    assert len(report.warnings) == 1
    assert report.to_dict() == {
        "stage": "higgsfield",
        "ok": True,
        "exit_code": 0,
        "checked": ["register.json"],
        "issues": [
            {
                "severity": "WARNING",
                "code": "VALIDATION_WARNING",
                "message": "capability has no observed generation yet",
                "source": "",
                "json_pointer": "",
                "related_ids": [],
                "suggestion": "",
            }
        ],
        "errors": [],
        "warnings": ["capability has no observed generation yet"],
    }


def test_error_report_has_nonzero_exit_code():
    report = ValidationReport.from_messages("higgsfield", [], ["invalid evidence"])
    assert report.ok is False
    assert report.exit_code == 1
    assert report.to_dict()["errors"] == ["invalid evidence"]


def test_higgsfield_register_golden_fixture_is_unverified_until_observed():
    fixture = Path(__file__).parent / "fixtures" / "v2" / "golden" / "higgsfield-evidence-register.json"
    register = json.loads(fixture.read_text(encoding="utf-8"))
    assert register["schema_version"] == "higgsfield-evidence.v1"
    assert register["provider"] == "higgsfield"
    assert register["capabilities"]
    assert all(item["evidence_level"] == "UNVERIFIED" for item in register["capabilities"])
    assert register["evidence"] == []


def test_higgsfield_register_invalid_fixture_is_rejected_by_shape():
    fixture = Path(__file__).parent / "fixtures" / "v2" / "invalid" / "higgsfield-evidence-register.json"
    register = json.loads(fixture.read_text(encoding="utf-8"))
    assert register["provider"] != "higgsfield"
    assert "schema_version" not in register
