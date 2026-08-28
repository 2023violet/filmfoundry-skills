#!/usr/bin/env python3
"""Validate FilmFoundry agentic eval metadata without running an LLM."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ALLOWED_TYPES = {"contains_any", "contains_all", "not_contains", "human"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("skill_name") != "generative-film-production":
        errors.append("skill_name must be generative-film-production")
    if not isinstance(data.get("version"), str) or not data["version"].strip():
        errors.append("version is required")
    evals = data.get("evals")
    if not isinstance(evals, list) or not evals:
        return errors + ["evals must be a non-empty list"]
    seen: set[str] = set()
    for i, case in enumerate(evals):
        cid = case.get("id")
        if not isinstance(cid, str) or not cid:
            errors.append(f"eval[{i}].id required")
        elif cid in seen:
            errors.append(f"duplicate eval id: {cid}")
        seen.add(cid)
        for key in ("name", "prompt", "expected_output"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                errors.append(f"{cid or i}.{key} required")
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or len(assertions) < 3:
            errors.append(f"{cid or i}.assertions requires at least 3 entries")
            continue
        for j, assertion in enumerate(assertions):
            atype = assertion.get("type")
            if atype not in ALLOWED_TYPES:
                errors.append(f"{cid or i}.assertions[{j}].type invalid")
            if not isinstance(assertion.get("text"), str) or not assertion["text"].strip():
                errors.append(f"{cid or i}.assertions[{j}].text required")
            if atype != "human":
                terms = assertion.get("terms")
                if not isinstance(terms, list) or not terms or not all(isinstance(x, str) and x for x in terms):
                    errors.append(f"{cid or i}.assertions[{j}].terms required for {atype}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_evals.py <evals.json>")
        return 2
    try:
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 2
    if not isinstance(data, dict):
        print("FAIL: top-level JSON must be an object")
        return 1
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {len(data['evals'])} evals schema-valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
