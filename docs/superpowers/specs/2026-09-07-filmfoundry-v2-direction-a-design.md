# FilmFoundry v2 Direction A: Evidence-Gated Provider Adapters

**Date:** 2026-09-07
**Status:** Implementation specification
**Scope:** provider-neutral adapter contracts, validation reports, and the Higgsfield evidence register

## Goal

Direction A keeps FilmFoundry's production contracts independent from provider
clients. An adapter may compile a canonical prompt into provider parameters, but
it can only advertise a route or default behavior when the exact provider
surface and version have evidence at the required level. Static package tests
prove schema and report behavior; they do not prove provider obedience, visual
quality, or market performance.

## Boundaries

- `filmfoundry_v2` owns canonical contracts, deterministic validation, and
  report serialization.
- Provider adapters own API authentication, network calls, retries, and
  provider-specific parameter translation.
- `docs/evidence/higgsfield-evidence-register.json` is the machine-readable
  register for Higgsfield capabilities. It is evidence metadata, not a claim
  that a route has passed a real generation test.
- Markdown remains human-readable design authority. JSON is machine-readable
  contract authority. Stable IDs use the existing ASCII ID policy.

## Validation API

`ValidationIssue` contains `severity` (`ERROR` or `WARNING`), `code`,
`message`, and optional `source`, `json_pointer`, `related_ids`, and
`suggestion` fields. Unknown severities fail at construction so callers cannot
  silently downgrade a failure.

`ValidationReport` contains a stage, a sorted/deduplicated `checked` list, and
  a deterministic issue list. Issues sort by severity (ERROR first), source,
  JSON pointer, code, message, related IDs, and suggestion. Consequently the
  same inputs produce the same report regardless of discovery order.

`report.ok` is true when no ERROR issue exists. Warnings are visible in the
  report but do not fail a validation run. `report.exit_code` is `0` for
  warning-only or empty reports and `1` when at least one ERROR exists.
  `to_dict()`/`to_json()` expose the structured issues plus convenience
  `errors` and `warnings` message arrays for CLI consumers.

## Higgsfield evidence register

The register uses `schema_version: "higgsfield-evidence.v1"` and records:

- provider and register identity;
- the minimum evidence level for default adapter behavior;
- capability records with stable `capability_id`, route, scope, evidence
  level, and linked evidence IDs;
- dated evidence records when a real generation is run, including the exact
  provider surface/version, generation IDs, test context, result, and review
  date.

An empty evidence list is valid for a newly configured provider. A capability
with `UNVERIFIED` evidence must use route `UNVERIFIED` and an empty evidence ID
list; it cannot unlock production. `OBSERVED_ONCE` may inform the next
controlled experiment but cannot become a default adapter behavior. Only
`REPEATED` or stronger evidence can support a default behavior, and changing
the provider surface or version invalidates only the affected capabilities.

## Acceptance criteria

1. The report API rejects unknown severity, provides stable ordering, and
   serializes all fields deterministically.
2. Warning-only reports return `ok == True` and exit code `0`; reports with an
   ERROR return exit code `1`.
3. Golden and invalid Higgsfield register fixtures make the unverified boundary
   explicit and reproducible.
4. Existing v1 tests and v2 contract/CLI behavior remain unchanged.
5. No provider result, benchmark, or production approval is fabricated by this
   package.
