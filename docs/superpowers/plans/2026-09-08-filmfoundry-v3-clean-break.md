# FilmFoundry v3.0 clean-break execution plan

This plan implements the approved transition from the v2.3 Creator Read Model
work to a generic v3.0 creator-to-production package.

## Binding decisions

- v2.3 Creator Source Catalog, Snapshot, Navigation, and Terminology are reused
  as v3.0 foundations; no separate v2.3.0 release is produced.
- The active package is a clean break: no v1/v2 schema acceptance, fallback
  parsing, or compatibility CLI. Git history remains the historical record.
- The canonical Python namespace is `filmfoundry`; the `ff` executable remains.
- FilmFoundry Core contains no Wucheng project adapter or Wucheng-specific
  fixture. Project adapters live in the consuming project.
- Creative, Commit, Production, and Gate are explicit skill routing modes.

## Delivery order

1. Close v2.3 Task 4 evidence and create v3 contract tests.
2. Rename the active package and schemas; remove compatibility branches and
   migration command while preserving current normative behavior.
3. Add Creative Mode routing and deferred-check output contracts.
4. Complete generic Creator prototype, renderers, `ff render`, and deterministic
   manifests.
5. Move Wucheng integration to the project adapter and add a generic smoke
   adapter contract.
6. Package v3.0.0, update project pointers, run clean-extraction acceptance,
   and create only a local reversible RC marker.

## Acceptance

- v3 tests reject v1/v2 inputs with explicit unsupported-version errors.
- Generic smoke data passes without a project-specific branch.
- Creative requests do not run full validation or mutate machine-layer files.
- Production and Gate modes retain strict validation and deterministic output.
- Two default renders are byte-identical; unsafe paths and external URLs fail.
- Wucheng adapter is read-only and reports source facts without entering Core.
