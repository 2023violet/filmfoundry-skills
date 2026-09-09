#!/usr/bin/env python3
"""Validate FilmFoundry asset-registry CSV files.

v1.1 keeps the v1.0.1 columns backward compatible while adding runtime
fields for asset authority, version/hash evidence, and lightweight generic /
ephemeral asset classes.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

LEGACY_REQUIRED_COLUMNS = {
    "asset_id",
    "asset_type",
    "canonical_descriptor",
    "state_variant",
    "parent_asset_id",
    "reference_id",
    "reference_role",
    "does_not_control",
}

ALLOWED_CLASSES = {"CANONICAL", "GENERIC", "EPHEMERAL"}
ALLOWED_STATUS = {"PLANNED", "DRAFT", "LOCKED", "RETIRED"}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _blank(row: dict[str, str], key: str) -> bool:
    return not (row.get(key) or "").strip()


def _asset_class(row: dict[str, str]) -> str:
    # Legacy registries did not have asset_class. Treat them as canonical so
    # existing projects remain valid while new projects can opt into v1.1.
    return (row.get("asset_class") or "CANONICAL").strip().upper()


def _status(row: dict[str, str]) -> str:
    return (row.get("status") or "PLANNED").strip().upper()


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

        for key in ("asset_type", "canonical_descriptor", "state_variant"):
            if _blank(row, key):
                errors.append(f"row {i}: {key} is required")

        asset_class = _asset_class(row)
        if asset_class not in ALLOWED_CLASSES:
            errors.append(f"row {i}: asset_class must be one of {sorted(ALLOWED_CLASSES)}")

        status = _status(row)
        if status not in ALLOWED_STATUS:
            errors.append(f"row {i}: status must be one of {sorted(ALLOWED_STATUS)}")

        # Canonical visual authorities need explicit reference boundaries.
        # Generic extras and ephemeral props intentionally do not carry fixed
        # identity unless a reference is actually supplied.
        if asset_class == "CANONICAL":
            for key in ("reference_id", "reference_role", "does_not_control"):
                if _blank(row, key):
                    errors.append(f"row {i}: {key} is required for CANONICAL asset")
        else:
            ref_id = (row.get("reference_id") or "").strip()
            if ref_id:
                if _blank(row, "reference_role"):
                    errors.append(f"row {i}: reference_role is required when reference_id is set")
                if _blank(row, "does_not_control"):
                    errors.append(f"row {i}: does_not_control is required when reference_id is set")

        if asset_class == "EPHEMERAL" and status == "LOCKED":
            errors.append(f"row {i}: EPHEMERAL asset cannot claim LOCKED file authority; promote it to CANONICAL if persistence matters")

        # A LOCKED canonical asset is an authority claim. If the v1.1 hash
        # column is present, it must contain a real SHA-256 rather than a
        # placeholder. Legacy rows with no hash column remain accepted.
        if asset_class == "CANONICAL" and status == "LOCKED" and "sha256" in row:
            sha = (row.get("sha256") or "").strip()
            if not SHA256_RE.fullmatch(sha):
                errors.append(f"row {i}: sha256 must be a 64-character hexadecimal digest for LOCKED CANONICAL asset")

        if "version" in row and status == "LOCKED" and _blank(row, "version"):
            errors.append(f"row {i}: version is required for LOCKED asset")

    id_set = {asset_id for asset_id in ids if asset_id}
    variant_by_id = {
        (row.get("asset_id") or "").strip(): (row.get("state_variant") or "").strip().upper()
        for row in rows
        if (row.get("asset_id") or "").strip()
    }
    class_by_id = {
        (row.get("asset_id") or "").strip(): _asset_class(row)
        for row in rows
        if (row.get("asset_id") or "").strip()
    }

    for i, row in enumerate(rows, start=2):
        asset_id = (row.get("asset_id") or "").strip()
        asset_class = _asset_class(row)
        variant = (row.get("state_variant") or "").strip().upper()
        parent = (row.get("parent_asset_id") or "").strip()

        if asset_class != "CANONICAL":
            if parent:
                errors.append(f"row {i}: {asset_class} asset must not use parent_asset_id; state variants belong to CANONICAL assets")
            continue

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
            elif class_by_id.get(parent) != "CANONICAL" or variant_by_id.get(parent) != "CANON":
                errors.append(f"row {i}: parent_asset_id {parent} must reference a CANON CANONICAL asset directly")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_asset_registry.py <asset-registry.csv>")
        return 2
    path = Path(argv[1])
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            fieldnames = set(reader.fieldnames or [])
            missing = LEGACY_REQUIRED_COLUMNS - fieldnames
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
