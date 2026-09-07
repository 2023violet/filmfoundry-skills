# Task 3 Report: Typed Creator Snapshot

## RED/GREEN

- RED: `python -m pytest tests/test_v23_creator_read_model_contract.py -q` -> 5 failed, 30 passed. Failures were the missing Snapshot API/dataclass/schema and the two asset observations.
- GREEN: `python -m pytest tests/test_v23_creator_read_model_contract.py tests/test_v23_creator_read_model_fixtures.py -q` -> 42 passed.
- Regression: `python -m pytest -q` -> 276 passed.
- Additional checks: `git diff --check`, Python compilation, fixture-wide Snapshot collection, and JSON Schema validation passed.

## Files

- Added `filmfoundry_v2/creator_read_model.py` with frozen typed entities, provenance, read-only collection, deterministic `to_dict()`/`to_json()`, asset observations, aggregates, coverage, and authority conflicts.
- Exported the v2.3 Snapshot entities and `collect_creator_snapshot` from `filmfoundry_v2/__init__.py`.
- Added `schemas/creator-snapshot.v1.json`.
- Added focused contract tests for deterministic serialization, stable provenance, authority mismatch, invalid coverage, and the frozen boundary fixture.
- Added the self-contained `wucheng-frozen` fixture and registered it in the v2.3 fixture index.

## Decisions

- Snapshot contains facts, provenance, blockers, conflicts, and coverage only; Actions and Navigation are separate typed entities and are not Snapshot fields.
- Registry declarations remain `declared_state`; filesystem observations become the exact readiness enum without rewriting declarations.
- Provenance paths are workspace-relative POSIX paths with source-byte SHA-256 and JSON pointers.
- Current and historical source facts are both parsed; a current narrative source plus historical production mapping emits `AUTHORITY_MISMATCH`.
- Unsupported catalog gaps are `UNKNOWN`; explicitly invalid gaps are `INVALID`; neither contributes a successful aggregate.
- The frozen fixture declares story v3 as `CURRENT` and production mapping as `HISTORICAL`, and proves `75 / 19 / 21 / 0 / 0`.

## Self-review

- No Wucheng identifier, name, or directory branching exists in core code or the Snapshot schema.
- Existing Task 2 source-catalog behavior and all pre-existing tests remain green.
- Snapshot serialization is stable under repeated calls and contains no action/navigation data.
- No live AI-Short-Drama files were read or modified.

## Commit

Implementation commit: `2c91082` (`feat(v2.3): add typed creator snapshot`)

## Concerns

- Navigation derivation and rendering remain intentionally unimplemented for later v2.3 tasks.
- Required invalid catalog sources retain Task 2 fail-fast behavior; `INVALID` Snapshot coverage is represented when a catalog supplies an invalid coverage gap.
