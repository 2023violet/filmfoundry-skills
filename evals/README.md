# FilmFoundry Agentic Evals

`evals.json` contains 27 realistic behavior tests for `generative-film-production` 3.0.0.

v1.2 adds adversarial cases for Content Market Gate routing, cheapest-MVP restraint, no-monetization traffic experiments, partial-Select salvage, provider controllability over-timing, eyeline-critical keyframes, evidence overgeneralization, and the thirty-episode series engine.

## Verification layers

**Static/TDD verification** runs in this repository with pytest. It proves the skill package, validators, templates, and eval metadata satisfy deterministic contracts.

**Provider/model smoke verification** is project-specific. MiniMax H3 reference-role binding, camera hold, acting stability, spatial persistence, and other behaviors must be tested on the exact product surface/version before an adapter relies on them. The repository defines the evidence schema; it does not fabricate provider results.

**Market MVP verification** is also project-specific. FilmFoundry stores the hypothesis/evidence contract but does not fabricate audience demand, retention, payout, or monetization results.

**Agentic benchmark verification** requires a fresh-context agent runner. Run each prompt twice with the same model/settings: once without FilmFoundry and once with the skill.

Recommended external procedure:

1. Run every eval prompt in a fresh context with no FilmFoundry skill loaded; save output under `runs/<date>/baseline/<eval-id>.md`.
2. Run the same prompts/model/settings/input files with the skill loaded; save under `runs/<date>/with-skill/<eval-id>.md`.
3. Grade machine assertions first, then human assertions blind to configuration when practical.
4. Record model/version, reasoning profile, token/runtime cost, and reviewer notes.
5. Compare failure modes and variance, not only average pass rate.

The files under `fixtures/` are harness demonstrations only. They are deliberately authored examples, not LLM benchmark results. Keyword scores are smoke checks and can be gamed; they are never sufficient evidence of production quality.

E27 is a single-turn authored guardrail for the blank-script entry. Only a completed run of `creator-first-trial-protocol.md` can supply current multi-turn product evidence. One completed run still does not prove creator speed or broad market fit.
