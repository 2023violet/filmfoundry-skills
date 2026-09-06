import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def locked_canon():
    return {
        "asset_id": "CHAR_A",
        "asset_type": "character",
        "asset_class": "CANONICAL",
        "file_name": "char_a.png",
        "canonical_descriptor": "middle-aged envoy",
        "state_variant": "CANON",
        "parent_asset_id": "",
        "version": "1.0",
        "sha256": "a" * 64,
        "status": "LOCKED",
        "reference_id": "REF_A",
        "reference_role": "identity",
        "does_not_control": "background, lighting",
        "supersedes": "",
    }


def test_locked_canonical_asset_requires_real_sha256():
    from validate_asset_registry import validate_rows
    row = locked_canon()
    assert validate_rows([row]) == []
    row["sha256"] = "UNVERIFIED"
    errors = validate_rows([row])
    assert any("sha256" in e.lower() for e in errors)


def test_generic_asset_does_not_require_fixed_reference_identity():
    from validate_asset_registry import validate_rows
    row = {
        "asset_id": "GENERIC_VILLAGERS",
        "asset_type": "character-group",
        "asset_class": "GENERIC",
        "file_name": "",
        "canonical_descriptor": "background villagers sharing one costume language",
        "state_variant": "CANON",
        "parent_asset_id": "",
        "version": "1.0",
        "sha256": "UNVERIFIED",
        "status": "PLANNED",
        "reference_id": "",
        "reference_role": "",
        "does_not_control": "",
        "supersedes": "",
    }
    assert validate_rows([row]) == []


def test_ephemeral_asset_can_be_descriptor_only_and_must_not_claim_locked_file_authority():
    from validate_asset_registry import validate_rows
    row = {
        "asset_id": "EPHEMERAL_BASKET",
        "asset_type": "prop",
        "asset_class": "EPHEMERAL",
        "file_name": "",
        "canonical_descriptor": "ordinary woven basket",
        "state_variant": "CANON",
        "parent_asset_id": "",
        "version": "1.0",
        "sha256": "UNVERIFIED",
        "status": "PLANNED",
        "reference_id": "",
        "reference_role": "",
        "does_not_control": "",
        "supersedes": "",
    }
    assert validate_rows([row]) == []
    row["status"] = "LOCKED"
    errors = validate_rows([row])
    assert any("ephemeral" in e.lower() for e in errors)
