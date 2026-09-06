from __future__ import annotations

import json
from pathlib import Path

from test_v2_cli import run_ff


def test_cli_compile_accepts_visual_control_option(tmp_path: Path):
    source = Path(__file__).parents[1] / "tests/fixtures/v2/visual-control/visual-control-plan.golden.json"
    prompt = tmp_path / "prompt.md"
    prompt.write_text(
        "```json\n" + json.dumps({
            "prompt_id":"EP01_SH001_P01","prompt_type":"I2V","production_unit":"EP01_SH001_G01",
            "visual_fact":"watcher","output_profile":"VIDEO_SOURCE_NATIVE","start_state":"start","end_state":"end",
            "subjects":["CHAR_FIXTURE"],"dominant_action":"turn","camera":"fixed","continuity_locks":["position"],
            "references":[{"slot":"character","asset_id":"CHAR_FIXTURE","role":"identity","controls":"face","does_not_control":"camera"}],
            "forbidden":["extra subject"],"acceptance":["stable identity"]}) + "\n```\n" + "\n".join(f"## {x}\n" for x in ("visual_fact","output_profile","start_state","end_state","subjects","dominant_action","camera","continuity_locks","references","forbidden","acceptance")), encoding="utf-8")
    out = tmp_path / "payload.txt"
    result = run_ff("compile", "--prompt", str(prompt), "--visual-control", str(source), "--provider", "minimax-h3", "--out", str(out), "--format", "json")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["visual_control_id"] == "VC_FIXTURE_001"
    assert out.exists()
