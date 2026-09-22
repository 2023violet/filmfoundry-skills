"""External adapter boundary kept out of the FilmFoundry Core.

The Core emits :class:`ProviderNeutralHandoff`. A downstream integration may
translate that handoff for a selected external tool; this module contains no
provider names, clients, credentials, smoke execution, or media download logic.
"""
from __future__ import annotations

from typing import Any, Mapping, Protocol

from .handoff import ProviderNeutralHandoff


class ExternalHandoffAdapter(Protocol):
    """Translate, but never redefine, a neutral handoff."""

    name: str

    def translate(self, handoff: ProviderNeutralHandoff) -> Mapping[str, Any]: ...


__all__ = ["ExternalHandoffAdapter"]
