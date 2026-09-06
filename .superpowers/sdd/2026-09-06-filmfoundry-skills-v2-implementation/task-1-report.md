# Task 1 report: v2 contract package

Implemented the additive `filmfoundry_v2` contract layer. The v1.3.3 source,
fixtures, and tests were not modified by this task.

## Public APIs

The package root and focused modules expose:

- `validate_workspace_manifest(data)` and `resolve_manifest_path(root, value)`
- `validate_asset_registry(rows)`
- `validate_shot_spec(data)`
- `parse_prompt_metadata(text)` and `validate_prompt_markdown(text)`
- `validate_state_transition(old, new)` and `validate_production_state(data)`
- `validate_evidence(data)`
- `validate_reference_graph(graph)`
- `LIFECYCLE_STATES`

Focused import modules (`workspace`, `assets`, `shots`, `prompts`, `state`,
`evidence`, `references`) are thin re-exports so the CLI can depend on stable
names without duplicating validation logic.

## Contract behavior

- Stable ASCII IDs are enforced with `^[A-Z][A-Z0-9_]{2,63}$`.
- Unknown fields are rejected unless placed under `extensions`.
- Manifest authority and `99_归档` read-only declarations are checked.
- Manifest-relative paths reject absolute paths and traversal outside root.
- Asset hashes, dimensions, profile-specific aspect rules, state, and duplicate
  IDs are validated without resampling media.
- Shot conditional fields cover dialogue, reverse-angle eyeline, prop
  interaction, and continuous handoff requirements; source duration must cover
  edit target duration.
- Prompt JSON metadata fences and all fixed Markdown section headings are
  required; reference slots must be unique and fully role-bound.
- Lifecycle transitions cannot skip gates. Video-ready states require visual
  control alignment and provider evidence. Partial selects require a contiguous
  source range and observed state.
- `OBSERVED_ONCE` evidence cannot be promoted to default behavior.
- Reference/dependency graph edges must point at known nodes and be unique.

## Fixtures and verification

JSON Schemas live under `schemas/` and golden JSON/Markdown fixtures live under
`tests/fixtures/v2/golden/`; together they cover the manifest, registry, shot,
prompt, state, evidence, and reference graph.

Command:

```text
python -m pytest -q tests/test_v2_contracts.py
```

Result: `19 passed`.
