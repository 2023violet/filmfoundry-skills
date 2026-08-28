import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def valid_rows():
    return [
        {
            "asset_id": "CHAR_A",
            "asset_type": "character",
            "canonical_descriptor": "middle-aged envoy, narrow face, black Han robe, red belt",
            "state_variant": "CANON",
            "parent_asset_id": "",
            "reference_id": "REF_A",
            "reference_role": "face identity",
            "does_not_control": "wardrobe, background, lighting",
        },
        {
            "asset_id": "CHAR_A_WET",
            "asset_type": "character-state",
            "canonical_descriptor": "same envoy, robe and hair visibly rain-wet",
            "state_variant": "WET",
            "parent_asset_id": "CHAR_A",
            "reference_id": "REF_A_WET",
            "reference_role": "wet state only",
            "does_not_control": "face identity",
        },
    ]


def test_valid_registry_has_no_errors():
    from validate_asset_registry import validate_rows
    assert validate_rows(valid_rows()) == []


def test_asset_ids_must_be_unique():
    from validate_asset_registry import validate_rows
    rows = valid_rows()
    rows[1]["asset_id"] = "CHAR_A"
    errors = validate_rows(rows)
    assert any("duplicate asset_id" in e for e in errors)


def test_required_canonical_descriptor_and_reference_boundaries():
    from validate_asset_registry import validate_rows
    rows = valid_rows()
    rows[0]["canonical_descriptor"] = ""
    rows[0]["does_not_control"] = ""
    errors = validate_rows(rows)
    assert any("canonical_descriptor" in e for e in errors)
    assert any("does_not_control" in e for e in errors)


def test_state_variant_requires_existing_parent():
    from validate_asset_registry import validate_rows
    rows = valid_rows()
    rows[1]["parent_asset_id"] = "MISSING"
    errors = validate_rows(rows)
    assert any("parent_asset_id" in e for e in errors)


def test_noncanonical_variant_cannot_parent_itself():
    from validate_asset_registry import validate_rows
    rows = valid_rows()
    rows[1]["parent_asset_id"] = "CHAR_A_WET"
    errors = validate_rows(rows)
    assert any("cannot parent itself" in e for e in errors)


def test_cli_rejects_invalid_csv(tmp_path):
    path = tmp_path / "assets.csv"
    fields = list(valid_rows()[0])
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        bad = valid_rows()[0]
        bad["reference_role"] = ""
        writer.writerow(bad)
    script = SCRIPT_DIR / "validate_asset_registry.py"
    result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "reference_role" in result.stdout


def test_canon_asset_must_not_have_parent():
    from validate_asset_registry import validate_rows
    rows = valid_rows()
    rows[0]["parent_asset_id"] = "CHAR_A_WET"
    errors = validate_rows(rows)
    assert any("canon" in e.lower() and "parent" in e.lower() for e in errors)


def test_state_variant_must_parent_a_canon_asset_directly():
    from validate_asset_registry import validate_rows
    rows = valid_rows()
    rows.append({
        "asset_id": "CHAR_A_DIRTY",
        "asset_type": "character-state",
        "canonical_descriptor": "same envoy, robe visibly dirty",
        "state_variant": "DIRTY",
        "parent_asset_id": "CHAR_A_WET",
        "reference_id": "REF_A_DIRTY",
        "reference_role": "dirty state only",
        "does_not_control": "face identity",
    })
    errors = validate_rows(rows)
    assert any("parent" in e.lower() and "canon" in e.lower() for e in errors)
