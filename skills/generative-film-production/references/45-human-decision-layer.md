# Human Decision Layer

Use this reference when a creator, director, producer, client, editor, or other
decision-maker needs to review the current story direction or approve the next
step. It is a presentation layer over the accepted creative facts and the
Creator Read Model; it is not a second Canon, Runtime, or Registry.

## What the decision-maker should see

Produce a compact `Decision Brief` with these sections, in this order:

1. **Context** — project, current stage, audience promise, and the role of the
   person being asked to decide.
2. **Decision ask** — one sentence describing the single choice needed now.
3. **Recommendation** — the preferred option and the evidence or accepted
   fact that makes it preferable.
4. **Options and consequences** — two or three materially different options;
   state what each strengthens and what it gives up.
5. **Locked facts** — accepted creator decisions that this choice must not
   silently overwrite.
6. **Open risks** — unresolved questions, contradictions, missing evidence, or
   downstream work affected by the decision.
7. **Next action** — the smallest action after approval, rejection, or deferral.
8. **Evidence** — links or source IDs for the facts used in the brief.

The brief should be readable without knowing Gate names, schema field names, or
provider syntax. Technical identifiers may appear in the evidence section, not
as a substitute for the decision explanation.

## Rules

- Ask for one blocking decision at a time when a decision-maker must protect
  Canon, acceptance, or an external side effect. For reversible exploration,
  combine non-blocking alternatives into one compact comparison package; do not
  turn every creative option into a separate approval turn. Never combine
  logline, character, structure, and visual-style approvals into one large vote.
- Never invent a creative trade-off from a validation status. If no accepted
  story fact supports a recommendation, label it as a hypothesis and ask the
  creator to choose.
- Keep alternatives as `CREATIVE_DRAFT` until the creator explicitly accepts
  one. A recommendation is not approval.
- Separate technical readiness, creative approval, and external-media quality.
  A passing render or validator does not approve the story or a generated clip.
- Preserve provenance for every fact that materially affects the recommendation.
- If the source is `UNKNOWN`, say what is unknown and how it affects the
  decision; never turn missing evidence into a neutral-looking blank.
- Keep the brief short enough for a human to scan in a few minutes. Put full
  scripts, ledgers, and schemas behind links or in the relevant working files.

## Creator workflow integration

During the seven-gate script workflow, the normal conversational output is a
small decision card after each accepted gate. Use the full template only when a
second person must review the work, the decision spans sessions, or the creator
asks for a durable artifact.

For a blank idea, the first brief should explain the audience experience and
core situation. For a revision, add a version diff: what changed, why it
changed, which accepted promise it protects, and which downstream facts may be
affected.

## Read Model integration

The static Creator Dashboard `Decision` view is evidence-bound navigation. It
can recommend resolving a blocker, completing a prerequisite, or recording a
human approval, but it must not infer artistic preferences from asset counts or
runtime states. Creative options belong in the creator-first conversation or a
completed decision brief supplied by the creator.
