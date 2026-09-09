# FilmFoundry clean handoff

**Date:** 2026-09-10
**Source branch:** `codex/filmfoundry-v2.3-creator-read-model`
**Observed HEAD before this documentation pass:** `79585a331d5d1ff536b769ec787770d59d6b8c26`

## Decision

Pause publication. The repository contains a strong technical v3 foundation, but the product is not yet a successful creator-first Skill. A from-zero trial exposed the central gap: the Skill can route a script request to Creative Mode, yet it has no concise, reusable process for premise → logline → characters → dramatic rules → structure → draft → revision.

The local annotated tag `v3.0.0-rc1` points to the earlier release checkpoint. It is local only and must not be pushed or presented as product approval.

## Product boundary

FilmFoundry owns script creation, script analysis and revision, then asset/image/prompt/shot preparation. Humans and external tools own provider calls, video generation, downloads, and aesthetic video QC.

Current code, tests, references, adapters, and guides still contain H3/MiniMax/provider compilation, execution evidence, smoke gates, and video-production responsibilities. These are known pending removals, not accepted v3 responsibilities.

Wucheng is a downstream integration project. Do not add Wucheng identifiers, paths, counts, fixtures, or status rules to FilmFoundry Core. The separate Wucheng working tree is dirty and must remain untouched by this cleanup. A final read-only check observed 123 tracked deletions under its `99_归档` path; they pre-existed this FilmFoundry knowledge pass and their ownership is unresolved, so do not restore, stage, or delete anything there from this handoff.

## Six-surface status

| Surface | Status | Evidence / action |
|---|---|---|
| Code | Pending | Technical v3 contracts exist; provider-specific product debt remains active. |
| Docs | Changed and verified | Public status, documentation index, historical banners, and this handoff are reconciled in this pass. |
| Runtime | Out of scope | FilmFoundry is a distributable Skill; downstream project Runtime remains project-owned. |
| Rules | Changed and verified | `AGENTS.md` records current boundaries and verification commands. |
| Memory | Changed and verified | A user-authorized correction note records the creator-first direction without editing machine-generated memory files. |
| Workspace | Pending | Generated output and stale worktree/branch candidates are inventoried below; no deletion is authorized yet. |

## Keep from the technical foundation

- canonical `filmfoundry` v3 namespace and clean-break schemas;
- path traversal protection and UTF-8 BOM-safe current behavior;
- `UNKNOWN` / `INVALID` distinction and provenance;
- state alignment and deterministic serialization;
- Creator Source Catalog, Snapshot, Navigation, and render data model;
- Creative / Commit / Production / Gate as a routing concept, with strict separation between draft and committed facts.

These are implementation assets, not evidence that the creator workflow is fast, clear, or complete.

## Required work before a release decision

1. Write the creator-first contract: one question at a time, minimal context loading, explicit optional depth, and a complete from-zero script path.
2. Remove H3/MiniMax/provider-specific execution, evidence ingestion, provider smoke, and video-quality gate responsibility from active Skill instructions, Python APIs, CLI, tests, templates, adapters, and user docs.
3. Preserve only generic prompt and shot-planning output intended for handoff to external tools.
4. Run a fresh-context trial on a genuinely blank project. Record time, references loaded, user interventions, missing steps, and whether a formal emotional map is produced when useful.
5. Re-run deterministic tests, active-surface scans, package builds, and clean extraction.
6. Review the exact diff, create a deliberate release commit, and only then decide the version and tag. Do not reuse the existing local RC tag as approval.

## Verification baseline

The last dated RC report recorded `299 passed`, clean extraction, and deterministic artifacts. That evidence predates this product reset and proves only the earlier technical checkpoint. Re-run it after the product-scope changes.

```powershell
python -m pytest -q
python scripts/build_release_artifacts.py --out .dist
python scripts/check_clean_extraction.py --wheel .dist/filmfoundry_skills-3.0.0-py3-none-any.whl --archive .dist/filmfoundry-skills-v3.0.0.zip
git diff --check
```

## Cleanup preview — awaiting post-report confirmation

Do not delete these during the knowledge pass. After the cleanup report, resolve exact paths again and ask the user to confirm:

- generated `build/` and `.dist/` outputs;
- `.pytest_cache/`, `__pycache__/`, `*.egg-info/`, and other reproducible caches;
- the clean local worktree `filmfoundry-skills-v133-checkpoint`, if its annotated tag and underlying commit are rechecked;
- stale local branches after verifying unique commits and remote state;
- superseded patch piles or temporary diff bundles, if any are found by the final inventory.

The `filmfoundry-skills` main worktree and `filmfoundry-skills-v2` worktree both contain substantial uncommitted changes and are protected, not cleanup candidates. Historical tags, Git history, dated reports, and plans are not cleanup candidates by default. The Wucheng project and its `99_归档` tree are explicitly out of scope; 123 existing archive deletions were observed and must be preserved pending separate attribution. See `docs/reports/2026-09-09-neat-freak-clean-handoff.md` for the verified inventory.

## New-agent first action

Do not start with Renderer, Projection, Provider smoke, packaging, or another architecture expansion. First inspect `skills/generative-film-production/SKILL.md` and its creative references against one concrete question: can a new creator complete a script from a blank idea without loading production machinery? Make that path work, test it in a fresh context, and only then revisit release readiness.
