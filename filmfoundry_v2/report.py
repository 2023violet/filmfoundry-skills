"""Structured validation results shared by core and adapters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True, order=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    source: str = ""
    json_pointer: str = ""
    related_ids: tuple[str, ...] = ()
    suggestion: str = ""

    def __post_init__(self) -> None:
        if self.severity not in {"ERROR", "WARNING"}:
            raise ValueError("severity must be ERROR or WARNING")


@dataclass
class ValidationReport:
    stage: str
    checked: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.checked = sorted(set(self.checked))
        self.issues = sorted(self.issues, key=lambda i: (i.severity != "ERROR", i.source, i.json_pointer, i.code, i.message))

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)

    @classmethod
    def from_messages(cls, stage: str, checked: Iterable[str], errors: Iterable[str], warnings: Iterable[str] = ()) -> "ValidationReport":
        issues = [ValidationIssue("ERROR", "VALIDATION_ERROR", value) for value in errors]
        issues.extend(ValidationIssue("WARNING", "VALIDATION_WARNING", value) for value in warnings)
        return cls(stage, list(checked), issues)


__all__ = ["ValidationIssue", "ValidationReport"]
