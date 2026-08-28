import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALS = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))["evals"]
import importlib.util

SCORER = ROOT / "scripts" / "score_eval_output.py"
_spec = importlib.util.spec_from_file_location("filmfoundry_score_eval_output", SCORER)
assert _spec and _spec.loader
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
score_case = _module.score_case


def score(eval_id: str, path: Path):
    case = next(case for case in EVALS if case["id"] == eval_id)
    output = path.read_text(encoding="utf-8")
    return score_case(case, output)


def test_baseline_and_golden_fixtures_exist_for_every_eval():
    for case in EVALS:
        assert (ROOT / "evals" / "fixtures" / "baseline" / f"{case['id']}.md").is_file()
        assert (ROOT / "evals" / "fixtures" / "golden" / f"{case['id']}.md").is_file()


def test_golden_fixtures_pass_all_machine_assertions():
    for case in EVALS:
        report = score(case["id"], ROOT / "evals" / "fixtures" / "golden" / f"{case['id']}.md")
        assert report["machine_passed"] == report["machine_total"], report


def test_authored_baseline_fixtures_score_lower_than_golden_set():
    baseline = []
    golden = []
    for case in EVALS:
        baseline.append(score(case["id"], ROOT / "evals" / "fixtures" / "baseline" / f"{case['id']}.md")["machine_rate"])
        golden.append(score(case["id"], ROOT / "evals" / "fixtures" / "golden" / f"{case['id']}.md")["machine_rate"])
    assert sum(baseline) / len(baseline) < sum(golden) / len(golden)
    assert sum(golden) / len(golden) == 1.0
