"""Measure local reference loading for FilmFoundry work modes.

This benchmark intentionally excludes model inference, provider calls, and
workspace validation. Its numbers describe progressive reference loading only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from filmfoundry.modes import MODE_COMMIT, MODE_CREATIVE, MODE_GATE, MODE_PRODUCTION, reference_profile


MODES = (MODE_CREATIVE, MODE_COMMIT, MODE_PRODUCTION, MODE_GATE)


def measure(root: Path, mode: str) -> dict[str, object]:
    references = reference_profile(mode)
    started = perf_counter()
    total_bytes = 0
    missing: list[str] = []
    for relative in references:
        path = root / relative
        try:
            total_bytes += len(path.read_bytes())
        except OSError:
            missing.append(relative)
    elapsed_ms = (perf_counter() - started) * 1000
    return {
        "mode": mode,
        "references": len(references),
        "bytes_read": total_bytes,
        "load_ms": round(elapsed_ms, 3),
        "missing_references": missing,
        "runtime_loaded": False,
        "media_audit": False,
        "provider_call": False,
        "source_write": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "skills" / "generative-film-production")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    root = args.root.resolve()
    cold = [measure(root, mode) for mode in MODES]
    warm = [measure(root, mode) for mode in MODES]
    payload = {"root": str(root), "cold": cold, "warm": warm, "scope": "reference loading only"}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for row in cold:
            print(f"{row['mode']}: {row['references']} refs, {row['bytes_read']} bytes, {row['load_ms']} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
