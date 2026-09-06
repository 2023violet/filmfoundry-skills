# FilmFoundry Skills v2.0 implementation plan

This execution plan implements the supplied FilmFoundry Skills v2.0 design in
an isolated branch. The existing v1.3.3 tree remains the compatibility baseline.

## Tasks

1. Add the v2 package contract: workspace manifest, asset registry, shot spec,
   prompt metadata, lifecycle/evidence validation, golden fixtures, and tests.
2. Add the provider-neutral compiler and unified `ff` CLI for init, validate,
   index, compile, audit, and dry-run migration. Keep v1 scripts usable.
3. Add migration/index/audit adapters, project-facing documentation and
   templates, and the v1-to-v2 migration report/checkpoint behavior.
4. Run the v1 regression suite and v2 tests, then perform a whole-branch review.

## Binding constraints

- v1.3.3 source, fixtures, tests, and behavior remain available and passing.
- v2 uses stable ASCII machine IDs and explicit `extensions` namespaces.
- Markdown is human-authoritative; JSON/CSV are machine-authoritative; media
  hashes and measured dimensions remain factual.
- Relative paths resolve from the manifest root; no fixed `parents[n]` logic.
- Provider clients are adapters outside the core; evidence is contractual.
- Migration dry-run is repeatable and never touches archive boundaries.

## Acceptance

- `python -m pytest -q` keeps the v1 baseline green.
- v2 tests cover schema, conditional fields, transitions, references, paths,
  media profiles, CLI exit codes, and dry-run migration idempotence.
- `python -m filmfoundry_v2 --help` and the `ff` entry point work from any cwd.
