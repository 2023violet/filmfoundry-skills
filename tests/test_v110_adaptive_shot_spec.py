import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def base_environment_spec():
    return {
        "shot_id": "SH001",
        "generation_unit": "SH001_G01",
        "chapter": "CH01",
        "duration_target": "8-10s",
        "narrative_goal": "Establish an enclosed mountain valley",
        "dominant_action": "Camera slowly advances toward the settlement",
        "location": {"canonical": "LOC_VALLEY"},
        "initial_state": "settlement distant; mist thin",
        "end_state": "camera settled; geography unchanged",
        "shot_size": "extreme_wide",
        "composition": "mountains dominate; settlement lower-center",
        "camera_move": "slow_forward_push",
        "timing_granularity": "stages",
        "action_stages": [
            {"stage": 1, "action": "mist drifts", "end_state": "geography stable"},
            {"stage": 2, "action": "camera advances", "end_state": "settlement slightly clearer"},
        ],
        "transition_type": "hard_cut",
        "reference_bindings": [
            {"ref_id": "KF_A", "controls": "primary visual", "does_not_control": "none"}
        ],
        "failure_risks": ["terrain morph"],
        "quality_bar": "strict_environment_continuity",
    }


def test_environment_spec_does_not_require_dialogue_character_or_eyeline_fields():
    from validate_shot_spec import validate_shot_spec
    assert validate_shot_spec(base_environment_spec()) == []


def test_dialogue_condition_requires_voice_route_timing_authority_and_speech_intent():
    from validate_shot_spec import validate_shot_spec
    spec = base_environment_spec()
    spec["dialogue"] = "Where are we?"
    errors = validate_shot_spec(spec)
    for token in ("voice_id", "dialogue_route", "timing_authority", "speech_intent"):
        assert any(token in e for e in errors), (token, errors)


def test_reverse_angle_condition_requires_structured_axis_and_eyeline():
    from validate_shot_spec import validate_shot_spec
    spec = base_environment_spec()
    spec["transition_type"] = "reverse_angle"
    errors = validate_shot_spec(spec)
    for token in ("camera_axis", "screen_direction", "eyeline_subject", "eyeline_target", "eyeline_screen_direction"):
        assert any(token in e for e in errors), (token, errors)


def test_prop_interaction_condition_requires_persistent_prop_states():
    from validate_shot_spec import validate_shot_spec
    spec = base_environment_spec()
    spec["canonical_props"] = ["PROP_MAP"]
    spec["prop_interaction"] = True
    errors = validate_shot_spec(spec)
    for token in ("prop_initial_state", "prop_end_state", "prop_persistence"):
        assert any(token in e for e in errors), (token, errors)


def test_continuous_condition_requires_handoff_state_fields():
    from validate_shot_spec import validate_shot_spec
    spec = base_environment_spec()
    spec["transition_type"] = "continuous"
    errors = validate_shot_spec(spec)
    for token in ("continuity_source", "previous_observed_state", "handoff_state"):
        assert any(token in e for e in errors), (token, errors)


def test_second_level_timing_requires_named_authority_and_constraint():
    from validate_shot_spec import validate_shot_spec
    spec = base_environment_spec()
    spec["timing_granularity"] = "seconds"
    errors = validate_shot_spec(spec)
    assert any("timing_constraint" in e for e in errors)
    assert any("timing_authority" in e for e in errors)


def test_v11_core_requires_explicit_location_transition_and_reference_list():
    from validate_shot_spec import validate_shot_spec
    spec = base_environment_spec()
    spec.pop("location")
    spec.pop("transition_type")
    spec.pop("reference_bindings")
    errors = validate_shot_spec(spec)
    for token in ("location", "transition_type", "reference_bindings"):
        assert any(token in e for e in errors), (token, errors)
