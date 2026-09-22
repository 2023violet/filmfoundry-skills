# Creator-First Fresh-Context Trial Protocol

## Fixed start

Open a genuinely fresh agent context with the current FilmFoundry Skill and no project Runtime. Use the same request for both paths:

> 我想写一个 8–12 分钟的短片，但现在没有故事。请从零带我完成。

Run two comparable trials with the same model, reasoning setting, and blank-project state:

- **A / strict baseline** — use the previous seven-gate interaction contract;
- **B / adaptive** — use `FAST/R0` for reversible exploration, `STANDARD/R1` for grouped decisions, and `STRICT/R2` only when Canon or acceptance is involved.

Load `skills/generative-film-production/references/46-execution-evidence.md` and record each response cycle in `templates/execution-evidence.md`. Record model/version, reasoning setting, route and lane, execution budget, references actually loaded, wall-clock start/end, human waiting time, agent turns, blocking decisions, internal steps, automatic revisions, creator interventions, accepted gates, lane upgrades, and final artifacts. Reference-loading time is useful diagnostic data but is not creator completion time.

## Comparison requirements

| Metric | Required evidence |
|---|---|
| Time to first useful comparison package | Human wall-clock record and artifact pointer |
| Time to first creator-usable script section | Human wall-clock record and artifact pointer |
| Interaction cost | Turns, blocking decisions, internal steps, automatic revisions, loaded references |
| Creator cost | Interventions, decision reversals, corrections, downstream rework |
| Story quality | Premise, character causality, structural readability, continuity, creator control |
| Safety | Canon/external mutations, missed Strict escalation, output status labels |

Do not declare B better from speed alone. It must reduce interaction cost without increasing contradictions, unauthorized mutation, or creator correction cost.

## Path-specific pass conditions

### Both paths

| Requirement | Evidence |
|---|---|
| No production/provider references before an explicit production request | Per-cycle reference log |
| All seven creator gates are accepted or explicitly rejected by the creator before final acceptance | Gate ledger |
| Complete draft has no missing scene or placeholder beat | Draft review |
| Revision includes intent/causality and character/dialogue/continuity checks | Revision record |
| Emotional map appears only when the story or creator needs it | Transcript and artifact list |
| Creator choices are not silently overwritten | Decision-diff review |

### A / strict baseline

- The transcript shows the previous one-material-question-per-turn contract;
- every Gate transition is visible;
- no budget stop or lane upgrade is used to shorten the baseline.

### B / adaptive

- `FAST` may batch options and non-blocking unknowns;
- every cycle asks at most one blocking decision;
- `OPEN`, `DEFERRED`, and `NOOP` are used only with an explicit reason or resume trigger;
- the execution budget is honored; reaching it returns the current artifact rather than silently adding turns;
- Canon or external side effects are preceded by `STRICT/R2` and explicit approval.

Any missing transcript, timing record, reference log, creator intervention record, or final draft makes the result `INSUFFICIENT_EVIDENCE`, not pass.
