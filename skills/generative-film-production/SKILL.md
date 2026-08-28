---
name: generative-film-production
description: Use when planning, generating, reviewing, repairing, or finishing AI video, film, ads, music videos, product films, shorts, storyboards, recurring characters, multi-shot sequences, model-specific video prompts, continuity, or generative-video production workflows.
---

# Generative Film Production

## Overview

**Spec before prompt.** Treat prompts as compiled outputs, not as the place where story, continuity, asset identity, cinematography, timing, and model quirks are invented at once.

This skill owns production decisions from brief to final QC while keeping model-specific dialect in adapters. Use progressive disclosure: load only the reference files required by the current production stage.

## Core invariants

1. Lock intent before scaling production.
2. Give every recurring asset one authoritative Asset Passport.
3. Give every reference an explicit `controls` role and `does_not_control` boundary.
4. Stress-test expensive recurring assets before video generation.
5. Design one dominant action per generative clip by default.
6. Express camera instructions physically: placement, lens, height, path, speed, stop.
7. Use stages plus an observable end state as the default narrative timing grammar.
8. Use second-level timing only when an external hard constraint requires it.
9. Maintain continuity through state, axis, direction, eyeline, prop state, and transition type—not blind tail-frame chaining.
10. Keep the Canonical Shot Spec model-agnostic; compile it through a Model Adapter.
11. Regenerate only the failed unit and use a single-variable retry.
12. Final editors consume approved Selects, not the generations directory.
13. Move deterministic text, captions, standard transitions, assembly, and exact timing into deterministic post-production tools when practical.
14. Never claim a model behavior is verified unless a dated Model Profile records real evidence.

## Route by current stage

| User state | Load |
|---|---|
| Idea, concept, campaign goal | `references/01-creative-brief.md` |
| Script or narrative exists | `references/02-story-breakdown.md` |
| Images/references exist | `references/03-reference-board.md` |
| Character/product/location must recur | `references/04-asset-passport.md` then `references/05-asset-stress-test.md` |
| Need shots or prompts | `references/06-shot-engineering.md`, `references/08-video-spec.md`, `references/09-prompt-compiler.md` |
| Multi-shot continuity | `references/07-continuity-engine.md` |
| Generation is failing | `references/13-qc.md`, `references/14-failure-recovery.md` |
| Clips are approved | `references/11-editing.md`, `references/12-audio.md` |
| Whole project needs first principles | `references/00-production-philosophy.md` |

## Production gates

Do not expand downstream work while an upstream gate is unresolved:

`BRIEF_LOCKED → BREAKDOWN_LOCKED → REFERENCES_BOUND → ASSETS_LOCKED → SHOT_SPEC_VALID → REPRESENTATIVE_PASS → SELECTED → TIMELINE_QC → MASTER_QC`

A gate may be skipped only when the job genuinely does not need that layer, such as a one-off abstract atmosphere shot with no recurring asset.

## Canonical Shot Spec

Before writing a provider prompt, define the smallest relevant subset of:

- `shot_id`, `scene_id`, `narrative_goal`, `dominant_action`, target duration
- recurring assets and their state variants
- location, props, initial state, observable end state
- screen direction, camera axis, eyelines when continuity requires them
- shot size, lens, physical camera position, support, path, speed, stop
- action stages and stage end states
- acting cues, physics, persistent consequences
- lighting/color constraints that are expensive to redo
- dialogue/audio source when present
- edit-in, edit-out, transition type
- reference bindings with `controls` and `does_not_control`
- quality bar, failure risks, and retry lineage

Use `templates/shot-card.md` or the JSON example validated by `scripts/validate_shot_spec.py`.

## Timing decision

| Signal | Granularity |
|---|---|
| Single continuous action or mood shot | Event order only |
| Multi-event narrative without hard clock | **Stages + observable end states** |
| Supplied music/VO, lip sync, fixed reveal or handoff time | Second-level timing |

Do not add timestamps merely to make a prompt look precise. Precision that the model cannot reliably honor creates fragmentation rather than control.

## Continuity decision

- **Uninterrupted action / extension:** prior tail may control the next start; inspect the seam.
- **Hard cut:** design the next shot independently; preserve only required story state.
- **Reverse angle:** redesign composition while preserving axis, eyeline, character side logic, and prop state.
- **Match cut:** match the intended shape, motion direction, color, or composition—not pixel identity.
- **Insert / cutaway:** generate independently unless the insert contains a stateful recurring prop.

Load `references/07-continuity-engine.md` for the ledger and transition rules.

## Choose a Model Adapter

First inspect capability facts: route support, duration, reference count, reference addressing, start/end frames, native audio, resolution, timing adherence, and known identity behavior. Unknown capability means **unknown**, not assumed.

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

Adapters compile the canonical decisions. They do not redefine the story or silently invent unsupported capabilities.

## Generation loop

1. Submit one representative pass before scaling a large batch.
2. Record generation ID, model/profile version, prompt/spec version, references, and cost/status when available.
3. Review in order: identity → count → locks → end state → anatomy/prop → spatial continuity → camera/motion → audio → editability.
4. Stop review at the first expensive failure.
5. Record one failure hypothesis.
6. Change one variable tied to that hypothesis; keep unrelated decisions fixed.
7. If the same failure persists after several controlled retries, simplify the shot, reduce references, change the route, or split the clip instead of continuing blind sampling.
8. Promote only approved outputs to Selects.

Load `references/10-generation-loop.md`, `references/13-qc.md`, and `references/14-failure-recovery.md` when iterating.

## Output contracts

Prefer explicit production artifacts over prose-only advice:

- Creative Brief
- Production Bible
- Asset Passport / Asset Registry
- Canonical Shot Spec / Shot Card
- Continuity Ledger
- Compiled Prompt + Adapter/Profile identity
- Generation Log
- Selects Log
- QC Report

Use the templates in `templates/` and run validators before declaring a production artifact ready.

## Common mistakes

| Mistake | Correction |
|---|---|
| One giant “cinematic” prompt | Separate production decisions, then compile |
| Eight references with no roles | Bind each reference to one role and boundary |
| “Keep consistent” | Write visible invariants and end states |
| Every shot inherits prior tail frame | Choose continuity strategy by transition type |
| Every beat gets timestamps | Use the loosest timing grammar that meets the constraint |
| Retry rewrites the whole prompt | Single-variable retry tied to a failure hypothesis |
| Exact long text generated in-video | Prepare/reference it or overlay in post |
| Editor sees every generation | Editor consumes Selects only |
| Model folklore treated as fact | Store dated evidence in a Model Profile |

## Verification

Use the bundled scripts before treating structured artifacts as valid:

```bash
python scripts/validate_shot_spec.py templates/shot-spec.example.json
python scripts/validate_asset_registry.py templates/asset-registry.example.csv
python scripts/prompt_lint.py prompt.txt
```

A still-frame review cannot validate motion rhythm, seam quality, pacing, or audio sync. Do not issue an overall playback verdict from stills alone.
