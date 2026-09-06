#!/usr/bin/env python3
"""Compute a reproducible SHA-256 digest for a FilmFoundry asset file."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    target = Path(path)
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: hash_asset.py <asset-file>")
        return 2
    target = Path(argv[1])
    if not target.is_file():
        print(f"ERROR: not a file: {target}")
        return 2
    print(f"{sha256_file(target)}  {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
