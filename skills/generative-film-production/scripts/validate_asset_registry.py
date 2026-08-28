#!/usr/bin/env python3
"""Validate FilmFoundry asset-registry CSV files."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REQUIRED_COLUMNS = {
    "asset_id",
    "asset_type",
    "canonical_descriptor",
    "state_variant",
    "parent_asset_id",
    "reference_id",
    "reference_role",
    "does_not_control",
}


def _blank(row: dict[str, str], key: str) -> bool:
    return not (row.get(key) or "").strip()


def validate_rows(rows: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    ids: list[str] = []

    for i, row in enumerate(rows, start=2):
        asset_id = (row.get("asset_id") or "").strip()
        if not asset_id:
            errors.append(f"row {i}: asset_id is required")
        elif asset_id in ids:
            errors.append(f"row {i}: duplicate asset_id {asset_id}")
        ids.append(asset_id)

        for key in ("asset_type", "canonical_descriptor", "state_variant", "reference_id", "reference_role", "does_not_control"):
            if _blank(row, key):
                errors.append(f"row {i}: {key} is required")

    id_set = {asset_id for asset_id in ids if asset_id}
    variant_by_id = {
        (row.get("asset_id") or "").strip(): (row.get("state_variant") or "").strip().upper()
        for row in rows
        if (row.get("asset_id") or "").strip()
    }
    for i, row in enumerate(rows, start=2):
        asset_id = (row.get("asset_id") or "").strip()
        variant = (row.get("state_variant") or "").strip().upper()
        parent = (row.get("parent_asset_id") or "").strip()
        if variant == "CANON":
            if parent:
                errors.append(f"row {i}: CANON asset must not have parent_asset_id")
        else:
            if not parent:
                errors.append(f"row {i}: parent_asset_id is required for non-CANON state variant")
            elif parent == asset_id:
                errors.append(f"row {i}: noncanonical state variant cannot parent itself")
            elif parent not in id_set:
                errors.append(f"row {i}: parent_asset_id {parent} does not exist")
            elif variant_by_id.get(parent) != "CANON":
                errors.append(f"row {i}: parent_asset_id {parent} must reference a CANON asset directly")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_asset_registry.py <asset-registry.csv>")
        return 2
    path = Path(argv[1])
    try:
        with path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            fieldnames = set(reader.fieldnames or [])
            missing = REQUIRED_COLUMNS - fieldnames
            if missing:
                print("FAIL: missing columns: " + ", ".join(sorted(missing)))
                return 1
            rows = list(reader)
    except OSError as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_rows(rows)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: asset registry valid ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
