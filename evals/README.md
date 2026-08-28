# FilmFoundry Agentic Evals

`evals.json` contains 12 realistic behavior tests for `generative-film-production`.

## Two different verification layers

**Static/TDD verification** runs in this repository with pytest. It proves the skill package, validators, and eval metadata satisfy their deterministic contracts.

**Agentic benchmark verification** requires a fresh-context agent runner capable of executing each prompt twice: once without the skill and once with the skill. This repository does not convert fixture scores into claims about real model behavior.

Recommended external procedure:

1. Run every eval prompt in a fresh context with no FilmFoundry skill loaded; save output under `runs/<date>/baseline/<eval-id>.md`.
2. Run the same prompts, model, temperature/reasoning profile, and input files with the skill loaded; save under `runs/<date>/with-skill/<eval-id>.md`.
3. Grade machine assertions first, then human assertions blind to configuration when practical.
4. Record model/version, duration, token usage, and reviewer notes.
5. Compare failure modes and variance, not only average pass rate.

The files under `fixtures/` are harness demonstrations only. They are deliberately authored examples, not LLM benchmark results.
