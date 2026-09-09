"""Capability snapshot helpers; snapshots never imply provider execution."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


def capability_allows(capability: dict[str, Any], key: str) -> bool:
    value = capability.get(key, False)
    return value is True or (isinstance(value, str) and value.upper() in {"YES", "SUPPORTED", "VERIFIED"})


@dataclass(frozen=True)
class CapabilitySnapshot:
    snapshot_id: str
    provider: str
    provider_surface: str
    provider_version: str
    evidence_level: str
    capabilities: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "CapabilitySnapshot":
        return cls(
            snapshot_id=str(value.get("snapshot_id", "UNVERIFIED")),
            provider=str(value.get("provider", "")),
            provider_surface=str(value.get("provider_surface", "")),
            provider_version=str(value.get("provider_version", "")),
            evidence_level=str(value.get("evidence_level", "UNVERIFIED")),
            capabilities=dict(value.get("capabilities", {}) or {}),
        )

    def allows(self, key: str) -> bool:
        return capability_allows(self.capabilities, key)


def load_capability_snapshot(path: Path) -> CapabilitySnapshot:
    return CapabilitySnapshot.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))


__all__ = ["CapabilitySnapshot", "capability_allows", "load_capability_snapshot"]
