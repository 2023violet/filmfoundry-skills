# FilmFoundry Skills v1.2.0 — Content-Market-First Production Design

## Purpose

v1.2.0 keeps one primary skill, `generative-film-production`, and adds a mandatory project-level Content Market Gate for audience-growth, monetization, and repeatable-series work. The production engine remains model-agnostic; the new front end decides whether a concept deserves expensive asset and shot production before FilmFoundry scales it.

## Problem statement

v1.1.0 is strong after a project has already been chosen: it governs recurring assets, keyframes, continuity, provider evidence, retries, selects, audio, and finishing. It is weak before that point. A project can therefore become visually polished while still lacking a clear audience, click reason, three-second hook, viewer payoff, follow reason, thirty-episode engine, monetization path, or cheap MVP. The result is production quality without content-market evidence.

The Yelang Pilot also exposed three production-specific gaps:

1. generated source duration and usable edit duration are not distinguished;
2. a visually strong clip can fail late yet contain an approved contiguous segment that should become a traceable partial Select;
3. model evidence needs a place for project observations such as mid-clip spatial reset, weak edit-hold adherence, acting amplification, and character-identity stability without promoting one observation into folklore.

A fourth gap is keyframe eyeline governance: a character can be identity-correct and aesthetically strong while looking away from the narrative target. Eyeline-critical shots need an adaptive conditional contract even when they are not reverse angles.

## Architecture

### One skill, two project-level routes

`generative-film-production` remains the only primary skill.

For commercial/creator series work:

`Idea → Content Market Gate → Cheapest MVP → Evidence Review → Production Approval → Creative Brief → Existing FilmFoundry Production Engine`

For non-market work such as a client-locked commission, pure artistic experiment, portfolio sample, or model capability test, the market gate can be explicitly bypassed with a reason. Bypass is never implicit.

### Content Market Gate

The gate is stored as deterministic JSON and validated before expensive production. Core answers are:

- one-sentence conflict
- audience
- click reason
- first-three-second hook
- viewer payoff
- follow/next-episode reason
- thirty-episode series engine
- monetization route
- cheapest MVP
- AI-production fit
- platform hypothesis

Answers may begin as hypotheses. A concept with complete hypotheses may reach `MVP_ONLY`; it may not reach `PRODUCTION_APPROVED` until real MVP evidence is recorded. If monetization has no answer, the project remains a traffic experiment rather than production-approved commercial content.

No global numeric platform threshold is hard-coded. Platforms change; each MVP defines its own success criteria and captures dated evidence.

### Project market lifecycle

Project-level lifecycle is separate from generation-unit runtime:

`IDEA → MARKET_GATE_RESOLVED → MVP_READY → MVP_TESTING → MVP_EVALUATED → PRODUCTION_APPROVED`

Generation-unit lifecycle remains unchanged. Project market approval gates expensive scale; it does not replace shot-level runtime.

### Source duration vs edit duration

v1.2 shot specs distinguish:

- `generation_duration_seconds`: what the provider is asked to generate;
- `edit_target_duration_seconds`: how much contiguous usable footage the edit actually needs.

The edit target must be positive and no longer than the generated source. This makes “generate 10 seconds, use the best 5 seconds” an explicit production strategy rather than an ad-hoc exception.

### Partial Selects

`PARTIAL_SELECT` is a selection disposition, not a new runtime state. A generation unit still reaches `SELECT`, but the selected artifact may specify an in/out range. The observed state is written at the selected out-point, not at the raw source clip end.

A partial Select is allowed when:

- the selected range satisfies the shot narrative goal and quality bar;
- the failure lies outside the selected range or does not invalidate the selected range;
- the range is contiguous and time-valid;
- downstream continuity is based on the selected out-state.

This prevents unnecessary retries for late-source failures while preserving traceability.

### Adaptive eyeline-critical shots

v1.2 adds `eyeline_critical: true`. When enabled, the spec must define `eyeline_subject`, `eyeline_target`, and `eyeline_screen_direction`, even for a single-character environmental shot. This catches “character + home valley” compositions where identity is correct but the character looks off-screen away from the intended target.

### Model observation evidence

Model Profiles gain `behavior_observations`. Every observation records:

- capability
- context
- evidence level
- source generation IDs
- observation
- production consequence

Any level above `UNVERIFIED` requires source generation IDs. Only `REPEATED` or stronger can become a default adapter behavior. One successful or failed clip remains `OBSERVED_ONCE`.

### Controllability budget

v1.2 changes provider guidance from “write more precise timing prose” to “spend model control budget deliberately.” For ordinary I2V without a hard clock:

- one dominant action;
- one primary camera intent;
- minimal acting change;
- few stages;
- source duration may exceed edit target;
- use the best contiguous segment when valid;
- precise late hold/deceleration is not assumed unless provider evidence supports it.

Provider prompts are still linted structurally, but prompt wording is never treated as obedience evidence.

## Runtime integration

`project-runtime.json` v1.2 adds:

- `project_goal`
- `content_market_gate`

For `AUDIENCE_GROWTH`, `MONETIZATION`, or `SERIES_BUSINESS`, the gate file is required. A runtime can exist during `MVP_ONLY`; generation units may be created for MVP work. Expensive production scaling is a workflow policy governed by the gate decision, while structural runtime validators prevent a `PRODUCTION_APPROVED` claim without MVP evidence.

v1.1 manifests remain readable for compatibility.

## New/updated artifacts

New:

- `references/20-content-market-gate.md`
- `references/21-market-mvp.md`
- `references/22-ai-native-content-design.md`
- `references/23-controllability-budget.md`
- `templates/content-market-gate.example.json`
- `templates/content-market-gate.md`
- `templates/market-mvp-report.md`
- `scripts/validate_content_market_gate.py`
- `scripts/validate_selects_log.py`

Updated:

- primary `SKILL.md`
- runtime manifest/example and validator
- shot spec/example and validator
- production-state selection object and validator
- selects log
- Model Profile schema/example and validator
- keyframe, QC, generation loop, editing, failure recovery, model evidence, H3 adapter, prompt compiler guidance
- README, changelog, package version
- eval suite

## Testing strategy

All behavior changes use red-green TDD. New tests cover:

1. market gate completeness and decision rules;
2. commercial runtime requiring a market gate;
3. production approval requiring real MVP evidence;
4. v1.2 source/edit duration validation;
5. eyeline-critical conditional validation;
6. partial-select range validation and production-state integration;
7. model observation evidence discipline;
8. published examples passing their validators;
9. adversarial eval coverage for market-first routing, MVP restraint, partial salvage, prompt over-control, eyeline, and evidence overgeneralization.

Final verification runs the full pytest suite, all published validators, eval schema validation, package metadata checks, archive content checks, and a clean extraction rerun.

## Non-goals

- No hard-coded current monetization payout or platform algorithm thresholds.
- No claim that a particular AI-video genre is guaranteed profitable.
- No provider behavior claim derived from the Yelang Pilot is promoted to a default without repeated evidence.
- No second primary skill is introduced.
- No requirement that non-commercial art or model tests pass a market gate.
