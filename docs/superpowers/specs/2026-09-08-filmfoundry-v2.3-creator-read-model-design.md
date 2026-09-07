# FilmFoundry Skills v2.3.0 Creator Read Model Design

## Purpose

FilmFoundry v2.3 adds a read-only Creator Layer over existing FilmFoundry
machine contracts. It turns validated Canon, Runtime, JSON, CSV, and media
observations into traceable production views. It does not alter authoring
authorities, lifecycle state, Registry data, provider evidence, media, or
archives.

The implementation boundary is:

```text
Canon / Runtime / JSON / CSV / Media
                  -> Creator Source Catalog
                  -> Parser Registry + Validation
                  -> Typed Creator Snapshot
                  -> Deterministic Navigation
                  -> Creator Read Model
                  -> HTML / Markdown / SVG Views
```

`CreatorSnapshot -> CreatorNavigation -> CreatorReadModel` is acyclic.
Snapshot contains facts and provenance only. Navigation derives actions from
Snapshot. Renderers consume the Read Model and do not add production rules.

## Baseline And Scope

- Base release: `941fcda99506427a521d1ff20252bf7544114ea3` (`2.2.0`).
- Existing Workspace, Asset, Shot, Prompt, State, Evidence, Emotional Beat
  Map, and Provider contracts remain public and unchanged.
- The Creator Layer never repairs source data or turns missing/invalid inputs
  into successful zero values. It reports `UNKNOWN` or `INVALID`.
- The Core must not branch on a Wucheng identifier, name, or directory.
- `99_归档` is never an active creator source. The layer does not restore
  character media, invoke a provider, or modify archive content.
- v2 emotion data remains discrete. Views may draw points, straight segments,
  or steps, but never infer a peak, valley, breathing zone, climax, or
  aftershock.

## Source Authority

The versioned `creator-source-catalog.v1.json` contract declares the sources
that a project adapter makes available:

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

Machine IDs are stable ASCII IDs. Resolved paths must stay inside the
workspace. There is one `CURRENT` source per `source_kind + scope`.
`HISTORICAL` sources support comparison and `SUPPORTING` sources add context;
neither can override `CURRENT`. The adapter declares authority, while the Core
validates the declaration and records filesystem observations separately.

## Public Creator API

The runtime API is frozen dataclasses plus the following functions:

```python
discover_creator_sources(root: Path, adapter: CreatorProjectAdapter | None = None) -> CreatorSourceCatalog
collect_creator_snapshot(root: Path, catalog: CreatorSourceCatalog) -> CreatorSnapshot
derive_creator_navigation(snapshot: CreatorSnapshot) -> CreatorNavigation
build_creator_read_model(root: Path, catalog: CreatorSourceCatalog) -> CreatorReadModel
render_creator_view(
    model: CreatorReadModel,
    out_dir: Path,
    *,
    views: set[str],
    output_formats: set[str],
    language: str = "zh-CN",
    include_render_time: bool = False,
) -> RenderResult
```

The minimum public data types are `CreatorSourceRef`, `CreatorProvenance`,
`CreatorMetric`, `CreatorOverview`, `CreatorNarrativeNode`,
`CreatorEmotionPoint`, `CreatorAsset`, `CreatorShot`,
`CreatorContinuityEdge`, `CreatorBlocker`, `CreatorCoverage`, and
`CreatorAction`. Dataclasses define the runtime contract. JSON Schema defines
the serialized contract; contract tests keep dataclass fields, enums, and
round trips aligned without adding a runtime framework.

`CreatorSourceRef` records source ID, kind, path, pointer, SHA-256,
authority role, and optional version. `CreatorProvenance` contains source
references, a `DIRECT`, `VALIDATED`, or `AGGREGATED` derivation, and an
optional rule ID. `CreatorMetric` holds an ID, an int/float/string/null value,
a `KNOWN`, `UNKNOWN`, or `INVALID` status, and provenance. Entity and
aggregate conclusions carry provenance; scalar decoration is not required.

Assets preserve both declared state and observed readiness. Observed readiness
is exactly `PRESENT_HASH_OK`, `PRESENT_HASH_UNVERIFIED`,
`PRESENT_HASH_MISMATCH`, `MISSING`, `NOT_APPLICABLE`, or `UNKNOWN`.

The optional `narrative-index.v1.json` expresses only navigation structure:
`Season -> Arc -> Episode -> Sequence -> Scene -> Beat`. Each node has a
stable ID, display name, narrative responsibility, parent, and Canon source.
It never duplicates story content. A missing index is a coverage gap; Markdown
headings are not inferred.

## Navigation And Terminology

Terminology is versioned, zh-CN-first, with English fallback. It covers
lifecycle, asset state, evidence level, select type, authority, severity,
support boundary, and observed readiness. An unrecognized enum is rendered as
the raw value with an explicit no-explanation label.

Navigation sorts actions by `priority -> severity -> entity_id -> action_id`.
It evaluates, in order:

1. unreadable sources and authority conflicts;
2. integrity, path escape, archive boundaries, and hard blockers;
3. conditionally required artifacts that are missing;
4. missing previous-shot Observed State;
5. the next lifecycle state; and
6. non-blocking advice.

The first stable-sorted action is primary. All equal-priority actionable items
remain parallel actions. Every action records rule ID, reason, prerequisites,
support boundary, and source provenance.

## Rendering And CLI

The formal views are `index`, `emotional-map`, `story-map`, `assets`, `shots`,
and `continuity` in HTML and Markdown. The renderer additionally writes
`emotional-map.svg`, `creator-snapshot.json`, and `render-manifest.json`.

The HTML is a dense, high-contrast production interface with semantic markup,
text plus status icons, accessible `details`, local CSS/SVG, and minimal inline
JavaScript. It has no CDN, remote font/script, external URL, copied workspace
media, color-only status, clipped text, large framework, or nested-card
dependency. Text is HTML escaped. Media paths are safe workspace-relative
links; missing media renders a placeholder plus its source path.

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

Exit code `0` means render success with no integrity error; `1` means a
trustworthy integrity-error dashboard rendered; `2` remains argparse usage;
`3` is discovery/input contract failure and produces no misleading page; `4`
is an internal render failure. Ordinary production blockers and warnings do
not change the exit code.

Default JSON uses UTF-8, LF, and sorted keys. HTML, Markdown, and SVG omit the
current time by default. The manifest records input, Snapshot, and output
hashes. Optional render time does not change the content consistency hash.
Repeated default renders are byte-identical and do not change source hashes.

## Evidence Limits

`TECHNICALLY_VERIFIED` requires automated contracts, read-only behavior,
determinism, and rendering checks. `CREATOR_REVIEWED` requires owner review of
the views. `CREATOR_VALIDATED` requires two creators completing defined tasks
in two real projects with at least 80 percent success and no critical state
misreading. Generic fixtures are not creator-validation evidence. v2.3.0 may
be released at `CREATOR_REVIEWED`; this design does not claim
`CREATOR_VALIDATED`.
