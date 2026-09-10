# Creator-First Script Workflow

Use this path when the creator starts from a blank idea, a fragment, a premise, an outline, or an existing draft. The goal is a reviewed script, not production setup.

## Interaction contract

- Ask one question per turn. Choose the unanswered question that can invalidate the most downstream work.
- If the creator is stuck, offer two or three materially different options plus a recommendation; do not manufacture weak choices.
- Summarize the accepted decision before moving to the next gate.
- Keep alternatives as `CREATIVE_DRAFT`; only creator-approved choices cross an `*_ACCEPTED` gate.
- Do not load Runtime, assets, provider adapters, model evidence, prompt compilation, or video QC during this path.
- The workbook is optional depth. Use it only when the creator wants durable state or the script spans enough turns that decisions may be lost.

## Entry state

Classify the supplied material as `BLANK`, `SEED`, `OUTLINE`, or `DRAFT`. Start at the earliest unresolved gate; never force a creator with a usable draft back through blank-idea exercises.

## Required gates

1. `SEED_ACCEPTED` — audience experience, format/length, and the core situation are clear enough to explore.
2. `LOGLINE_ACCEPTED` — protagonist, goal, obstacle, stakes, and distinguishing hook form one causal sentence.
3. `CHARACTER_ENGINE_ACCEPTED` — the protagonist’s want, need, contradiction, pressure response, and change/non-change can drive scenes.
4. `DRAMATIC_RULES_ACCEPTED` — point of view, world constraints, tone boundary, and non-negotiable ending facts are explicit.
5. `STRUCTURE_ACCEPTED` — the inciting change, escalating decisions, irreversible turn, climax, and payoff form a causal chain.
6. `DRAFT_ACCEPTED` — a complete draft exists with no missing scenes or placeholder beats.
7. `REVISION_ACCEPTED` — at least one intent/causality pass and one character/dialogue/continuity pass have been reviewed by the creator.

## Stage loop

For the current gate: show the accepted facts, expose one blocking unknown, ask one question, then wait. After the answer, either accept the gate or explain the single remaining contradiction. Do not silently rewrite accepted decisions.

Draft short work as a complete script after structure approval. Draft long work in creator-approved sections, carrying forward a concise decision recap. Revision preserves the creator’s intent unless the creator explicitly changes it.

Before marking `REVISION_ACCEPTED`, compare the revised draft against every accepted revision decision. Check for wording that preserves a rejected idea under a synonym or softer formulation; do not claim a change is applied while an equivalent contradiction remains.

## Optional depth

- Load Content Market Gate only for audience-growth, monetization, or repeatable-series goals.
- Build a formal Emotional Beat Map only when several beats, dialogue/music timing, or a diagnosed pacing problem makes it useful.
- Expand worldbuilding only when a story decision depends on it.
- Enter visual-production preparation only after the creator accepts the script or explicitly asks to work on an already stable section.

## Completion and handoff

Report the accepted logline, character engine, dramatic rules, structure, revision decisions, unresolved questions, and the script location if the creator authorized a write. Label the result `CREATIVE_DRAFT` until Commit Mode records creator approval. A completed fresh-context trial is product evidence; an authored fixture or local reference-loading measurement is not.
