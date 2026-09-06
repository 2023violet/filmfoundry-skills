import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
SCRIPTS = SKILL / "scripts"
TEMPLATES = SKILL / "templates"


def _with_bom(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text, encoding="utf-8-sig")


def test_asset_registry_cli_accepts_utf8_bom(tmp_path):
    target = tmp_path / "asset-registry.csv"
    shutil.copy2(TEMPLATES / "asset-registry.example.csv", target)
    _with_bom(target)
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_asset_registry.py"), str(target)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_project_runtime_accepts_bom_asset_registry(tmp_path):
    for source in TEMPLATES.iterdir():
        if source.is_file():
            shutil.copy2(source, tmp_path / source.name)
    _with_bom(tmp_path / "asset-registry.example.csv")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_project_runtime.py"), str(tmp_path / "project-runtime.example.json")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
