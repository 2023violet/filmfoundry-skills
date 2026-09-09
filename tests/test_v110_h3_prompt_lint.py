import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

SECTIONS = [
    "REFERENCE BINDING",
    "GLOBAL SHOT",
    "LOCKS",
    "CAMERA",
    "ACTION STAGES + END STATES",
    "ACTING",
    "PHYSICS / PERSISTENCE",
    "AUDIO",
    "FAILURE CONSTRAINTS",
]


def prompt_with(body_by_section=None):
    body_by_section = body_by_section or {}
    chunks = []
    for section in SECTIONS:
        body = body_by_section.get(section, "none")
        chunks.append(f"【{section}】\n{body}")
    return "\n\n".join(chunks)


def test_h3_lint_requires_all_nine_sections():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with().replace("【AUDIO】\nnone\n\n", "")
    errors = lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED")
    assert any("AUDIO" in e for e in errors)


def test_h3_r1_is_blocked_without_verified_role_binding_evidence():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({"REFERENCE BINDING": "@图1 controls identity only; does_not_control background."})
    errors = lint_h3_prompt(text, adapter_mode="R1", role_binding_status="UNVERIFIED")
    assert any("role binding" in e.lower() and "verified" in e.lower() for e in errors)


def test_h3_r3_rejects_multiple_visual_reference_pointers():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({"REFERENCE BINDING": "@图1 primary visual. @图2 identity."})
    errors = lint_h3_prompt(text, adapter_mode="R3", role_binding_status="UNVERIFIED")
    assert any("r3" in e.lower() and "reference" in e.lower() for e in errors)


def test_h3_lint_rejects_dual_duration_execution_plans():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({"ACTION STAGES + END STATES": "If 6 seconds: 0-2s hold. If 10 seconds: 0-3s hold. FINAL END STATE: stable."})
    errors = lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED")
    assert any("duration" in e.lower() for e in errors)


def test_h3_lint_requires_final_end_state_for_stage_timing():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({"ACTION STAGES + END STATES": "STAGE 1: move slowly. END STATE: subject stops."})
    errors = lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED")
    assert any("final end state" in e.lower() for e in errors)


def test_h3_lint_accepts_complete_r2_environment_prompt():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({
        "REFERENCE BINDING": "@图1 is the primary visual reference.",
        "GLOBAL SHOT": "One continuous establishing shot. Dominant action: camera slowly advances.",
        "LOCKS": "Character count: 0. Geography remains fixed.",
        "CAMERA": "One slow forward push. Do not orbit. Do not pan.",
        "ACTION STAGES + END STATES": "STAGE 1: mist drifts. END STATE: geography stable. FINAL END STATE: camera settled.",
        "ACTING": "none",
        "PHYSICS / PERSISTENCE": "River path and buildings remain fixed.",
        "AUDIO": "Dialogue: none. Generated music: none. Light wind ambience.",
        "FAILURE CONSTRAINTS": "No cuts. No terrain morphing. No subtitle.",
    })
    assert lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED") == []


def test_h3_lint_rejects_chinese_dual_duration_execution_plans():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({"ACTION STAGES + END STATES": "如果是 6 秒镜头：0–2 秒建立。如果平台固定生成 10 秒：0–3 秒建立。FINAL END STATE: stable."})
    errors = lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED")
    assert any("duration" in e.lower() for e in errors)


def test_h3_lint_accepts_hard_timing_section_as_stage_section_alternative():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({
        "REFERENCE BINDING": "@图1 is primary visual.",
        "GLOBAL SHOT": "One dialogue shot. Dominant action: speaker delivers one line.",
        "LOCKS": "Character count: 1.",
        "CAMERA": "Fixed camera.",
        "ACTION STAGES + END STATES": "placeholder"
    }).replace("【ACTION STAGES + END STATES】\nplaceholder", "【TIMING】\n0-3s: deliver supplied line. FINAL END STATE: speaker holds final gaze.")
    errors = lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED")
    assert not any("ACTION STAGES" in e for e in errors), errors


def test_h3_lint_includes_generic_camera_conflict_checks():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({
        "REFERENCE BINDING": "@图1 is primary visual.",
        "GLOBAL SHOT": "One continuous shot. Dominant action: subject stays still.",
        "LOCKS": "Character count: 1.",
        "CAMERA": "Camera slowly pushes in, then orbits around the subject, then pulls back.",
        "ACTION STAGES + END STATES": "STAGE 1: subject remains still. END STATE: subject still. FINAL END STATE: subject still.",
        "ACTING": "neutral",
        "PHYSICS / PERSISTENCE": "identity remains stable",
        "AUDIO": "Dialogue: none. Generated music: none.",
        "FAILURE CONSTRAINTS": "No cuts.",
    })
    errors = lint_h3_prompt(text, adapter_mode="R2", role_binding_status="UNVERIFIED")
    assert any("camera move" in e.lower() for e in errors), errors


def test_h3_r1_requires_explicit_role_and_boundary_for_each_visual_pointer():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({
        "REFERENCE BINDING": "@图1 primary. @图2 secondary.",
        "GLOBAL SHOT": "One establishing shot. Dominant action: slow push.",
        "LOCKS": "Character count: 0.",
        "CAMERA": "One slow push-in.",
        "ACTION STAGES + END STATES": "STAGE 1: move. END STATE: stable. FINAL END STATE: settled.",
        "ACTING": "none", "PHYSICS / PERSISTENCE": "geography fixed",
        "AUDIO": "Dialogue: none. Generated music: none.", "FAILURE CONSTRAINTS": "No cuts."
    })
    errors = lint_h3_prompt(text, adapter_mode="R1", role_binding_status="REPEATED")
    assert any("@图1" in e or "@图2" in e for e in errors), errors


def test_h3_r1_accepts_explicit_role_and_boundary_for_each_pointer_when_evidenced():
    from h3_prompt_lint import lint_h3_prompt
    text = prompt_with({
        "REFERENCE BINDING": "@图1 controls composition only; does_not_control motion.\n@图2 controls geography only; does_not_control composition.",
        "GLOBAL SHOT": "One establishing shot. Dominant action: slow push.",
        "LOCKS": "Character count: 0.", "CAMERA": "One slow push-in. Do not orbit. Do not pan.",
        "ACTION STAGES + END STATES": "STAGE 1: move. END STATE: stable. FINAL END STATE: settled.",
        "ACTING": "none", "PHYSICS / PERSISTENCE": "geography fixed",
        "AUDIO": "Dialogue: none. Generated music: none.", "FAILURE CONSTRAINTS": "No cuts."
    })
    errors = lint_h3_prompt(text, adapter_mode="R1", role_binding_status="REPEATED")
    assert errors == [], errors
