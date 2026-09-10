# Work Modes

FilmFoundry separates exploration from production evidence. The mode is a request boundary, not a project state and not a replacement for the source-of-truth contracts.

## Creative Mode

Use when the user asks for possibilities, hooks, emotional directions, story analysis, character motivation, or a prompt draft. For a blank idea, fragment, outline, or draft, load `41-creator-first-script-workflow.md` first and advance only the earliest unresolved creator gate. Load Creative Brief, Story Development and Breakdown, Script Facts and Emotion, or market references only when the current stage requires them.

A blank project requires one creator question, not Runtime initialization. Ask one question per turn, wait for the creator's answer, and keep alternatives as drafts until the creator accepts them.

Do not run full Runtime validation, media audit, dependency indexing, Provider Smoke, or provider calls. Do not write Canon, Runtime, Registry, assets, or archive content. Treat missing project facts as `ASSUMPTION` or `DEFERRED_CHECK`, and expose a real contradiction as `HARD_CANON_CONFLICT`.

The response shape is:

1. `CREATIVE_DRAFT`: the proposed direction or alternatives.
2. `ASSUMPTION`: facts supplied by the user or temporarily assumed for exploration.
3. `DEFERRED_CHECK`: checks that belong to Production or Gate Mode.
4. `HARD_CANON_CONFLICT`: only when the supplied sources directly disagree.

## Commit Mode

Use when the user selects or locks a direction. Summarize the choice, convert assumptions into explicit facts or open questions, and report Canon conflicts. Do not silently write source authorities or invoke providers. The user must authorize the actual source update as a separate operation.

## Production Mode

Use for Shot Specs, asset bindings, prompt compilation, timelines, voice, and provider payloads. Load the relevant production references and run only the checks needed for the requested artifact: runtime, state, asset, and dependency checks as applicable. Provider behavior remains unknown until scoped evidence exists.

## Gate Mode

Use for readiness, producibility, release, publish, or acceptance questions. Run the complete capability-scoped validation, media and dependency review, and provider smoke checks required by the route. Report blockers and actions separately; `UNKNOWN` is not success.

## Routing rule

When a request contains both exploration and production language, answer the smallest requested creative part first and state the exact boundary that would enter Production or Gate Mode. Do not upgrade a Creative request merely because project files are incomplete.
