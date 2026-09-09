from pathlib import Path

import filmfoundry

ROOT = Path(__file__).resolve().parents[1]


def test_readme_uses_public_suite_and_repo_name():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "FilmFoundry Skills" in text
    assert "filmfoundry-skills" in text
    assert "generative-film-production" in text


def test_readme_distinguishes_verified_static_tests_from_pending_agentic_benchmark():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "static" in text and "verified" in text
    assert "agentic" in text and "pending" in text
    assert "fixtures" in text and "not" in text and "benchmark" in text


def test_repo_has_release_metadata_and_ci():
    for rel in ["CHANGELOG.md", "LICENSE", "pyproject.toml", ".github/workflows/test.yml"]:
        assert (ROOT / rel).is_file(), rel


def test_ci_runs_v3_artifact_and_clean_extraction_gates():
    workflow = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
    for token in (
        "python -m pip wheel . --no-deps --no-build-isolation --wheel-dir .dist",
        "python scripts/build_release_artifacts.py --out .dist",
        "python scripts/check_clean_extraction.py",
        "SOURCE_DATE_EPOCH: \"0\"",
        "filmfoundry_skills-3.0.0-py3-none-any.whl",
        "filmfoundry-skills-v3.0.0.zip",
    ):
        assert token in workflow


def test_public_package_version_matches_v30_release_metadata():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert filmfoundry.__version__ == "3.0.0"
    assert 'version = "3.0.0"' in pyproject
    assert "**Version:** 3.0.0" in readme


def test_model_profile_template_exists_and_records_evidence_scope():
    path = ROOT / "skills" / "generative-film-production" / "templates" / "model-profile.md"
    text = path.read_text(encoding="utf-8").lower()
    for token in ["model", "provider", "verified", "strengths", "weaknesses", "reference", "timing", "identity"]:
        assert token in text
