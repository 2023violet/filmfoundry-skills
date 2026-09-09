import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
SCRIPT_DIR = SKILL / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def test_published_runtime_example_passes_full_runtime_validator():
    script = SCRIPT_DIR / "validate_project_runtime.py"
    manifest = SKILL / "templates" / "project-runtime.example.json"
    result = subprocess.run([sys.executable, str(script), str(manifest)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS" in result.stdout


def test_project_runtime_blocks_ready_for_video_when_model_profile_is_unverified(tmp_path):
    from validate_project_runtime import validate_project_runtime

    # Use published runtime and mutate only the runtime status in memory.
    manifest_path = SKILL / "templates" / "project-runtime.example.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = validate_project_runtime(manifest, base_dir=manifest_path.parent)
    assert errors == []

    state_path = SKILL / "templates" / manifest["production_state"]
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["units"]["SH001_G01"]["runtime_status"] = "READY_FOR_VIDEO"
    state["units"]["SH001_G01"]["keyframe"] = {"file": "kf.png", "sha256": "a" * 64, "qc": "PASS"}
    temp_state = tmp_path / "state.json"
    temp_state.write_text(json.dumps(state), encoding="utf-8")
    manifest2 = dict(manifest)
    manifest2["production_state"] = str(temp_state)
    errors = validate_project_runtime(manifest2, base_dir=manifest_path.parent)
    assert any("model profile" in e.lower() and "minimum" in e.lower() for e in errors)


def test_v11_project_runtime_rejects_legacy_asset_registry_without_version_hash_columns(tmp_path):
    from validate_project_runtime import validate_project_runtime
    manifest_path = SKILL / "templates" / "project-runtime.example.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    legacy = tmp_path / "legacy.csv"
    legacy.write_text(
        "asset_id,asset_type,canonical_descriptor,state_variant,parent_asset_id,reference_id,reference_role,does_not_control\n"
        "LOC_A,location,hall,CANON,,REF_A,architecture,people\n",
        encoding="utf-8",
    )
    manifest["asset_registry"] = str(legacy)
    errors = validate_project_runtime(manifest, base_dir=manifest_path.parent)
    assert any("v1.1" in e and "asset" in e.lower() for e in errors), errors


def test_project_runtime_allows_ready_for_video_with_scoped_route_pilot_pass(tmp_path):
    from validate_project_runtime import validate_project_runtime

    template_dir = SKILL / "templates"
    manifest = json.loads((template_dir / "project-runtime.example.json").read_text(encoding="utf-8"))
    state = json.loads((template_dir / manifest["production_state"]).read_text(encoding="utf-8"))
    state["units"]["SH001_G01"]["runtime_status"] = "READY_FOR_VIDEO"
    state["units"]["SH001_G01"]["keyframe"] = {"file": "kf.png", "sha256": "a" * 64, "qc": "PASS"}
    state["units"]["SH001_G01"]["provider_route_gate"] = "I2V_IDENTITY_MICROMOTION"

    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    route_path = tmp_path / "routes.json"
    route_path.write_text(
        json.dumps({
            "routes": {
                "I2V_IDENTITY_MICROMOTION": {
                    "release_status": "PILOT_PASS",
                    "evidence_ids": ["GEN_TEST_001"],
                }
            }
        }),
        encoding="utf-8",
    )
    manifest["production_state"] = str(state_path)
    manifest["model_route_registry"] = str(route_path)

    errors = validate_project_runtime(manifest, base_dir=template_dir)
    assert not any("model evidence" in e.lower() or "model profile minimum" in e.lower() for e in errors), errors


def test_project_runtime_rejects_ready_for_video_when_scoped_route_is_unverified(tmp_path):
    from validate_project_runtime import validate_project_runtime

    template_dir = SKILL / "templates"
    manifest = json.loads((template_dir / "project-runtime.example.json").read_text(encoding="utf-8"))
    state = json.loads((template_dir / manifest["production_state"]).read_text(encoding="utf-8"))
    state["units"]["SH001_G01"]["runtime_status"] = "READY_FOR_VIDEO"
    state["units"]["SH001_G01"]["keyframe"] = {"file": "kf.png", "sha256": "a" * 64, "qc": "PASS"}
    state["units"]["SH001_G01"]["provider_route_gate"] = "I2V_IDENTITY_MICROMOTION"

    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    route_path = tmp_path / "routes.json"
    route_path.write_text(
        json.dumps({"routes": {"I2V_IDENTITY_MICROMOTION": {"release_status": "BLOCKED"}}}),
        encoding="utf-8",
    )
    manifest["production_state"] = str(state_path)
    manifest["model_route_registry"] = str(route_path)

    errors = validate_project_runtime(manifest, base_dir=template_dir)
    assert any("route gate" in e.lower() and "blocked" in e.lower() for e in errors), errors
