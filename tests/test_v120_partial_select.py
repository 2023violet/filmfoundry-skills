import csv
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def partial_row():
    return {
        "shot_id": "SH001",
        "select_id": "SH001_E01_SELECT",
        "generation_id": "GEN001",
        "filename": "SH001.mp4",
        "in_handle": "",
        "out_handle": "",
        "notes": "late scene reset excluded",
        "disposition": "PARTIAL_SELECT",
        "source_in_seconds": "0",
        "source_out_seconds": "5",
        "source_duration_seconds": "10.125",
        "selected_duration_seconds": "5"
    }


def test_partial_select_accepts_valid_contiguous_range():
    from validate_selects_log import validate_select_rows
    assert validate_select_rows([partial_row()]) == []


def test_partial_select_rejects_invalid_or_out_of_source_range():
    from validate_selects_log import validate_select_rows
    row = partial_row()
    row["source_out_seconds"] = "11"
    errors = validate_select_rows([row])
    assert any("source_out_seconds" in e and "source duration" in e.lower() for e in errors)
    row = partial_row()
    row["source_in_seconds"] = "6"
    row["source_out_seconds"] = "5"
    errors = validate_select_rows([row])
    assert any("greater than" in e.lower() for e in errors)


def test_partial_select_selected_duration_must_match_range():
    from validate_selects_log import validate_select_rows
    row = partial_row()
    row["selected_duration_seconds"] = "4.5"
    errors = validate_select_rows([row])
    assert any("selected_duration_seconds" in e for e in errors)


def test_full_select_with_timing_must_cover_whole_source():
    from validate_selects_log import validate_select_rows
    row = partial_row()
    row["disposition"] = "FULL_SELECT"
    errors = validate_select_rows([row])
    assert any("FULL_SELECT" in e for e in errors)


def base_state(selection):
    return {
        "units": {
            "SH001_G01": {
                "runtime_status": "SELECT",
                "spec_version": 1,
                "asset_registry_version": 1,
                "model_profile_version": 1,
                "keyframe": {"file": "kf.png", "qc": "PASS", "sha256": "a" * 64},
                "video": {"generation_id": "GEN001", "selected": selection},
                "observed_state_written": False
            }
        }
    }


def test_production_state_accepts_partial_select_selection_object():
    from validate_production_state import validate_production_state
    selection = {
        "file": "SH001.mp4",
        "disposition": "PARTIAL_SELECT",
        "source_duration_seconds": 10.125,
        "in_seconds": 0.0,
        "out_seconds": 5.0
    }
    assert validate_production_state(base_state(selection)) == []


def test_production_state_partial_select_requires_valid_range():
    from validate_production_state import validate_production_state
    selection = {"file": "SH001.mp4", "disposition": "PARTIAL_SELECT", "source_duration_seconds": 10.0, "in_seconds": 5.0, "out_seconds": 5.0}
    errors = validate_production_state(base_state(selection))
    assert any("video.selected" in e and "range" in e.lower() for e in errors)
