# Task 2 report: unified ff CLI and compiler

## Status

DONE

## Implemented

- Added `filmfoundry_v2` module execution via `python -m filmfoundry_v2`.
- Added the `ff` console entry point in `pyproject.toml` while preserving the
  v1 package version and metadata contract.
- Implemented `init`, `validate`, `index`, `compile`, `audit`, and `migrate`
  commands with `--root`, text/JSON output, and non-zero failure semantics.
- `validate` delegates to v2 contract validators for manifests, prompts, shot
  specs, runtime state, evidence, reference graphs, and asset CSVs.
- `audit` computes SHA-256 records, filters media, and reports broken or
  root-escaping Markdown/JSON references without traversing `99_归档`.
- Added deterministic provider-neutral Prompt Markdown compilation. The source
  Markdown is read-only; provider clients remain outside the core.
- Migration command delegates to the shared archive-aware planner when present;
  the core remains conservative and dry-run by default.

## Verification

- `python -m pytest -q tests/test_v2_cli.py tests/test_v2_contracts.py`: 22 passed.
- `python -m pytest -q`: 188 passed.
- `python -m compileall -q filmfoundry_v2`: passed.
- `python -m filmfoundry_v2 --help` works from a temporary current directory
  after editable installation; `ff` is exposed as the project console script.

## Notes

The v1.3.3 source, fixtures, tests, and semantics were not modified. The
project metadata remains v1.3.3 for compatibility; the additive package exposes
`filmfoundry_v2.__version__ == "2.0.0"`.
