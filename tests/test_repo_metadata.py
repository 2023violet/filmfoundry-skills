from pathlib import Path

import filmfoundry_v2

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


def test_public_package_version_matches_v21_release_metadata():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert filmfoundry_v2.__version__ == "2.1.0"
    assert 'version = "2.1.0"' in pyproject
    assert "**Version:** 2.1.0" in readme


def test_model_profile_template_exists_and_records_evidence_scope():
    path = ROOT / "skills" / "generative-film-production" / "templates" / "model-profile.md"
    text = path.read_text(encoding="utf-8").lower()
    for token in ["model", "provider", "verified", "strengths", "weaknesses", "reference", "timing", "identity"]:
        assert token in text
