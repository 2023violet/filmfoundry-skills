from __future__ import annotations

import json
from pathlib import Path

import pytest

from filmfoundry import (
    parse_dependency_graph,
    parse_emotional_beat_map,
    parse_look_bible,
    parse_scene_topology,
    parse_script_analysis,
    validate_dependency_graph,
    validate_emotional_beat_map,
    validate_location_coverage,
    validate_look_bible,
    validate_scene_topology,
    validate_script_analysis,
)
from filmfoundry.creator_sources import _PARSERS


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("filename", "expected_id"),
    [
        ("workspace-manifest", "workspace-manifest.v3.json"),
        ("asset-registry", "asset-registry.v3.json"),
        ("production-state", "production-state.v3.json"),
        ("shot-spec", "shot-spec.v3.json"),
        ("asset-dependency-graph", "asset-dependency-graph.v3.json"),
        ("emotional-beat-map", "emotional-beat-map.v3.json"),
        ("location-coverage-set", "location-coverage-set.v3.json"),
        ("look-bible", "look-bible.v3.json"),
        ("scene-topology", "scene-topology.v3.json"),
        ("script-analysis", "script-analysis.v3.json"),
        ("production-ledger", "production-ledger.v3.json"),
        ("production-policy", "production-policy.v3.json"),
        ("prompt", "prompt.v3.json"),
    ],
)
def test_active_schema_files_are_v3(filename: str, expected_id: str):
    assert (ROOT / "schemas" / expected_id).is_file()
    assert not (ROOT / "schemas" / expected_id.replace(".v3.", ".v2.")).is_file()


def test_parser_registry_is_v3_only_for_production_artifacts():
    expected = {
        ("workspace-manifest-json", "workspace-manifest.v3"),
        ("asset-registry-json", "asset-registry.v3"),
        ("production-state-json", "production-state.v3"),
        ("shot-spec-json", "shot-spec.v3"),
        ("dependency-graph-json", "asset-dependency-graph.v3"),
        ("emotional-beat-map-json", "emotional-beat-map.v3"),
    }
    assert expected <= set(_PARSERS)
    assert not any(version.endswith(".v2") for _, version in _PARSERS)


def test_v2_structured_context_is_rejected_as_invalid():
    look = {"schema_version": "look-bible.v2"}
    assert any(issue.code == "INVALID_SCHEMA_VERSION" for issue in validate_look_bible(look).errors)
    script = {"schema_version": "script-analysis.v2"}
    assert any(issue.code == "INVALID_SCHEMA_VERSION" for issue in validate_script_analysis(script).errors)


def test_v3_structured_context_is_accepted_when_other_fields_are_valid():
    look = {
        "schema_version": "look-bible.v3", "look_id": "LOOK_MAIN", "scope": "project",
        "reference_sources": [], "composition_language": "clean", "camera_behavior": "steady",
        "palette": ["blue"], "contrast": "high", "saturation": "normal",
        "color_temperature": "neutral", "light_direction": "front", "light_quality": "soft",
        "weather": "clear", "skin_tone_protection": "preserve", "does_not_control": "story",
        "review_status": "REVIEWED",
    }
    assert validate_look_bible(parse_look_bible(look)).ok
