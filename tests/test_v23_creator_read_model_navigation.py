"""Focused RED/GREEN contracts for Creator navigation and terminology."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path

import pytest

import filmfoundry_v2


ROOT = Path(__file__).resolve().parents[1]
SMOKE_PROJECT = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "smoke-project"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def collect_snapshot():
    catalog = filmfoundry_v2.discover_creator_sources(SMOKE_PROJECT)
    return catalog, filmfoundry_v2.collect_creator_snapshot(SMOKE_PROJECT, catalog)


def test_terminology_registry_is_versioned_and_uses_english_fallback_for_unknown_language():
    registry = filmfoundry_v2.CreatorTerminologyRegistry()

    assert registry.schema_version == "creator-terminology.v1"
    assert registry.label("lifecycle", "DRAFT", language="zh-CN") == "草稿"
    assert registry.label("lifecycle", "DRAFT", language="en") == "Draft"
    assert registry.label("lifecycle", "DRAFT", language="fr") == "Draft"


def test_terminology_registry_keeps_unknown_enum_raw_with_explicit_no_explanation():
    registry = filmfoundry_v2.CreatorTerminologyRegistry()

    unknown_zh = registry.label("lifecycle", "FUTURE_STATE", language="zh-CN")
    unknown_en = registry.label("lifecycle", "FUTURE_STATE", language="en")

    assert "FUTURE_STATE" in unknown_zh
    assert "无解释" in unknown_zh
    assert unknown_en == "FUTURE_STATE (no explanation)"


def test_navigation_is_derived_from_action_free_snapshot_and_read_model_composes_both():
    catalog, snapshot = collect_snapshot()

    navigation = filmfoundry_v2.derive_creator_navigation(snapshot)
    model = filmfoundry_v2.build_creator_read_model(SMOKE_PROJECT, catalog)

    assert not hasattr(snapshot, "actions")
    assert not hasattr(snapshot, "navigation")
    assert navigation == model.navigation
    assert model.snapshot == snapshot
    assert not hasattr(navigation, "snapshot")


def test_navigation_returns_one_primary_and_all_same_priority_parallel_actions_in_stable_order():
    _, snapshot = collect_snapshot()
    ref = snapshot.assets[0].provenance.source_refs[0]
    provenance = filmfoundry_v2.CreatorProvenance((ref,), "VALIDATED", "test.rule")
    blockers = (
        filmfoundry_v2.CreatorBlocker(
            "BLOCKER_Z", "ERROR", "ENTITY_Z", "test.z", "z reason", "test boundary", provenance
        ),
        filmfoundry_v2.CreatorBlocker(
            "BLOCKER_A", "ERROR", "ENTITY_A", "test.a", "a reason", "test boundary", provenance
        ),
    )
    snapshot = replace(snapshot, blockers=blockers)

    navigation = filmfoundry_v2.derive_creator_navigation(snapshot)

    assert [action.action_id for action in navigation.actions[:2]] == ["BLOCKER_BLOCKER_A", "BLOCKER_BLOCKER_Z"]
    assert navigation.primary_action == navigation.actions[0]
    assert [action.action_id for action in navigation.parallel_actions] == ["BLOCKER_BLOCKER_Z"]
    assert all(action.priority == navigation.primary_action.priority for action in navigation.same_priority_actions)
    for action in navigation.actions:
        assert action.rule_id
        assert action.prerequisites
        assert action.support_boundary
        assert action.provenance.source_refs
        assert action.provenance.rule_id == action.rule_id


def test_navigation_prioritizes_source_conflicts_before_hard_blockers_and_lifecycle_advice():
    _, snapshot = collect_snapshot()
    ref = snapshot.assets[0].provenance.source_refs[0]
    provenance = filmfoundry_v2.CreatorProvenance((ref,), "VALIDATED", "test.rule")
    conflict = filmfoundry_v2.CreatorConflict(
        "AUTHORITY_MISMATCH", "AUTHORITY_MISMATCH", None, "authority differs", provenance
    )
    blocker = filmfoundry_v2.CreatorBlocker(
        "BLOCKER_HARD", "ERROR", "ENTITY_HARD", "test.hard", "hard reason", "test boundary", provenance
    )
    snapshot = replace(snapshot, conflicts=(conflict,), blockers=(blocker,))

    navigation = filmfoundry_v2.derive_creator_navigation(snapshot)

    assert navigation.actions[0].priority == 1
    assert navigation.actions[0].action_id == "CONFLICT_AUTHORITY_MISMATCH"
    assert any(action.priority == 2 for action in navigation.actions)
    assert any(action.priority == 5 for action in navigation.actions)


def test_navigation_reports_missing_observed_state_before_lifecycle_progression():
    _, snapshot = collect_snapshot()
    shot = snapshot.shots[0]
    selected = replace(shot, runtime_status="SELECT", observed_state=None)
    snapshot = replace(snapshot, shots=(selected, *snapshot.shots[1:]))

    navigation = filmfoundry_v2.derive_creator_navigation(snapshot)

    observed = next(action for action in navigation.actions if action.entity_id == selected.shot_id)
    assert observed.priority == 4
    assert observed.rule_id == "creator.navigation.previous_observed_state"
    assert "Observed State" in observed.reason


def test_navigation_treats_hash_mismatch_as_integrity_priority():
    _, snapshot = collect_snapshot()
    asset = replace(snapshot.assets[0], observed_readiness="PRESENT_HASH_MISMATCH")
    snapshot = replace(snapshot, assets=(asset, *snapshot.assets[1:]))

    navigation = filmfoundry_v2.derive_creator_navigation(snapshot)

    integrity = next(action for action in navigation.actions if action.entity_id == asset.asset_id)
    assert integrity.priority == 2
    assert integrity.severity == "ERROR"
    assert integrity.rule_id == "creator.navigation.asset.integrity"


def test_hard_blocker_severity_precedes_observed_state_rule_heuristic():
    _, snapshot = collect_snapshot()
    ref = snapshot.assets[0].provenance.source_refs[0]
    provenance = filmfoundry_v2.CreatorProvenance((ref,), "VALIDATED", "test.rule")
    blocker = filmfoundry_v2.CreatorBlocker(
        "BLOCKER_STATE", "CRITICAL", "ENTITY_STATE", "creator.navigation.previous_observed_state",
        "critical state blocker", "BLOCKER_REVIEW", provenance,
    )

    navigation = filmfoundry_v2.derive_creator_navigation(replace(snapshot, blockers=(blocker,)))

    action = next(action for action in navigation.actions if action.action_id == "BLOCKER_BLOCKER_STATE")
    assert action.priority == 2


def test_continuity_edge_before_select_does_not_require_observed_state():
    _, snapshot = collect_snapshot()
    predecessor = next(shot for shot in snapshot.shots if shot.shot_id == "EP01_SH002")
    predecessor = replace(predecessor, runtime_status="DRAFT", observed_state=None)
    shots = tuple(predecessor if shot.shot_id == predecessor.shot_id else shot for shot in snapshot.shots)

    navigation = filmfoundry_v2.derive_creator_navigation(replace(snapshot, shots=shots))

    assert not any(action.action_id == "OBSERVED_STATE_EP01_SH002_BEFORE_EP02_SH002" for action in navigation.actions)


def test_continuity_edge_with_selected_predecessor_requires_observed_state_handoff():
    _, snapshot = collect_snapshot()
    predecessor = next(shot for shot in snapshot.shots if shot.shot_id == "EP01_SH002")
    predecessor = replace(predecessor, runtime_status="SELECT", observed_state=None)
    shots = tuple(predecessor if shot.shot_id == predecessor.shot_id else shot for shot in snapshot.shots)

    navigation = filmfoundry_v2.derive_creator_navigation(replace(snapshot, shots=shots))

    action = next(action for action in navigation.actions if action.action_id == "OBSERVED_STATE_EP01_SH002_BEFORE_EP02_SH002")
    assert action.priority == 4
    assert action.rule_id == "creator.navigation.previous_observed_state"


def test_derived_action_rejects_empty_provenance_with_contract_error():
    _, snapshot = collect_snapshot()
    empty_provenance = filmfoundry_v2.CreatorProvenance((), "VALIDATED", "test.rule")
    blocker = filmfoundry_v2.CreatorBlocker(
        "BLOCKER_EMPTY_PROVENANCE", "ERROR", "ENTITY_EMPTY", "test.rule", "missing provenance", "BLOCKER_REVIEW", empty_provenance,
    )

    with pytest.raises(ValueError, match="CREATOR_NAVIGATION_PROVENANCE: derived action requires non-empty provenance"):
        filmfoundry_v2.derive_creator_navigation(replace(snapshot, blockers=(blocker,)))


def test_terminology_registry_is_deeply_immutable():
    registry = filmfoundry_v2.CreatorTerminologyRegistry()

    with pytest.raises(TypeError):
        registry.registry["lifecycle"]["DRAFT"]["en"] = "Changed"


def test_action_support_boundaries_resolve_in_registry_in_both_languages():
    _, snapshot = collect_snapshot()
    navigation = filmfoundry_v2.derive_creator_navigation(snapshot)
    registry = filmfoundry_v2.TERMINOLOGY_REGISTRY

    for action in navigation.actions:
        assert action.support_boundary in registry.registry["support_boundary"]
        assert "无解释" not in registry.label("support_boundary", action.support_boundary, language="zh-CN")
        assert "no explanation" not in registry.label("support_boundary", action.support_boundary, language="en")


def test_navigation_and_read_model_have_versioned_schemas_and_round_trip():
    navigation_schema = read_json(ROOT / "schemas" / "creator-navigation.v1.json")
    read_model_schema = read_json(ROOT / "schemas" / "creator-read-model.v1.json")
    assert navigation_schema["$id"] == "creator-navigation.v1"
    assert read_model_schema["$id"] == "creator-read-model.v1"
    assert set(navigation_schema["properties"]) == {"actions", "primary_action", "parallel_actions", "terminology_version", "schema_version"}
    assert set(read_model_schema["properties"]) == {"snapshot", "navigation", "schema_version"}

    catalog, snapshot = collect_snapshot()
    model = filmfoundry_v2.build_creator_read_model(SMOKE_PROJECT, catalog)
    assert json.loads(model.navigation.to_json()) == model.navigation.to_dict()
    assert json.loads(model.to_json()) == model.to_dict()
    assert model.snapshot == snapshot
