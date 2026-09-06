"""Small helpers for lens results used by the canonical compiler."""
from __future__ import annotations

from typing import Any


def normalize_lens_result(value: dict[str, Any]) -> dict[str, Any]:
    """Return a stable lens result with an observable framing statement."""
    result = dict(value)
    result.setdefault("framing_result", "")
    result.setdefault("camera_path", "fixed")
    return result


__all__ = ["normalize_lens_result"]
