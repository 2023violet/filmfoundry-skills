from __future__ import annotations
import json
from pathlib import Path
from filmfoundry_v2 import compile_canonical

def prompt(path: Path) -> None:
    path.write_text("```json\n" + json.dumps({"prompt_id":"PROMPT_CTX","prompt_type":"I2V","production_unit":"UNIT_CTX","visual_fact":"A watcher waits.","output_profile":"VIDEO_SOURCE_NATIVE","start_state":"dark","end_state":"lit","subjects":["CHAR_A"],"dominant_action":"waits","camera":"locked","continuity_locks":["identity"],"references":[{"slot":"character","asset_id":"CHAR_A","role":"identity","controls":"face","does_not_control":"camera"}],"forbidden":["extra people"],"acceptance":["stable face"]}) + "\n```\n\n" + "\n".join(f"## {x}\n\nvalue" for x in ("visual_fact","output_profile","start_state","end_state","subjects","dominant_action","camera","continuity_locks","references","forbidden","acceptance")), encoding="utf-8")

def analysis(): return {"schema_version":"script-analysis.v2","script_analysis_id":"SCRIPT_CTX","source_script":{"path":"script.md","sha256":"a"*64},"facts":[],"unresolved_questions":[],"review_status":"REVIEWED"}
def test_compile_context_is_ordered_hashed_and_read_only(tmp_path: Path):
    p=tmp_path/"prompt.md"; prompt(p); a=tmp_path/"analysis.json"; a.write_text(json.dumps(analysis()),encoding="utf-8"); before=p.read_bytes()
    compiled=compile_canonical(p,"provider",{"route":"I2V","snapshot_id":"CAP_CTX","parameters":{}},context_paths={"script_analysis":a},production_ledger_event_ids=("EVENT_001",))
    assert compiled.input_hashes["script_analysis"] and compiled.production_ledger_event_ids == ("EVENT_001",)
    assert "[script_analysis]" in compiled.body and p.read_bytes()==before
