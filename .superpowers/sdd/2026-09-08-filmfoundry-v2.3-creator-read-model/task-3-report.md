# Task 3 Report: Typed Creator Snapshot

## Fix Round 1 TDD

- RED: `python -m pytest tests/test_v23_creator_read_model_contract.py -q` -> 8 failed, 31 passed after adding the authority, invalid-source, provenance, version, and recursive-schema behavioral tests.
- RED follow-ups: the missing-source test and the invalid-current/historical-fallback test each failed once for the expected missing behavior.
- GREEN: `python -m pytest tests/test_v23_creator_read_model_contract.py -q` -> 41 passed.
- Focused regression: `python -m pytest tests/test_v23_creator_read_model_contract.py tests/test_v23_creator_read_model_fixtures.py -q` -> 46 passed.
- Full regression: `python -m pytest -q` -> 280 passed.
- `python -m compileall -q filmfoundry_v2`, working-tree `git diff --check`, and committed-range `git diff --check 3bfc32a..HEAD` passed.

## Fixes

- Production mapping is grouped by `source_kind + scope`; `CURRENT` wins in a scope, and a sole `HISTORICAL` source supplies explicitly historical facts only when that scope has no current declaration. Invalid current sources prevent historical fallback.
- Optional known-parser files that are missing become typed `UNKNOWN` gaps; present unreadable or parser-invalid files become typed `INVALID` gaps. Required invalid sources still fail fast. Invalid/unknown source-kind status taints only the affected aggregates, which exclude failed sources.
- Metrics cite only their contributing sources; production row pointers use `/units/<escaped-id>`; missing-media blockers carry the derived `creator.asset.media` rule; gaps carry source-backed provenance; `AUTHORITY_MISMATCH` compares matching scopes only.
- `CreatorSnapshot.schema_version` is the fixed `Literal["creator-snapshot.v1"]`; tests recursively guard nested dataclass fields, references, and enums against the Snapshot schema. `CreatorNavigation` and `CreatorReadModel` are held for Task 4 and are no longer package exports.
- Removed the six surplus JSON EOF blank lines from the frozen Wucheng fixture.

## Scope

- No Wucheng branch was added to core code or the Snapshot schema. The frozen fixture still proves `75 / 19 / 21 / 0 / 0`.
- Navigation derivation and rendering remain intentionally unimplemented for later v2.3 tasks.
- No live AI-Short-Drama files, Canon, Registry, media, state, provider evidence, or archive paths were read or modified.
