"""Unified ``ff`` command line interface for FilmFoundry v2."""
from __future__ import annotations

import argparse
import hashlib
import json
import csv
import re
from pathlib import Path
from typing import Any

from .compiler import PromptCompilationError, compile_canonical, compile_prompt
from .ledger import evaluate_requirements, production_ledger_report, validate_production_ledger
from . import (
    parse_prompt_metadata,
    validate_asset_registry,
    validate_evidence,
    validate_prompt_markdown,
    validate_production_state,
    validate_reference_graph,
    validate_shot_spec,
    validate_workspace_manifest,
    resolve_manifest_path,
)


def _root(value: str) -> Path:
    return Path(value).expanduser().resolve()


def _path_from_root(root: Path | None, value: str) -> Path:
    path = Path(value).expanduser()
    if root is not None and not path.is_absolute():
        return resolve_manifest_path(root, value)
    return path.resolve()


def _emit(payload: dict[str, Any], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload.get("ok", True):
            print("PASS")
        else:
            print("FAIL")
        for error in payload.get("errors", []):
            print(f"ERROR: {error}")
        for warning in payload.get("warnings", []):
            print(f"WARNING: {warning}")
        for key, value in payload.items():
            if key not in {"ok", "errors"}:
                print(f"{key}: {value}")


def _default_manifest() -> dict[str, Any]:
    return {
        "workspace_version": "2.0.0",
        "project_id": "PROJECT",
        "top_level": {"entry": "00_入口与规则"},
        "authorities": {"human": "markdown", "machine": ["json", "csv"], "media": "registry"},
        "archive_boundary": {"path": "99_归档", "mode": "read_only"},
        "id_policy": {"pattern": "^[A-Z][A-Z0-9_]{2,63}$", "charset": "ASCII"},
        "adapter_compatibility": {"filmfoundry": ">=2.0.0,<3.0.0"},
        "required_tools": ["python>=3.11"],
    }


def _cmd_init(args: argparse.Namespace) -> int:
    root = _root(args.root)
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "workspace-manifest.v2.json"
    if manifest_path.exists() and not args.force:
        _emit({"ok": False, "errors": [f"manifest exists: {manifest_path}"]}, args.format)
        return 1
    manifest_path.write_text(json.dumps(_default_manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _emit({"ok": True, "manifest": str(manifest_path)}, args.format)
    return 0


def _load_manifest(root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = root / "workspace-manifest.v2.json"
    if not path.exists():
        return None, [f"missing workspace manifest: {path}"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"invalid workspace manifest: {exc}"]
    return value, validate_workspace_manifest(value)


def _cmd_validate(args: argparse.Namespace) -> int:
    root = _root(args.root)
    manifest, errors = _load_manifest(root)
    errors = list(errors)
    warnings: list[str] = []
    checked: list[str] = []
    if manifest is not None and args.stage in {"all", "workspace"}:
        checked.append("workspace-manifest.v2.json")
    if manifest is not None and args.stage in {"all", "prompt"}:
        for path in sorted(root.rglob("*.md")):
            if "99_归档" in path.parts or path.name.lower() == "readme.md":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"{path.relative_to(root)}: {exc}")
                continue
            if "```json" in text and '"prompt_id"' in text:
                checked.append(path.relative_to(root).as_posix())
                errors.extend(f"{path.relative_to(root)}: {error}" for error in validate_prompt_markdown(text))
    if manifest is not None and args.stage in {"all", "shot", "runtime", "evidence", "visual-control"}:
        for path in sorted(root.rglob("*.json")):
            if "99_归档" in path.parts or path.name == "workspace-manifest.v2.json":
                continue
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            relative = path.relative_to(root).as_posix()
            if args.stage in {"all", "shot"} and isinstance(value, dict) and "shot_id" in value:
                checked.append(relative)
                errors.extend(f"{relative}: {error}" for error in validate_shot_spec(value))
            if args.stage in {"all", "visual-control"} and isinstance(value, dict) and "visual_control_id" in value:
                from .visual_control import validate_visual_control
                checked.append(relative)
                report = validate_visual_control(value, source=relative)
                errors.extend(f"{relative}: {issue.message}" for issue in report.errors)
                warnings.extend(f"{relative}: {issue.message}" for issue in report.warnings)
            if args.stage in {"all", "runtime"} and isinstance(value, dict) and "units" in value:
                checked.append(relative)
                errors.extend(f"{relative}: {error}" for error in validate_production_state(value))
            if args.stage in {"all", "evidence"} and isinstance(value, dict) and "evidence_id" in value:
                checked.append(relative)
                errors.extend(f"{relative}: {error}" for error in validate_evidence(value))
            if args.stage == "all" and isinstance(value, dict) and "nodes" in value and "edges" in value:
                checked.append(relative)
                errors.extend(f"{relative}: {error}" for error in validate_reference_graph(value))
        if args.stage in {"all", "runtime"}:
            for path in sorted(root.rglob("*.csv")):
                if "99_归档" in path.parts:
                    continue
                try:
                    with path.open("r", encoding="utf-8-sig", newline="") as handle:
                        rows = list(csv.DictReader(handle))
                except (OSError, csv.Error):
                    continue
                if rows and "asset_id" in rows[0]:
                    relative = path.relative_to(root).as_posix()
                    checked.append(relative)
                    errors.extend(f"{relative}: {error}" for error in validate_asset_registry(rows))
    payload = {"ok": not errors, "errors": errors, "warnings": warnings, "root": str(root), "stage": args.stage, "checked": sorted(set(checked))}
    if isinstance(manifest, dict):
        payload["workspace_version"] = manifest.get("workspace_version")
    _emit(payload, args.format)
    return 0 if not errors else 1


def _cmd_index(args: argparse.Namespace) -> int:
    root = _root(args.root)
    if not root.exists():
        _emit({"ok": False, "errors": [f"root does not exist: {root}"]}, args.format)
        return 1
    files = [str(p.relative_to(root).as_posix()) for p in root.rglob("*") if p.is_file() and "99_归档" not in p.parts and p.name != "workspace-index.v2.json"]
    files.sort()
    index_path = root / "workspace-index.v2.json"
    index_path.write_text(json.dumps({"schema_version": "index.v2", "files": files}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _emit({"ok": True, "root": str(root), "files": files, "count": len(files), "index": str(index_path)}, args.format)
    return 0


def _cmd_compile(args: argparse.Namespace) -> int:
    try:
        prompt = _path_from_root(_root(args.root) if args.root else None, args.prompt)
        out = _path_from_root(_root(args.root) if args.root else None, args.out)
        if args.visual_control:
            capability = {"route": args.provider, "snapshot_id": "CLI_UNVERIFIED", "parameters": {}}
            visual_control = _path_from_root(_root(args.root) if args.root else None, args.visual_control)
            compiled = compile_canonical(prompt, args.provider, capability, visual_control)
            payload = compiled.body
        else:
            payload = compile_prompt(prompt, args.provider)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload, encoding="utf-8")
    except (OSError, PromptCompilationError, ValueError) as exc:
        _emit({"ok": False, "errors": [str(exc)]}, args.format)
        return 1
    response = {"ok": True, "out": str(out), "provider": args.provider}
    if args.visual_control:
        response.update({"visual_control_id": compiled.visual_control_id, "visual_control_hash": compiled.visual_control_hash, "input_hashes": compiled.input_hashes})
    _emit(response, args.format)
    return 0


def _cmd_audit(args: argparse.Namespace) -> int:
    root = _root(args.root)
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    if not root.exists():
        errors.append(f"root does not exist: {root}")
    else:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "99_归档" in path.parts:
                continue
            relative = path.relative_to(root).as_posix()
            if args.kind == "media" and path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".mov", ".wav", ".mp3"}:
                continue
            if args.kind == "hashes" or args.kind == "media" or args.kind == "all":
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                records.append({"path": relative, "sha256": digest, "size": path.stat().st_size})
            if args.kind in {"references", "all"} and path.suffix.lower() in {".md", ".json"}:
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                references = re.findall(r"(?:\]\(|\"path\"\s*:\s*\"|path:\s*)([^)\"\s]+)", text)
                for reference in references:
                    try:
                        target = resolve_manifest_path(root, reference)
                    except ValueError:
                        errors.append(f"{relative}: path escapes root: {reference}")
                        continue
                    if not target.exists():
                        errors.append(f"{relative}: broken reference: {reference}")
    _emit({"ok": not errors, "errors": errors, "kind": args.kind, "records": records}, args.format)
    return 0 if not errors else 1


def _cmd_migrate(args: argparse.Namespace) -> int:
    root = _root(args.root)
    try:
        from .migration import plan_migration
    except ImportError:  # pragma: no cover - the adapter is shipped with v2
        payload = {"ok": root.exists(), "source": args.source, "root": str(root), "dry_run": True, "changes": [], "errors": [] if root.exists() else [f"root does not exist: {root}"]}
    else:
        payload = plan_migration(root, source=args.source)
    if args.apply:
        payload["ok"] = False
        payload.setdefault("errors", []).append("migration apply is provided by the project adapter; use --dry-run for the core planner")
    _emit(payload, args.format)
    return 0 if payload.get("ok") else 1


def _load_json_argument(path: str, label: str) -> Any:
    try:
        return json.loads(Path(path).expanduser().resolve().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label}: {exc}") from exc


def _cmd_requirements(args: argparse.Namespace) -> int:
    try:
        policy = _load_json_argument(args.policy, "policy")
        facts = _load_json_argument(args.facts, "facts")
        artifacts = _load_json_argument(args.artifacts, "artifacts")
        report = evaluate_requirements(policy, facts, artifacts)
        payload = report.to_dict()
    except ValueError as exc:
        payload = {"ok": False, "errors": [str(exc)], "warnings": []}
    _emit(payload, args.format)
    return 0 if payload.get("ok") else 1


def _cmd_ledger_validate(args: argparse.Namespace) -> int:
    try:
        ledger = _load_json_argument(args.ledger, "ledger")
        payload = validate_production_ledger(ledger).to_dict()
    except ValueError as exc:
        payload = {"ok": False, "errors": [str(exc)], "warnings": []}
    _emit(payload, args.format)
    return 0 if payload.get("ok") else 1


def _cmd_ledger_report(args: argparse.Namespace) -> int:
    try:
        ledger = _load_json_argument(args.ledger, "ledger")
        payload = production_ledger_report(ledger)
    except ValueError as exc:
        payload = {"ok": False, "errors": [str(exc)], "warnings": []}
    _emit(payload, args.format)
    return 0 if payload.get("ok") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ff", description="FilmFoundry Skills v2 CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a v2 workspace manifest")
    init.add_argument("--root", required=True)
    init.add_argument("--force", action="store_true")
    init.add_argument("--format", choices=("text", "json"), default="text")
    init.set_defaults(func=_cmd_init)

    validate = sub.add_parser("validate", help="validate workspace contracts")
    validate.add_argument("--root", required=True)
    validate.add_argument("--stage", choices=("all", "workspace", "prompt", "shot", "runtime", "evidence", "visual-control"), default="all")
    validate.add_argument("--format", choices=("text", "json"), default="text")
    validate.set_defaults(func=_cmd_validate)

    index = sub.add_parser("index", help="index workspace files")
    index.add_argument("--root", required=True)
    index.add_argument("--format", choices=("text", "json"), default="text")
    index.set_defaults(func=_cmd_index)

    compile_parser = sub.add_parser("compile", help="compile Prompt Markdown for a provider")
    compile_parser.add_argument("--prompt", required=True)
    compile_parser.add_argument("--provider", required=True)
    compile_parser.add_argument("--out", required=True)
    compile_parser.add_argument("--root", required=False)
    compile_parser.add_argument("--visual-control", required=False)
    compile_parser.add_argument("--format", choices=("text", "json"), default="text")
    compile_parser.set_defaults(func=_cmd_compile)

    audit = sub.add_parser("audit", help="audit hashes and references")
    audit.add_argument("--root", required=True)
    audit.add_argument("--kind", choices=("all", "media", "references", "hashes"), default="all")
    audit.add_argument("--format", choices=("text", "json"), default="text")
    audit.set_defaults(func=_cmd_audit)

    migrate = sub.add_parser("migrate", help="plan a v1 migration")
    migrate.add_argument("--root", required=True)
    migrate.add_argument("--from", dest="source", required=True)
    migrate.add_argument("--dry-run", action="store_true")
    migrate.add_argument("--apply", action="store_true")
    migrate.add_argument("--format", choices=("text", "json"), default="text")
    migrate.set_defaults(func=_cmd_migrate)

    requirements = sub.add_parser("requirements", help="evaluate artifact requirements")
    requirements.add_argument("--policy", required=True)
    requirements.add_argument("--facts", required=True)
    requirements.add_argument("--artifacts", required=True)
    requirements.add_argument("--format", choices=("text", "json"), default="text")
    requirements.set_defaults(func=_cmd_requirements)

    ledger = sub.add_parser("ledger", help="validate and report production ledger events")
    ledger_sub = ledger.add_subparsers(dest="ledger_command", required=True)
    ledger_validate = ledger_sub.add_parser("validate", help="validate an append-only production ledger")
    ledger_validate.add_argument("--ledger", required=True)
    ledger_validate.add_argument("--format", choices=("text", "json"), default="text")
    ledger_validate.set_defaults(func=_cmd_ledger_validate)
    ledger_report = ledger_sub.add_parser("report", help="report production ledger status")
    ledger_report.add_argument("--ledger", required=True)
    ledger_report.add_argument("--format", choices=("text", "json"), default="text")
    ledger_report.set_defaults(func=_cmd_ledger_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


__all__ = ["build_parser", "main"]
