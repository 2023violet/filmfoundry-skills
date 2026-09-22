# FilmFoundry clean handoff

**Date:** 2026-09-22
**Primary branch after handoff:** `main`
**Source branch:** `codex/filmfoundry-v2.3-creator-read-model`

## Main integration recovery

On 2026-09-10, an attempted integration moved the v3 working files into the old `main` checkout without creating a Git merge. The old v1/v2 tree and new v3 tree coexisted, while the source v3 worktree appeared deleted.

The recovery preserved the interrupted filesystem snapshot on local branch `rescue/filmfoundry-main-pre-repair-20260910` at commit `8fef9a6`. The v3 source worktree was restored, the documentation cleanup was committed as `8d361f9`, and the real two-parent integration merge was created as `af94d58`.

The merge result deliberately removes the active `filmfoundry_v2` package, v2 schemas, v2 active fixtures/tests, and the old v2 guide. Historical v2 contract coverage remains under `tests/historical/`. The merge result passed 299 tests before this handoff update.

This is a repository integration for AI handoff, not a product release. No new release tag or GitHub Release is authorized by this merge; the existing local `v3.0.0-rc1` tag remains historical technical evidence.
**Observed HEAD at the 2026-09-10 handoff:** `79585a331d5d1ff536b769ec787770d59d6b8c26`

## P0/P1 generalization implementation — 2026-09-21

The requested implementation pass keeps the Core project/style/provider-neutral:

- `filmfoundry.profiles` now provides minimal Project Profile and Style Profile
  dataclasses, explicit `UNKNOWN` values, JSON loading, and structural validation.
- `filmfoundry.modes.route_creation_goal` now routes from-zero ideas, existing
  scripts, short-video tests, scene assets, style exploration, and single-shot
  handoffs before selecting a work mode.
- Prompt compilation now emits a deterministic Provider-neutral handoff. The old
  provider argument is accepted only for compatibility and is ignored by Core.
- Gate routing no longer authorizes provider calls or provider smoke/media-audit;
  external adapters receive the handoff and own execution and returned-media review.
- Provider-specific Python smoke adapters were removed from the active Core boundary;
  external adapter references remain documentation-only translation surfaces.

The requested five-case/multi-style regression matrix and P2 work were explicitly
not implemented. Remaining release blockers are fresh human creator evidence and a
final review of legacy provider evidence/runtime fields that are still representable
for external handoff history.

## Human decision layer implementation — 2026-09-21

The creator-facing presentation gap was addressed without adding a second source
of truth:

- `filmfoundry.decision` derives an evidence-bound Decision Brief from the
  existing Creator Read Model. It exposes the current question, recommendation,
  operational options, locked facts, open risks, next action, and evidence IDs.
- `ff render` now includes a deterministic `decision` view and emits
  `render-manifest.v3`; this view is a review aid, not creative approval or a
  provider/media-quality gate.
- The active Skill now routes human review to
  `references/45-human-decision-layer.md` and provides
  `templates/creator-decision-brief.md`. Creative trade-offs must still be
  proposed or accepted in the creator-first conversation rather than inferred
  from runtime metadata.
- A Provider-neutral handoff request now routes to Production mode instead of
  remaining in Creative mode, while still keeping provider execution external.

This improves human readability and routing, but it does not replace the required
fresh-context trial with a real creator or decision-maker.

## P0 adaptive execution lanes — 2026-09-22

The creator workflow now separates interaction speed from Gate semantics:

- `FAST/R0` batches reversible exploration into a small creator-readable package;
- `STANDARD/R1` groups related creative decisions and asks only blocking questions;
- `STRICT/R2` preserves Canon, acceptance, external-cost, and irreversible-action approval;
- `RECOVERY/R1` diagnoses the narrowest failed layer and resumes from saved state.

`filmfoundry.modes.route_request()` exposes the selected `lane` and `risk_level`, and
the route CLI includes both fields. `OPEN`, `DEFERRED`, and `NOOP` make non-blocking
unknowns and safe no-action outcomes explicit. This is a P0 workflow optimization,
not evidence that human creator elapsed time has improved; the fresh-context trial
and A/B measurement remain required before publication claims.

## P1 execution evidence and soft budgets — 2026-09-22

Each route now exposes a soft execution budget: maximum blocking decisions, internal
steps, and automatic revisions. When a ceiling is reached, the workflow returns the
current artifact as `DEFERRED` with a resume trigger instead of continuing a planning
loop; a budget never bypasses a Strict Gate.

`references/46-execution-evidence.md` and `templates/execution-evidence.md` define
the cycle-level record. `evals/creator-first-trial-protocol.md` now compares the
previous strict path against the adaptive path with the same fresh request, model,
and blank-project state. This provides a measurement path, not a completed human
benchmark; evidence remains `INSUFFICIENT_EVIDENCE` until a real creator supplies
the transcript, elapsed time, interventions, and final artifacts.

## Decision

Pause publication. The seven-gate instruction-first path from premise → logline → characters → dramatic rules → structure → draft → revision is now implemented, with minimal Creative routing and an optional workbook. An agent-controlled fresh-context rerun completed the behavior contract, but product evidence remains `INSUFFICIENT_EVIDENCE`: no real human creator supplied the decisions, human elapsed time was not measured, and no durable verbatim transcript was committed. See `docs/reports/2026-09-10-creator-first-fresh-context-trial.md`.

The local annotated tag `v3.0.0-rc1` points to the earlier release checkpoint. It is local only and must not be pushed or presented as product approval.

## Product boundary

FilmFoundry owns script creation, script analysis and revision, then asset/image/prompt/shot preparation. Humans and external tools own provider calls, video generation, downloads, and aesthetic video QC.

Historical schemas and external adapter references still mention provider evidence
for traceability, but active Core compilation and routing do not execute providers or
run provider smoke/media gates. Those external evidence fields are not accepted as
Core product responsibilities.

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
3. Finish the read-only classification of remaining historical provider evidence/runtime fields; do not reintroduce execution into Core.
4. Preserve only generic Prompt and shot-planning output intended for handoff to external tools.
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

Next action is the fresh-context creator trial in `evals/creator-first-trial-protocol.md`, with a real human creator, measured human elapsed time, and a durable verbatim transcript. Do not start the five-case matrix or P2 expansion; release remains paused until creator evidence is complete.
