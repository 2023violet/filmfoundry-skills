---
name: generative-film-production
description: Use when planning, generating, reviewing, repairing, or finishing AI video, film, ads, music videos, product films, shorts, storyboards, recurring characters, multi-shot sequences, model-specific video prompts, continuity, or generative-video production workflows.
---

# Generative Film Production

## Overview

**Market before production. Spec before prompt. Evidence before trust. Runtime before memory.** Treat provider prompts as compiled outputs, not as the place where audience demand, story, continuity, asset identity, cinematography, timing, state, and model folklore are invented at once.

Use progressive disclosure: load only the references required by the current production stage. For multi-shot/recurring-asset projects, move current facts into the runtime artifacts instead of relying on a long Markdown plan.

## Core invariants

1. For audience-growth, monetization, or repeatable-series work, pass a Content Market Gate before expensive production scale.
2. Resolve audience, click reason, three-second hook, payoff, follow reason, thirty-episode engine, monetization hypothesis, cheapest MVP, and AI-production fit before building a large asset/shot system.
3. Treat complete hypotheses as `MVP_ONLY`; promote to `PRODUCTION_APPROVED` only with real MVP evidence declared against pre-set criteria.
4. Lock creative intent before scaling production.
5. Give every recurring asset one authoritative Asset Passport and versioned registry identity.
6. Distinguish canonical assets, generic extras, and ephemeral one-off elements so process cost matches continuity risk.
7. Give every reference an explicit intended role; do not assume a video model obeys semantic role language until the Model Profile has repeated evidence.
8. Stress-test expensive recurring assets before video generation.
9. Separate Narrative Shot, Generation Unit, and Edit Unit IDs.
10. Design one dominant action per generative clip by default.
11. Separate provider `generation_duration_seconds` from required `edit_target_duration_seconds`.
12. Express camera instructions physically: placement, lens relationship, height, path, speed, stop.
13. Use stages plus observable end states as the default timing grammar; use second-level timing only when a real timing authority creates a hard clock.
14. Maintain continuity through state, axis, direction, structured eyelines, prop state, transition type, and observed Select state—not blind tail-frame chaining.
15. Mark narrative-target eyelines as explicit shot/keyframe contracts when they are story-critical, even outside reverse angles.
16. Keep the Canonical Shot Spec model-agnostic; compile it through a Model Adapter backed by a dated Model Profile.
17. Gate I2V behind approved keyframes when the keyframe owns expensive composition/identity/location decisions.
18. Inspect for a valid contiguous `PARTIAL_SELECT` before paying for a retry; regenerate only when the required edit range still fails.
19. When retrying, change one variable tied to evidence.
20. Final editors consume approved full/partial Selects, not raw generations.
21. Move deterministic text, captions, standard transitions, assembly, and exact timing into deterministic post-production when practical.
22. Never claim model behavior is verified without evidence recorded for the exact provider surface/version; `OBSERVED_ONCE` is not a default.
23. Treat visual planning artifacts as optional control tools; storyboard panels are not automatically final edit shots.
24. Gate model behavior by the capabilities required by the selected route rather than unrelated global tests.
25. Require explicit edit-timeline coverage before final Picture Lock; static/keyframe readiness is not Picture Lock.
26. Treat an approved visual-control asset as potentially **partial authority**: before provider use, compare the visible state against the Shot Spec and require a **state-matched** start/end authority for every state the route claims to control.
27. A **proxy smoke** result may prove a provider capability, but it does not directly unlock a production route when the production shot has materially different prop/location/state conditions.
28. Do not treat a runtime state label as proof; validate state transitions and hard dependencies.

## Route by current stage

