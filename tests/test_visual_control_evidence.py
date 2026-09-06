from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_visual_control_evidence_register_preserves_baselines_and_boundaries():
    path = ROOT / "docs" / "evidence" / "visual-control-evidence-register.v2.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["baseline"]["v1_tests"] == 167
    assert data["baseline"]["v2_tests"] == 199
    assert data["baseline"]["wucheng"] == {
        "registry_assets": 75,
        "active_media": 109,
        "prompts": 21,
        "routed_units": 19,
        "h3_real_outputs": 0,
    }
    assert any(item["source_id"] == "HF_SKILLS" and item["revision"] == "fb18134" for item in data["sources"])
    assert all(item["status"] in {"CONTRACTED", "HUMAN_REVIEW", "UNVERIFIED"} for item in data["practices"])
