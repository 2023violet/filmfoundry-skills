from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"


def test_v132_metadata_and_state_alignment_reference_exist():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 'version = "1.3.3"' in pyproject
    assert "**Version:** 1.3.3" in readme
    assert (SKILL / "references" / "31-visual-control-state-alignment.md").is_file()
    assert (SKILL / "templates" / "visual-control-state-audit.csv").is_file()


def test_v132_root_skill_requires_state_matched_visual_authority():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8").lower()
    for token in ("state-matched", "partial authority", "proxy smoke", "picture lock"):
        assert token in text


def test_v132_picture_lock_does_not_require_final_sound_mix():
    editing = (SKILL / "references" / "30-edit-timeline-contract.md").read_text(encoding="utf-8").lower()
    assert "final sound mix" in editing
    assert "after picture lock" in editing
