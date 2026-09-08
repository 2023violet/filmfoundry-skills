from __future__ import annotations

import json
from pathlib import Path

from .contracts import validate_workspace_manifest, validate_prompt_markdown
from .visual_control import validate_visual_control
from .report import ValidationReport


def validate_workspace(root: Path, stages: set[str] | None = None) -> ValidationReport:
    stages = stages or {"all"}
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    manifest_path = root / "workspace-manifest.v2.json"
    if not manifest_path.exists():
        errors.append(f"missing workspace manifest: {manifest_path}")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            errors.extend(validate_workspace_manifest(manifest))
            checked.append(manifest_path.relative_to(root).as_posix())
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid workspace manifest: {exc}")
    if "all" in stages or "prompt" in stages:
        for path in sorted(root.rglob("*.md")):
            if "99_归档" in path.parts or path.name.lower() == "readme.md":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "prompt_id" in text and "```json" in text:
                checked.append(path.relative_to(root).as_posix())
                errors.extend(f"{path}: {item}" for item in validate_prompt_markdown(text))
    if "all" in stages or "visual-control" in stages:
        for path in sorted(root.rglob("*.json")):
            if "99_归档" in path.parts or path.name == "workspace-manifest.v2.json":
                continue
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(value, dict) and "visual_control_id" in value:
                report = validate_visual_control(value, source=path.relative_to(root).as_posix())
                checked.append(path.relative_to(root).as_posix())
                errors.extend(issue.message for issue in report.errors)
                warnings.extend(issue.message for issue in report.warnings)
    return ValidationReport.from_messages("workspace", checked, errors, warnings)


__all__ = ["validate_workspace"]
