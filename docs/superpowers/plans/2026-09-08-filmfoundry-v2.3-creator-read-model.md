# FilmFoundry Skills v2.3.0 Creator Read Model and Production Navigation Implementation Plan

> Execution: use `superpowers:subagent-driven-development`; feature code follows test-driven development. Test, review, and commit every task independently.

## Goal

Build one trusted, read-only creator model over the existing FilmFoundry machine contracts and render traceable HTML, Markdown, and SVG production views without changing Canon, Runtime, Registry, media, production state, archives, or provider evidence.

The fixed data flow is:

```text
Canon / Runtime / JSON / CSV / Media
                  ->
        Creator Source Catalog
                  ->
       Parser Registry + Validation
                  ->
        Typed Creator Snapshot
                  ->
    Deterministic Navigation Rules
                  ->
         Creator Read Model
                  ->
      HTML / Markdown / SVG Views
```

## Baseline and constraints

- Release base: `941fcda99506427a521d1ff20252bf7544114ea3`, version `2.2.0`, `234 passed`, main `SKILL.md` 280 lines.
- Wucheng baseline: 75 Registry assets, 19 historical production units, 21 missing character media, 0 Generation, 0 Select; story v3.0 is current authority.
- Do not change existing Workspace, Asset, Shot, Prompt, State, Evidence, Emotional Beat Map, or Provider contracts.
- Do not restore deleted character images, invoke a provider, or modify `99_归档`.
- Creator Layer is read-only and never repairs source data.
- Core must not branch on Wucheng project IDs, names, or directory literals.
- Missing or invalid data is `UNKNOWN` or `INVALID`; never replace it with a successful zero.
- Provenance is required at entity/aggregate conclusion level, not around every scalar.
- v2 emotion data is discrete. Do not infer or smooth peaks, valleys, breathing zones, climax, or aftershock.
- Default output is deterministic and contains no current time.
- Preserve argparse exit code 2.

## Public contracts

Add `creator-source-catalog.v1.json`, `creator-snapshot.v1.json`, and optional `narrative-index.v1.json`.

Source Catalog fields:

```text
schema_version
project_id
runtime_path
sources[]:
  source_id
  source_kind
  path
  path_base: WORKSPACE_ROOT | RUNTIME_DIR
  parser_id
  schema_version
  authority_role: CURRENT | HISTORICAL | SUPPORTING
  scope
  required
```

Rules: stable ASCII machine IDs; paths stay inside the workspace; `99_归档` is never active; one `CURRENT` per `source_kind + scope`; `HISTORICAL` and `SUPPORTING` never override `CURRENT`; adapters declare authority explicitly.

Runtime types:

```python
@dataclass(frozen=True)
class CreatorSourceRef:
    source_id: str
    source_kind: str
    path: str
    pointer: str
    sha256: str
    authority_role: str
    version: str | None

@dataclass(frozen=True)
class CreatorProvenance:
    source_refs: tuple[CreatorSourceRef, ...]
    derivation: str  # DIRECT | VALIDATED | AGGREGATED
    rule_id: str | None

@dataclass(frozen=True)
class CreatorMetric:
    metric_id: str
    value: int | float | str | None
    data_status: str  # KNOWN | UNKNOWN | INVALID
    provenance: CreatorProvenance
```

Add typed `CreatorOverview`, `CreatorNarrativeNode`, `CreatorEmotionPoint`, `CreatorAsset`, `CreatorShot`, `CreatorContinuityEdge`, `CreatorBlocker`, `CreatorCoverage`, and `CreatorAction`.

Assets retain `declared_state` and `observed_readiness`, whose values are `PRESENT_HASH_OK`, `PRESENT_HASH_UNVERIFIED`, `PRESENT_HASH_MISMATCH`, `MISSING`, `NOT_APPLICABLE`, and `UNKNOWN`.

The lifecycle is acyclic:

```text
CreatorSnapshot -> CreatorNavigation -> CreatorReadModel(snapshot + navigation)
```

Public functions:

```python
discover_creator_sources(root: Path, adapter: CreatorProjectAdapter | None = None) -> CreatorSourceCatalog
collect_creator_snapshot(root: Path, catalog: CreatorSourceCatalog) -> CreatorSnapshot
derive_creator_navigation(snapshot: CreatorSnapshot) -> CreatorNavigation
build_creator_read_model(root: Path, catalog: CreatorSourceCatalog) -> CreatorReadModel
render_creator_view(model: CreatorReadModel, out_dir: Path, *, views: set[str], output_formats: set[str], language: str = "zh-CN", include_render_time: bool = False) -> RenderResult
```

Dataclasses are the runtime API and JSON Schema is the serialization contract. Contract tests keep fields, enums, and round trips aligned without a new runtime framework.

Narrative Index expresses `Season -> Arc -> Episode -> Sequence -> Scene -> Beat` with stable ID, display name, narrative responsibility, parent, and Canon source. It never copies story content. Missing indexes display a coverage gap; Markdown headings are not guessed.

## Authority, terminology, and navigation

