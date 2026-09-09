# FilmFoundry knowledge cleanup report

**Date:** 2026-09-09
**Scope:** documentation, repository rules, authorized memory correction, and read-only workspace cleanup preview
**Method:** full-path cleanup because the repository has a remote, multiple worktrees, a local RC tag, distributable artifacts, and a downstream project consumer

## Outcome

The repository now has one current decision: publication is paused while FilmFoundry is reset around real script creation. The older RC report, v3 technical guide, production guide, v2.3 handoff, and SDD ledger remain as evidence but are visibly marked as non-current. No source behavior, Git history, worktree, project asset, or archive content was deleted.

## Six fact surfaces

| Surface | Status | Result |
|---|---|---|
| Code | Pending | Tests pass, but a broad keyword inventory finds 42 active-scope files containing H3/MiniMax/provider execution, evidence, smoke, payload, or video-gate concepts. The scan is a triage list, not proof that every matching line should be deleted. |
| Docs | Changed and verified | `README.md` is concise and truthful; `docs/README.md` indexes current user docs; historical checkpoints have supersession banners; `CURRENT_HANDOFF.md` is the current repository handoff. |
| Runtime | Out of scope | Downstream project Runtime and Wucheng data were not changed by this pass. A read-only check found 123 existing tracked deletions under Wucheng `99_归档`; their origin is not attributed here. |
| Rules | Changed and verified | Root `AGENTS.md` records the product boundary, evidence rules, and safe cleanup constraints in 38 lines. |
| Memory | Changed and verified | A user-authorized correction note was added under Codex ad-hoc memory extensions; generated memory registries were not edited. |
| Workspace | Pending confirmation | Reproducible output and one clean historical worktree are potential cleanup targets. Dirty worktrees are explicitly protected. |

## Files changed for knowledge governance

- `README.md`: replaced the outdated production-first entry with the current creator-first status and release rule.
- `docs/README.md`: added the active documentation index.
- `CURRENT_HANDOFF.md`: added the clean newcomer handoff and exact next work.
- `AGENTS.md`: added minimal repository-local operating rules.
- `CHANGELOG.md`: added an Unreleased product-reset section without rewriting history.
- `docs/filmfoundry-v3.md`, `docs/filmfoundry-v3-support-matrix.md`, and `docs/ai-video-production-guide-zh.md`: marked as technical/production-stage documents, not approved creator onboarding.
- `docs/reports/2026-09-09-v3-rc-review.md`, the v3 SDD ledger, and the v2.3 handoff: marked as superseded release evidence.
- `.gitignore`: added generated `build/` output.
- Codex ad-hoc memory note: recorded the user’s creator-first, project-neutral, concise-interaction decisions and the fact that Wucheng deletion was not executed.

## Workspace cleanup preview

### Reproducible local output

| Exact target | Files | Bytes | Proposed action |
|---|---:|---:|---|
| `D:\study\Software\filmfoundry-skills-v2-release\build` | 52 | 265,817 | Delete only after post-report confirmation. |
| `D:\study\Software\filmfoundry-skills-v2-release\.dist` | 2 | 336,222 | Delete only after confirmation; artifacts predate the current docs and are not publishable. |
| `D:\study\Software\filmfoundry-skills-v2-release\.pytest_cache` | 5 | 35,957 | Reproducible cache; delete only after confirmation. |
| `D:\study\Software\filmfoundry-skills-v2-release\filmfoundry_skills.egg-info` | 5 | 2,827 | Reproducible packaging metadata; delete only after confirmation. |
| `__pycache__` directories under the release worktree | 130 files | 1,716,384 | Reproducible cache; resolve exact directories again before deletion. |

Total previewed reproducible data: 2,357,207 bytes. None was deleted.

### Worktrees and branches

| Worktree / branch | Live state | Cleanup decision |
|---|---|---|
| `filmfoundry-skills` / `main` | Dirty; `main` is 9 commits ahead of `origin/main` | Protected. Do not remove or reset. |
| `filmfoundry-skills-v133-checkpoint` / `codex/filmfoundry-v1.3.3-checkpoint` | Clean; branch is merged into the current branch; annotated checkpoint tag exists | Potential removable worktree/branch, but only after post-report confirmation and a final tag/object check. |
| `filmfoundry-skills-v2` / `codex/filmfoundry-v2` | Heavily dirty | Protected. Do not remove, reset, or clean. |
| `filmfoundry-skills-v2-release` / current branch | Dirty only with this knowledge-governance change set | Keep; this is the active handoff worktree. |
| local `codex/filmfoundry-v2-release` branch | No attached worktree; merged into the current branch | Potential branch-only cleanup after confirmation and a final unique-commit check. |

The remote currently exposes only `origin/main`; no remote tag or GitHub release was observed. The local `v3.0.0-rc1` tag is retained as technical checkpoint evidence and is not approved for push.

The separate Wucheng worktree currently reports 123 tracked deletions under `99_归档`. This FilmFoundry cleanup did not create, restore, stage, or extend those deletions. Because their origin and intent are unresolved, the entire downstream worktree is protected from cleanup here.

## Verification

- `python -m pytest -q`: `299 passed in 5.08s`.
- `git diff --check`: passed; only line-ending normalization warnings were printed.
- README/documentation-index local links: passed.
- Repository-local `AGENTS.md`: 38 lines, below the 60-line governance target.
- Wucheng `99_归档`: not touched by this pass; 123 pre-existing tracked deletions were detected and left unchanged.

## Next agent

Read `CURRENT_HANDOFF.md`, then solve the creator-first gap before any further release optimization. The first implementation checkpoint is a small, testable from-zero script workflow. Do not remove provider-related files mechanically from the 42-file keyword list; classify each matching contract as keep, generalize, or delete, and prove the public surface after the change.

## Awaiting confirmation

This report authorizes no deletion by itself. If the user asks to continue cleanup after reading it, re-resolve the exact targets and delete only the confirmed generated outputs and/or the clean v1.3.3 checkpoint worktree. Dirty main and v2 worktrees remain protected.
