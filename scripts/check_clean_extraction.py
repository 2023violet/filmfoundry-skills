"""Verify the v3 wheel and skill archive in a clean temporary directory."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    args = parser.parse_args()
    args.wheel = args.wheel.resolve()
    args.archive = args.archive.resolve()
    with tempfile.TemporaryDirectory(prefix="filmfoundry-v3-clean-") as temporary:
        root = Path(temporary)
        extracted = root / "skill"
        with zipfile.ZipFile(args.archive) as archive:
            members = archive.namelist()
            forbidden_members = (
                ".git/",
                ".pytest_cache/",
                "__pycache__/",
                "filmfoundry_v2",
                "filmfoundry-v2",
                "wucheng",
                "雾城",
            )
            if any(
                any(token in member.lower() for token in forbidden_members if token.isascii())
                or any(token in member for token in forbidden_members if not token.isascii())
                for member in members
            ):
                print("archive boundary violation: legacy or Wucheng member present", file=sys.stderr)
                return 1
            archive.extractall(extracted)
        assert (extracted / "filmfoundry-skills-v3.0.0" / "skills" / "generative-film-production" / "SKILL.md").is_file()
        install = root / "install"
        install.mkdir()
        installed = run([sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(install), str(args.wheel)], cwd=root, env=dict(os.environ))
        if installed.returncode:
            print(installed.stdout)
            print(installed.stderr, file=sys.stderr)
            return installed.returncode
        env = dict(os.environ)
        env["PYTHONPATH"] = str(install)
        workspace = root / "workspace"
        checks: list[tuple[str, list[str]]] = [
            ("help", [sys.executable, "-m", "filmfoundry", "--help"]),
            ("init", [sys.executable, "-m", "filmfoundry", "init", "--root", str(workspace), "--format", "json"]),
            ("validate", [sys.executable, "-m", "filmfoundry", "validate", "--root", str(workspace), "--format", "json"]),
            ("route", [sys.executable, "-m", "filmfoundry", "route", "--request", "给我三个 hook", "--format", "json"]),
        ]
        for name, command in checks:
            result = run(command, cwd=root, env=env)
            if result.returncode:
                print(f"{name} failed:\n{result.stdout}\n{result.stderr}", file=sys.stderr)
                return result.returncode
        legacy_migration = run(
            [
                sys.executable,
                "-m",
                "filmfoundry",
                "migrate",
                "--root",
                str(workspace),
                "--from",
                "1.x",
                "--dry-run",
                "--format",
                "json",
            ],
            cwd=root,
            env=env,
        )
        if legacy_migration.returncode == 0:
            print("legacy migration command unexpectedly exists", file=sys.stderr)
            return 1
        runtime = workspace / "runtime" / "sources"
        runtime.mkdir(parents=True)
        (workspace / "runtime" / "project-runtime.json").write_text(json.dumps({"schema_version": "project-runtime.v1", "project_id": "PROJECT", "phase": "creative"}) + "\n", encoding="utf-8")
        (workspace / "narrative-index.v1.json").write_text(json.dumps({"schema_version": "narrative-index.v1", "nodes": [{"node_id": "STORY", "node_type": "SEASON", "display_name": "Generic Smoke", "narrative_responsibility": "smoke", "parent_id": None, "canon_source": "README.md"}]}) + "\n", encoding="utf-8")
        (runtime / "asset-registry.v3.json").write_text("[]\n", encoding="utf-8")
        (runtime / "production-state.v3.json").write_text(json.dumps({"schema_version": "3.0.0", "units": {}}) + "\n", encoding="utf-8")
        (workspace / "creator-source-catalog.v1.json").write_text(json.dumps({
            "schema_version": "creator-source-catalog.v1", "project_id": "PROJECT", "runtime_path": "runtime/project-runtime.json",
            "sources": [
                {"source_id": "SRC_WORKSPACE", "source_kind": "workspace_manifest", "path": "workspace-manifest.v3.json", "path_base": "WORKSPACE_ROOT", "parser_id": "workspace-manifest-json", "schema_version": "workspace-manifest.v3", "authority_role": "CURRENT", "scope": "project", "required": True},
                {"source_id": "SRC_STORY", "source_kind": "narrative_index", "path": "narrative-index.v1.json", "path_base": "WORKSPACE_ROOT", "parser_id": "narrative-index-json", "schema_version": "narrative-index.v1", "authority_role": "CURRENT", "scope": "STORY", "required": True},
                {"source_id": "SRC_ASSETS", "source_kind": "asset_registry", "path": "sources/asset-registry.v3.json", "path_base": "RUNTIME_DIR", "parser_id": "asset-registry-json", "schema_version": "asset-registry.v3", "authority_role": "CURRENT", "scope": "project", "required": True},
                {"source_id": "SRC_STATE", "source_kind": "production_state", "path": "sources/production-state.v3.json", "path_base": "RUNTIME_DIR", "parser_id": "production-state-json", "schema_version": "production-state.v3", "authority_role": "CURRENT", "scope": "project", "required": True},
            ],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        render = run([sys.executable, "-m", "filmfoundry", "render", "--root", str(workspace), "--out", str(root / "render"), "--format", "json"], cwd=root, env=env)
        if render.returncode:
            print(f"render failed:\n{render.stdout}\n{render.stderr}", file=sys.stderr)
            return render.returncode
        assert json.loads((root / "render" / "render-manifest.json").read_text(encoding="utf-8"))["schema_version"] == "render-manifest.v2"
        route = json.loads(run(checks[-1][1], cwd=root, env=env).stdout)
        assert route["mode"] == "CREATIVE"
        probe = run([sys.executable, "-c", "import filmfoundry; print(filmfoundry.__version__)"] , cwd=root, env=env)
        assert probe.returncode == 0 and probe.stdout.strip() == "3.0.0"
        isolated_env = {"PYTHONPATH": str(install), "SystemRoot": os.environ.get("SystemRoot", "")}
        legacy = run([sys.executable, "-S", "-c", "import filmfoundry_v2"], cwd=root, env=isolated_env)
        assert legacy.returncode != 0
        print(json.dumps({"ok": True, "workspace": str(workspace), "archive": str(args.archive), "wheel": str(args.wheel)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
