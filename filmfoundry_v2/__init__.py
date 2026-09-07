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
from .compiler import compile_canonical
from .visual_control import VisualControlPlan, parse_visual_control, validate_visual_control
from .alignment import validate_visual_control_alignment
from .experiments import record_experiment_result
from .capabilities import CapabilitySnapshot, capability_allows, load_capability_snapshot
from .ledger import (
    ArtifactRequirement,
    RequirementReport,
    evaluate_requirements,
    production_ledger_report,
    validate_production_ledger,
    validate_production_policy,
)

__version__ = "2.1.0"

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
    "compile_canonical",
    "VisualControlPlan",
    "parse_visual_control",
    "validate_visual_control",
    "validate_visual_control_alignment",
    "record_experiment_result",
    "CapabilitySnapshot",
    "capability_allows",
    "load_capability_snapshot",
    "ArtifactRequirement",
    "RequirementReport",
    "evaluate_requirements",
    "production_ledger_report",
    "validate_production_ledger",
    "validate_production_policy",
]
