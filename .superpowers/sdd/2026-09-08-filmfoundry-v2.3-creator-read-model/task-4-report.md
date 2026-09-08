# Task 4 Report: Navigation and terminology

## Scope

- Added the versioned `creator-terminology.v1` registry with zh-CN-first labels, English fallback, category aliases, and raw-value plus explicit no-explanation output for unknown enums.
- Added immutable `CreatorNavigation` and `CreatorReadModel` contracts. Navigation is derived only from `CreatorSnapshot`; `CreatorSnapshot` remains facts/provenance-only and contains no actions or navigation.
- Added deterministic navigation rules for source coverage and authority conflicts, hard blockers, missing artifacts, missing Observed State, next lifecycle state, and non-blocking advice.
- Actions sort by priority, severity, entity ID, and action ID. Every derived action carries source provenance, a non-null rule ID, prerequisites, and support boundary. One primary action and all same-priority parallel actions remain available.
- Core implementation contains no Wucheng/project-specific branch.
- Review fixes add hard-severity precedence, lifecycle-gated continuity handoffs, non-empty action provenance enforcement, deeply immutable terminology mappings, stable terminology-backed support-boundary IDs, and versioned Navigation/ReadModel schemas.
- Review-fix commit: `bcd2898`.

## TDD Evidence

- RED: `python -m pytest tests/test_v23_creator_read_model_navigation.py -q` -> `6 failed`; failures were the expected missing public Task 4 registry/navigation APIs.
- RED follow-up: the hash-mismatch integrity contract failed with `StopIteration` when its action derivation was temporarily absent.
- GREEN: `python -m pytest tests/test_v23_creator_read_model_navigation.py -q` -> `7 passed` after restoring the integrity rule.
- Focused regression: `python -m pytest tests/test_v23_creator_read_model_contract.py tests/test_v23_creator_read_model_fixtures.py tests/test_v23_creator_read_model_navigation.py -q` -> `54 passed`.
- Review-fix focused regression: `python -m pytest tests/test_v23_creator_read_model_contract.py tests/test_v23_creator_read_model_fixtures.py tests/test_v23_creator_read_model_navigation.py -q` -> `61 passed`.

## Verification

- Full regression: `python -m pytest -q` -> `288 passed in 4.40s`.
- Compile check: `python -m compileall -q filmfoundry_v2` -> exit 0.
- Working-tree `git diff --check` and `git diff -- 99_归档` -> exit 0 with no archive diff.
