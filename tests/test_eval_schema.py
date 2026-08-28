import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVAL_PATH = ROOT / "evals" / "evals.json"
VALIDATOR = ROOT / "scripts" / "validate_evals.py"


def test_eval_file_has_twelve_realistic_cases():
    data = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    assert data["skill_name"] == "generative-film-production"
    assert data["version"] == "1.0.1"
    assert len(data["evals"]) == 12
    ids = [case["id"] for case in data["evals"]]
    assert len(ids) == len(set(ids))
    for case in data["evals"]:
        assert len(case["prompt"]) >= 60
        assert len(case["expected_output"]) >= 40
        assert len(case["assertions"]) >= 3


def test_each_eval_has_machine_and_human_assertions():
    data = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    for case in data["evals"]:
        types = {a["type"] for a in case["assertions"]}
        assert "human" in types
        assert types & {"contains_any", "contains_all", "not_contains"}
        for assertion in case["assertions"]:
            assert assertion["text"].strip()
            if assertion["type"] != "human":
                assert assertion.get("terms")


def test_eval_validator_cli_passes_schema():
    result = subprocess.run([sys.executable, str(VALIDATOR), str(EVAL_PATH)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "12 evals" in result.stdout


def test_no_placeholder_markers_in_evals():
    text = EVAL_PATH.read_text(encoding="utf-8")
    for marker in ["TBD", "TODO", "<fill", "Lorem ipsum"]:
        assert marker not in text
