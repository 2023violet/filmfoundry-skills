"""Provider adapter protocol; network clients remain outside the core."""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Protocol

from .report import ValidationReport


@dataclass(frozen=True)
class CompiledPayload:
    provider: str
    route: str
    parameters: dict[str, Any]
    reference_slots: tuple[str, ...]
    capability_snapshot_id: str
    body: str
    input_hashes: dict[str, str] = field(default_factory=dict)


class ProviderAdapter(Protocol):
    name: str

    def compile(self, prompt: dict[str, Any], capability: dict[str, Any]) -> CompiledPayload: ...

    def validate(self, payload: CompiledPayload) -> ValidationReport: ...


def hash_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


__all__ = ["CompiledPayload", "ProviderAdapter", "hash_text"]
