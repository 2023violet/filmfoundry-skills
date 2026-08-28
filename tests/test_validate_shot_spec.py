import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def valid_spec():
    return {
        "shot_id": "SH001",
        "scene_id": "SC01",
        "narrative_goal": "Reveal the map clue",
        "dominant_action": "CHAR_A unfolds the map",
        "timing_granularity": "stages",
        "initial_state": "CHAR_A stands frame left holding a folded map",
        "end_state": "The map is fully open; CHAR_A remains frame left with left hand on the lower-left corner",
        "transition_type": "reverse_angle",
        "camera_axis": "table-to-CHAR_A axis, do not cross",
        "screen_direction": "CHAR_A:left|CHAR_B:right",
        "eyeline": "CHAR_A looks screen right toward CHAR_B",
        "eyeline_subject": "CHAR_A",
        "eyeline_target": "CHAR_B",
        "eyeline_screen_direction": "right",
        "reference_bindings": [
            {"ref_id": "REF_A", "controls": "face identity", "does_not_control": "wardrobe, background"}
        ],
        "action_stages": [
            {"stage": 1, "action": "CHAR_A places the folded map on the table", "end_state": "The folded map rests centered on the table"},
            {"stage": 2, "action": "CHAR_A unfolds the map", "end_state": "The map is fully open and both hands stop moving"},
        ],
    }


def test_valid_spec_has_no_errors():
    from validate_shot_spec import validate_shot_spec
    assert validate_shot_spec(valid_spec()) == []


def test_requires_identity_and_end_state_fields():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec.pop("shot_id")
    spec["end_state"] = ""
    errors = validate_shot_spec(spec)
    assert any("shot_id" in e for e in errors)
    assert any("end_state" in e for e in errors)


def test_rejects_multiple_dominant_actions_encoded_as_list():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["dominant_action"] = ["walks", "opens map"]
    errors = validate_shot_spec(spec)
    assert any("dominant_action" in e for e in errors)


def test_reverse_angle_requires_axis_and_eyeline():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    for field in ("camera_axis", "screen_direction", "eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
        spec.pop(field)
    errors = validate_shot_spec(spec)
    assert any("camera_axis" in e for e in errors)
    assert any("screen_direction" in e for e in errors)
    assert any("eyeline_subject" in e for e in errors)
    assert any("eyeline_target" in e for e in errors)
    assert any("eyeline_screen_direction" in e for e in errors)


def test_reference_binding_requires_controls_and_boundary():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["reference_bindings"] = [{"ref_id": "REF_A", "controls": "identity"}]
    errors = validate_shot_spec(spec)
    assert any("does_not_control" in e for e in errors)


def test_stages_require_observable_end_state_each():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["action_stages"][1]["end_state"] = ""
    errors = validate_shot_spec(spec)
    assert any("action_stages[1].end_state" in e for e in errors)


def test_second_level_requires_hard_timing_reason():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["timing_granularity"] = "seconds"
    errors = validate_shot_spec(spec)
    assert any("timing_constraint" in e for e in errors)
    spec["timing_constraint"] = "lip sync: brand name at 7.0s"
    assert not any("timing_constraint" in e for e in validate_shot_spec(spec))


def test_cli_exits_nonzero_for_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"shot_id": "SH1"}), encoding="utf-8")
    script = SCRIPT_DIR / "validate_shot_spec.py"
    result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "dominant_action" in result.stdout


def test_rejects_unsupported_transition_type():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["transition_type"] = "teleport"
    errors = validate_shot_spec(spec)
    assert any("transition_type" in e and "unsupported" in e.lower() for e in errors)


def test_rejects_duplicate_reference_ids_in_one_shot():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["reference_bindings"].append({"ref_id": "REF_A", "controls": "wardrobe", "does_not_control": "face identity"})
    errors = validate_shot_spec(spec)
    assert any("duplicate ref_id" in e.lower() for e in errors)


def test_stages_require_explicit_sequential_stage_numbers():
    from validate_shot_spec import validate_shot_spec
    spec = valid_spec()
    spec["action_stages"][0].pop("stage")
    spec["action_stages"][1]["stage"] = 3
    errors = validate_shot_spec(spec)
    assert any("action_stages[0].stage" in e for e in errors)
    assert any("sequential" in e.lower() for e in errors)
