import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
SCRIPT_DIR = SKILL / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def test_axis_registry_rejects_duplicate_axis_id():
    from validate_axis_registry import validate_axis_registry
    axis = {
        "axis_id": "AXIS_A", "location_id": "LOC_A", "subject_a": "A", "subject_b": "B",
        "screen_side": {"A": "left", "B": "right"},
        "eyeline": {"A": "right", "B": "left"},
        "crossing_allowed": False, "status": "LOCKED",
    }
    errors = validate_axis_registry({"axes": [axis, dict(axis)]})
    assert any("duplicate" in e.lower() for e in errors)


def test_axis_registry_rejects_non_boolean_crossing_rule():
    from validate_axis_registry import validate_axis_registry
    data = {"axes": [{
        "axis_id": "AXIS_A", "location_id": "LOC_A", "subject_a": "A", "subject_b": "B",
        "screen_side": {"A": "left", "B": "right"}, "eyeline": {"A": "right", "B": "left"},
        "crossing_allowed": "no", "status": "LOCKED",
    }]}
    assert any("crossing_allowed" in e for e in validate_axis_registry(data))


def test_voice_registry_planned_voice_may_leave_provider_unverified():
    from validate_voice_registry import validate_voice_registry
    data = {"voices": [{"voice_id": "VOICE_A", "character_id": "CHAR_A", "status": "PLANNED"}]}
    assert validate_voice_registry(data) == []


def test_voice_registry_rejects_duplicate_voice_id():
    from validate_voice_registry import validate_voice_registry
    v = {"voice_id": "VOICE_A", "character_id": "CHAR_A", "status": "PLANNED"}
    assert any("duplicate" in e.lower() for e in validate_voice_registry({"voices": [v, dict(v)]}))


def test_voice_registry_rejects_nonpositive_locked_speech_rate():
    from validate_voice_registry import validate_voice_registry
    data = {"voices": [{
        "voice_id": "VOICE_A", "character_id": "CHAR_A", "provider": "p", "voice_model": "m",
        "voice_reference": "a.wav", "speech_rate": {"neutral": 0}, "status": "LOCKED",
    }]}
    assert any("speech_rate" in e for e in validate_voice_registry(data))


def test_model_profile_rejects_duplicate_smoke_id_and_attempt_mismatch():
    from validate_model_profile import validate_model_profile
    item = {"test_id": "TEST_MODEL_01", "verdict": "VERIFIED", "attempts": 2, "passes": 1, "fails": 0}
    data = {
        "model_id": "model-a", "provider": "p", "product_surface": "s", "model_version": "v1",
        "tested_date": "2026-09-01", "verification_status": "UNVERIFIED",
        "reference_role_binding": {"status": "UNVERIFIED", "evidence_ids": []},
        "prompt_language_strategy": {"instruction_language": "en", "dialogue_language": "en"},
        "smoke_tests": [item, dict(item)],
    }
    errors = validate_model_profile(data)
    assert any("duplicate" in e.lower() for e in errors)
    assert any("attempts" in e.lower() for e in errors)


def test_model_profile_evidenced_role_binding_requires_evidence_ids():
    from validate_model_profile import validate_model_profile
    data = {
        "model_id": "model-a", "provider": "p", "product_surface": "s", "model_version": "v1",
        "tested_date": "2026-09-01", "verification_status": "UNVERIFIED",
        "reference_role_binding": {"status": "REPEATED", "evidence_ids": []},
        "prompt_language_strategy": {"instruction_language": "en", "dialogue_language": "en"},
        "smoke_tests": [],
    }
    assert any("evidence_ids" in e for e in validate_model_profile(data))


def test_production_state_kf_generated_requires_keyframe_file():
    from validate_production_state import validate_production_state
    data = {"units": {"SH1_G01": {"runtime_status": "KF_GENERATED", "keyframe": {}, "video": {}}}}
    assert any("keyframe.file" in e for e in validate_production_state(data))


