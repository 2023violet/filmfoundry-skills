# SDD ledger — plan: FilmFoundry v2.1 视觉控制扩展实施计划

## Scope

Implement the provider-neutral visual-control extension on the v2 release branch. Preserve the v1.3.3 checkpoint, existing v2 contracts, Wucheng invariants, and the archive boundary.

## Task scan

| Task | Inputs/outputs | Shared surface | Ruling |
|---|---|---|---|
| 0 | evidence register and fixtures | docs/tests | baseline facts are recorded, no generated-provider claim |
| 1 | schemas and data model | contracts/public exports | independent artifacts keep Shot Spec stable |
| 2 | validation/alignment | contracts/report | structural failures ERROR; guidance WARNING |
| 3 | skill references/templates | skill docs | documentation may describe controls but cannot promise outcomes |
| 4 | guidance artifacts | visual-control model/compiler | optional controls are explicit and traceable |
| 5 | compiler/CLI/lens | CompiledPayload | source artifacts remain read-only during compile |
| 6 | capabilities/adapters/evidence | provider adapters | unverified capabilities never unlock routes |
| 7 | experiments/QC manifests | evidence model | human review is required for promotion |
| 8 | Wucheng adapter | project files | read-only aggregation; H3 output remains zero |
| 9 | skill workflow/support docs | SKILL.md | main entry remains under 300 lines |
| 10 | reports/release metadata | all checks | release only after full verification |

## Rulings

- Ruling: Use the existing v2 lightweight validators and deterministic ValidationReport rather than adding a runtime JSON Schema dependency — why: preserves the current dependency-free package and compatibility; cost if wrong: schema validation coverage must be tested explicitly.
- Ruling: Treat visual-control artifact references as optional at the core boundary — why: the plan explicitly forbids adding provider-specific fields to Shot Spec; cost if wrong: projects must opt in per shot.

## Status

Task 0: complete — evidence register and fixtures committed.
Task 1: complete — schemas and VisualControlPlan committed.
Task 2: complete — validation and alignment gates committed.
Task 3: complete — references, templates and skill routing committed.
Task 4: complete — spatial, scale, physics, previs and lens guidance committed.
Task 5: complete — compiler and CLI visual-control integration committed.
Task 6: complete — capability snapshot and provider evidence boundary committed.
Task 7: complete — experiment, generation, select and QC contracts committed.
Task 8: complete — Wucheng H3 handoff helpers committed separately in project worktree.
Task 9: complete — user guide, support matrix and small-team workflow committed.
Task 10: complete — verification report committed; full suite and diff check pass.
