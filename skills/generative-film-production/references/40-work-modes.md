# Work Modes

FilmFoundry separates exploration from production evidence. The mode is a request boundary, not a project state and not a replacement for the source-of-truth contracts.

## Creative Mode

Use when the user asks for possibilities, hooks, emotional directions, story analysis, character motivation, shot alternatives, or a prompt draft. Load only the references needed for that question, normally Production Philosophy, Creative Brief, Story Breakdown, Script Facts and Emotion, or AI-native Content Design.

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
