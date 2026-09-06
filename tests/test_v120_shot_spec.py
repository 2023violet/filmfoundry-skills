import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def v12_spec():
    return {
        "schema_version": "1.2",
        "shot_id": "SH003",
        "generation_unit": "SH003_G01",
        "chapter": "CH01",
        "generation_duration_seconds": 10.0,
        "edit_target_duration_seconds": 5.0,
        "narrative_goal": "Establish the child looking at home valley",
        "dominant_action": "The child quietly looks toward the valley",
        "location": {"canonical": "LOC_OVERLOOK"},
        "initial_state": "child stands frame right; valley is frame left",
        "end_state": "child remains frame right looking toward the valley",
        "shot_size": "medium_wide",
        "composition": "child frame right, valley frame left",
        "camera_move": "near-static with one subtle push",
        "timing_granularity": "stages",
        "transition_type": "hard_cut",
        "reference_bindings": [{"ref_id": "KF_A", "controls": "primary visual", "does_not_control": "future motion"}],
        "action_stages": [{"stage": 1, "action": "micro-motion only", "end_state": "identity and geography stable"}],
        "failure_risks": ["identity drift", "eyeline mismatch"],
        "quality_bar": "identity and eyeline before aesthetics",
        "eyeline_critical": True,
        "eyeline_subject": "CHAR_AHOU",
        "eyeline_target": "LOC_VALLEY",
        "eyeline_screen_direction": "left"
    }


def test_v12_accepts_separate_generation_and_edit_durations():
    from validate_shot_spec import validate_shot_spec
    assert validate_shot_spec(v12_spec()) == []


def test_v12_requires_positive_numeric_generation_and_edit_durations():
    from validate_shot_spec import validate_shot_spec
    data = v12_spec()
    data["generation_duration_seconds"] = "10s"
    data["edit_target_duration_seconds"] = 0
    errors = validate_shot_spec(data)
    assert any("generation_duration_seconds" in e for e in errors)
    assert any("edit_target_duration_seconds" in e for e in errors)


def test_v12_edit_target_cannot_exceed_generated_source():
    from validate_shot_spec import validate_shot_spec
    data = v12_spec()
    data["edit_target_duration_seconds"] = 12.0
    errors = validate_shot_spec(data)
    assert any("cannot exceed" in e.lower() for e in errors)


def test_eyeline_critical_requires_subject_target_and_screen_direction():
    from validate_shot_spec import validate_shot_spec
    data = v12_spec()
    for field in ("eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
        data.pop(field)
    errors = validate_shot_spec(data)
    for field in ("eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
        assert any(field in e for e in errors), errors


def test_eyeline_critical_rejects_invalid_screen_direction():
    from validate_shot_spec import validate_shot_spec
    data = v12_spec()
    data["eyeline_screen_direction"] = "up-left"
    errors = validate_shot_spec(data)
    assert any("eyeline_screen_direction" in e for e in errors)


def test_published_v12_shot_spec_example_passes():
    from validate_shot_spec import validate_shot_spec
    path = ROOT / "skills" / "generative-film-production" / "templates" / "shot-spec.example.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "1.2"
    assert validate_shot_spec(data) == []
