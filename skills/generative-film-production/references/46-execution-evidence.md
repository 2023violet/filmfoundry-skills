# Execution Evidence and A/B Trial

Use this reference only when measuring workflow speed, comparing execution lanes,
or diagnosing repeated interaction cost. It is not required for ordinary story
creation and it does not replace a fresh human creator trial.

## What to record

Record one row per response cycle, not only the final result:

- trial ID, lane, risk level, and execution budget;
- model/version and reasoning setting;
- user request and entry state (`BLANK`, `SEED`, `OUTLINE`, `DRAFT`);
- references actually loaded, not the references merely available;
- wall-clock start/end and human waiting time;
- agent turns, blocking decisions, internal steps, automatic revisions, and creator interventions;
- output labels (`CREATIVE_DRAFT`, `ASSUMPTION`, `OPEN`, `DEFERRED`, `NOOP`, or Gate labels);
- accepted facts, changed facts, unresolved risks, and the next action;
- whether Canon, Runtime, Registry, or external systems were mutated;
- quality observations and the reason for any recovery or lane upgrade.

Reference-loading time is useful diagnostic data, but it is not a substitute for
human creator elapsed time. A static fixture, local file-count benchmark, or agent
that supplies its own decisions is not human speed evidence.

## Lane A/B protocol

Run the same user request with the same model, reasoning setting, and blank-project
state:

### A — strict baseline

Use the previous seven-gate interaction contract. Preserve the transcript and count
every question, turn, loaded reference, and accepted decision.

### B — adaptive path

Use the default route: `FAST/R0` for reversible exploration, `STANDARD/R1` when a
grouped decision is required, and `STRICT/R2` only for Canon or acceptance. Record
every lane upgrade and its reason. The adaptive path may batch options but may not
silently accept a Canon change.

## Required comparisons

Compare both trials on:

1. time to first useful comparison package;
2. time to first creator-usable script section;
3. agent turns, blocking decisions, internal steps, and automatic revisions;
4. reference count and repeated-context count;
5. creator interventions, decision reversals, and downstream rework;
6. premise clarity, character causality, structural readability, continuity, and creator control;
7. unauthorized Canon/external writes and missed Strict escalations.

Do not declare the adaptive path better from speed alone. A successful result must
reduce interaction cost without increasing contradiction, unauthorized mutation,
or creator correction cost.

## Stop and upgrade rules

- Upgrade `FAST` to `STANDARD` when the creator selects a direction that affects the next stage.
- Upgrade to `STRICT` before Canon writes, formal acceptance, external cost, or irreversible changes.
- Enter `RECOVERY` only when there is a declared failure or contradiction; repair the narrowest layer first.
- If the budget is reached, return the current artifact as `DEFERRED` and record the resume trigger.
- If a trial loses the transcript, timing, reference log, or creator intervention record, mark it `INSUFFICIENT_EVIDENCE`.

