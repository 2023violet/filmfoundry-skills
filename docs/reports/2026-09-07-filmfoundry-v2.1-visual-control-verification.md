# FilmFoundry v2.1 Visual Control Verification

Date: 2026-09-07

## Verified

- v1.3.3 compatibility checkpoint remains tagged at `filmfoundry-v1.3.3-checkpoint` (`167 passed`).
- v2.1 release worktree tests: `210 passed`.
- Visual Control Plan parsing, strict unknown-field and namespace checks, conditional previs/physics/lens checks, alignment and compiler hash tests pass.
- Provider payload compilation remains read-only and records prompt plus visual-control hashes.
- Main `SKILL.md` is 278 lines.
- Higgsfield evidence remains `UNVERIFIED`; no paid generation was called.

## Boundary

Core contracts can represent and inspect visual controls. Provider execution, identity fidelity, spatial fidelity, physics realism, aesthetic QC, audio, NLE, encoding and publishing remain external or human-reviewed. `OBSERVED_ONCE` evidence cannot promote a default route.

## Wucheng handoff

The H3 vertical slice remains a dry-run handoff for `TEST_H3_06_A`: 5 seconds, 768P, adaptive ratio, `NONE` postprocessing. Returned evidence is accepted only as raw MP4, settings screenshot and generation ID; no output is currently recorded (`0`). The project adapter additions are read-only plan construction and evidence ingestion helpers; archive content is not touched.

## Pending evidence

Real Higgsfield/H3 output, controlled gray-background and reference-strategy A/B experiments, multi-project migration, and final human visual QC are still required before any capability or route promotion.
