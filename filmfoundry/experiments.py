"""Experiment result recording without automatic capability promotion."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import ID_RE, SHA256_RE
from .report import ValidationIssue, ValidationReport


def record_experiment_result(experiment_path: Path, result: dict[str, Any]) -> ValidationReport:
    path = Path(experiment_path)
    issues: list[ValidationIssue] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ValidationReport("experiment", [str(path)], [ValidationIssue("ERROR", "EXPERIMENT_READ", str(exc), str(path), "")])
    if not isinstance(data, dict):
        return ValidationReport("experiment", [str(path)], [ValidationIssue("ERROR", "TOP_LEVEL_TYPE", "experiment must be an object", str(path), "")])
    for field in ("experiment_id", "hypothesis", "control_variables", "treatment_variables", "provider", "provider_surface", "input_asset_ids", "result_ids", "evaluation_method", "conclusion", "evidence_level"):
        if field not in data:
            issues.append(ValidationIssue("ERROR", "REQUIRED_FIELD", f"{field}: required", str(path), f"/{field}"))
    if not isinstance(result, dict):
        issues.append(ValidationIssue("ERROR", "RESULT_TYPE", "result must be an object", str(path), "/result"))
    else:
        result_id = result.get("result_id")
        if not isinstance(result_id, str) or not ID_RE.fullmatch(result_id):
            issues.append(ValidationIssue("ERROR", "INVALID_ID", "result.result_id must be a stable ASCII ID", str(path), "/result/result_id"))
        if result.get("media_sha256") is not None and not SHA256_RE.fullmatch(str(result["media_sha256"])):
            issues.append(ValidationIssue("ERROR", "INVALID_HASH", "result.media_sha256 must be SHA-256", str(path), "/result/media_sha256"))
        if result.get("evidence_level", "OBSERVED_ONCE") == "OBSERVED_ONCE":
            issues.append(ValidationIssue("WARNING", "OBSERVED_ONCE_NOT_DEFAULT", "single experiment result cannot promote default provider behavior", str(path), "/result/evidence_level"))
    report = ValidationReport("experiment", [str(path)], issues)
    if report.ok:
        if result["result_id"] not in data.setdefault("result_ids", []):
            data["result_ids"].append(result["result_id"])
            data["result_ids"] = sorted(data["result_ids"])
        data.setdefault("results", []).append(result)
        data["results"] = sorted(data["results"], key=lambda item: str(item.get("result_id", "")))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


__all__ = ["record_experiment_result"]
