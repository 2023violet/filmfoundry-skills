# Creator-First Script Workflow

Use this path when the creator starts from a blank idea, a fragment, a premise, an outline, or an existing draft. The goal is a reviewed script, not production setup.

## Interaction contract

- Select an execution lane before asking questions: `FAST` for reversible exploration, `STANDARD` for a grouped creative decision, `STRICT` for Canon/acceptance/external side effects, and `RECOVERY` for a declared failure diagnosis.
- In `FAST`, return two or three materially different options or a small creative package without waiting for a question unless a missing fact blocks all safe progress. In `STANDARD`, group related choices and ask at most one blocking decision per turn. In `STRICT`, preserve the full Gate and approval boundary.
- Choose the unanswered question that can invalidate the most downstream work, but do not ask about a fact that can be safely assumed for the current reversible draft.
- If the creator is stuck, offer two or three materially different options plus a recommendation; do not manufacture weak choices.
- Summarize accepted decisions before moving to the next gate or committing a grouped package.
- When a second person must review the work, turn that summary into a compact
  decision card: current question, recommendation, trade-offs, locked facts,
  open risks, and next action. Load `references/45-human-decision-layer.md`
  for the durable form.
- Keep alternatives as `CREATIVE_DRAFT`; only creator-approved choices cross an `*_ACCEPTED` gate.
- Keep provisional information visible as `ASSUMPTION`, `OPEN`, or `DEFERRED`; do not force every unknown into an immediate creator decision.
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

For `FAST`: show the goal, accepted facts, assumptions, two or three options or a small creative package, checks run, and the next optional choice. Do not pause for a decision unless no safe draft can be produced.

For `STANDARD`: show the accepted facts, expose the smallest blocking unknown, return the grouped result, and ask at most one blocking decision. Keep non-blocking items as `OPEN` or `DEFERRED` and continue without a separate turn for each one.

For `STRICT`: show the accepted facts, current Gate, blocking unknown, consequence of each option, and the exact approval required. After the answer, either accept the Gate or explain the single remaining contradiction. Do not silently rewrite accepted decisions.

For `RECOVERY`: read the narrowest failure evidence, identify the failing layer, propose the smallest repair, and resume from the saved state. Do not restart the full creator workflow unless the evidence shows that a previously accepted fact is invalid.

Apply the route's soft execution budget to each response cycle. Track blocking decisions, internal planning/tool steps, and automatic revisions. When any ceiling is reached, stop and return the current useful artifact as `DEFERRED`, with the remaining work and resume trigger; do not silently spend more turns or use the limit to bypass a creator approval.

Draft short work as a complete script after structure approval. Draft long work in creator-approved sections, carrying forward a concise decision recap. Revision preserves the creator’s intent unless the creator explicitly changes it.

Before marking `REVISION_ACCEPTED`, compare the revised draft against every accepted revision decision. Check for wording that preserves a rejected idea under a synonym or softer formulation; do not claim a change is applied while an equivalent contradiction remains.

## Optional depth

- Load Content Market Gate only for audience-growth, monetization, or repeatable-series goals.
- Build a formal Emotional Beat Map only when several beats, dialogue/music timing, or a diagnosed pacing problem makes it useful.
- Expand worldbuilding only when a story decision depends on it.
- Enter visual-production preparation only after the creator accepts the script or explicitly asks to work on an already stable section.

## Completion and handoff

Report the accepted logline, character engine, dramatic rules, structure, revision decisions, unresolved/open/deferred questions, assumptions, checks run, and the script location if the creator authorized a write. Include a human-readable Decision Brief when someone besides the creator must approve the result. Label exploratory output `CREATIVE_DRAFT` until Commit Mode records creator approval. A completed fresh-context trial is product evidence; an authored fixture or local reference-loading measurement is not.
