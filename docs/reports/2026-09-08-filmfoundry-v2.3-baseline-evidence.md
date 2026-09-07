# FilmFoundry Skills v2.3.0 Baseline Evidence

## Scope

This record fixes the v2.2 baseline before Creator Read Model implementation.
It is evidence for the FilmFoundry repository only. It does not claim live
Wucheng adapter, provider, media, rendering, or creator-usability validation.

## Git Baseline

- Required base and current `HEAD` before this documentation task:
  `941fcda99506427a521d1ff20252bf7544114ea3`
  (`docs: record FilmFoundry v2.2 verification boundaries`).
- Branch: `codex/filmfoundry-v2.3-creator-read-model`.
- Package version: `2.2.0` from `pyproject.toml` and
  `filmfoundry_v2.__version__`.
- Before Task 0, the tracked tree was clean. The approved v2.3 execution plan
  was the only untracked file and is intentionally included by this task.

## Fresh Verification

| Command | Result |
|---|---|
| `python -m pytest -q` | `234 passed in 2.64s` |
| `git diff --check` before documentation edits | passed with no output |
| `(Get-Content skills/generative-film-production/SKILL.md).Count` | `280` lines |
| `python -m filmfoundry_v2.cli --help` | Existing commands are `init`, `validate`, `index`, `compile`, `audit`, `migrate`, `requirements`, and `ledger`. |
| `python -m filmfoundry_v2.cli` | argparse reports a required command; its existing usage-error contract is exit code `2`. |

## Release Surface Hashes

SHA-256 values are calculated from the required base worktree files. Git blob
IDs are recorded separately because they use Git's object hash format.

| File | SHA-256 | Git blob ID |
|---|---|---|
| `CHANGELOG.md` | `09eb8e93b0804edcc9b655ee23e4e1c5838924a65150e6904d5c0819a1ce6ece` | `7f851aa67731ee785678b529215e265de984f2b5` |
| `LICENSE` | `37ef7daeefa58c5ab20c74385144c0ab04918eddc5245774f727c9eca191622f` | `0053000b0d9e2ab8b80f7a6ae34986fac9e66901` |
| `README.md` | `dc2b928cf5a91d2b75a0e6077b1281964746bab7ce28e493ded033f69a4f0605` | `f9a63c21b0a1c9d91b71cc2d26cb458389c4dcd8` |
| `pyproject.toml` | `53c497d8f40582ee3a4206c2ddfc2929ef901fa4684c84b1947ae91c43eacc86` | `a363d3e00017a774e3f235696ac9a7c070f3a7a3` |
| `skills/generative-film-production/SKILL.md` | `e44ee435db00200809f2d7befdc4a35a8bd385e5d9e3d974c08b52870247213f` | `fa5593527faedc4d46fd41301f5125250cc6b907` |

## Existing Public API

The `filmfoundry_v2` package reports version `2.2.0` and exports 52 symbols:

```text
LIFECYCLE_STATES, parse_prompt_metadata, resolve_manifest_path,
validate_asset_registry, validate_evidence, validate_prompt_markdown,
validate_production_state, validate_reference_graph, validate_shot_spec,
validate_state_transition, validate_workspace_manifest, __version__,
ValidationIssue, ValidationReport, CompiledPayload, ProviderAdapter,
validate_workspace, compile_canonical, VisualControlPlan, parse_visual_control,
validate_visual_control, validate_visual_control_alignment,
record_experiment_result, CapabilitySnapshot, capability_allows,
load_capability_snapshot, ArtifactRequirement, RequirementReport,
evaluate_requirements, production_ledger_report, validate_production_ledger,
validate_production_policy, ScriptAnalysis, parse_script_analysis,
validate_script_analysis, EmotionalBeatMap, parse_emotional_beat_map,
validate_emotional_beat_map, production_requirement_facts, SceneTopology,
parse_scene_topology, validate_scene_topology, LocationCoverageSet,
parse_location_coverage, validate_location_coverage, LookBible,
parse_look_bible, validate_look_bible, DependencyGraph,
build_dependency_graph, parse_dependency_graph, validate_dependency_graph
```

Task 0 adds no runtime API, Schema, CLI command, or change to these exports.

## Guardrails For Follow-on Tasks

- Preserve existing public Workspace, Asset, Shot, Prompt, State, Evidence,
  Emotional Beat Map, and Provider contracts.
- Do not touch Wucheng, provider calls, media, or `99_归档` in this task.
- Creator sources, snapshots, navigation, and views remain read-only.
- Missing or invalid source data remains `UNKNOWN` or `INVALID`; it is never
  reported as a successful zero.
- Main `SKILL.md` starts at 280 lines and must remain at or below 300 lines.
