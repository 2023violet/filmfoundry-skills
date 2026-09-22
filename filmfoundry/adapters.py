"""Provider adapter protocol; network clients remain outside the core."""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Mapping, Protocol

@dataclass(frozen=True)
class CompiledPayload:
    """Compatibility envelope for a neutral handoff.

    ``provider`` is always ``provider-neutral`` when produced by Core. External
    adapters may wrap this envelope with their own target metadata.
    """
    provider: str
    route: str
    parameters: dict[str, Any]
    reference_slots: tuple[str, ...]
    capability_snapshot_id: str
    body: str
    input_hashes: dict[str, str] = field(default_factory=dict)
    visual_control_id: str | None = None
    visual_control_hash: str | None = None
    production_ledger_event_ids: tuple[str, ...] = ()
    requirement_report_hash: str | None = None


class ProviderAdapter(Protocol):
    name: str

    def translate(self, handoff: Any) -> Mapping[str, Any]: ...


def hash_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


__all__ = ["CompiledPayload", "ProviderAdapter", "hash_text"]