| User state | Load |
|---|---|
| Commercial/creator idea, monetization, repeatable series | `references/20-content-market-gate.md`, then `references/21-market-mvp.md`, `references/22-ai-native-content-design.md` |
| Non-market idea / client-locked brief | `references/01-creative-brief.md` |
| Script or narrative exists | `references/02-story-breakdown.md` |
| Images/references exist | `references/03-reference-board.md` |
| Character/product/location must recur | `references/04-asset-passport.md` then `references/05-asset-stress-test.md` |
| Need shots | `references/06-shot-engineering.md`, `references/19-adaptive-spec.md` |
| Need optional visual planning / storyboard / authority frames | `references/24-visual-planning-layer.md`, `references/27-storyboard-keyframe-planning.md`, `references/28-visual-plan-qc.md` |
| Need recurring character reference strategy | `references/25-character-reference-system.md` |
| Need recurring location/spatial reference strategy | `references/26-location-reference-system.md` |
| Need provider evidence for a specific route | `references/29-capability-scoped-model-gates.md`, `references/16-model-evidence.md` |
| Need full edit timeline / Picture Lock | `references/30-edit-timeline-contract.md`, `references/11-editing.md` |
| Need to verify a keyframe/First-Last pair actually matches shot state | `references/31-visual-control-state-alignment.md` |
| Multi-shot continuity | `references/07-continuity-engine.md` |
| I2V needs a stable visual start state | `references/17-keyframe-engineering.md` |
| Need provider prompt | `references/08-video-spec.md`, `references/09-prompt-compiler.md`, `references/23-controllability-budget.md`, then one adapter |
| Recurring dialogue / lip sync | `references/12-audio.md`, `references/18-voice-passport.md` |
| Project has many units/dependencies | `references/15-runtime-contract.md` |
| Model behavior is unknown or changing | `references/16-model-evidence.md` |
| Generation is failing | `references/13-qc.md`, `references/14-failure-recovery.md` |
| Clips are approved | `references/11-editing.md`, `references/12-audio.md` |
| Whole project needs first principles | `references/00-production-philosophy.md` |

## Content Market Gate and project approval

For audience-growth, monetization, or repeatable-series work, do **not** start with full worldbuilding. Resolve the market gate, run the cheapest publishable MVP, and use real evidence to decide whether the concept deserves Production scale.

Project-level path:

`IDEA → MARKET_GATE_RESOLVED → MVP_READY → MVP_TESTING → MVP_EVALUATED → PRODUCTION_APPROVED`

`TRAFFIC_EXPERIMENT` is valid when content is worth testing but monetization is unknown. `BYPASS` must be explicit for client-locked work, pure art, portfolio studies, or model-capability tests. Platform rules and monetization conditions are time-sensitive; research them fresh at execution time rather than freezing them into the skill.

Use `references/20-content-market-gate.md`, `templates/content-market-gate.example.json`, and `scripts/validate_content_market_gate.py`.

## Production gates

For lightweight one-off work, use only the gates that carry real risk. For a runtime-managed production, the generation-unit lifecycle is:

`DRAFT → SPEC_RESOLVED → PREFLIGHT_PASS → READY_FOR_KF → KF_GENERATED → KF_QC_PASS → READY_FOR_VIDEO → VIDEO_GENERATED → VIDEO_QC_PASS → SELECT → OBSERVED_STATE_RECORDED → EDIT_READY`

Do not skip gates. A unit may be design-ready while runtime-blocked by an upstream Select, axis, asset, voice, or model-evidence dependency.

## Adaptive Canonical Shot Spec

Do not force every shot to fill the same thirty fields. Require every applicable field.

**Core (v1.2):** narrative shot ID, generation-unit ID, generation duration, edit target duration, narrative goal, one dominant action, location, initial state, observable end state, shot size, composition, camera move, action stages/event order, transition, reference bindings, failure risks, quality bar.

**Conditional:**

- recurring character → character IDs/states, wardrobe, acting, identity authority
- dialogue → voice ID, dialogue route, timing authority, speech intent
- reverse angle → axis, screen-side logic, reciprocal structured eyelines
- eyeline-critical narrative target → subject, target, screen direction
- important prop interaction → prop initial/end state and persistence
- continuous action → continuity source, prior observed state, handoff state
- second-level timing → hard timing constraint + named timing authority

