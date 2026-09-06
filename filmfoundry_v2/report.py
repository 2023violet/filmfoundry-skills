"""Structured validation results shared by core and adapters."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Iterable


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
        object.__setattr__(self, "related_ids", tuple(self.related_ids))

    @property
    def sort_key(self) -> tuple[Any, ...]:
        """Return the canonical ordering key used by validation reports."""
        return (
            0 if self.severity == "ERROR" else 1,
            self.source,
            self.json_pointer,
            self.code,
            self.message,
            self.related_ids,
            self.suggestion,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "source": self.source,
            "json_pointer": self.json_pointer,
            "related_ids": list(self.related_ids),
            "suggestion": self.suggestion,
        }


@dataclass
class ValidationReport:
    stage: str
    checked: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.checked = sorted(set(self.checked))
        self.issues = sorted(self.issues, key=lambda issue: issue.sort_key)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)

    @property
    def exit_code(self) -> int:
        return 0 if self.ok else 1

    @property
    def errors(self) -> list[str]:
        return [issue.message for issue in self.issues if issue.severity == "ERROR"]

    @property
    def warnings(self) -> list[str]:
        return [issue.message for issue in self.issues if issue.severity == "WARNING"]

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "checked": self.checked,
            "issues": [
                {"severity": i.severity, "code": i.code, "message": i.message,
                 "source": i.source, "json_pointer": i.json_pointer,
                 "related_ids": list(i.related_ids), "suggestion": i.suggestion}
                for i in self.issues
            ],
        }

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "ERROR"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "WARNING"]

    @property
    def exit_code(self) -> int:
        """Return the process status for this report (warnings remain successful)."""
        return 0 if self.ok else 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize a deterministic, CLI-friendly representation."""
        return {
            "stage": self.stage,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "checked": list(self.checked),
            "issues": [issue.to_dict() for issue in self.issues],
            "errors": [issue.message for issue in self.errors],
            "warnings": [issue.message for issue in self.warnings],
        }

    as_dict = to_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_messages(cls, stage: str, checked: Iterable[str], errors: Iterable[str], warnings: Iterable[str] = ()) -> "ValidationReport":
        issues = [ValidationIssue("ERROR", "VALIDATION_ERROR", value) for value in errors]
        issues.extend(ValidationIssue("WARNING", "VALIDATION_WARNING", value) for value in warnings)
        return cls(stage, list(checked), issues)


__all__ = ["ValidationIssue", "ValidationReport"]