One unique `CURRENT` source supplies current declared facts. `HISTORICAL` is comparison only, `SUPPORTING` adds context, and filesystem checks add observed facts. Observations never rewrite declarations. Aggregates count only successfully parsed sources. Metrics, blockers, conflicts, and actions carry provenance.

Add a versioned zh-CN-first, English-fallback terminology registry covering lifecycle, asset state, evidence level, select type, authority, severity, support boundary, and observed readiness. Unknown values show the raw value and an explicit no-explanation label.

Navigation priority:

1. unreadable sources or authority conflicts;
2. integrity, path escape, archive boundary, or hard blockers;
3. missing conditionally required artifacts;
4. missing previous-shot Observed State;
5. next lifecycle state;
6. non-blocking advice.

Sort by `priority -> severity -> entity_id -> action_id`. Show one primary action and all equal-priority parallel actions. Every action includes rule ID, reason, prerequisites, support boundary, and sources.

## Dashboard and CLI

Output `index`, `emotional-map`, `story-map`, `assets`, `shots`, and `continuity` as HTML and Markdown, plus `emotional-map.svg`, `creator-snapshot.json`, and `render-manifest.json`.

Use a dark, high-contrast, dense production UI with text plus status icons, semantic HTML, accessible `<details>`, local CSS/SVG, and minimal inline JavaScript. Do not use CDNs, remote fonts/scripts, large frameworks, card-within-card layouts, clipped text, or color-only state. Workspace media uses safe relative paths and is never copied. Missing media shows a placeholder and source path. HTML escape all content and reject external URLs.

Emotion v2 renders only points, straight segments, or steps. Missing values say data is unavailable.

Add:

```text
ff render --root <path>
          [--runtime <project-runtime.json>]
          [--source-map <creator-source-catalog.json>]
          [--adapter <name>]
          [--view all|overview|emotion|story|assets|shots|continuity]
          [--output-format html|markdown|both]
          [--lang zh-CN|en]
          [--out <directory>]
          [--include-render-time]
          [--format text|json]
```

Exit codes: 0 success without integrity ERROR; 1 rendered with integrity ERROR; 2 argparse usage; 3 discovery/input contract failure; 4 internal render error. Ordinary production blockers and warnings do not affect the exit code. Render integrity-error dashboards where trustworthy data remains; discovery/core parsing failures must not produce misleading pages.

Default JSON is UTF-8/LF/sorted keys. HTML, Markdown, and SVG contain no current time by default. The manifest records input, Snapshot, and output hashes. Optional render time does not affect the content consistency hash. Repeated default renders are byte-identical and source hashes are unchanged.

## Task 0: Baseline and specifications

- Confirm branch starts at `941fcda` and preserve the clean v2.2 baseline.
- Record public API, `234 passed`, main Skill line count, and release file hashes.
- Add the v2.3 design spec, data mapping, execution plan, and a tracked baseline/evidence report.
- Initialize the SDD execution ledger.
- Verify documentation-only checks and commit independently.

## Task 1: Golden fixtures and failing tests

- Add fixtures for Empty Project, Early Development, Asset Production, Shot Production, Blocked Dependency, Full Select, Partial Select, Continuity Conflict, Season Emotion, Episode Emotion, Chinese Project, and English Project.
- Add a generic Smoke Project with 1 Season, 2 Episodes, 5 Assets, 4 Shots, and 1 Continuity Chain.
- Write failing tests for multiple CURRENT authorities, path escape, archive-as-active-source, LOCKED-but-missing media, hash mismatch, unknown schema, unknown enum, and dataclass/Schema drift.
- Preserve fixture clarity and commit failing-contract scaffolding independently; failures must be the expected missing implementation, not malformed fixtures.

## Task 2: Source Catalog and Parser Registry

- Implement Source Catalog models, parsing, discovery, and validation.
- Dispatch parsers by `parser_id + schema_version`.
- Support `WORKSPACE_ROOT` and `RUNTIME_DIR` path bases.
- Reject workspace escape and active archive sources; detect multiple CURRENT authorities.
- Core must not branch on `project_id`; unsupported formats produce a coverage gap or contract error.
- Cover Windows/POSIX syntax, Chinese paths, and case behavior. Run focused and regression tests, review, and commit.

## Task 3: Typed Creator Snapshot

- Implement all typed entities and deterministic serialization.
- Add entity, metric, blocker, conflict, and coverage provenance.
- Compute `declared_state` separately from `observed_readiness`.
- Represent current authority, historical mapping, and `AUTHORITY_MISMATCH` without choosing or rewriting a source.
- Coverage distinguishes `KNOWN`, `UNKNOWN`, and `INVALID` and excludes failed sources from valid aggregates.
- Add a frozen Wucheng fixture that proves `75 / 19 / 21 / 0 / 0` and commit after focused/regression tests and review.

## Task 4: Navigation and terminology

- Implement the versioned terminology registry with zh-CN-first and English fallback.
- Implement deterministic navigation rules, priorities, and sorting.
- Keep Snapshot action-free; derive `CreatorNavigation` only from Snapshot; compose in `CreatorReadModel`.
- Ensure every action has provenance, rule ID, prerequisites, and support boundary.
- Test unknown enums, primary/parallel actions, and stable ordering; review and commit.

