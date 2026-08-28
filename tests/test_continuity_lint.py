import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def base_prev():
    return {
        "shot_id": "SH001",
        "transition_out": "hard_cut",
        "end_state": "CHAR_A frame left, cup in left hand, seated",
        "camera_axis": "A-B dialogue axis",
        "eyeline": "A looks screen right toward B",
        "eyeline_subject": "A",
        "eyeline_target": "B",
        "eyeline_screen_direction": "right",
        "screen_direction": "A:left|B:right",
        "prop_state": "cup in A left hand",
        "asset_state": "CHAR_A:CANON",
        "wardrobe_state": "robe:dry",
        "light_state": "warm firelight",
        "time_state": "night",
        "tail_frame_id": "GEN001_TAIL",
    }


def base_next():
    return {
        "shot_id": "SH002",
        "transition_in": "hard_cut",
        "initial_state": "CHAR_A frame left, cup in left hand, seated",
        "camera_axis": "A-B dialogue axis",
        "eyeline": "B looks screen left toward A",
        "eyeline_subject": "B",
        "eyeline_target": "A",
        "eyeline_screen_direction": "left",
        "screen_direction": "A:left|B:right",
        "prop_state": "cup in A left hand",
        "asset_state": "CHAR_A:CANON",
        "wardrobe_state": "robe:dry",
        "light_state": "warm firelight",
        "time_state": "night",
        "start_frame_source": "independent",
    }


def test_hard_cut_does_not_require_tail_frame_relay():
    from continuity_lint import validate_transition
    assert validate_transition(base_prev(), base_next()) == []


def test_continuous_action_requires_tail_relay_and_state_match():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "continuous"
    nxt["transition_in"] = "continuous"
    errors = validate_transition(prev, nxt)
    assert any("tail" in e.lower() for e in errors)
    nxt["start_frame_source"] = "GEN001_TAIL"
    nxt["initial_state"] = prev["end_state"]
    assert validate_transition(prev, nxt) == []


def test_reverse_angle_requires_axis_eyeline_and_prop_continuity():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "reverse_angle"
    nxt["transition_in"] = "reverse_angle"
    nxt["camera_axis"] = "different axis"
    nxt["eyeline_screen_direction"] = "right"
    nxt["prop_state"] = "cup vanished"
    errors = validate_transition(prev, nxt)
    assert any("camera_axis" in e for e in errors)
    assert any("eyeline" in e for e in errors)
    assert any("prop_state" in e for e in errors)


def test_match_cut_requires_match_feature():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "match_cut"
    nxt["transition_in"] = "match_cut"
    errors = validate_transition(prev, nxt)
    assert any("match_feature" in e for e in errors)
    prev["match_feature"] = "clock circle shape"
    nxt["match_feature"] = "clock circle shape"
    assert validate_transition(prev, nxt) == []


def test_transition_type_must_agree_between_shots():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    nxt["transition_in"] = "reverse_angle"
    errors = validate_transition(prev, nxt)
    assert any("transition mismatch" in e.lower() for e in errors)


def test_reverse_angle_rejects_screen_direction_drift():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "reverse_angle"
    nxt["transition_in"] = "reverse_angle"
    nxt["screen_direction"] = "A frame right"
    errors = validate_transition(prev, nxt)
    assert any("screen_direction" in e for e in errors)


def test_continuous_transition_rejects_asset_wardrobe_light_and_time_state_drift():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev.update({
        "transition_out": "continuous",
        "asset_state": "CHAR_A:DRY",
        "wardrobe_state": "robe:dry",
        "light_state": "warm firelight",
        "time_state": "night",
    })
    nxt.update({
        "transition_in": "continuous",
        "start_frame_source": prev["tail_frame_id"],
        "initial_state": prev["end_state"],
        "asset_state": "CHAR_A:WET",
        "wardrobe_state": "robe:wet",
        "light_state": "cold daylight",
        "time_state": "morning",
    })
    errors = validate_transition(prev, nxt)
    for field in ("asset_state", "wardrobe_state", "light_state", "time_state"):
        assert any(field in e for e in errors), (field, errors)


def test_continuous_transition_requires_explicit_continuity_state_fields():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "continuous"
    nxt["transition_in"] = "continuous"
    nxt["start_frame_source"] = prev["tail_frame_id"]
    nxt["initial_state"] = prev["end_state"]
    for field in ("asset_state", "wardrobe_state", "light_state", "time_state"):
        prev.pop(field, None)
        nxt.pop(field, None)
    errors = validate_transition(prev, nxt)
    for field in ("asset_state", "wardrobe_state", "light_state", "time_state"):
        assert any(field in e and "required" in e.lower() for e in errors), (field, errors)


def test_reverse_angle_accepts_reciprocal_structured_eyelines_even_when_legacy_text_differs():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "reverse_angle"
    nxt["transition_in"] = "reverse_angle"
    prev.update({
        "eyeline": "A looks screen right toward B",
        "eyeline_subject": "A",
        "eyeline_target": "B",
        "eyeline_screen_direction": "right",
    })
    nxt.update({
        "eyeline": "B looks screen left toward A",
        "eyeline_subject": "B",
        "eyeline_target": "A",
        "eyeline_screen_direction": "left",
    })
    assert validate_transition(prev, nxt) == []


def test_reverse_angle_rejects_nonreciprocal_structured_eyelines():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "reverse_angle"
    nxt["transition_in"] = "reverse_angle"
    prev.update({"eyeline_subject": "A", "eyeline_target": "B", "eyeline_screen_direction": "right"})
    nxt.update({"eyeline_subject": "B", "eyeline_target": "A", "eyeline_screen_direction": "right"})
    errors = validate_transition(prev, nxt)
    assert any("eyeline" in e.lower() and "opposite" in e.lower() for e in errors)


def test_reverse_angle_rejects_same_moment_asset_wardrobe_light_and_time_drift():
    from continuity_lint import validate_transition
    prev, nxt = base_prev(), base_next()
    prev["transition_out"] = "reverse_angle"
    nxt["transition_in"] = "reverse_angle"
    prev.update({"asset_state": "CHAR_A:DRY", "wardrobe_state": "robe:dry", "light_state": "warm", "time_state": "night"})
    nxt.update({"asset_state": "CHAR_A:WET", "wardrobe_state": "robe:wet", "light_state": "cold", "time_state": "morning"})
    errors = validate_transition(prev, nxt)
    for field in ("asset_state", "wardrobe_state", "light_state", "time_state"):
        assert any(field in e for e in errors), (field, errors)
