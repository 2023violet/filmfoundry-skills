#!/usr/bin/env python3
"""Validate FilmFoundry model-evidence profile JSON."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from runtime_common import EVIDENCE_LEVELS, EVIDENCE_RANK, load_json, nonempty

SMOKE_IDS_H3 = {f"TEST_H3_{i:02d}" for i in range(1, 11)}
ALLOWED_VERDICTS = {"UNVERIFIED", "VERIFIED", "PARTIAL", "FAIL"}


def validate_model_profile(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in ("model_id", "provider", "product_surface", "model_version", "tested_date", "verification_status"):
        if not nonempty(data.get(field)):
            errors.append(f"{field}: required")

    binding = data.get("reference_role_binding")
    if not isinstance(binding, dict):
        errors.append("reference_role_binding: required object")
    else:
        status = str(binding.get("status", "UNVERIFIED")).strip().upper()
        if status not in EVIDENCE_RANK:
            errors.append(f"reference_role_binding.status: must be one of {EVIDENCE_LEVELS}")
        evidence_ids = binding.get("evidence_ids", [])
        if status != "UNVERIFIED" and (not isinstance(evidence_ids, list) or not evidence_ids):
            errors.append("reference_role_binding.evidence_ids: required once behavior has evidence")

    strategy = data.get("prompt_language_strategy")
    if not isinstance(strategy, dict) or not nonempty(strategy.get("instruction_language")) or not nonempty(strategy.get("dialogue_language")):
        errors.append("prompt_language_strategy: instruction_language and dialogue_language are required")

    smoke = data.get("smoke_tests")
    if not isinstance(smoke, list):
        errors.append("smoke_tests: required list")
        smoke = []
    seen: set[str] = set()
    verdict_by_id: dict[str, str] = {}
    for i, item in enumerate(smoke):
        if not isinstance(item, dict):
            errors.append(f"smoke_tests[{i}]: must be an object")
            continue
        tid = str(item.get("test_id", "")).strip()
        if not tid:
            errors.append(f"smoke_tests[{i}].test_id: required")
            continue
        if tid in seen:
            errors.append(f"smoke_tests[{i}].test_id: duplicate {tid}")
        seen.add(tid)
        verdict = str(item.get("verdict", "UNVERIFIED")).strip().upper()
        if verdict not in ALLOWED_VERDICTS:
            errors.append(f"smoke_tests[{i}].verdict: unsupported {verdict}")
        verdict_by_id[tid] = verdict
        attempts = item.get("attempts")
        passes = item.get("passes")
        fails = item.get("fails")
        for label, value in (("attempts", attempts), ("passes", passes), ("fails", fails)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"smoke_tests[{i}].{label}: required non-negative integer")
        if all(isinstance(v, int) and not isinstance(v, bool) for v in (attempts, passes, fails)) and attempts != passes + fails:
            errors.append(f"smoke_tests[{i}]: attempts must equal passes + fails")


    observations = data.get("behavior_observations", [])
    if observations is None:
        observations = []
    if not isinstance(observations, list):
        errors.append("behavior_observations: must be a list when present")
    else:
        for i, item in enumerate(observations):
            prefix = f"behavior_observations[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix}: must be an object")
                continue
            for field in ("capability", "context", "observation", "production_consequence"):
                if not nonempty(item.get(field)):
                    errors.append(f"{prefix}.{field}: required")
            level = str(item.get("evidence_level", "UNVERIFIED")).strip().upper()
            if level not in EVIDENCE_RANK:
                errors.append(f"{prefix}.evidence_level: must be one of {EVIDENCE_LEVELS}")
                continue
            source_ids = item.get("source_generation_ids", [])
            if not isinstance(source_ids, list):
                errors.append(f"{prefix}.source_generation_ids: must be a list")
            elif level != "UNVERIFIED" and not any(nonempty(x) for x in source_ids):
                errors.append(f"{prefix}.source_generation_ids: required once behavior has evidence")
            if item.get("default_adapter_behavior") is True and EVIDENCE_RANK[level] < EVIDENCE_RANK["REPEATED"]:
                errors.append(f"{prefix}.default_adapter_behavior: requires REPEATED or stronger evidence")

    if str(data.get("verification_status", "")).strip().upper() == "MODEL_PROFILE_MINIMUM_PASS":
        model_id = str(data.get("model_id", "")).strip().lower()
        provider = str(data.get("provider", "")).strip().lower()
        is_h3 = "h3" in model_id and ("minimax" in model_id or "minimax" in provider)
        if is_h3:
            missing = SMOKE_IDS_H3 - set(verdict_by_id)
            if missing:
                errors.append("smoke_tests: MODEL_PROFILE_MINIMUM_PASS requires all H3 smoke tests; missing " + ", ".join(sorted(missing)))
            for tid in sorted(SMOKE_IDS_H3):
                if tid in verdict_by_id and verdict_by_id[tid] == "UNVERIFIED":
                    errors.append(f"smoke_tests: {tid} cannot remain UNVERIFIED at MODEL_PROFILE_MINIMUM_PASS")
        elif not verdict_by_id or not any(v != "UNVERIFIED" for v in verdict_by_id.values()):
            errors.append("smoke_tests: MODEL_PROFILE_MINIMUM_PASS requires at least one decided model-specific smoke test")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_model_profile.py <model-profile.json>")
        return 2
    try:
        data = load_json(Path(argv[1]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_model_profile(data if isinstance(data, dict) else {})
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("PASS: model profile is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