## Task 5: P0.5 visual prototype gate

- Build Overview, Emotional Map, and Shot Board prototypes using the real, validated Wucheng Read Model, never hand-authored prototype data.
- Produce desktop and mobile screenshots and inspect them visually.
- Verify within the artifact: project phase/current authority/largest blocker can be found in 30 seconds; emotional trend in 10 seconds; 21 missing character media are immediately visible; story v3 is clearly distinct from 19 historical units; primary and parallel actions are findable; no overflow, overlap, blank SVG, or unreadable text.
- If the gate fails, modify only Presenter/visual code and never fake inputs or alter the Machine Layer.
- Record evidence, focused tests, visual inspection, review, and commit.

## Task 6: Formal renderer

- Add one shared Presenter consumed by HTML, Markdown, and SVG renderers.
- Render all six formal views with progressive disclosure, filtering, safe links, and local media previews.
- Escape HTML, enforce path safety, and reject external URLs.
- Assert metrics, states, blockers, and actions agree across formats.
- Run focused/regression/security-oriented rendering tests, review, and commit.

## Task 7: CLI and deterministic manifest

- Add the complete `ff render` CLI contract and stable exit codes.
- Implement deterministic output and `render-manifest.json`.
- Verify `--root` works identically from arbitrary current directories.
- Verify two default runs are byte-identical and introduce no source changes.
- Review and commit.

## Task 8: Wucheng adapter

- Adapter only locates `07_运行时/RUNTIME/project-runtime.json`, declares path bases, marks story v3 CURRENT and existing production mapping HISTORICAL, and selects supported core parsers.
- Core owns entities, metrics, continuity, conflicts, and actions.
- Live acceptance must show 75 assets, 19 HISTORICAL units, 21 missing character media, 0 Generation, 0 Select, and Authority Mismatch YES.
- Default output is `09_新生成产出/creator-dashboard/`.
- Do not restore images or change Registry, Canon, states, media, provider evidence, or `99_归档`.
- Test read-only behavior, review, and commit in the appropriate repository.

## Task 9: Generic project validation

- Run complete `ff render` on the generic Smoke Project.
- Assert Core and Renderer contain no Wucheng ID, name, or directory branching.
- Use the same Snapshot, Navigation, and Renderer as Wucheng.
- Record this as generic code-path proof only, not cross-project creator validation.
- Review and commit.

## Task 10: Skill, documentation, packaging, and deployment

- Add/update Creator Visualization Architecture, Data Mapping, Terminology, User Guide, Migration Guide, Support Matrix, README, and CHANGELOG.
- Add only the Creator View entry and decision order to the main `SKILL.md`; keep it at or below 300 lines.
- Package `filmfoundry_v2/`, `schemas/`, `skills/generative-film-production/`, `pyproject.toml`, README, and CHANGELOG.
- Create `filmfoundry-skills-v2.3.0` beside v2.2 under Wucheng `08_工具与技能`; preserve prior releases.
- After final acceptance, update the Runtime tool pointer. Project wrappers use relative `python -m filmfoundry_v2`, not global installation.
- Create a separate ZIP and packaging audit; review and commit. Do not publish or tag final release in this task.

## Task 11: Final acceptance and release readiness

- Run the original 234 tests and all v2.3 unit/integration/contract tests.
- Verify dataclass/Schema round trips and all twelve fixtures.
- Verify live Wucheng and generic Smoke Project results.
- Verify injection/path safety, deterministic repeated renders, and unchanged source hashes.
- Perform desktop/mobile visual checks and canvas/SVG pixel checks where applicable.
- Run `git diff --check`; verify `git diff -- 99_归档` is empty, v2.2/v1.3.3 files are unchanged, and main `SKILL.md` is at most 300 lines.
- Produce final verification and evidence-gap reports.
- Create `v2.3.0-rc1` only if this is a local, reversible release marker permitted by repository policy; do not push, publish, merge, or create the final `v2.3.0` tag without explicit authority.

## Maturity gates

- `TECHNICALLY_VERIFIED`: automated contracts, read-only behavior, determinism, and rendering checks pass.
- `CREATOR_REVIEWED`: project owner reviews prototypes/final views and can find required information in the stated time.
- `CREATOR_VALIDATED`: at least two creators complete the defined tasks in two real projects with at least 80% success and no critical state misreading.

Generic fixtures do not count toward `CREATOR_VALIDATED`. v2.3.0 may be released at `CREATOR_REVIEWED`; do not claim `CREATOR_VALIDATED` without the evidence.

## Risks and rulings

The largest risk is incorrectly merging current story authority, historical production status, and filesystem reality. The next risks are a technically correct but unusable UI, Wucheng-specific logic entering Core, and drift among dataclasses, validators, and schemas.

The binding defaults are: Creator Layer is read-only; no automatic repair; no v2 emotion smoothing; ordinary blockers do not fail CLI; missing data is UNKNOWN; prototypes consume the real Read Model; Emotional Beat Map v3 is outside this version; Tasks 0-5 must pass the visual prototype gate before Tasks 6-11.
