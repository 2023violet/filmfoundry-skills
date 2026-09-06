# FilmFoundry Skills v1.2.0 Verification Report

**Release:** `filmfoundry-skills-v1.2.0`  
**Date:** 2026-09-02  
**Primary skill:** `generative-film-production`

## Release objective

v1.2.0 keeps one end-to-end production skill and closes the largest v1.1.0 gaps exposed by real Pilot work: content-market validation before expensive production, cheap MVP evidence, generated-source vs edit-target duration, partial-Select salvage, eyeline-critical keyframes, provider controllability discipline, and behavior-evidence writeback.

## Deterministic verification evidence

Fresh source-tree verification completed with:

- `python -m pytest -q` → **158 passed**
- Content Market Gate validator → PASS
- Project runtime validator → PASS
- Canonical Shot Spec validator → PASS
- Asset Registry validator → PASS (3 rows)
- Axis Registry validator → PASS
- Voice Registry validator → PASS
- Model Profile validator → PASS
- Production State validator → PASS
- Partial-Select Production State example → PASS
- Selects Log validator → PASS
- Eval metadata validator → **26 evals schema-valid**
- Skill placeholder scan (`TBD/TODO/Lorem ipsum/<fill`) → none
- Project-specific contamination scan (`夜郎/YELANG/Yelang/阿猴/夜郎侯`) inside reusable skill directory → none
- Metadata consistency → README / pyproject / changelog all publish **1.2.0**

## TDD additions

New automated coverage includes:

- Content Market Gate core answers and explicit bypass rules
- no-monetization traffic-experiment restriction
- Production approval requiring real MVP evidence IDs and result summary
- v1.2 commercial runtime requiring `project_goal` and market gate
- `MVP_ONLY` allowing MVP units while blocking Production-scope generation before approval
- `NO_GO` blocking expensive generation
- generation duration vs edit target duration
- eyeline-critical subject/target/direction validation
- traceable `PARTIAL_SELECT` ranges
- full vs partial Select range correctness
- Production State partial-Select object support
- behavior-observation evidence levels and source generation IDs
- prevention of `OBSERVED_ONCE` from becoming a default adapter behavior
- v1.2 repository/template contracts
- 26-case adversarial eval suite

## Release evidence boundary

This report proves deterministic package correctness for the tested repository tree. It does **not** prove:

- that any provider will obey a compiled prompt;
- that MiniMax H3 or another model has a capability not supported by real dated Model Profile evidence;
- that a Content Market Gate hypothesis has market demand;
- that a genre, platform, or monetization route is profitable;
- that authored baseline/golden eval fixtures are real agent benchmark runs.

Real provider generations, fresh-context Agentic A/B benchmarks, and real published Market MVP results remain separate evidence layers by design.

## Release decision

Deterministic release gates are satisfied on the source tree. The release archive must still pass a clean-extraction rerun before final delivery.

## Clean-extraction verification

A release archive was extracted into a separate clean directory and verified independently:

- clean-extraction `python -m pytest -q` → **158 passed**
- clean-extraction Content Market Gate validator → PASS
- clean-extraction Project Runtime validator → PASS
- clean-extraction Shot Spec validator → PASS
- clean-extraction Selects Log validator → PASS
- clean-extraction Eval validator → **26 evals schema-valid**

This verifies that the package does not depend on files outside the release archive.
