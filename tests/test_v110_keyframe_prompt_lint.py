import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

SECTIONS = [
    "REFERENCE BINDING",
    "SHOT / UNIT",
    "VISUAL STYLE",
    "CHARACTER LOCK",
    "LOCATION LOCK",
    "PROP LOCK",
    "SHOT SIZE + PHYSICAL CAMERA",
    "COMPOSITION",
    "BLOCKING",
    "ACTION MOMENT",
    "ACTING",
    "LIGHTING",
    "CONTINUITY INPUT",
    "MUST PRESERVE",
    "FAILURE CONSTRAINTS",
]


def make_prompt(overrides=None):
    overrides = overrides or {}
    out = []
    for section in SECTIONS:
        body = overrides.get(section, "none")
        out.append(f"【{section}】\n{body}")
    return "\n\n".join(out)


def test_keyframe_lint_requires_all_sections():
    from keyframe_prompt_lint import lint_keyframe_prompt
    text = make_prompt().replace("【BLOCKING】\nnone\n\n", "")
    errors = lint_keyframe_prompt(text)
    assert any("BLOCKING" in e for e in errors)


def test_keyframe_lint_rejects_multi_stage_video_timeline_language():
    from keyframe_prompt_lint import lint_keyframe_prompt
    text = make_prompt({"ACTION MOMENT": "STAGE 1 walks forward. STAGE 2 sits down. 0-3s walking, 3-6s sitting."})
    errors = lint_keyframe_prompt(text)
    assert any("keyframe" in e.lower() and ("timeline" in e.lower() or "sequence" in e.lower()) for e in errors)


def test_keyframe_lint_requires_single_still_action_moment():
    from keyframe_prompt_lint import lint_keyframe_prompt
    text = make_prompt({"ACTION MOMENT": ""})
    errors = lint_keyframe_prompt(text)
    assert any("ACTION MOMENT" in e for e in errors)


def test_keyframe_lint_accepts_complete_still_prompt():
    from keyframe_prompt_lint import lint_keyframe_prompt
    text = make_prompt({
        "REFERENCE BINDING": "REF_STYLE controls visual language; REF_CHAR controls identity.",
        "SHOT / UNIT": "SH001 / SH001_G01",
        "VISUAL STYLE": "restrained historical 3D feature",
        "CHARACTER LOCK": "character count 1; same face",
        "LOCATION LOCK": "same hall geometry",
        "PROP LOCK": "none",
        "SHOT SIZE + PHYSICAL CAMERA": "medium shot, eye level, 50mm relationship",
        "COMPOSITION": "subject on left third",
        "BLOCKING": "subject seated frame left",
        "ACTION MOMENT": "Single still moment: subject has just looked toward the doorway.",
        "ACTING": "subtle curiosity",
        "LIGHTING": "warm side light",
        "CONTINUITY INPUT": "hard cut; preserve wardrobe state",
        "MUST PRESERVE": "face, wardrobe, hall geometry",
        "FAILURE CONSTRAINTS": "no extra people; no text",
    })
    assert lint_keyframe_prompt(text) == []
