"""Behavioral contract tests for the additive FilmFoundry v2 package.

The v1 validators deliberately remain outside this test module.  These tests
describe the stricter v2 boundary that downstream CLI and project adapters
consume.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from filmfoundry_v2 import (
    LIFECYCLE_STATES,
    parse_prompt_metadata,
    resolve_manifest_path,
    validate_asset_registry,
    validate_evidence,
    validate_prompt_markdown,
    validate_production_state,
    validate_reference_graph,
    validate_shot_spec,
    validate_state_transition,
    validate_workspace_manifest,
)


def valid_manifest() -> dict:
    return {
        "workspace_version": "2.0.0",
        "project_id": "PROJECT_WUCHENG",
        "top_level": {"entry": "00_入口与规则", "stories": "02_故事与Canon"},
        "authorities": {
            "human": "markdown",
            "machine": ["json", "csv"],
            "media": "registry",
        },
        "archive_boundary": {"path": "99_归档", "mode": "read_only"},
        "id_policy": {"pattern": "^[A-Z][A-Z0-9_]{2,63}$", "charset": "ASCII"},
        "adapter_compatibility": {"filmfoundry": ">=2.0.0,<3.0.0", "project": "wucheng-v2"},
        "required_tools": ["python>=3.11"],
    }


def valid_asset(asset_id: str = "CHAR_SHENYE") -> dict:
    return {
        "asset_id": asset_id,
        "asset_type": "character",
        "asset_class": "CANONICAL",
        "display_name": "沈夜",
        "path": "04_资产库/角色/CHAR_SHENYE.png",
        "sha256": "a" * 64,
        "width": 1024,
        "height": 1536,
        "aspect_ratio": 1024 / 1536,
        "mode": "RGBA",
        "alpha": True,
        "profile": "CHARACTER_REFERENCE",
        "state": "LOCKED",
        "canonical_level": "CANONICAL",
        "reference_role": "identity and wardrobe",
        "does_not_control": "camera motion or dialogue timing",
        "source": "generated",
        "episode_scope": ["EP01"],
    }


def valid_shot() -> dict:
    return {
        "shot_id": "EP01_SH001",
        "generation_unit_id": "EP01_SH001_G01",
        "edit_unit_ids": ["EP01_EDIT001"],
        "generation_duration_seconds": 10,
        "edit_target_duration_seconds": 5,
        "narrative_goal": "Reveal the watcher at the inn entrance",
        "dominant_action": "The watcher turns once toward the lantern",
        "location": {"asset_id": "LOC_INN"},
        "initial_state": "Watcher stands in profile with lantern dark",
        "end_state": "Watcher faces the lantern with the same wardrobe and geography",
        "shot_size": "medium_wide",
        "composition": "Watcher frame right, entrance frame left",
        "camera": {"movement": "one slow push in", "axis": "screen-left"},
        "transition_type": "hard_cut",
        "reference_bindings": [
            {
                "slot": "character",
                "asset_id": "CHAR_SHENYE",
                "role": "identity",
                "controls": "face, wardrobe, silhouette",
                "does_not_control": "lantern position or camera motion",
            }
        ],
        "failure_risks": ["identity drift"],
        "quality_bar": "identity and geography remain readable",
    }


def valid_prompt() -> str:
    metadata = {
        "prompt_id": "EP01_SH001_P01",
        "prompt_type": "I2V",
        "production_unit": "EP01_SH001_G01",
        "visual_fact": "The watcher is in profile at the inn entrance.",
        "output_profile": "VIDEO_SOURCE_NATIVE",
        "start_state": "Lantern dark; watcher frame right.",
        "end_state": "Lantern lit; watcher turns once toward it.",
        "subjects": ["CHAR_SHENYE"],
        "dominant_action": "One turn toward the lantern.",
        "camera": "One slow push in.",
        "continuity_locks": ["wardrobe", "screen direction"],
        "references": [
            {
                "slot": "character",
                "asset_id": "CHAR_SHENYE",
                "role": "identity",
                "controls": "face and wardrobe",
                "does_not_control": "motion timing",
            }
        ],
        "forbidden": ["extra characters", "camera orbit"],
        "acceptance": ["single action", "stable identity"],
    }
    return "```json\n" + json.dumps(metadata, ensure_ascii=False, indent=2) + "\n```\n\n" + "\n".join(
        f"## {field}\n\n{field} content" for field in (
            "visual_fact", "output_profile", "start_state", "end_state", "subjects",
            "dominant_action", "camera", "continuity_locks", "references", "forbidden", "acceptance",
        )
    )


def test_valid_workspace_manifest_passes_strict_contract():
    assert validate_workspace_manifest(valid_manifest()) == []


def test_workspace_manifest_rejects_unknown_root_fields_and_bad_archive_mode():
    manifest = valid_manifest()
    manifest["unscoped_field"] = True
    manifest["archive_boundary"] = {"path": "99_归档", "mode": "mutable"}
    errors = validate_workspace_manifest(manifest)
    assert any("unscoped_field" in error for error in errors)
    assert any("archive_boundary" in error for error in errors)


def test_manifest_paths_are_root_relative_and_cannot_escape_archive_root(tmp_path: Path):
    root = tmp_path / "workspace"
    root.mkdir()
    assert resolve_manifest_path(root, "02_故事与Canon/README.md") == root / "02_故事与Canon/README.md"
    with pytest.raises(ValueError):
        resolve_manifest_path(root, "../outside.txt")


def test_asset_registry_rejects_duplicate_ids_and_delivery_profile_mismatch():
    first = valid_asset()
    second = valid_asset()
    second["path"] = "04_资产库/角色/CHAR_SHENYE_2.png"
    second["profile"] = "DELIVERY_VERTICAL"
    second["width"] = 1920
    second["height"] = 1080
    errors = validate_asset_registry([first, second])
    assert any("duplicate asset_id" in error for error in errors)
    assert any("DELIVERY_VERTICAL" in error for error in errors)


def test_asset_registry_rejects_invalid_machine_id_and_missing_core_field():
    asset = valid_asset("沈夜")
    asset.pop("sha256")
    errors = validate_asset_registry([asset])
    assert any("asset_id" in error for error in errors)
    assert any("sha256" in error for error in errors)


def test_asset_registry_requires_reference_boundary_text():
    asset = valid_asset()
    asset["does_not_control"] = ""
    assert any("does_not_control" in error for error in validate_asset_registry([asset]))


def test_shot_and_prompt_reject_wrong_core_field_types():
    shot = valid_shot()
    shot["narrative_goal"] = 42
    assert any("narrative_goal" in error for error in validate_shot_spec(shot))
    prompt = parse_prompt_metadata(valid_prompt())
    prompt["subjects"] = "CHAR_SHENYE"
    body = valid_prompt().split("```", 2)[-1]
    mutated = "```json\n" + json.dumps(prompt) + "\n```" + body[body.find("\n"):]
    assert any("subjects" in error for error in validate_prompt_markdown(mutated))


def test_nested_reference_bindings_reject_unscoped_fields():
    shot = valid_shot()
    shot["reference_bindings"][0]["rogue"] = True
    assert any("rogue" in error for error in validate_shot_spec(shot))
    metadata = parse_prompt_metadata(valid_prompt())
    metadata["references"][0]["rogue"] = True
    body = valid_prompt().split("```", 2)[-1]
    mutated = "```json\n" + json.dumps(metadata) + "\n```" + body[body.find("\n"):]
    assert any("rogue" in error for error in validate_prompt_markdown(mutated))


def test_shot_spec_accepts_base_contract():
    assert validate_shot_spec(valid_shot()) == []


def test_shot_spec_requires_dialogue_fields_when_dialogue_exists():
    shot = valid_shot()
    shot["dialogue"] = "别回头。"
    errors = validate_shot_spec(shot)
    assert any("voice_id" in error for error in errors)
    assert any("dialogue_route" in error for error in errors)
    assert any("timing_authority" in error for error in errors)


def test_shot_spec_requires_structured_eyeline_for_reverse_angle():
    shot = valid_shot()
    shot["transition_type"] = "reverse_angle"
    errors = validate_shot_spec(shot)
    assert any("eyeline" in error for error in errors)
    assert any("camera_axis" in error for error in errors)


def test_shot_spec_rejects_edit_duration_longer_than_source():
    shot = valid_shot()
    shot["edit_target_duration_seconds"] = 11
    assert any("edit_target_duration_seconds" in error for error in validate_shot_spec(shot))


def test_prompt_metadata_parses_and_validates():
    text = valid_prompt()
    metadata = parse_prompt_metadata(text)
    assert metadata["prompt_id"] == "EP01_SH001_P01"
    assert validate_prompt_markdown(text) == []


def test_prompt_rejects_duplicate_slots_and_unscoped_fields():
    text = valid_prompt()
    metadata = parse_prompt_metadata(text)
    metadata["references"].append(dict(metadata["references"][0]))
    metadata["references"][1]["slot"] = "character"
    metadata["rogue"] = "must fail"
    body = text.split("```", 2)[-1]
    mutated = "```json\n" + json.dumps(metadata) + "\n```" + body[body.find("\n"):]
    errors = validate_prompt_markdown(mutated)
    assert any("duplicate reference slot" in error for error in errors)
    assert any("rogue" in error for error in errors)


def test_state_transition_is_sequential_and_known():
    assert validate_state_transition("DRAFT", "SPEC_RESOLVED") == []
    assert validate_state_transition("DRAFT", "READY_FOR_VIDEO")
    assert validate_state_transition("UNKNOWN", "DRAFT")
    assert len(LIFECYCLE_STATES) == 12


def test_production_state_requires_alignment_and_route_evidence_before_video():
    state = {
        "units": {
            "EP01_SH001_G01": {
                "runtime_status": "READY_FOR_VIDEO",
                "visual_control_state_alignment": "PENDING",
                "provider_route": "minimax-h3",
            }
        }
    }
    errors = validate_production_state(state)
    assert any("alignment" in error for error in errors)
    assert any("evidence" in error for error in errors)


def test_partial_select_requires_range_and_observed_state():
    state = {
        "units": {
            "EP01_SH001_G01": {
                "runtime_status": "SELECT",
                "select_type": "PARTIAL_SELECT",
                "source_in": 1.0,
                "source_out": 0.0,
            }
        }
    }
    errors = validate_production_state(state)
    assert any("source_out" in error for error in errors)
    assert any("observed_state" in error for error in errors)


def test_evidence_rejects_observed_once_as_default_behavior():
    evidence = {
        "evidence_id": "EVID_H3_001",
        "provider": "minimax",
        "provider_surface": "video",
        "provider_version": "2026-01",
        "capability": "I2V_REFERENCE",
        "route": "minimax-h3",
        "result": "PASS",
        "evidence_level": "OBSERVED_ONCE",
        "generation_ids": ["GEN_001"],
        "scope": "single test",
        "observed_at": "2026-09-07T12:00:00Z",
        "review_due": "2026-10-07",
        "default_behavior": True,
    }
    assert any("OBSERVED_ONCE" in error for error in validate_evidence(evidence))


def test_reference_graph_rejects_dangling_edges_and_duplicate_edges():
    graph = {
        "nodes": ["ASSET_001", "SHOT_001", "PROMPT_001"],
        "edges": [
            {"source": "ASSET_001", "target": "SHOT_001", "relation": "asset_to_shot"},
            {"source": "ASSET_001", "target": "SHOT_001", "relation": "asset_to_shot"},
            {"source": "PROMPT_001", "target": "MISSING", "relation": "prompt_to_reference"},
        ],
    }
    errors = validate_reference_graph(graph)
    assert any("duplicate" in error for error in errors)
    assert any("MISSING" in error for error in errors)


def test_state_and_graph_reject_unscoped_fields():
    state = {"units": {}, "rogue": True}
    assert any("rogue" in error for error in validate_production_state(state))
    graph = {"nodes": [], "edges": [], "rogue": True}
    assert any("rogue" in error for error in validate_reference_graph(graph))


def test_golden_fixtures_validate_as_published_contracts():
    fixture = Path(__file__).parent / "fixtures" / "v2" / "golden"
    manifest = json.loads((fixture / "workspace-manifest.v2.json").read_text(encoding="utf-8"))
    assets = json.loads((fixture / "asset-registry.v2.json").read_text(encoding="utf-8"))
    shot = json.loads((fixture / "shot-spec.v2.json").read_text(encoding="utf-8"))
    evidence = json.loads((fixture / "evidence.v2.json").read_text(encoding="utf-8"))
    state = json.loads((fixture / "production-state.v2.json").read_text(encoding="utf-8"))
    graph = json.loads((fixture / "reference-graph.v2.json").read_text(encoding="utf-8"))
    prompt = (fixture / "prompt.v2.md").read_text(encoding="utf-8")
    assert validate_workspace_manifest(manifest) == []
    assert validate_asset_registry(assets) == []
    assert validate_shot_spec(shot) == []
    assert validate_prompt_markdown(prompt) == []
    assert validate_evidence(evidence) == []
    assert validate_production_state(state) == []
    assert validate_reference_graph(graph) == []
