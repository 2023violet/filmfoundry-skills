"""Conservative, archive-aware v1 to v2 migration planning."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def plan_migration(root: Path, source: str = "1.x") -> dict[str, Any]:
    root = root.resolve()
    if not root.exists():
        return {
            "ok": False,
            "source": source,
            "root": str(root),
            "dry_run": True,
            "changes": [],
            "archive_files": [],
            "errors": [f"root does not exist: {root}"],
        }
    records: list[dict[str, Any]] = []
    archive_files: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if "99_归档" in path.parts or "99_archive" in path.parts or path.name.lower() == "99_archive":
            archive_files.append(rel)
        else:
            records.append(
                {
                    "path": rel,
                    "size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    return {
        "ok": True,
        "source": source,
        "root": str(root),
        "dry_run": True,
        "changes": [],
        "records": records,
        "archive_files": archive_files,
        "errors": [],
    }


__all__ = ["plan_migration"]
