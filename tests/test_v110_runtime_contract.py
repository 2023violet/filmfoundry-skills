import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
SCRIPT_DIR = SKILL / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def test_v110_release_history_is_preserved_under_current_metadata():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "**Version:** 1.3.3" in readme
    assert 'version = "1.3.3"' in pyproject
    assert "## 1.1.0" in changelog


def test_runtime_references_and_templates_exist():
    expected = [
        "references/15-runtime-contract.md",
        "references/16-model-evidence.md",
        "references/17-keyframe-engineering.md",
        "references/18-voice-passport.md",
        "references/19-adaptive-spec.md",
        "templates/project-runtime.example.json",
        "templates/production-state.example.json",
        "templates/axis-registry.example.json",
        "templates/voice-registry.example.json",
        "templates/dependency-graph.example.json",
        "templates/model-profile.example.json",
    ]
    for rel in expected:
        assert (SKILL / rel).is_file(), rel


def test_runtime_scripts_exist():
    expected = [
        "validate_axis_registry.py",
        "validate_voice_registry.py",
        "validate_model_profile.py",
        "validate_production_state.py",
        "validate_dependencies.py",
        "validate_project_runtime.py",
        "validate_state_transition.py",
        "h3_prompt_lint.py",
        "keyframe_prompt_lint.py",
    ]
    for name in expected:
        assert (SCRIPT_DIR / name).is_file(), name


def test_production_state_accepts_valid_lifecycle_and_rejects_missing_select_artifact():
    from validate_production_state import validate_production_state

    good = {
        "units": {
            "SH001_G01": {
                "design_status": "SPEC_RESOLVED",
                "runtime_status": "SELECT",
                "spec_version": 2,
                "asset_registry_version": 1,
                "model_profile_version": 1,
                "keyframe": {"file": "SH001_KF.png", "sha256": "a" * 64, "qc": "PASS"},
                "video": {"generation_id": "GEN001", "selected": "SH001_E01_SELECT.mp4"},
                "observed_state_written": False,
            }
        }
    }
    assert validate_production_state(good) == []

    bad = json.loads(json.dumps(good))
    bad["units"]["SH001_G01"]["video"]["selected"] = ""
    errors = validate_production_state(bad)
    assert any("selected" in e.lower() for e in errors)


def test_state_transition_rejects_skipping_gates():
    from validate_state_transition import validate_state_transition

    assert validate_state_transition("DRAFT", "SPEC_RESOLVED") == []
    errors = validate_state_transition("DRAFT", "READY_FOR_VIDEO")
    assert any("illegal" in e.lower() or "transition" in e.lower() for e in errors)


def test_axis_registry_requires_unique_ids_and_reciprocal_screen_sides():
    from validate_axis_registry import validate_axis_registry

    data = {
        "axes": [
            {
                "axis_id": "AXIS_DIALOGUE_01",
                "location_id": "LOC_HALL",
                "subject_a": "CHAR_A",
                "subject_b": "CHAR_B",
                "screen_side": {"CHAR_A": "right", "CHAR_B": "left"},
                "eyeline": {"CHAR_A": "left", "CHAR_B": "right"},
                "crossing_allowed": False,
                "status": "LOCKED",
            }
        ]
    }
    assert validate_axis_registry(data) == []

    bad = json.loads(json.dumps(data))
    bad["axes"][0]["screen_side"]["CHAR_B"] = "right"
    errors = validate_axis_registry(bad)
    assert any("screen_side" in e.lower() for e in errors)


def test_voice_registry_locked_voice_requires_measured_rate_and_reference():
    from validate_voice_registry import validate_voice_registry

    good = {
        "voices": [
            {
                "voice_id": "VOICE_A",
                "character_id": "CHAR_A",
                "provider": "provider-x",
                "voice_model": "voice-v1",
                "voice_reference": "voice_a.wav",
                "speech_rate": {"neutral": 3.0, "reflective": 2.4},
                "status": "LOCKED",
            }
        ]
    }
    assert validate_voice_registry(good) == []
    bad = json.loads(json.dumps(good))
    bad["voices"][0]["voice_reference"] = ""
    bad["voices"][0]["speech_rate"] = {}
    errors = validate_voice_registry(bad)
    assert any("voice_reference" in e for e in errors)
    assert any("speech_rate" in e for e in errors)