def test_production_state_kf_qc_pass_requires_pass_marker():
    from validate_production_state import validate_production_state
    data = {"units": {"SH1_G01": {"runtime_status": "KF_QC_PASS", "keyframe": {"file": "kf.png", "qc": "FAIL"}, "video": {}}}}
    assert any("keyframe.qc" in e for e in validate_production_state(data))


def test_production_state_video_generated_requires_video_artifact_identity():
    from validate_production_state import validate_production_state
    data = {"units": {"SH1_G01": {"runtime_status": "VIDEO_GENERATED", "keyframe": {"file": "kf.png", "qc": "PASS"}, "video": {}}}}
    assert any("video" in e.lower() for e in validate_production_state(data))


def test_production_state_observed_state_stage_requires_writeback_flag():
    from validate_production_state import validate_production_state
    data = {"units": {"SH1_G01": {
        "runtime_status": "OBSERVED_STATE_RECORDED",
        "keyframe": {"file": "kf.png", "qc": "PASS"},
        "video": {"generation_id": "G1", "selected": "select.mp4"},
        "observed_state_written": False,
    }}}
    assert any("observed_state_written" in e for e in validate_production_state(data))


def test_dependency_validator_checks_asset_axis_and_voice_hard_dependencies():
    from validate_dependencies import validate_dependencies
    graph = {"units": {"SH2_G01": {"hard": [
        {"type": "asset", "id": "CHAR_A"},
        {"type": "axis", "id": "AXIS_A"},
        {"type": "voice", "id": "VOICE_A"},
    ], "soft": []}}}
    state = {"units": {"SH2_G01": {"runtime_status": "DRAFT"}}}
    errors = validate_dependencies(graph, state, assets=set(), axes=set(), voices=set())
    for token in ("CHAR_A", "AXIS_A", "VOICE_A"):
        assert any(token in e for e in errors), (token, errors)


def test_dependency_validator_does_not_block_on_soft_dependency():
    from validate_dependencies import validate_dependencies
    graph = {"units": {"SH2_G01": {"hard": [], "soft": [{"type": "asset", "id": "OPTIONAL"}]}}}
    state = {"units": {"SH2_G01": {"runtime_status": "DRAFT"}}}
    assert validate_dependencies(graph, state, assets=set(), axes=set(), voices=set()) == []


def test_state_transition_allows_noop_but_not_unknown_state():
    from validate_state_transition import validate_state_transition
    assert validate_state_transition("DRAFT", "DRAFT") == []
    assert any("unknown" in e.lower() for e in validate_state_transition("DRAFT", "MAGIC"))


def test_asset_registry_rejects_unknown_asset_class():
    from validate_asset_registry import validate_rows
    row = {
        "asset_id": "A", "asset_type": "prop", "asset_class": "MYSTERY", "canonical_descriptor": "x",
        "state_variant": "CANON", "parent_asset_id": "", "reference_id": "", "reference_role": "", "does_not_control": "",
    }
    assert any("asset_class" in e for e in validate_rows([row]))


def test_v11_shot_rejects_unsupported_dialogue_route():
    from validate_shot_spec import validate_shot_spec
    spec = {
        "schema_version": "1.1", "shot_id": "SH1", "generation_unit": "SH1_G01", "chapter": "C1", "duration_target": "8s",
        "narrative_goal": "speaker answers", "dominant_action": "speaker says one line", "location": {"canonical": "LOC_A"},
        "initial_state": "speaker quiet", "end_state": "speaker finishes", "shot_size": "medium", "composition": "center",
        "camera_move": "fixed", "quality_bar": "strict", "failure_risks": ["lip sync"], "timing_granularity": "stages",
        "transition_type": "hard_cut", "reference_bindings": [], "action_stages": [{"stage": 1, "action": "speaks", "end_state": "mouth closes"}],
        "dialogue": "hello", "voice_id": "VOICE_A", "dialogue_route": "TELEPATHY", "timing_authority": "APPROVED_VOICE_TRACK", "speech_intent": "calm"
    }
    assert any("dialogue_route" in e for e in validate_shot_spec(spec))
