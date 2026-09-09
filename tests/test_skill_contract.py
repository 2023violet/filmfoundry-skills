from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "generative-film-production"
SKILL = SKILL_DIR / "SKILL.md"

REQUIRED_REFERENCES = [
    "references/00-production-philosophy.md",
    "references/01-creative-brief.md",
    "references/02-story-breakdown.md",
    "references/03-reference-board.md",
    "references/04-asset-passport.md",
    "references/05-asset-stress-test.md",
    "references/06-shot-engineering.md",
    "references/07-continuity-engine.md",
    "references/08-video-spec.md",
    "references/09-prompt-compiler.md",
    "references/10-generation-loop.md",
    "references/11-editing.md",
    "references/12-audio.md",
    "references/13-qc.md",
    "references/14-failure-recovery.md",
]

REQUIRED_ADAPTERS = [
    "references/adapters/generic-t2v.md",
    "references/adapters/generic-i2v.md",
    "references/adapters/first-last-frame.md",
    "references/adapters/multi-reference-video.md",
    "references/adapters/storyboard-to-video.md",
    "references/adapters/seedance.md",
    "references/adapters/minimax-h3.md",
    "references/adapters/veo.md",
    "references/adapters/kling.md",
    "references/adapters/image-generation.md",
]

REQUIRED_TEMPLATES = [
    "templates/creative-brief.md",
    "templates/production-bible.md",
    "templates/asset-passport.md",
    "templates/shot-card.md",
    "templates/generation-log.csv",
    "templates/selects-log.csv",
    "templates/qc-report.md",
]


def test_root_skill_exists_and_has_valid_frontmatter():
    text = SKILL.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert re.search(r"(?m)^name: generative-film-production$", text)
    description = re.search(r"(?m)^description:\s*(.+)$", text)
    assert description, "description frontmatter is required"
    assert description.group(1).startswith("Use when")
    assert len(description.group(1)) < 500


def test_root_skill_stays_compact_and_routes_by_stage():
    lines = SKILL.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 500
    text = "\n".join(lines)
    for token in [
        "Creative Mode",
        "Commit Mode",
        "Production Mode",
        "Gate Mode",
        "Creative Brief",
        "Asset Passport",
        "Canonical Shot Spec",
        "Continuity",
        "Model Adapter",
        "QC",
    ]:
        assert token in text


def test_root_skill_routes_lightweight_creative_work_without_gate_escalation():
    text = SKILL.read_text(encoding="utf-8")
    assert "does not run full Runtime, media, provider, or index validation" in text
    assert "CREATIVE_DRAFT" in text
    assert "HARD_CANON_CONFLICT" in text
    assert "references/40-work-modes.md" in text


def test_mode_reference_exists():
    assert (SKILL_DIR / "references/40-work-modes.md").is_file()


def test_progressive_disclosure_files_exist():
    for rel in REQUIRED_REFERENCES + REQUIRED_ADAPTERS + REQUIRED_TEMPLATES:
        path = SKILL_DIR / rel
        assert path.is_file(), f"missing {rel}"


def test_skill_has_no_placeholders_or_project_specific_legacy_terms():
    text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in SKILL_DIR.rglob("*.md")
    )
    for forbidden in ["TBD", "TODO", "上司警道府"]:
        assert forbidden not in text


def test_skill_states_core_invariants():
    text = SKILL.read_text(encoding="utf-8")
    invariants = [
        "Spec before prompt",
        "one dominant action",
        "observable end state",
        "single-variable retry",
        "Selects",
    ]
    for invariant in invariants:
        assert invariant.lower() in text.lower()


def test_model_specific_adapters_do_not_claim_unverified_capabilities():
    for rel in [
        "references/adapters/seedance.md",
        "references/adapters/minimax-h3.md",
        "references/adapters/veo.md",
        "references/adapters/kling.md",
    ]:
        text = (SKILL_DIR / rel).read_text(encoding="utf-8").lower()
        assert "confirm" in text or "profile" in text or "verified" in text
        assert "canonical" in text


def test_reference_role_guidance_names_positive_and_negative_boundaries():
    for rel in [
        "references/03-reference-board.md",
        "references/adapters/multi-reference-video.md",
    ]:
        text = (SKILL_DIR / rel).read_text(encoding="utf-8")
        assert "controls" in text
        assert "does_not_control" in text
