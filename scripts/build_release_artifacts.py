"""Build deterministic FilmFoundry v3 RC artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
INCLUDE_ROOTS = ("filmfoundry", "skills", "schemas", "docs", "evals", "scripts")
INCLUDE_FILES = ("README.md", "CHANGELOG.md", "LICENSE", "pyproject.toml")
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__", ".dist", "build", "dist"}


def is_active_path(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    if relative in {
        "docs/filmfoundry-v2.md",
        "docs/filmfoundry-v2-support-matrix.md",
    }:
        return False
    if relative.startswith("docs/superpowers/"):
        return False
    if relative.startswith("docs/reports/"):
        return False
    if relative in {"docs/ai-video-production-guide-v2.2.md"}:
        return False
    if relative.startswith("docs/reports/") and ("-v1" in relative or "-v2" in relative):
        return False
    if relative.startswith("docs/evidence/") and ".v2." in relative:
        return False
    return True


def files_for_archive() -> list[Path]:
    paths: list[Path] = []
    for relative in INCLUDE_FILES:
        path = ROOT / relative
        if path.is_file():
            paths.append(path)
    for relative_root in INCLUDE_ROOTS:
        root = ROOT / relative_root
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and is_active_path(path) and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT).parts):
                paths.append(path)
    return sorted(set(paths), key=lambda path: path.relative_to(ROOT).as_posix())


def build_archive(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / "filmfoundry-skills-v3.0.0.zip"
    entries = files_for_archive()
    checksums = {
        path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in entries
    }
    manifest = {
        "artifact": "filmfoundry-skills-v3.0.0.zip",
        "version": "3.0.0",
        "top_level": "filmfoundry-skills-v3.0.0/",
        "file_count": len(entries) + 1,
        "files": checksums,
        "exclusions": [".git", ".pytest_cache", "__pycache__", "build", "dist", "internal reports and superpowers history", "historical v1/v2 docs and evidence", "Wucheng-specific fixtures and adapters"],
    }
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in entries:
            relative = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(f"filmfoundry-skills-v3.0.0/{relative}")
            info.date_time = (1980, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
        info = zipfile.ZipInfo("filmfoundry-skills-v3.0.0/release-manifest.json")
        info.date_time = (1980, 1, 1, 0, 0, 0)
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / ".dist")
    args = parser.parse_args()
    archive = build_archive(args.out.resolve())
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
