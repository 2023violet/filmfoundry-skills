import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def gate(decision="MVP_ONLY"):
    return {
        "schema_version": "1.2",
        "gate_mode": "REQUIRED",
        "project_intent": "SERIES_BUSINESS",
        "one_sentence_conflict": "A courier can move after the whole city freezes.",
        "audience": "16-35 short-form suspense viewers",
        "click_reason": "An impossible event is visible immediately.",
        "hook_3s": "Everyone freezes except the courier.",
        "viewer_payoff": "A reveal explains one rule and opens a bigger mystery.",
        "follow_reason": "The same anomaly system escalates each episode.",
        "series_engine_30": "One anomaly per episode plus a serial mystery.",
        "monetization_route": "platform revenue, IP licensing, sponsorship after validation",
        "cheapest_mvp": {
            "format": "45-60s vertical episode",
            "variants": 3,
            "production_limit": "5-8 simple shots, one lead, 1-2 locations"
        },
        "ai_production_fit": "voiceover-led, limited cast, short shots, no complex lip sync",
        "platform_hypothesis": "short-form discovery platform first; long compilation later",
        "decision": decision,
        "mvp_evidence": {
            "status": "NOT_RUN",
            "evidence_ids": [],
            "success_criteria": "project-defined retention/follow/comment thresholds before publish",
            "result_summary": ""
        }
    }


def test_market_gate_accepts_complete_mvp_only_hypothesis():
    from validate_content_market_gate import validate_content_market_gate
    assert validate_content_market_gate(gate()) == []


def test_market_gate_blocks_missing_core_answer():
    from validate_content_market_gate import validate_content_market_gate
    data = gate()
    data["hook_3s"] = ""
    errors = validate_content_market_gate(data)
    assert any("hook_3s" in e for e in errors)


def test_missing_monetization_route_can_only_be_traffic_experiment_or_no_go():
    from validate_content_market_gate import validate_content_market_gate
    data = gate("MVP_ONLY")
    data["monetization_route"] = ""
    errors = validate_content_market_gate(data)
    assert any("monetization_route" in e and "TRAFFIC_EXPERIMENT" in e for e in errors)
    data["decision"] = "TRAFFIC_EXPERIMENT"
    assert validate_content_market_gate(data) == []


def test_production_approved_requires_passed_real_mvp_evidence():
    from validate_content_market_gate import validate_content_market_gate
    data = gate("PRODUCTION_APPROVED")
    errors = validate_content_market_gate(data)
    assert any("mvp_evidence" in e and "PASS" in e for e in errors)
    data["mvp_evidence"] = {
        "status": "PASS",
        "evidence_ids": ["PUB_20260902_A01", "PUB_20260903_A02"],
        "success_criteria": "two of three MVP posts exceed project thresholds",
        "result_summary": "2/3 variants passed the predeclared thresholds"
    }
    assert validate_content_market_gate(data) == []


def test_explicit_market_gate_bypass_requires_reason():
    from validate_content_market_gate import validate_content_market_gate
    data = {"schema_version": "1.2", "gate_mode": "BYPASS", "decision": "BYPASS", "bypass_reason": ""}
    assert any("bypass_reason" in e for e in validate_content_market_gate(data))
    data["bypass_reason"] = "MODEL_CAPABILITY_TEST"
    assert validate_content_market_gate(data) == []


def test_v12_commercial_runtime_requires_market_gate(tmp_path):
    from validate_project_runtime import validate_project_runtime
    manifest_path = ROOT / "skills" / "generative-film-production" / "templates" / "project-runtime.example.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["runtime_version"] = "1.2"
    manifest["project_goal"] = "MONETIZATION"
    manifest.pop("content_market_gate", None)
    errors = validate_project_runtime(manifest, base_dir=manifest_path.parent)
    assert any("content_market_gate" in e for e in errors), errors


def test_v12_runtime_requires_project_goal():
    from validate_project_runtime import validate_project_runtime
    manifest_path = ROOT / "skills" / "generative-film-production" / "templates" / "project-runtime.example.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("project_goal", None)
    errors = validate_project_runtime(manifest, base_dir=manifest_path.parent)
    assert any("project_goal" in e for e in errors), errors


def test_mvp_only_gate_allows_mvp_unit_but_blocks_production_unit(tmp_path):
    from validate_project_runtime import validate_project_runtime
    templates = ROOT / "skills" / "generative-film-production" / "templates"
    manifest = json.loads((templates / "project-runtime.example.json").read_text(encoding="utf-8"))

    gate_data = gate("MVP_ONLY")
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps(gate_data), encoding="utf-8")
    manifest["content_market_gate"] = str(gate_path)

    state = json.loads((templates / "production-state.example.json").read_text(encoding="utf-8"))
    unit = state["units"]["SH001_G01"]
    unit["runtime_status"] = "READY_FOR_KF"
    unit["production_scope"] = "MVP"
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    manifest["production_state"] = str(state_path)
    assert not any("market gate" in e.lower() for e in validate_project_runtime(manifest, base_dir=templates))

    unit["production_scope"] = "PRODUCTION"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    errors = validate_project_runtime(manifest, base_dir=templates)
    assert any("market gate" in e.lower() and "PRODUCTION" in e for e in errors), errors


def test_no_go_gate_blocks_expensive_mvp_generation(tmp_path):
    from validate_project_runtime import validate_project_runtime
    templates = ROOT / "skills" / "generative-film-production" / "templates"
    manifest = json.loads((templates / "project-runtime.example.json").read_text(encoding="utf-8"))
    gate_data = gate("NO_GO")
    gate_path = tmp_path / "gate.json"
    gate_path.write_text(json.dumps(gate_data), encoding="utf-8")
    manifest["content_market_gate"] = str(gate_path)
    state = json.loads((templates / "production-state.example.json").read_text(encoding="utf-8"))
    unit = state["units"]["SH001_G01"]
    unit["runtime_status"] = "READY_FOR_KF"
    unit["production_scope"] = "MVP"
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(state), encoding="utf-8")
    manifest["production_state"] = str(state_path)
    errors = validate_project_runtime(manifest, base_dir=templates)
    assert any("NO_GO" in e for e in errors), errors
