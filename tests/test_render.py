from __future__ import annotations

import json
from pathlib import Path
import os
import subprocess
import sys

from filmfoundry.creator_read_model import build_creator_read_model
from filmfoundry.creator_sources import discover_creator_sources
from filmfoundry.render import VIEW_NAMES, render_read_model


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "tests" / "fixtures" / "v23" / "creator-read-model" / "smoke-project"


def test_render_smoke_project_writes_all_views_and_stable_manifest(tmp_path: Path):
    model = build_creator_read_model(SMOKE, discover_creator_sources(SMOKE))

    first = render_read_model(model, tmp_path / "first")
    second = render_read_model(model, tmp_path / "second")

    assert tuple(first["views"]) == VIEW_NAMES
    assert first["schema_version"] == "render-manifest.v3"
    assert first["project_id"] == "SMOKE_PROJECT"
    assert first["formats"] == ["html", "markdown", "svg"]
    assert json.dumps(first, ensure_ascii=False, sort_keys=True) == json.dumps(second, ensure_ascii=False, sort_keys=True)
    for view in VIEW_NAMES:
        assert (tmp_path / "first" / f"{view}.html").is_file()
        assert (tmp_path / "first" / f"{view}.md").is_file()
        assert (tmp_path / "first" / f"{view}.svg").is_file()


def test_render_keeps_unknown_distinct_and_rejects_unsafe_media_links(tmp_path: Path):
    model = build_creator_read_model(SMOKE, discover_creator_sources(SMOKE))
    manifest = render_read_model(model, tmp_path / "render")

    overview = (tmp_path / "render" / "overview.html").read_text(encoding="utf-8")
    decision = (tmp_path / "render" / "decision.html").read_text(encoding="utf-8")
    assets = (tmp_path / "render" / "assets.html").read_text(encoding="utf-8")
    assert "UNKNOWN" in overview
    assert "Decision Brief" in decision
    assert "question" in decision
    assert 'href="media/moss-reference.txt"' in assets
    assert "../" not in overview
    assert 'href="../' not in assets
    assert manifest["warnings"] == []


def test_ff_render_uses_generic_smoke_project_and_stable_exit_code(tmp_path: Path):
    output = tmp_path / "cli-render"
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    result = subprocess.run(
        [sys.executable, "-m", "filmfoundry", "render", "--root", str(SMOKE), "--out", str(output), "--format", "json"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["manifest"].endswith("render-manifest.json")
    assert (output / "render-manifest.json").is_file()
