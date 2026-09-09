# FilmFoundry v3 Consumer Inventory

Date: 2026-09-09

## Scope

The inventory covers the FilmFoundry release worktree, the Wucheng project worktree, and the surrounding `D:\study\Software` workspace where readable paths were available. The scan excludes `.git` and `99_归档` content. A broken historical junction under `Curing-Lite-worktrees` was reported by `rg`; that path is treated as unknown rather than silently ignored.

## Worktree baselines

| Worktree | Branch | HEAD | State |
|---|---|---|---|
| `D:\study\Software\filmfoundry-skills-v2-release` | `codex/filmfoundry-v2.3-creator-read-model` | `b6f3f9db5f5ecbb9daa8ef053bd1449f0729a3a6` | dirty; existing creator-read-model edits and untracked `build/` |
| `D:\study\Software\AI-Short-Drama` | `codex/wucheng-v2-foundation` | `2192d053315f88ee516197dad47deb2088ab2eb3` | dirty; existing Canon, media, Runtime, adapter, and v3 document edits |

## Classification

### Active runtime dependencies

- `AI-Short-Drama/07_运行时/RUNTIME/project-runtime.json` is the active Wucheng Runtime pointer and still declares `2.0.0` metadata at inventory time.
- `AI-Short-Drama/08_工具与技能/雾城项目适配器/scripts/build_creator_catalog.py` is the active project adapter and currently emits a v3-named projection, but does not yet emit active `runtime_status` values or copy verified media into the projection.
- `filmfoundry/` and the `ff` console entry point are the active FilmFoundry package and CLI.

### Active documentation

- Wucheng root README, entry README, tools README, tools index, and the current handoff are active navigation surfaces and contain v1/v2 references that must be migrated or explicitly marked historical.
- FilmFoundry `README.md`, `CHANGELOG.md`, Creator Read Model tests, and v3 fixture manifests are active release surfaces.

### Historical evidence

- `99_归档/**` and Git history/tags remain historical and are outside the v3 active search path.
- `tests/fixtures/v2/**` and `tests/test_v2_*.py` are historical contract evidence once moved out of the active suite. They must not be used as v3 acceptance inputs.
- Wucheng v1.9.3 handoff content, v2.0.0 Runtime facts, and prior production states remain valid historical facts but cannot remain the current authority.

### External or unknown consumers

- No additional readable active import consumer of `filmfoundry_v2` was found in the scanned workspace.
- The scan cannot prove that no consumer exists outside `D:\study\Software`; v3 RC release notes must state clean-break risk.
- One broken path under `Curing-Lite-worktrees` prevented a completely clean recursive scan and is recorded as an unknown rather than inferred absent.

## Search findings

The following tokens still occur outside the archive boundary and require migration review: `filmfoundry_v2`, `filmfoundry-skills-v2`, `migrate`, `>=2.0.0,<3.0.0`, `v1.9.3`, and `v2.0.0`. Some hits are intentionally historical tests or reports; active Runtime, adapter, README, and index hits are not historical by default.

## Decision

Proceed with the v3 clean break. Do not restore a long-lived compatibility layer. Preserve historical evidence and provide a release-note warning for consumers outside the scanned workspace.
