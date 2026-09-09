import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "skills" / "generative-film-production" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


def profile():
    path = ROOT / "skills" / "generative-film-production" / "templates" / "model-profile.example.json"
    return json.loads(path.read_text(encoding="utf-8"))


def observation(level="OBSERVED_ONCE"):
    return {
        "capability": "spatial_persistence",
        "context": "10s environment I2V with one slow camera push",
        "evidence_level": level,
        "source_generation_ids": ["GEN_SH001_01"],
        "observation": "mid-clip scene reset occurred after usable early segment",
        "production_consequence": "allow partial select; do not assume ten-second geography persistence"
    }


def test_model_profile_accepts_observed_once_behavior_with_source_generation():
    from validate_model_profile import validate_model_profile
    data = profile()
    data["behavior_observations"] = [observation()]
    assert validate_model_profile(data) == []


def test_behavior_observation_rejects_unknown_evidence_level():
    from validate_model_profile import validate_model_profile
    data = profile()
    data["behavior_observations"] = [observation("PROBABLY")]
    errors = validate_model_profile(data)
    assert any("behavior_observations" in e and "evidence_level" in e for e in errors)


def test_behavior_evidence_above_unverified_requires_source_generation_ids():
    from validate_model_profile import validate_model_profile
    data = profile()
    item = observation()
    item["source_generation_ids"] = []
    data["behavior_observations"] = [item]
    errors = validate_model_profile(data)
    assert any("source_generation_ids" in e for e in errors)


def test_observed_once_cannot_be_marked_default_adapter_behavior():
    from validate_model_profile import validate_model_profile
    data = profile()
    item = observation("OBSERVED_ONCE")
    item["default_adapter_behavior"] = True
    data["behavior_observations"] = [item]
    errors = validate_model_profile(data)
    assert any("default_adapter_behavior" in e and "REPEATED" in e for e in errors)


def test_repeated_behavior_may_be_marked_default_adapter_behavior():
    from validate_model_profile import validate_model_profile
    data = profile()
    item = observation("REPEATED")
    item["source_generation_ids"] = ["GEN_A", "GEN_B"]
    item["default_adapter_behavior"] = True
    data["behavior_observations"] = [item]
    assert validate_model_profile(data) == []
