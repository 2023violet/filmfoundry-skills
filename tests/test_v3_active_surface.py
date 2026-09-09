from pathlib import Path

from scripts.build_release_artifacts import files_for_archive, is_active_path


ROOT = Path(__file__).resolve().parents[1]


def test_active_release_docs_use_v3_names_and_exclude_legacy_v2_paths():
    archived = {path.relative_to(ROOT).as_posix() for path in files_for_archive()}
    assert "docs/filmfoundry-v3.md" in archived
    assert "docs/filmfoundry-v3-support-matrix.md" in archived
    assert "docs/filmfoundry-v2.md" not in archived
    assert "docs/filmfoundry-v2-support-matrix.md" not in archived
    assert not is_active_path(ROOT / "docs" / "filmfoundry-v2.md")
    assert not is_active_path(ROOT / "docs" / "filmfoundry-v2-support-matrix.md")
    assert not any(path.relative_to(ROOT).as_posix().startswith("docs/reports/") for path in files_for_archive())


def test_active_chinese_guide_is_project_neutral():
    guide = (ROOT / "docs" / "ai-video-production-guide-zh.md").read_text(encoding="utf-8")
    assert "雾城项目使用" not in guide
    assert "雾城 H3" not in guide
    assert "雾城当前推荐顺序" not in guide
    assert "<project-adapter>" in guide


def test_clean_extraction_probes_removed_migration_command():
    checker = (ROOT / "scripts" / "check_clean_extraction.py").read_text(encoding="utf-8")
    assert '"migrate"' in checker
    assert "legacy migration command" in checker.lower()
    assert "archive boundary" in checker.lower()
    assert "wucheng" in checker.lower()
