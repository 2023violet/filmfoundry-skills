#!/usr/bin/env python3
"""Score only deterministic assertions for one FilmFoundry eval output.

Human assertions are reported but never auto-passed. This tool is intentionally
simple and transparent; it is a smoke grader, not a semantic judge.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path


def score_case(case: dict, output: str) -> dict:
    lower = output.lower()
    details = []
    passed = 0
    total = 0
    for assertion in case["assertions"]:
        atype = assertion["type"]
        if atype == "human":
            details.append({"text": assertion["text"], "type": "human", "passed": None})
            continue
        terms = assertion["terms"]
        total += 1
        if atype == "contains_any":
            ok = any(term.lower() in lower for term in terms)
        elif atype == "contains_all":
            ok = all(term.lower() in lower for term in terms)
        elif atype == "not_contains":
            ok = all(term.lower() not in lower for term in terms)
        else:
            ok = False
        passed += int(ok)
        details.append({"text": assertion["text"], "type": atype, "passed": ok, "terms": terms})
    return {
        "eval_id": case["id"],
        "machine_passed": passed,
        "machine_total": total,
        "machine_rate": 1.0 if total == 0 else passed / total,
        "assertions": details,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: score_eval_output.py <evals.json> <eval-id> <output.md>", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        output = Path(argv[3]).read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    case = next((c for c in data.get("evals", []) if c.get("id") == argv[2]), None)
    if case is None:
        print(f"unknown eval id: {argv[2]}", file=sys.stderr)
        return 2
    report = score_case(case, output)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["machine_passed"] == report["machine_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