Use `templates/shot-spec.example.json` and `scripts/validate_shot_spec.py`.

## Asset authority

Use `CANONICAL` for recurring identity/geometry/location authority, `GENERIC` for repeatable background language without fixed individual identity, and `EPHEMERAL` for one-off elements. State variants parent a canonical authority directly rather than silently mutating canon.

A locked canonical file should be versioned and hashed. If a supposedly recurring prop/extra starts carrying continuity, promote it rather than pretending an ephemeral item is authoritative.

## Timing decision

| Signal | Granularity |
|---|---|
| Single continuous action or mood shot | Event order only |
| Multi-event narrative without hard clock | **Stages + observable end states** |
| Approved voice/music, lip sync, fixed reveal or handoff time | Second-level timing |

Do not add timestamps merely to make a prompt look precise. If external voice owns timing, approve the voice first and compile its real duration/pauses into the shot. A provider may generate more source time than the edit needs; do not demand perfect unused seconds when a shorter contiguous edit target is sufficient.

## Continuity decision

- **Uninterrupted action / extension:** prior tail may control the next start; inspect the seam.
- **Hard cut:** design independently; preserve only required story state.
- **Reverse angle:** redesign composition while preserving axis, canonical side logic, reciprocal eyelines, wardrobe/prop/light/time state.
- **Match cut:** match intended shape, motion direction, color, or composition—not pixel identity.
- **Insert / cutaway:** generate independently unless a stateful recurring prop requires continuity.

Write planned state before generation, observed state after Select, then run next-shot preflight against the observed state. Load `references/07-continuity-engine.md`.

## Keyframe gate

When I2V start-state quality is expensive, compile a keyframe from the resolved shot spec, then QC it before video. A keyframe is one still action moment, not a video timeline. Reject identity/count/state/prop/axis/location failures before H3/Kling/Veo/etc. For eyeline-critical shots, reject a beautiful frame if the subject visibly looks away from the narrative target.

Load `references/17-keyframe-engineering.md` and use `scripts/keyframe_prompt_lint.py`.

## Choose a Model Adapter

First inspect evidence for route support, duration, reference count/addressing, start/end frames, native audio, resolution, prompt-language behavior, timing adherence, identity behavior, hand/prop stability, and multi-character behavior. Unknown means **unknown**.

Then load exactly one relevant adapter:

- `references/adapters/generic-t2v.md`
- `references/adapters/generic-i2v.md`
- `references/adapters/first-last-frame.md`
- `references/adapters/multi-reference-video.md`
- `references/adapters/storyboard-to-video.md`
- `references/adapters/seedance.md`
- `references/adapters/minimax-h3.md`
- `references/adapters/veo.md`
- `references/adapters/kling.md`
- `references/adapters/image-generation.md`

Adapters compile canonical decisions. They do not redefine the story or silently invent unsupported capabilities.

## Model Evidence and reference strategy under uncertainty

If a provider's semantic role-binding behavior is not repeatedly verified, do not rely on elaborate `controls identity only` prose as if it were an API contract. Prefer:

1. **R1 Semantic Role Binding** only with repeated-or-stronger evidence.
2. **R2 Minimal Reference** when multi-reference works but role semantics are uncertain.
3. **R3 Precomposed Keyframe** when reference interference is high.

For MiniMax H3, load the adapter, `references/adapters/minimax-h3-smoke-tests.md`, and the model-evidence reference before scaling.

## Generation loop

