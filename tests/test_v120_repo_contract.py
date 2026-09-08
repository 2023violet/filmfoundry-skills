import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"


def test_v120_metadata_and_skill_market_first_contract():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert 'version = "3.0.0"' in pyproject
    assert "**Version:** 3.0.0" in readme
    for token in ("Content Market Gate", "MVP", "PARTIAL_SELECT", "edit target", "eyeline"):
        assert token.lower() in skill.lower(), token


def test_v120_published_references_scripts_and_templates_exist():
    for rel in (
        "references/20-content-market-gate.md",
        "references/21-market-mvp.md",
        "references/22-ai-native-content-design.md",
        "references/23-controllability-budget.md",
        "scripts/validate_content_market_gate.py",
        "scripts/validate_selects_log.py",
        "templates/content-market-gate.example.json",
        "templates/content-market-gate.md",
        "templates/market-mvp-report.md",
        "templates/production-state-partial-select.example.json",
    ):
        assert (SKILL / rel).is_file(), rel


def test_v120_published_examples_pass_new_validators():
    cases = [
        ("validate_content_market_gate.py", "content-market-gate.example.json"),
        ("validate_shot_spec.py", "shot-spec.example.json"),
        ("validate_selects_log.py", "selects-log.csv"),
        ("validate_model_profile.py", "model-profile.example.json"),
        ("validate_project_runtime.py", "project-runtime.example.json"),
    ]
    for script, artifact in cases:
        result = subprocess.run(
            [sys.executable, str(SKILL / "scripts" / script), str(SKILL / "templates" / artifact)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"{script}: {result.stdout}{result.stderr}"


def test_v120_eval_suite_has_26_cases_and_new_market_production_risks():
    data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    assert data["version"] == "3.0.0"
    assert len(data["evals"]) == 26
    ids = {case["id"] for case in data["evals"]}
    for prefix in (
        "E19-content-market-gate",
        "E20-cheapest-mvp-before-production",
        "E21-monetization-missing-traffic-only",
        "E22-partial-select-salvage",
        "E23-controllability-over-timing",
        "E24-eyeline-critical-keyframe",
        "E25-observed-once-not-default",
        "E26-thirty-episode-engine",
    ):
        assert prefix in ids


def test_v120_human_templates_expose_market_duration_eyeline_and_selection_contracts():
    shot_card = (SKILL / "templates" / "shot-card.md").read_text(encoding="utf-8").lower()
    for token in ("generation duration", "edit target duration", "eyeline critical", "partial_select"):
        assert token in shot_card, token
    bible = (SKILL / "templates" / "production-bible.md").read_text(encoding="utf-8").lower()
    assert "content market gate" in bible
    brief = (SKILL / "templates" / "creative-brief.md").read_text(encoding="utf-8").lower()
    assert "market gate" in brief
    header = (SKILL / "templates" / "generation-log.csv").read_text(encoding="utf-8").splitlines()[0]
    for field in ("generation_duration_seconds", "edit_target_duration_seconds", "selection_disposition"):
        assert field in header
