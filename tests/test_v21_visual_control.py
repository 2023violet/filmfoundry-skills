from __future__ import annotations

import json

import pytest

from filmfoundry import (
    VisualControlPlan,
    parse_visual_control,
    validate_visual_control,
    validate_visual_control_alignment,
)


def valid_character() -> dict:
    return {
        "asset_id": "CHAR_SHENYE",
        "reference_kind": "RECURRING_CORE",
        "face_closeup_asset_id": "CHAR_SHENYE_FACE",
        "front_body_asset_id": "CHAR_SHENYE_FRONT",
        "back_body_asset_id": "CHAR_SHENYE_BACK",
        "headless_body_strategy": "OPTIONAL",
        "state_variant": "NEUTRAL",
        "controls": "face, silhouette, wardrobe",
        "does_not_control": "camera, location, story state",
        "qc_status": "PASS",
    }


def valid_plan() -> dict:
    return {
        "visual_control_id": "VC_EP01_SH001",
        "production_unit": "EP01_SH001_G01",
        "character_references": [valid_character()],
        "location_reference": {
            "location_id": "LOC_INN",
            "preferred_view": "THREE_QUARTER",
            "anchor_objects": ["door", "lantern hook"],
            "camera_side": "SCREEN_LEFT",
            "light_sources": ["lantern"],
            "geometry_controls": "door and hook persist",
            "does_not_control": "character identity or action timing",
        },
        "spatial_map": {
            "relations": [
                {
                    "subject_id": "CHAR_SHENYE",
                    "anchor_id": "LOC_INN_DOOR",
                    "relation": "stands beside",
                    "distance": "2m",
                    "facing": "door",
                    "screen_direction": "RIGHT",
                    "camera_side": "SCREEN_LEFT",
                    "light_direction": "from left",
                }
            ]
        },
        "scale_references": [
            {
                "subject_id": "CHAR_SHENYE",
                "reference_object_id": "LOC_INN_DOOR",
                "visible_relation": "person reaches half the door height",
                "intended_scale": "human scale",
                "scale_confidence": "PASS",
            }
        ],
        "physics_cues": [
            {
                "material": "wood",
                "force": "small push",
                "weight": "light",
                "inertia": "settles once",
                "gravity": "down",
                "observable_result": "door moves a few centimeters and stops",
            }
        ],
        "previsualization": {
            "duration_seconds": 3,
            "state_alignment": "PASS",
            "initial_state": "door closed",
            "end_state": "door ajar",
        },
        "lens_result": {
            "fov_degrees": 50,
            "observable_framing": "door and full figure remain readable",
        },
        "review_status": "PENDING",
        "experiment_ids": [],
    }


def test_valid_visual_control_plan_parses_and_validates():
    payload = valid_plan()
    plan = parse_visual_control(json.dumps(payload))
    assert isinstance(plan, VisualControlPlan)
    assert plan.visual_control_id == "VC_EP01_SH001"
    assert validate_visual_control(plan).ok


def test_visual_control_unknown_field_is_error_but_namespaced_extension_is_allowed():
    payload = valid_plan()
    payload["rogue"] = True
    payload["extensions"] = {"project:wucheng": {"note": "local"}, "provider:minimax": {}}
    report = validate_visual_control(payload)
    assert not report.ok
    assert any(issue.severity == "ERROR" and "rogue" in issue.message for issue in report.issues)

    payload.pop("rogue")
    payload["extensions"]["local"] = True
    report = validate_visual_control(payload)
    assert any(issue.severity == "ERROR" and "extensions" in issue.message for issue in report.issues)


def test_visual_control_missing_gray_identity_background_is_warning_only():
    report = validate_visual_control(valid_plan())
    assert report.ok
    assert any(issue.severity == "WARNING" and "gray" in issue.message.lower() for issue in report.warnings)


@pytest.mark.parametrize(
    "field, expected",
    [
        ("observable_result", "observable_result"),
        ("duration_seconds", "duration"),
        ("state_alignment", "state_alignment"),
    ],
)
def test_visual_control_conditional_fields_are_structural_errors(field: str, expected: str):
    payload = valid_plan()
    if field == "duration_seconds":
        payload["previsualization"][field] = 0
    elif field == "state_alignment":
        payload["previsualization"][field] = "FAIL"
    else:
        payload["physics_cues"][0][field] = ""
    report = validate_visual_control(payload)
    assert not report.ok
    assert any(issue.severity == "ERROR" and expected in issue.message.lower() for issue in report.errors)


def test_alignment_rejects_camera_side_and_state_mismatch():
    shot = {
        "shot_id": "EP01_SH001",
        "initial_state": "door closed",
        "end_state": "door ajar",
        "camera": {"axis": "SCREEN_RIGHT"},
    }
    payload = valid_plan()
    payload["previsualization"]["state_alignment"] = "FAIL"
    report = validate_visual_control_alignment(shot, payload)
    assert not report.ok
    assert any("camera" in issue.message.lower() for issue in report.errors)
    assert any("state" in issue.message.lower() for issue in report.errors)


def test_visual_control_fixture_files_cover_golden_and_invalid_cases():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1] / "tests" / "historical" / "fixtures" / "v2" / "visual-control"
    assert (root / "visual-control-plan.golden.json").is_file()
    assert (root / "visual-control-plan.invalid.json").is_file()