1. Validate market/runtime/spec/dependencies before expensive generation.
2. Submit one representative pass before scaling a batch.
3. Record generation ID, narrative shot, generation unit, model/profile version, spec/prompt versions, input asset versions, source duration, edit target, and status/cost when available.
4. Review full playback with timestamps: identity → count/state/locks → narrative target/eyeline → spatial persistence → anatomy/prop → camera/motion → acting → audio → editability → aesthetics.
5. Score Prompt Compliance, Narrative Fitness, Identity/Continuity, Visual Quality, and Editability separately when diagnosis matters.
6. Before retrying, ask whether a contiguous range satisfies the shot goal and quality bar. If yes, record `PARTIAL_SELECT` with source in/out and stop.
7. If retry is still necessary, record the first expensive failure and one causal hypothesis.
8. Change one variable; keep unrelated variables fixed.
9. Attempts 1–3 diagnose normally; attempts 4–5 require simplification; a sixth repeated failure blocks the current route and triggers a split or route change.
10. Promote only approved full/partial outputs to Selects.
11. Write observed Select state at the selected out-point before downstream continuity is considered ready.

## Output contracts

Prefer production artifacts over prose-only advice:

- Content Market Gate / Market MVP Report
- Creative Brief / Production Bible
- Sequence Plan / optional Visual Control Board / Character & Location Reference Sheet
- Visual Control State Audit
- Edit Timeline Ledger / Picture Lock record
- Asset Passport / Asset Registry
- Axis Registry / Voice Registry
- Adaptive Canonical Shot Spec / Shot Card
- Continuity Ledger / Observed State
- Model Profile + evidence
- Compiled Keyframe Prompt / Provider Prompt
- Production State / Dependency Graph
- Generation Log / Selects Log (FULL/PARTIAL) / QC Report

## Verification tools

Use the bundled validators when the corresponding artifact exists:

```bash
python scripts/validate_content_market_gate.py templates/content-market-gate.example.json
python scripts/hash_asset.py <asset-file>
python scripts/validate_asset_registry.py templates/asset-registry.example.csv
python scripts/validate_shot_spec.py templates/shot-spec.example.json
python scripts/validate_axis_registry.py templates/axis-registry.example.json
python scripts/validate_voice_registry.py templates/voice-registry.example.json
python scripts/validate_model_profile.py templates/model-profile.example.json
python scripts/validate_production_state.py templates/production-state.example.json
python scripts/validate_selects_log.py templates/selects-log.csv
python scripts/validate_project_runtime.py templates/project-runtime.example.json
```

Provider-specific gates:

```bash
python scripts/keyframe_prompt_lint.py keyframe-prompt.txt
python scripts/h3_prompt_lint.py h3-prompt.txt R2 UNVERIFIED
```

The linters validate FilmFoundry structure, not visual quality or provider obedience. Still-frame review cannot validate motion rhythm, seam quality, pacing, or audio sync.

## Common mistakes

| Mistake | Correction |
|---|---|
| Beautiful Production before audience/hook/payoff/series answers | Run Content Market Gate + cheapest MVP first |
| One giant “cinematic” prompt | Separate decisions, then compile |
| Eight references with no role/risk thinking | Use smallest sufficient reference pack |
| Model role-language treated as API fact | Verify A/B or downgrade adapter mode |
| “Keep consistent” | Write visible invariants/end states |
| Every shot inherits prior tail | Choose transition strategy intentionally |
| Every beat gets timestamps | Use loosest timing grammar that meets the authority |
| Provider outputs 10s so edit must use 10s | Separate generation duration from edit target; permit traceable PARTIAL_SELECT |
| Late failure triggers automatic regeneration | Check whether the required contiguous edit range already passes |
| Character identity is right, so keyframe passes | Also verify narrative target/eyeline when critical |
| Dialogue timing invented before final voice | Let approved voice own timing when required |
| Bad keyframe sent to video hoping it is fixed | Reject upstream and repair keyframe |
| Runtime state manually jumps gates | Validate state transition and dependencies |
| Retry rewrites everything | Single-variable retry tied to evidence |
| Exact long text generated in-video | Prepare/reference or overlay in post |
| Editor sees every generation | Editor consumes Selects only |
| One observed provider behavior becomes a rule | Keep it OBSERVED_ONCE until repeated evidence |
| Model folklore treated as fact | Store dated evidence in Model Profile |
