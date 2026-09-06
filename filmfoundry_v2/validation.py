from __future__ import annotations

import json
from pathlib import Path

from .contracts import validate_workspace_manifest, validate_prompt_markdown
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
    return ValidationReport.from_messages("workspace", checked, errors, warnings)


__all__ = ["validate_workspace"]
