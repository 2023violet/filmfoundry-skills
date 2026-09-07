# FilmFoundry Skills v2.3.0 Creator Source And Data Mapping

## Mapping Rule

The Creator Layer reads validated source records and separately records
filesystem observations. It does not choose between authorities, repair an
input, write to a source, or promote observed data into a declaration.
`CURRENT` supplies current declared facts; `HISTORICAL` supplies comparison;
`SUPPORTING` adds context. A failed source cannot contribute to a known
aggregate.

| Source kind | Existing or new contract | Authority and parser responsibility | Creator output |
|---|---|---|---|
| Workspace boundary | `workspace-manifest.v2.json` | Validate project ID, workspace root, and the read-only archive boundary. Reject path escape and active `99_归档` inputs. | Project identity, source coverage, integrity blockers. |
| Runtime locator | Existing project runtime or `runtime_path` in `creator-source-catalog.v1.json` | Adapter locates the runtime and declares `WORKSPACE_ROOT` or `RUNTIME_DIR`; Core resolves it without project-specific branches. | Source provenance, runtime coverage, project phase inputs. |
| Asset declarations | Asset Registry / `asset-registry.v2.json` | Parse declared IDs, states, paths, and declared hashes from the unique current source. | `CreatorAsset.declared_state`, asset metrics, declared blockers. |
| Media observations | Files addressed by valid Registry entries | Inspect existence and hash without changing the Registry or media. | `CreatorAsset.observed_readiness`: hash OK, unverified, mismatch, missing, not applicable, or unknown. |
| Production lifecycle | `production-state.v2.json` | Parse only valid current lifecycle data. Historical production mappings remain comparison data. | `CreatorShot`, lifecycle metrics, next-state inputs. |
| Select and observed state | Existing Select / Continuity / observed-state records | Parse available valid source records; a missing predecessor observed state remains missing. | Select coverage, continuity edges, navigation blockers. |
| Script facts | `script-analysis.v2.json` | Preserve Canon provenance and confirmation boundary. Never make an inferred fact Canon. | Narrative responsibility and source references. |
| Emotion | `emotional-beat-map.v2.json` | Preserve reviewed discrete beat values, order, direction, and source scope. | `CreatorEmotionPoint` and emotion coverage. |
| Narrative navigation | Optional `narrative-index.v1.json` | Validate stable hierarchy and Canon reference without copying story text. | `CreatorNarrativeNode`; missing index is a coverage gap. |
| Geography and visual context | `scene-topology.v2.json`, coverage, Look Bible, dependency graph, visual control | Parse only supported schema versions and treat these as supporting context unless declared current. | Context coverage, dependency/continuity facts, support boundaries. |
| Evidence and requirements | Evidence, production policy, production ledger, capability records | Preserve evidence level, required artifact findings, and append-only history. | Evidence coverage, blockers, and provenance. |

## Catalog Resolution

Every source catalog item identifies a `source_id`, `source_kind`, relative
`path`, `path_base`, `parser_id`, `schema_version`, `authority_role`, `scope`,
and `required` flag. The resolver must:

1. resolve a path beneath the selected base and workspace root;
2. reject an active source in `99_归档` and all path escape attempts;
3. dispatch by `parser_id + schema_version` rather than a project name;
4. verify one `CURRENT` declaration per source kind and scope; and
5. return a contract failure for an unsupported required source or a coverage
   gap for an unsupported optional source.

The catalog contains declarations. Parser results contain validated source
facts. Filesystem checks contain observations. Those three layers stay
separate through Snapshot serialization.

## Snapshot Derivations

| Snapshot element | Inputs | Required provenance and status rule |
|---|---|---|
| Overview | Valid runtime, lifecycle, source coverage, declared and observed asset aggregates | Each conclusion carries source references and `DIRECT`, `VALIDATED`, or `AGGREGATED` derivation. |
| Metrics | Successfully parsed relevant sources only | A number is `KNOWN`; unavailable data is `UNKNOWN`; parsed-but-invalid data is `INVALID`. Invalid/missing values never become zero. |
| Asset | Current registry declaration plus a non-mutating media observation | Keep `declared_state` distinct from `observed_readiness`; an observation cannot rewrite the declaration. |
| Shot and continuity | Current production state, Select/observed state, valid continuity data | Missing prior observed state becomes a blocker, not a guessed continuation. |
| Narrative node | Canon-backed index or supported script source | Never synthesize Markdown hierarchy from headings. |
| Emotion point | Valid discrete emotional beat record | No smoothing or inferred dramatic labels. |
| Coverage | Catalog declarations, parser results, supported-source status | Failed sources are excluded from known aggregates and represented as coverage gaps. |
| Blocker/conflict | Validation findings, authority scan, integrity checks, requirement evaluation | Include severity, support boundary, rule ID when derived, and source references. |

## Navigation Inputs And Outputs

`derive_creator_navigation` consumes a complete `CreatorSnapshot` and creates
actions only from reported facts. It ranks source/authority failures first,
then integrity/hard blockers, missing required artifacts, missing predecessor
Observed State, next lifecycle state, and advisory items. Its stable sorting
key is `priority -> severity -> entity_id -> action_id`.

Each `CreatorAction` maps one finding to a user-visible reason, rule ID,
prerequisites, support boundary, and provenance. It never calls a provider,
changes lifecycle state, repairs media, or changes Canon/Runtime/Registry.

## Wucheng Adapter Boundary

The Wucheng adapter is a future source locator only. It may locate
`07_运行时/RUNTIME/project-runtime.json`, declare path bases, mark story v3
as `CURRENT`, and mark production mapping as `HISTORICAL`. It does not own
entity aggregation, metrics, continuity, conflicts, navigation, or actions.

The frozen acceptance baseline is 75 Registry assets, 19 historical production
units, 21 missing character media, 0 Generation, 0 Select, and a story v3.0
current authority. These facts guide fixture and adapter acceptance work; they
are not generic Core defaults and are not evidence that a renderer exists.
