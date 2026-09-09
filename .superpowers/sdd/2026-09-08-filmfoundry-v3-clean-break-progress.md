# FilmFoundry v3.0 clean-break progress

Base: `b6f3f9d` on `codex/filmfoundry-v2.3-creator-read-model`; active implementation remains uncommitted so the existing dirty worktree is preserved.

- Task 0: execution plan and binding decisions recorded.
- Task 1: DONE — clean-break contract tests and package migration; v3 active suite currently passes 298 tests.
- Task 2: DONE — deterministic Creative/Commit/Production/Gate routing and progressive reference profiles (`tests/test_creative_modes.py`, `tests/test_skill_contract.py`).
- Task 3: DONE — generic six-view HTML/Markdown/SVG renderer, deterministic manifest, and `ff render` (`tests/test_render.py`).
- Task 4: DONE — Wucheng fixture and boundary assertions moved to the project adapter; FilmFoundry release keeps only generic fixtures. The adapter now verifies media path/hash evidence, reports 75 assets, 50 verified media, 25 on-disk sentinel markers, 19 historical units, and keeps source runtime statuses under historical history. Project adapter tests: 6 passed; cross-repo six-view render smoke passed.
- Task 5: PARTIAL — v3.0.0 artifacts and project pointer verified after clean extraction, active index/tooling references point to v3, old v2.2 is no longer an active runtime dependency, and legacy v2 document paths are excluded from the archive. FilmFoundry active suite: 298 passed; adapter suite: 6 passed; `git diff --check` clean; no archive changes. A real creator desktop/mobile visual prototype review, standalone skill-validator migration, and a deliberate release commit are still required before creating the local `v3.0.0-rc1` tag.
