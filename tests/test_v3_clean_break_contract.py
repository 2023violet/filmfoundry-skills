from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_ff(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "filmfoundry", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        env=env,
    )


def test_canonical_namespace_reports_v3_version():
    import filmfoundry

    assert filmfoundry.__version__ == "3.0.0"


def test_legacy_namespace_is_not_an_active_package():
    result = subprocess.run(
        [sys.executable, "-c", "import filmfoundry_v2"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={"PYTHONPATH": str(ROOT)},
    )
    assert result.returncode != 0
    assert "ModuleNotFoundError" in result.stderr


def test_legacy_migration_command_is_rejected(tmp_path: Path):
    result = run_ff("migrate", "--root", str(tmp_path), "--from", "1.x", "--dry-run", "--format", "json")
    assert result.returncode != 0
    assert "invalid choice" in result.stderr.lower() or "unrecognized arguments" in result.stderr.lower()


def test_v1_and_v2_workspace_versions_are_rejected(tmp_path: Path):
    import filmfoundry

    base = {
        "project_id": "PROJECT",
        "top_level": {"entry": "入口"},
        "authorities": {"human": "markdown", "machine": ["json", "csv"]},
        "archive_boundary": {"path": "99_archive", "mode": "read_only"},
        "id_policy": {"charset": "ASCII"},
        "adapter_compatibility": {"filmfoundry": ">=3.0.0,<4.0.0"},
        "required_tools": ["python>=3.11"],
    }
    for version in ("1.0.0", "2.0.0"):
        errors = filmfoundry.validate_workspace_manifest({**base, "workspace_version": version})
        assert any("unsupported" in error.lower() for error in errors)


