# FilmFoundry v3.0 clean-break Task 1 report

## Status

Implemented the package, schema, and CLI clean-break slice from the v3.0 plan.
The active Python namespace is now `filmfoundry`, package metadata is `3.0.0`,
and the `ff` executable continues to target the canonical package. The legacy
`filmfoundry_v2` package and core migration planner are no longer active.

Workspace manifests now require `workspace_version` `3.0.0`; v1/v2 values are
reported as unsupported. Existing normative validation behavior, including BOM
safe reads, root path safety, UNKNOWN/INVALID semantics, state alignment, and
provenance handling, was retained.

## Tests

- Focused clean-break, metadata, and CLI tests: `14 passed`.
- Full suite: `299 passed`.

The new contract tests cover canonical import/version, rejection of the legacy
namespace, rejection of the `migrate` command, and rejection of v1/v2 workspace
versions.

## Commit

The implementation commit is `625ada4` (`feat: establish filmfoundry v3
clean-break package`).

## Concerns and follow-up

- Existing contract filenames still carry historical `.v2` labels for artifact
  schemas; this task only hard-breaks the package/workspace version boundary.
  A later schema rename should be coordinated with adapters and fixtures.
- The v2.3 Task 4 report modification was preserved and was not included in the
  implementation commit.
- Creative Mode, renderers/CLI rendering, and project adapters remain pending
  tasks and were intentionally not changed here.
