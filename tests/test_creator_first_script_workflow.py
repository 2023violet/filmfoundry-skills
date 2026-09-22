from pathlib import Path

from filmfoundry.modes import MODE_CREATIVE, route_request


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
WORKFLOW = SKILL / "references" / "41-creator-first-script-workflow.md"
WORKBOOK = SKILL / "templates" / "script-development-workbook.md"


def test_blank_idea_routes_to_creator_workflow_without_production_references():
    decision = route_request("我只有一个模糊想法，请从零带我完成一个短片剧本")

    assert decision.mode == MODE_CREATIVE
    assert decision.references[0] == "references/41-creator-first-script-workflow.md"
    assert "references/40-work-modes.md" in decision.references
    forbidden = ("video-spec", "prompt-compiler", "model-evidence", "runtime-contract")
    assert not any(token in reference for reference in decision.references for token in forbidden)
    assert decision.validators == ()
    assert decision.allow_provider_calls is False
    assert decision.allow_source_writes is False


def test_creator_workflow_defines_the_complete_path_and_interaction_limits():
    text = WORKFLOW.read_text(encoding="utf-8")
    lower = text.lower()

    for stage in (
        "SEED_ACCEPTED",
        "LOGLINE_ACCEPTED",
        "CHARACTER_ENGINE_ACCEPTED",
        "DRAMATIC_RULES_ACCEPTED",
        "STRUCTURE_ACCEPTED",
        "DRAFT_ACCEPTED",
        "REVISION_ACCEPTED",
    ):
        assert stage in text
    assert "fast" in lower and "standard" in lower and "strict" in lower
    assert "one blocking decision" in lower
    assert "deferred" in lower
    assert "optional depth" in lower
    assert "fresh-context" in lower


def test_optional_workbook_matches_the_creator_workflow_gates():
    text = WORKBOOK.read_text(encoding="utf-8")

    for heading in (
        "## Seed",
        "## Logline",
        "## Character engine",
        "## Dramatic rules",
        "## Structure",
        "## Draft",
        "## Revision",
    ):
        assert heading in text
    assert "Creator decision" in text
    assert "Open question" in text
