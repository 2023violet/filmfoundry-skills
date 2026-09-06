from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_ff(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    repo = str(Path(__file__).resolve().parents[1])
    env["PYTHONPATH"] = repo + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "filmfoundry_v2", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        env=env,
    )


def test_help_and_init_are_available_from_any_cwd(tmp_path: Path):
    result = run_ff("--help", cwd=tmp_path)
    assert result.returncode == 0
    assert "validate" in result.stdout

    root = tmp_path / "workspace"
    result = run_ff("init", "--root", str(root), cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    manifest = root / "workspace-manifest.v2.json"
    assert manifest.exists()
    assert json.loads(manifest.read_text(encoding="utf-8"))["workspace_version"] == "2.0.0"


def test_validate_supports_json_format_and_nonzero_on_invalid_manifest(tmp_path: Path):
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "workspace-manifest.v2.json").write_text(json.dumps({"workspace_version": "2.0.0"}), encoding="utf-8")
    result = run_ff("validate", "--root", str(root), "--format", "json")
    assert result.returncode != 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["errors"]


def test_compile_prompt_is_provider_neutral_and_read_only(tmp_path: Path):
    prompt = tmp_path / "shot.md"
    prompt.write_text(
        "```json\n"
        + json.dumps(
            {
                "prompt_id": "EP01_SH001_P01",
                "prompt_type": "I2V",
                "production_unit": "EP01_SH001_G01",
                "visual_fact": "Watcher at inn entrance.",
                "output_profile": "VIDEO_SOURCE_NATIVE",
                "start_state": "Lantern dark.",
                "end_state": "Lantern lit.",
                "subjects": ["CHAR_SHENYE"],
                "dominant_action": "Turns once.",
                "camera": "One slow push in.",
                "continuity_locks": ["wardrobe"],
                "references": [
                    {
                        "slot": "character",
                        "asset_id": "CHAR_SHENYE",
                        "role": "identity",
                        "controls": "face",
                        "does_not_control": "camera",
                    }
                ],
                "forbidden": ["extra characters"],
                "acceptance": ["stable identity"],
            },
            ensure_ascii=False,
        )
        + "\n```\n\n"
        + "\n".join(
            f"## {field}\n\ncontent" for field in (
                "visual_fact", "output_profile", "start_state", "end_state", "subjects",
                "dominant_action", "camera", "continuity_locks", "references", "forbidden", "acceptance",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    out = tmp_path / "payload.txt"
    before = prompt.read_bytes()
    result = run_ff("compile", "--prompt", str(prompt), "--provider", "example-provider", "--out", str(out))
    assert result.returncode == 0, result.stderr
    assert out.exists()
    payload = out.read_text(encoding="utf-8")
    assert "EP01_SH001_P01" in payload
    assert "example-provider" in payload
    assert prompt.read_bytes() == before


def test_audit_hashes_and_migrate_dry_run_are_safe(tmp_path: Path):
    root = tmp_path / "workspace"
    root.mkdir()
    (root / "99_归档").mkdir()
    (root / "99_归档" / "keep.txt").write_text("immutable", encoding="utf-8")
    result = run_ff("audit", "--root", str(root), "--kind", "hashes", "--format", "json")
    assert result.returncode == 0
    assert json.loads(result.stdout)["ok"] is True

    result = run_ff("migrate", "--root", str(root), "--from", "1.x", "--dry-run", "--format", "json")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert (root / "99_归档" / "keep.txt").read_text(encoding="utf-8") == "immutable"
