# Work Modes

FilmFoundry separates exploration from production evidence. The mode is a request boundary, not a project state and not a replacement for the source-of-truth contracts.

## Creative Mode

Use when the user asks for possibilities, hooks, emotional directions, story analysis, character motivation, or a prompt draft. For a blank idea, fragment, outline, or draft, load `41-creator-first-script-workflow.md` first and advance only the earliest unresolved creator gate. Load Creative Brief, Story Development and Breakdown, Script Facts and Emotion, or market references only when the current stage requires them.

Choose the lightest safe execution lane before interacting:

| Lane | Use when | Interaction contract |
|---|---|---|
| `FAST` / `R0` | Reversible exploration or a disposable draft | Batch two or three materially different options; ask no question unless blocked; do not write Canon |
| `STANDARD` / `R1` | A grouped decision affects the next creative stage | Produce one compact decision package; ask at most one blocking decision; record assumptions and open items |
| `STRICT` / `R2` | Canon, acceptance, external cost, or irreversible side effect is involved | Preserve the full Gate and human-approval boundary; do not infer approval from generation |
| `RECOVERY` / `R1` | A declared validation failure, contradiction, or failed handoff needs diagnosis | Read only the narrowest failure evidence; repair the smallest failing layer and resume from the saved state |

A blank project requires a creator decision, not Runtime initialization. In `FAST` and `STANDARD`, do not force one question for every gate: ask at most one blocking decision per turn and batch non-blocking alternatives into a creator-readable package. In `STRICT`, a single decision may still be required when it protects Canon or a high-cost action.

Use the route's soft execution budget as a stop condition. The default budget is expressed as `max_blocking_decisions`, `max_internal_steps`, and `max_auto_revisions`; it is a ceiling for one response cycle, not a quality score. When reached, return the best current result as `DEFERRED`, state what remains, and give the exact trigger for resuming. Never continue planning merely to consume the budget, and never treat a budget limit as permission to skip a Gate.

Do not run full Runtime validation, media audit, dependency indexing, Provider Smoke, or provider calls. Do not write Canon, Runtime, Registry, assets, or archive content. Treat missing project facts as `ASSUMPTION` or `DEFERRED_CHECK`, and expose a real contradiction as `HARD_CANON_CONFLICT`.

The response shape is:

1. `CREATIVE_DRAFT`: the proposed direction or alternatives.
2. `ASSUMPTION`: facts supplied by the user or temporarily assumed for exploration.
3. `OPEN`: an unresolved item that does not block the current draft.
4. `DEFERRED`: a decision or check intentionally postponed with a trigger for resuming it.
5. `DEFERRED_CHECK`: checks that belong to Production or Gate Mode.
6. `NOOP`: no safe action is needed yet; explain the trigger for continuing.
7. `HARD_CANON_CONFLICT`: only when the supplied sources directly disagree.

## Commit Mode

Use when the user selects or locks a direction. Summarize the choice, convert assumptions into explicit facts or open questions, and report Canon conflicts. Do not silently write source authorities or invoke providers. The user must authorize the actual source update as a separate operation.

## Production Mode

Use for Shot Specs, asset bindings, prompt compilation, timelines, voice, and
Provider-neutral handoffs. Load the relevant production references and run only the
checks needed for the requested artifact: runtime, state, asset, and dependency
checks as applicable. An external adapter may translate the handoff later; Core does
not call it or claim its behavior.

## Gate Mode

Use for readiness, producibility, release, publish, or acceptance questions. Run the
complete FilmFoundry-owned contract, dependency, and handoff review required by the
route. External generation, returned media, and aesthetic review are reported only as
human/external evidence; they are not executed by this Skill. Report blockers and
actions separately; `UNKNOWN` is not success.

## Routing rule

When a request contains both exploration and production language, answer the smallest requested creative part first and state the exact boundary that would enter Production or Gate Mode. Do not upgrade a Creative request merely because project files are incomplete.

For every response, expose only the minimum decision surface: `goal`, `lane`, `risk`, `execution budget`, `accepted facts`, `assumptions`, `open/deferred items`, `checks run`, and `next action`. A complete internal workflow is not a reason to show every intermediate step to the creator.
