from __future__ import annotations

import json

from filmfoundry import (
    EmotionalBeatMap,
    ScriptAnalysis,
    parse_emotional_beat_map,
    parse_script_analysis,
    production_requirement_facts,
    validate_emotional_beat_map,
    validate_script_analysis,
)


def valid_analysis() -> dict:
    return {
        "schema_version": "script-analysis.v3",
        "script_analysis_id": "SCRIPT_EP01_ANALYSIS",
        "source_script": {"path": "02_story/EP01.md", "sha256": "a" * 64},
        "facts": [
            {
                "fact_id": "FACT_EP01_LANGUAGE",
                "category": "LANGUAGE",
                "value": "Mandarin Chinese",
                "source_span": "lines 8-10",
                "evidence_level": "EXPLICIT_SCRIPT_FACT",
                "confidence": 1.0,
                "confirmed_by": None,
                "status": "ACTIVE",
            }
        ],
        "unresolved_questions": [],
        "review_status": "REVIEWED",
    }


def valid_beat_map() -> dict:
    beat = {
        "beat_id": "BEAT_EP01_01",
        "sequence": 1,
        "narrative_function": "HOOK",
        "primary_emotion": "unease",
        "tension_level": 4,
        "direction": "RISING",
        "turning_point": False,
        "rationale": "The watcher hears a voice before seeing its source.",
        "music_state": "LOW_DRONE",
        "silence_required": False,
        "dialogue_density": "LOW",
        "timing_authority": "EDIT_TIMELINE",
        "review_status": "REVIEWED",
    }
    return {
        "schema_version": "emotional-beat-map.v3",
        "beat_map_id": "BEATMAP_EP01",
        "production_unit": "EP01",
        "beats": [beat, {**beat, "beat_id": "BEAT_EP01_02", "sequence": 2, "turning_point": True}],
        "review_status": "REVIEWED",
    }


def test_script_analysis_parses_sourced_facts_and_rejects_unknown_fields():
    payload = valid_analysis()
    analysis = parse_script_analysis(json.dumps(payload))
    assert isinstance(analysis, ScriptAnalysis)
    assert analysis.source_hash == "a" * 64
    assert validate_script_analysis(analysis).ok

    payload["facts"][0]["unsupported"] = True
    report = validate_script_analysis(payload)
    assert not report.ok
    assert any(issue.code == "UNKNOWN_FIELD" for issue in report.errors)


def test_inferred_fact_cannot_be_promoted_to_canon_without_creator_confirmation():
    payload = valid_analysis()
    payload["facts"][0].update({"evidence_level": "INFERRED", "status": "CANON", "confirmed_by": None})
    report = validate_script_analysis(payload)
    assert not report.ok
    assert any(issue.code == "UNCONFIRMED_CANON_FACT" for issue in report.errors)


def test_emotional_map_treats_tension_and_music_as_reviewed_creator_intent():
    beat_map = parse_emotional_beat_map(valid_beat_map())
    assert isinstance(beat_map, EmotionalBeatMap)
    assert validate_emotional_beat_map(beat_map).ok

    payload = valid_beat_map()
    payload["beats"][0]["tension_level"] = 11
    payload["beats"][0]["music_state"] = ""
    report = validate_emotional_beat_map(payload)
    assert {issue.code for issue in report.errors} >= {"INVALID_TENSION", "REQUIRED_FIELD"}


def test_requirement_facts_trigger_beat_map_for_multi_beat_dialogue_or_music():
    facts = production_requirement_facts(valid_analysis(), valid_beat_map())
    assert facts["has_multiple_beats"] is True
    assert facts["has_dialogue_or_voice"] is True
    assert facts["has_music"] is True
    assert facts["requires_emotional_beat_map"] is True


def test_parsers_reject_non_object_documents():
    for parser in (parse_script_analysis, parse_emotional_beat_map):
        try:
            parser("[]")
        except ValueError as exc:
            assert "top-level object" in str(exc)
        else:
            raise AssertionError("parser accepted a non-object document")
