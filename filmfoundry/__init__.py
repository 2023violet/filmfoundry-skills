"""FilmFoundry v3 production contracts.

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
from .script_analysis import ScriptAnalysis, parse_script_analysis, validate_script_analysis
from .beat_map import EmotionalBeatMap, parse_emotional_beat_map, production_requirement_facts, validate_emotional_beat_map
from .scene_topology import SceneTopology, parse_scene_topology, validate_scene_topology
from .coverage import LocationCoverageSet, parse_location_coverage, validate_location_coverage
from .look_bible import LookBible, parse_look_bible, validate_look_bible
from .dependency_graph import DependencyGraph, build_dependency_graph, parse_dependency_graph, validate_dependency_graph
from .creator_sources import (
    CreatorCatalogSource,
    CreatorProjectAdapter,
    CreatorSourceCatalog,
    CreatorSourceCoverageGap,
    discover_creator_sources,
)
from .creator_read_model import (
    CreatorAction,
    CreatorAsset,
    CreatorBlocker,
    CreatorConflict,
    CreatorContinuityEdge,
    CreatorCoverage,
    CreatorEmotionPoint,
    CreatorMetric,
    CreatorNarrativeNode,
    CreatorNavigation,
    CreatorOverview,
    CreatorProvenance,
    CreatorReadModel,
    CreatorShot,
    CreatorSnapshot,
    CreatorSourceRef,
    CreatorTerminologyRegistry,
    TERMINOLOGY_REGISTRY,
    TERMINOLOGY_SCHEMA_VERSION,
    build_creator_read_model,
    collect_creator_snapshot,
    derive_creator_navigation,
    get_creator_terminology,
    terminology_label,
    translate_creator_term,
)

__version__ = "3.0.0"

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
    "ScriptAnalysis",
    "parse_script_analysis",
    "validate_script_analysis",
    "EmotionalBeatMap",
    "parse_emotional_beat_map",
    "validate_emotional_beat_map",
    "production_requirement_facts",
    "SceneTopology",
    "parse_scene_topology",
    "validate_scene_topology",
    "LocationCoverageSet",
    "parse_location_coverage",
    "validate_location_coverage",
    "LookBible",
    "parse_look_bible",
    "validate_look_bible",
    "DependencyGraph",
    "build_dependency_graph",
    "parse_dependency_graph",
    "validate_dependency_graph",
    "CreatorCatalogSource",
    "CreatorProjectAdapter",
    "CreatorSourceCatalog",
    "CreatorSourceCoverageGap",
    "discover_creator_sources",
    "CreatorAction",
    "CreatorAsset",
    "CreatorBlocker",
    "CreatorConflict",
    "CreatorContinuityEdge",
    "CreatorCoverage",
    "CreatorEmotionPoint",
    "CreatorMetric",
    "CreatorNarrativeNode",
    "CreatorNavigation",
    "CreatorOverview",
    "CreatorProvenance",
    "CreatorReadModel",
    "CreatorShot",
    "CreatorSnapshot",
    "CreatorSourceRef",
    "CreatorTerminologyRegistry",
    "TERMINOLOGY_REGISTRY",
    "TERMINOLOGY_SCHEMA_VERSION",
    "build_creator_read_model",
    "collect_creator_snapshot",
    "derive_creator_navigation",
    "get_creator_terminology",
    "terminology_label",
    "translate_creator_term",
]
