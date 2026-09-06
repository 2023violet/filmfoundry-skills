from __future__ import annotations

import json
from pathlib import Path

from filmfoundry_v2 import compile_canonical


def _prompt(path: Path) -> None:
    metadata = {
        "prompt_id": "EP01_SH001_P01", "prompt_type": "I2V", "production_unit": "EP01_SH001_G01",
        "visual_fact": "A watcher holds position at an inn entrance.", "output_profile": "VIDEO_SOURCE_NATIVE",
        "start_state": "Lantern dark.", "end_state": "Lantern remains dark.", "subjects": ["CHAR_WATCHER"],
        "dominant_action": "One restrained turn.", "camera": "Fixed camera.", "continuity_locks": ["position"],
        "references": [{"slot": "character", "asset_id": "CHAR_WATCHER", "role": "identity", "controls": "face", "does_not_control": "camera"}],
        "forbidden": ["extra subjects"], "acceptance": ["stable identity"],
    }
    sections = ["visual_fact", "output_profile", "start_state", "end_state", "subjects", "dominant_action", "camera", "continuity_locks", "references", "forbidden", "acceptance"]
    path.write_text("```json\n" + json.dumps(metadata) + "\n```\n\n" + "\n".join(f"## {x}\n\ncontent" for x in sections), encoding="utf-8")


def test_visual_control_is_hashed_and_compiled_without_mutating_sources(tmp_path: Path):
    prompt = tmp_path / "prompt.md"
    control = tmp_path / "control.json"
    _prompt(prompt)
    control.write_text((Path(__file__).parents[1] / "skills/generative-film-production/templates/visual-control-plan.example.json").read_text(encoding="utf-8"), encoding="utf-8")
    before_prompt, before_control = prompt.read_bytes(), control.read_bytes()
    payload = compile_canonical(prompt, "minimax-h3", {"route": "FIRST_FRAME", "snapshot_id": "H3_SNAPSHOT_001", "parameters": {}}, control)
    assert payload.visual_control_id == "EP01_SH001_VC"
    assert payload.visual_control_hash
    assert payload.input_hashes["prompt"]
    assert "[spatial_map]" in payload.body
    assert prompt.read_bytes() == before_prompt
    assert control.read_bytes() == before_control
