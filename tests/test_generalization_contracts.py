from __future__ import annotations

import json
from pathlib import Path

from filmfoundry import (
    GOAL_SCENE_ASSET,
    GOAL_SHORT_VIDEO_TEST,
    ProjectProfile,
    StyleProfile,
    build_provider_neutral_handoff,
    route_creation_goal,
    validate_provider_neutral_handoff,
    validate_project_profile,
    validate_style_profile,
)


def test_profiles_keep_missing_values_explicitly_unknown_and_reject_hidden_fields():
    assert ProjectProfile.from_mapping({"medium": "advertising"}).project_id == "UNKNOWN"
    assert StyleProfile.from_mapping({"palette": "cool"}).visual_language == "UNKNOWN"
    assert not validate_project_profile({"project_id": "EXAMPLE_PROJECT", "medium": "short"})
    assert not validate_style_profile({"visual_language": "illustration"})
    assert any("unsupported field" in error for error in validate_style_profile({"provider": "x"}))


def test_creation_goal_router_selects_minimal_non_project_specific_paths():
    short = route_creation_goal("做一个短视频试片，先验证 hook 和关键帧")
    assert short.goal == GOAL_SHORT_VIDEO_TEST
    assert short.route == ("hook", "beat_map", "keyframes", "motion_prompt", "end_frame_check")
    scene = route_creation_goal("prepare a location asset for this scene")
    assert scene.goal == GOAL_SCENE_ASSET
    assert "shot_demand_matrix" in scene.route


def test_provider_neutral_handoff_copies_facts_without_provider_syntax():
    prompt = {
        "prompt_id": "SHOT_PROMPT_01",
        "prompt_type": "I2V",
        "production_unit": "SHOT_G01",
        "visual_fact": "A courier waits at the station.",
        "output_profile": "vertical video",
        "start_state": "lamp off",
        "end_state": "lamp remains off",
        "subjects": ["COURIER"],
        "dominant_action": "one restrained turn",
        "camera": "fixed wide frame",
        "continuity_locks": ["screen direction"],
        "references": [{"slot": "identity", "asset_id": "COURIER_REF", "role": "identity", "controls": "face", "does_not_control": "location"}],
        "forbidden": ["extra people"],
        "acceptance": ["identity stable"],
    }
    handoff = build_provider_neutral_handoff(
        prompt,
        project_profile=ProjectProfile(project_id="EXAMPLE_PROJECT", medium="narrative_short"),
        style_profile=StyleProfile(visual_language="cinematic_realism"),
    )
    rendered = handoff.to_markdown()
    assert handoff.status == "SPEC_RESOLVED"
    assert "provider-neutral" in rendered
    assert "EXAMPLE_PROJECT" in rendered
    assert "COURIER_REF" in rendered
    assert "provider:" not in rendered.lower()
    assert "REFERENCE BINDING" in rendered
    assert "ACCEPTANCE CHECKS" in rendered
    assert validate_provider_neutral_handoff(handoff.to_dict()) == []


def test_compile_output_is_neutral_even_when_legacy_provider_argument_is_given(tmp_path: Path):
    prompt = {
        "prompt_id": "SHOT_PROMPT_02", "prompt_type": "T2V", "production_unit": "SHOT_G02",
        "visual_fact": "A door opens.", "output_profile": "16:9", "start_state": "closed",
        "end_state": "open", "subjects": ["DOOR"], "dominant_action": "open the door", "camera": "locked",
        "continuity_locks": ["door position"], "references": [{"slot": "door", "asset_id": "DOOR_REF", "role": "prop", "controls": "door geometry", "does_not_control": "camera"}], "forbidden": ["extra doors"], "acceptance": ["door open"],
    }
    sections = ["visual_fact", "output_profile", "start_state", "end_state", "subjects", "dominant_action", "camera", "continuity_locks", "references", "forbidden", "acceptance"]
    path = tmp_path / "prompt.md"
    path.write_text("```json\n" + json.dumps(prompt) + "\n```\n" + "\n".join(f"## {section}\ncontent" for section in sections), encoding="utf-8")
    from filmfoundry import compile_prompt

    output = compile_prompt(path, "legacy-provider")
    assert "provider-neutral handoff" in output
    assert "legacy-provider" not in output
