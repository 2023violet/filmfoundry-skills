import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
SCRIPT_DIR = SKILL / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def test_published_shot_spec_example_passes_current_validator():
    from validate_shot_spec import validate_shot_spec
    data = json.loads((SKILL / "templates" / "shot-spec.example.json").read_text(encoding="utf-8"))
    assert validate_shot_spec(data) == []


def test_published_continuity_example_passes_current_validator():
    from continuity_lint import validate_transition
    path = SKILL / "templates" / "continuity-ledger.example.csv"
    with path.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    assert validate_transition(rows[0], rows[1]) == []


def test_continuity_template_carries_structured_state_and_eyeline_fields():
    path = SKILL / "templates" / "continuity-ledger.example.csv"
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fields = set(reader.fieldnames or [])
    required = {
        "asset_state",
        "wardrobe_state",
        "light_state",
        "time_state",
        "eyeline_subject",
        "eyeline_target",
        "eyeline_screen_direction",
    }
    assert required <= fields


def test_release_version_is_consistent_across_metadata_and_readme():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "**Version:** 1.0.1" in readme
    assert 'version = "1.0.1"' in pyproject
    assert "## 1.0.1" in changelog


def test_continuity_reference_documents_structured_eyeline_and_state_requirements():
    text = (SKILL / "references" / "07-continuity-engine.md").read_text(encoding="utf-8").lower()
    for token in [
        "eyeline_subject",
        "eyeline_target",
        "eyeline_screen_direction",
        "asset_state",
        "wardrobe_state",
        "light_state",
        "time_state",
    ]:
        assert token in text
    assert "reciprocal" in text


def test_shot_card_exposes_structured_reverse_angle_fields():
    text = (SKILL / "templates" / "shot-card.md").read_text(encoding="utf-8").lower()
    for token in ["screen direction", "eyeline subject", "eyeline target", "eyeline screen direction"]:
        assert token in text
