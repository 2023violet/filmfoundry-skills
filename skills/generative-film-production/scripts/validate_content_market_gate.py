#!/usr/bin/env python3
"""Validate FilmFoundry v1.2 Content Market Gate JSON."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from runtime_common import load_json, nonempty

ALLOWED_GATE_MODES = {"REQUIRED", "BYPASS"}
ALLOWED_DECISIONS = {"NO_GO", "TRAFFIC_EXPERIMENT", "MVP_ONLY", "PRODUCTION_APPROVED", "BYPASS"}
ALLOWED_MVP_STATUS = {"NOT_RUN", "RUNNING", "PASS", "FAIL", "INCONCLUSIVE"}
CORE_TEXT_FIELDS = (
    "project_intent",
    "one_sentence_conflict",
    "audience",
    "click_reason",
    "hook_3s",
    "viewer_payoff",
    "follow_reason",
    "series_engine_30",
    "ai_production_fit",
    "platform_hypothesis",
)


def validate_content_market_gate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if str(data.get("schema_version", "")).strip() != "1.2":
        errors.append("schema_version: expected 1.2")

    mode = str(data.get("gate_mode", "")).strip().upper()
    if mode not in ALLOWED_GATE_MODES:
        errors.append(f"gate_mode: must be one of {sorted(ALLOWED_GATE_MODES)}")
        return errors

    decision = str(data.get("decision", "")).strip().upper()
    if decision not in ALLOWED_DECISIONS:
        errors.append(f"decision: must be one of {sorted(ALLOWED_DECISIONS)}")

    if mode == "BYPASS":
        if decision != "BYPASS":
            errors.append("decision: BYPASS gate_mode requires decision BYPASS")
        if not nonempty(data.get("bypass_reason")):
            errors.append("bypass_reason: required for explicit market-gate bypass")
        return errors

    if decision == "BYPASS":
        errors.append("decision: BYPASS is only valid when gate_mode is BYPASS")

    for field in CORE_TEXT_FIELDS:
        if not nonempty(data.get(field)):
            errors.append(f"{field}: required non-empty answer before MVP work")

    cheapest = data.get("cheapest_mvp")
    if not isinstance(cheapest, dict):
        errors.append("cheapest_mvp: required object")
    else:
        for field in ("format", "production_limit"):
            if not nonempty(cheapest.get(field)):
                errors.append(f"cheapest_mvp.{field}: required")
        variants = cheapest.get("variants")
        if not isinstance(variants, int) or isinstance(variants, bool) or variants < 1:
            errors.append("cheapest_mvp.variants: required positive integer")

    monetization = data.get("monetization_route")
    if not nonempty(monetization) and decision not in {"NO_GO", "TRAFFIC_EXPERIMENT"}:
        errors.append("monetization_route: missing route limits decision to TRAFFIC_EXPERIMENT or NO_GO")

    evidence = data.get("mvp_evidence")
    if not isinstance(evidence, dict):
        errors.append("mvp_evidence: required object")
        evidence = {}
    else:
        status = str(evidence.get("status", "")).strip().upper()
        if status not in ALLOWED_MVP_STATUS:
            errors.append(f"mvp_evidence.status: must be one of {sorted(ALLOWED_MVP_STATUS)}")
        if not nonempty(evidence.get("success_criteria")):
            errors.append("mvp_evidence.success_criteria: required and must be declared before interpreting results")
        ids = evidence.get("evidence_ids")
        if not isinstance(ids, list):
            errors.append("mvp_evidence.evidence_ids: must be a list")

    if decision == "PRODUCTION_APPROVED":
        status = str(evidence.get("status", "")).strip().upper()
        ids = evidence.get("evidence_ids", [])
        if status != "PASS":
            errors.append("mvp_evidence: PRODUCTION_APPROVED requires status PASS")
        if not isinstance(ids, list) or not any(nonempty(x) for x in ids):
            errors.append("mvp_evidence.evidence_ids: PRODUCTION_APPROVED requires real evidence IDs")
        if not nonempty(evidence.get("result_summary")):
            errors.append("mvp_evidence.result_summary: required for PRODUCTION_APPROVED")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_content_market_gate.py <content-market-gate.json>")
        return 2
    try:
        data = load_json(Path(argv[1]))
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    errors = validate_content_market_gate(data if isinstance(data, dict) else {})
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: content market gate is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
