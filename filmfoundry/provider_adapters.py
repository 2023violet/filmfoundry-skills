"""Small deterministic adapters for capability snapshots and smoke payloads."""
from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .adapters import CompiledPayload, ProviderAdapter, hash_text
from .report import ValidationReport


class SnapshotAdapter:
    def __init__(self, name: str) -> None:
        self.name = name

    def compile(self, prompt: dict[str, Any], capability: dict[str, Any]) -> CompiledPayload:
        body = json.dumps(prompt, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        refs = tuple(str(item["slot"]) for item in prompt.get("references", []))
        return CompiledPayload(
            provider=self.name,
            route=str(capability.get("route", "UNSPECIFIED")),
            parameters=dict(capability.get("parameters", {})),
            reference_slots=refs,
            capability_snapshot_id=str(capability.get("snapshot_id", "UNVERIFIED")),
            body=body,
            input_hashes={"prompt": hash_text(body)},
        )

    def validate(self, payload: CompiledPayload) -> ValidationReport:
        errors: list[str] = []
        warnings: list[str] = []
        if payload.provider != self.name:
            errors.append("payload provider does not match adapter")
        if not payload.capability_snapshot_id:
            errors.append("capability snapshot id is required")
        elif payload.capability_snapshot_id == "UNVERIFIED" or payload.capability_snapshot_id.startswith("CLI_UNVERIFIED"):
            if payload.parameters.get("requires_verified_evidence"):
                errors.append("verified capability evidence is required for this route")
            else:
                warnings.append("capability snapshot is unverified; provider obedience is not established")
        return ValidationReport.from_messages(self.name, [payload.route], errors, warnings)


class HiggsfieldAdapter(SnapshotAdapter):
    def __init__(self) -> None:
        super().__init__("higgsfield")


class MiniMaxH3Adapter(SnapshotAdapter):
    def __init__(self) -> None:
        super().__init__("minimax-h3")


__all__ = ["HiggsfieldAdapter", "MiniMaxH3Adapter", "SnapshotAdapter"]
