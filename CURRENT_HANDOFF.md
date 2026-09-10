# FilmFoundry clean handoff

**Date:** 2026-09-10
**Primary branch after handoff:** `main`
**Source branch:** `codex/filmfoundry-v2.3-creator-read-model`

## Main integration recovery

On 2026-09-10, an attempted integration moved the v3 working files into the old `main` checkout without creating a Git merge. The old v1/v2 tree and new v3 tree coexisted, while the source v3 worktree appeared deleted.

The recovery preserved the interrupted filesystem snapshot on local branch `rescue/filmfoundry-main-pre-repair-20260910` at commit `8fef9a6`. The v3 source worktree was restored, the documentation cleanup was committed as `8d361f9`, and the real two-parent integration merge was created as `af94d58`.

The merge result deliberately removes the active `filmfoundry_v2` package, v2 schemas, v2 active fixtures/tests, and the old v2 guide. Historical v2 contract coverage remains under `tests/historical/`. The merge result passed 299 tests before this handoff update.

This is a repository integration for AI handoff, not a product release. No new release tag or GitHub Release is authorized by this merge; the existing local `v3.0.0-rc1` tag remains historical technical evidence.
**Observed HEAD before this documentation pass:** `79585a331d5d1ff536b769ec787770d59d6b8c26`

## Decision

Pause publication. The seven-gate instruction-first path from premise → logline → characters → dramatic rules → structure → draft → revision is now implemented, with minimal Creative routing and an optional workbook. An agent-controlled fresh-context rerun completed the behavior contract, but product evidence remains `INSUFFICIENT_EVIDENCE`: no real human creator supplied the decisions, human elapsed time was not measured, and no durable verbatim transcript was committed. See `docs/reports/2026-09-10-creator-first-fresh-context-trial.md`.

The local annotated tag `v3.0.0-rc1` points to the earlier release checkpoint. It is local only and must not be pushed or presented as product approval.

## Product boundary

FilmFoundry owns script creation, script analysis and revision, then asset/image/prompt/shot preparation. Humans and external tools own provider calls, video generation, downloads, and aesthetic video QC.

Current code, tests, references, adapters, and guides still contain H3/MiniMax/provider compilation, execution evidence, smoke gates, and video-production responsibilities. These are known pending removals, not accepted v3 responsibilities.

Wucheng is a downstream integration project. Do not add Wucheng identifiers, paths, counts, fixtures, or status rules to FilmFoundry Core. The separate Wucheng working tree is dirty and must remain untouched by this cleanup. A final read-only check observed 123 tracked deletions under its `99_归档` path; they pre-existed this FilmFoundry knowledge pass and their ownership is unresolved, so do not restore, stage, or delete anything there from this handoff.

## Six-surface status

| Surface | Status | Evidence / action |
|---|---|---|
| Code | Pending | Technical v3 contracts exist; provider-specific product debt remains active. |
| Docs | Changed and verified | Public status, Chinese full-workflow manual, creator workflow, trial protocol/report, documentation index, and this handoff are reconciled in this pass. |
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

These are implementation assets, not evidence that the creator workflow is fast for real human creators or broadly accepted.

## Required work before a release decision

1. Run the registered fresh-context protocol with a real human creator and a genuinely blank project. Preserve the verbatim transcript and record human elapsed time, references loaded, interventions, missing steps, and optional-depth use.
2. Only after that trial passes, write a separate provider-surface classification and cleanup plan; do not mechanically delete active files during classification.
3. Remove H3/MiniMax/provider-specific execution, evidence ingestion, provider smoke, and video-quality gate responsibility from active Skill instructions, Python APIs, CLI, tests, templates, adapters, and user docs.
4. Preserve only generic prompt and shot-planning output intended for handoff to external tools.
5. Re-run deterministic tests, active-surface scans, package builds, and clean extraction.
6. Review the exact diff, create a deliberate release commit, and only then decide the version and tag. Do not reuse the existing local RC tag as approval.

## Verification baseline

The pre-implementation baseline recorded `299 passed`. The creator-first checkpoint adds deterministic routing/workflow/eval coverage and must be verified again on the final tree; package and clean-extraction success prove artifact structure only, not product acceptance or release readiness.

```powershell
python -m pytest -q
$env:SOURCE_DATE_EPOCH = "0"
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir .dist
python scripts/build_release_artifacts.py --out .dist
Remove-Item Env:SOURCE_DATE_EPOCH -ErrorAction SilentlyContinue
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

Do not reimplement the creator workflow or start with Renderer, Projection, Provider smoke, packaging, or another architecture expansion. Run `evals/creator-first-trial-protocol.md` with a real human creator, measured human elapsed time, and a durable verbatim transcript. If and only if that product-evidence gate passes, prepare the separate provider-surface classification and cleanup plan; release remains paused.
