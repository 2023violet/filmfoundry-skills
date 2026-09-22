from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import filmfoundry


ROOT = Path(__file__).resolve().parents[1]
SMOKE_PROJECT = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "smoke-project"


def _model():
    catalog = filmfoundry.discover_creator_sources(SMOKE_PROJECT)
    return filmfoundry.build_creator_read_model(SMOKE_PROJECT, catalog)


def test_decision_brief_is_human_readable_and_keeps_technical_evidence_separate():
    brief = filmfoundry.build_creator_decision_brief(_model())

    assert brief.schema_version == "creator-decision-brief.v1"
    assert brief.project_id == "SMOKE_PROJECT"
    assert brief.question
    assert brief.recommendation
    assert brief.options
    assert all(option.consequence for option in brief.options)
    assert brief.next_action
    assert brief.evidence_refs
    assert "schema" not in brief.question.lower()


def test_decision_brief_reports_evidence_gaps_without_turning_them_into_approval():
    model = _model()
    snapshot = replace(model.snapshot, coverage=tuple(replace(item, data_status="UNKNOWN", reason="source unavailable") for item in model.snapshot.coverage[:1]))
    model = replace(model, snapshot=snapshot)

    brief = filmfoundry.build_creator_decision_brief(model)

    assert brief.status == "EVIDENCE_INCOMPLETE"
    assert brief.open_risks
    assert "UNKNOWN" not in brief.recommendation
    assert any(option.option_id == "RESOLVE_EVIDENCE" for option in brief.options)
