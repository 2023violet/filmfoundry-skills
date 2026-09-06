"""Additive FilmFoundry v2 production contracts.

The package is intentionally dependency free.  It validates machine contracts
without making claims about provider obedience or visual quality.
"""
from .contracts import (
    LIFECYCLE_STATES,
    parse_prompt_metadata,
    resolve_manifest_path,
    validate_asset_registry,
    validate_evidence,
    validate_prompt_markdown,
    validate_production_state,
    validate_reference_graph,
    validate_shot_spec,
    validate_state_transition,
    validate_workspace_manifest,
)
from .report import ValidationIssue, ValidationReport
from .adapters import CompiledPayload, ProviderAdapter
from .validation import validate_workspace

__version__ = "2.0.0"

__all__ = [
    "LIFECYCLE_STATES",
    "parse_prompt_metadata",
    "resolve_manifest_path",
    "validate_asset_registry",
    "validate_evidence",
    "validate_prompt_markdown",
    "validate_production_state",
    "validate_reference_graph",
    "validate_shot_spec",
    "validate_state_transition",
    "validate_workspace_manifest",
    "__version__",
    "ValidationIssue",
    "ValidationReport",
    "CompiledPayload",
    "ProviderAdapter",
    "validate_workspace",
]
