# FilmFoundry Skills v1.0.1 Hardening Verification Report

**Date:** 2026-08-28  
**Repository:** `filmfoundry-skills`  
**Primary skill:** `generative-film-production`  
**Release target:** `1.0.1`

## 1. Scope

This pass converts the 11 coverage gaps found in the v1.0 comprehensive task test into regression tests and fixes them. It also resolves the unnumbered reverse-angle eyeline design risk by replacing literal prose equality with structured reciprocal eyeline fields.

## 2. Fixed defects / gaps

| ID | Gap | v1.0.1 result |
|---|---|---|
| G01 | Unsupported `transition_type` accepted | Fixed: enum enforced |
| G02 | Duplicate `ref_id` accepted in one shot | Fixed: duplicate binding rejected |
| G03 | Stage entry could omit stage ID | Fixed: integer IDs required and sequential from 1 |
| G04 | CANON asset could have parent | Fixed: CANON must be an authority root |
| G05 | Variant could parent another variant | Fixed: variant must directly parent CANON |
| G06 | Reverse-angle screen-side drift missed | Fixed: `screen_direction` required/preserved |
| G07 | Continuous asset/wardrobe/light/time drift missed | Fixed: explicit fields required and compared |
| G08 | Chinese `0-1秒` timing bypass | Fixed: localized timestamp detection |
| G09 | `REF_A` pointer could bypass role binding | Fixed: pointer role + boundary lint |
| G10 | Obvious multi-move camera conflict missed | Fixed: conservative 3+ move heuristic with negation handling |
| G11 | Uppercase `I2V` bypass | Fixed: route normalization |
| DR01 | Reverse-angle prose eyeline equality could reject physically correct reverse | Fixed: reciprocal `eyeline_subject` / `eyeline_target` + opposite screen direction |

## 3. Static/TDD regression evidence

Fresh full test run after implementation:

```text
70 passed
```

The suite covers repository/skill contracts, eval schema/fixtures, shot spec, asset authority, continuity, prompt linting, and published-template contracts.

## 4. Original adversarial matrix replay

The original 28-case matrix that previously produced 17 PASS / 11 GAP was replayed against v1.0.1 behavior:

```text
28/28 cases matched expected behavior
```

Machine-readable replay artifact is delivered as `filmfoundry-skills-v1.0.1-adversarial.tsv`.

## 5. Published artifact self-validation

The current published examples were executed through their validators:

```text
PASS: canonical shot spec is valid
PASS: asset registry valid (3 rows)
PASS: transition continuity checks passed
PASS: 12 evals schema-valid
PASS: no structural prompt lint findings
```

The `continuity-ledger.example.csv` now includes:

- `eyeline_subject`
- `eyeline_target`
- `eyeline_screen_direction`
- `asset_state`
- `wardrobe_state`
- `light_state`
- `time_state`

## 6. Syntax / hygiene

```text
SKILL.md: 164 lines
compileall: PASS
production TODO/TBD/FIXME scan: PASS
```

## 7. Targeted production-code coverage snapshot

A fast function-level coverage run excluding CLI subprocess tests produced:

```text
continuity_lint.py          69%
prompt_lint.py              74%
validate_asset_registry.py  59%
validate_shot_spec.py       68%
TOTAL                       68%
```

This snapshot is not used as a correctness claim; behavioral regression and adversarial tests are the release gate.

## 8. Evidence boundary

This release is **Static/TDD Verified**. It is not labeled **Production Validated** because two evidence gates remain intentionally separate:

1. fresh-context no-skill vs with-skill agentic A/B benchmark;
2. real multi-project production validation using live generation models and human visual review.

Authored eval fixtures remain scorer smoke fixtures, not proof of model improvement.

## 9. Release verdict

For the validator/schema defects discovered in the v1.0 comprehensive task test, the hardening pass is ready for packaging after final clean-tree and clean-install verification.
