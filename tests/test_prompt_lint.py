import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def test_clean_staged_prompt_passes():
    from prompt_lint import lint_prompt
    prompt = """[LOCKS]\nREF_A controls face identity only; does_not_control wardrobe and background.\n[TIME]\nStage 1: CHAR_A places the folded map on the table. End state: folded map lies centered on the table.\nStage 2: CHAR_A unfolds the map. End state: map is fully open; left hand remains on lower-left corner.\n"""
    assert lint_prompt(prompt) == []


def test_flags_unverifiable_consistency_language():
    from prompt_lint import lint_prompt
    errors = lint_prompt("Keep it consistent and cinematic throughout. 保持人物一致。")
    assert any("unverifiable" in e.lower() for e in errors)


def test_flags_unnamed_reference_without_role_binding():
    from prompt_lint import lint_prompt
    errors = lint_prompt("Use reference image 1 and reference image 2. The man walks forward.")
    assert any("reference role" in e.lower() for e in errors)


def test_stages_require_end_state_signal():
    from prompt_lint import lint_prompt
    errors = lint_prompt("Stage 1: he enters the room.\nStage 2: he opens the box.")
    assert any("end state" in e.lower() for e in errors)


def test_flags_dense_second_level_timing_without_hard_clock_reason():
    from prompt_lint import lint_prompt
    prompt = "0-1s walk; 1-2s turn; 2-3s smile; 3-4s reach; 4-5s open box"
    errors = lint_prompt(prompt)
    assert any("timestamp density" in e.lower() for e in errors)


def test_allows_second_level_when_audio_hard_clock_is_named():
    from prompt_lint import lint_prompt
    prompt = "Lip sync to supplied voiceover. 0-2s enter; 2-4s speak; 4-6s brand reveal. End state: logo reference is centered."
    errors = lint_prompt(prompt)
    assert not any("timestamp density" in e.lower() for e in errors)


def test_flags_keyword_soup():
    from prompt_lint import lint_prompt
    errors = lint_prompt("cinematic, epic, masterpiece, ultra detailed, award winning, stunning, dramatic, beautiful")
    assert any("keyword soup" in e.lower() for e in errors)


def test_cli_returns_one_when_findings_exist(tmp_path):
    path = tmp_path / "prompt.txt"
    path.write_text("Keep it consistent and cinematic.", encoding="utf-8")
    script = SCRIPT_DIR / "prompt_lint.py"
    result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "unverifiable" in result.stdout.lower()


def test_flags_dense_chinese_second_level_timing_without_hard_clock_reason():
    from prompt_lint import lint_prompt
    prompt = "0-1秒走路；1-2秒转身；2-3秒微笑；3-4秒抬手；4-5秒打开盒子"
    errors = lint_prompt(prompt)
    assert any("timestamp density" in e.lower() for e in errors)


def test_flags_ref_pointer_without_explicit_role_binding():
    from prompt_lint import lint_prompt
    errors = lint_prompt("Use REF_A and REF_B. The subject walks toward camera.")
    assert any("reference role" in e.lower() for e in errors)


def test_allows_each_ref_pointer_when_each_has_explicit_role_binding():
    from prompt_lint import lint_prompt
    prompt = "REF_A controls face identity only; does_not_control wardrobe.\nREF_B controls location architecture only; does_not_control people."
    errors = lint_prompt(prompt)
    assert not any("reference role" in e.lower() for e in errors)


def test_flags_obviously_conflicting_multi_move_camera_sequence():
    from prompt_lint import lint_prompt
    prompt = "Camera starts with a slow push-in, then orbits 180 degrees, then rapidly pulls back. Subject remains still."
    errors = lint_prompt(prompt)
    assert any("camera move" in e.lower() or "camera path" in e.lower() for e in errors)


def test_allows_coherent_two_axis_composite_camera_move():
    from prompt_lint import lint_prompt
    prompt = "Camera performs one continuous crane up and pull back, maintaining the same optical axis and subject center."
    errors = lint_prompt(prompt)
    assert not any("camera move" in e.lower() or "camera path" in e.lower() for e in errors)


def test_i2v_route_is_case_insensitive():
    from prompt_lint import lint_prompt
    prompt = "word " * 360
    errors = lint_prompt(prompt, route="I2V")
    assert any("i2v over-description" in e.lower() for e in errors)


def test_ref_pointer_binding_requires_explicit_non_control_boundary():
    from prompt_lint import lint_prompt
    errors = lint_prompt("REF_A controls face identity only. Subject walks forward.")
    assert any("does_not_control" in e.lower() or "boundary" in e.lower() for e in errors)


def test_negated_camera_moves_do_not_create_false_conflict():
    from prompt_lint import lint_prompt
    prompt = "Camera uses one slow push-in. Do not orbit. Do not pan. No pull-back."
    errors = lint_prompt(prompt)
    assert not any("camera move conflict" in e.lower() for e in errors)
