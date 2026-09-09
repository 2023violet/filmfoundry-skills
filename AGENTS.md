# FilmFoundry repository guidance

## Purpose

FilmFoundry is a general, creator-first Skill for script development and visual-production preparation. Do not add Wucheng or any other project-specific branch to Core.

## Current state

- The local v3 technical RC is not approved for publication.
- Product acceptance is blocked by the missing from-zero script-creation workflow.
- H3/provider execution, provider evidence ingestion, video generation, and video-quality gates are deprecated product surfaces pending removal.
- Read `CURRENT_HANDOFF.md` before changing behavior or release state.

## Commands

```powershell
python -m pytest -q
python scripts/build_release_artifacts.py --out .dist
python scripts/check_clean_extraction.py --wheel .dist/filmfoundry_skills-3.0.0-py3-none-any.whl --archive .dist/filmfoundry-skills-v3.0.0.zip
git diff --check
```

## Boundaries

- Keep Core project-neutral and provider-neutral.
- Do not claim creator speed, model obedience, market success, or visual quality from static tests.
- Do not treat authored fixtures as a fresh-context agent benchmark.
- Preserve dirty worktrees and unrelated user changes.
- Do not delete cleanup candidates until a cleanup report has been delivered and the user confirms the exact targets afterward.
- Do not modify downstream project assets, Canon, Runtime, or archives from this repository.

## Knowledge map

- `README.md`: concise public status and product boundary.
- `docs/README.md`: active documentation index.
- `CURRENT_HANDOFF.md`: current branch, decisions, pending work, and verification.
- `CHANGELOG.md`: immutable version history plus the current unreleased section.
- `docs/reports/` and `docs/superpowers/`: dated evidence and historical plans, not current instructions.