def test_model_profile_minimum_pass_requires_all_h3_smoke_tests_decided():
    from validate_model_profile import validate_model_profile

    tests = [
        {"test_id": f"TEST_H3_{i:02d}", "verdict": "VERIFIED", "attempts": 2, "passes": 2, "fails": 0}
        for i in range(1, 11)
    ]
    data = {
        "model_id": "minimax-h3",
        "provider": "MiniMax",
        "product_surface": "example",
        "model_version": "observed-version",
        "tested_date": "2026-09-01",
        "verification_status": "MODEL_PROFILE_MINIMUM_PASS",
        "reference_role_binding": {"status": "REPEATED", "evidence_ids": ["TEST_H3_10"]},
        "prompt_language_strategy": {"instruction_language": "mixed", "dialogue_language": "zh"},
        "smoke_tests": tests,
    }
    assert validate_model_profile(data) == []
    bad = json.loads(json.dumps(data))
    bad["smoke_tests"][9]["verdict"] = "UNVERIFIED"
    errors = validate_model_profile(bad)
    assert any("TEST_H3_10" in e or "smoke" in e.lower() for e in errors)


def test_dependency_validator_blocks_unsatisfied_hard_unit_state_dependency():
    from validate_dependencies import validate_dependencies

    graph = {
        "units": {
            "SH002_G01": {
                "hard": [
                    {"type": "unit_state", "id": "SH001_G01", "at_least": "OBSERVED_STATE_RECORDED"}
                ],
                "soft": [],
            }
        }
    }
    state = {
        "units": {
            "SH001_G01": {"runtime_status": "VIDEO_QC_PASS"},
            "SH002_G01": {"runtime_status": "DRAFT"},
        }
    }
    errors = validate_dependencies(graph, state, assets=set(), axes=set(), voices=set())
    assert any("SH001_G01" in e and "OBSERVED_STATE_RECORDED" in e for e in errors)


def test_skill_routes_runtime_model_evidence_keyframes_and_voice_without_project_specific_leakage():
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8").lower()
    for token in ["runtime", "model evidence", "keyframe", "voice", "adaptive", "evidence before trust"]:
        assert token in skill_text
    all_md = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in SKILL.rglob("*.md"))
    assert "夜郎自大" not in all_md
    assert "YELANG_ZIDA" not in all_md


def test_non_h3_model_profile_minimum_pass_does_not_require_h3_named_smoke_tests():
    from validate_model_profile import validate_model_profile
    data = {
        "model_id": "veo-example",
        "provider": "Provider",
        "product_surface": "surface",
        "model_version": "v1",
        "tested_date": "2026-09-01",
        "verification_status": "MODEL_PROFILE_MINIMUM_PASS",
        "reference_role_binding": {"status": "UNVERIFIED", "evidence_ids": []},
        "prompt_language_strategy": {"instruction_language": "en", "dialogue_language": "en"},
        "smoke_tests": [
            {"test_id": "TEST_MODEL_01", "verdict": "VERIFIED", "attempts": 1, "passes": 1, "fails": 0}
        ],
    }
    assert validate_model_profile(data) == []


def test_asset_hash_helper_exists_and_computes_real_sha256(tmp_path):
    import hashlib
    from hash_asset import sha256_file

    target = tmp_path / "asset.bin"
    target.write_bytes(b"FilmFoundry-v1.1")
    assert sha256_file(target) == hashlib.sha256(target.read_bytes()).hexdigest()


def test_minimax_h3_smoke_test_plan_covers_all_ten_tests_and_ab_role_binding():
    plan = SKILL / "references" / "adapters" / "minimax-h3-smoke-tests.md"
    assert plan.is_file()
    text = plan.read_text(encoding="utf-8")
    for i in range(1, 11):
        assert f"TEST_H3_{i:02d}" in text
    assert "A/B" in text
    assert "Reference Role Binding" in text
    assert "UNVERIFIED" in text
