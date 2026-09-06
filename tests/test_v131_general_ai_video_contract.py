from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"


def test_v131_general_visual_planning_contract():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "**version:** 1.3.3" in readme
    for token in ("visual planning", "capability", "edit timeline", "picture lock"):
        assert token in skill
    for rel in (
        "references/24-visual-planning-layer.md",
        "references/25-character-reference-system.md",
        "references/26-location-reference-system.md",
        "references/27-storyboard-keyframe-planning.md",
        "references/28-visual-plan-qc.md",
        "references/29-capability-scoped-model-gates.md",
        "references/30-edit-timeline-contract.md",
        "templates/character-reference-sheet.md",
        "templates/location-reference-sheet.md",
        "templates/storyboard-board.md",
        "templates/sequence-plan.md",
        "templates/edit-timeline-ledger.csv",
    ):
        assert (SKILL / rel).is_file(), rel


def test_v131_does_not_make_four_panel_or_comic_mandatory():
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8").lower()
    assert "four-panel" not in skill
    assert "need comic / 漫剧" not in skill
