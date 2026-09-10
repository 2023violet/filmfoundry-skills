# Creator-First Fresh-Context Trial — 2026-09-10

## Verdict

`INSUFFICIENT_EVIDENCE` for product acceptance. The fresh-context rerun passed the registered interaction and artifact checks, but the creator role was agent-controlled rather than a real human creator, human elapsed time was not measured, and the verbatim transcript is not stored as a durable repository artifact. The result must not be used as evidence of creator speed, broad usability, market fit, or release readiness.

## Execution record

| Field | First run | Fresh-context rerun |
|---|---|---|
| Context | `/root/fresh_context_trial` | `/root/fresh_context_rerun` |
| Model | `gpt-5.6-terra` | `gpt-5.6-terra` |
| Reasoning | `medium` | `medium` |
| Starting prompt | Protocol fixed start | Protocol fixed start |
| Project Runtime | None loaded | None loaded |
| References loaded | Root `SKILL.md`; `references/41-creator-first-script-workflow.md` | Root `SKILL.md`; `references/41-creator-first-script-workflow.md` |
| Agent turns | 19 | 19 |
| Creator interventions | 18 | 18 |
| Human elapsed time | Not applicable; creator was agent-controlled | Not applicable; creator was agent-controlled |
| Emotional Beat Map | Not loaded | Not loaded |
| Production/provider references | None | None |

The collaboration task mailboxes above contained the verbatim exchanges during this implementation session. The ledger below preserves the reviewed sequence, but it is not a verbatim transcript; under the preregistered protocol this alone prevents a product-evidence PASS.

## First-run finding and repair

The first run moved from `BLANK` through all seven creator gates and produced the complete script *《确认》*. It asked at most one material question per turn and never loaded Runtime, Provider, prompt-compilation, Shot Spec, or video-QC references.

The run failed the final decision-diff check. The creator accepted removal of reassuring language about the displaced patient, but the final revision still contained the semantically equivalent line “他会收到属于他的程序通知” while claiming that the issue had been removed. This was a workflow failure, not a script-taste disagreement.

The only resulting workflow change was a rule requiring a comparison between the revised draft and every accepted revision decision before `REVISION_ACCEPTED`, including a search for synonymous or softened remnants of rejected ideas.

## Fresh-context rerun ledger

| Turns | Gate | Observed result |
|---|---|---|
| 1–3 | `SEED_ACCEPTED` | Classified `BLANK`; established an 8–12 minute, painful-then-releasing story about a missing brother's unfinished recording. |
| 4–5 | `LOGLINE_ACCEPTED` | Locked 林然's last night in the family home and her choice to stop before hearing the unknown continuation. |
| 6–8 | `CHARACTER_ENGINE_ACCEPTED` | Locked want, need, contradiction, pressure response, and change without overwriting creator choices. |
| 9–11 | `DRAMATIC_RULES_ACCEPTED` | Locked realism, 林然-only viewpoint, no flashback, no explanatory monologue, and no revealed disappearance answer. |
| 12–15 | `STRUCTURE_ACCEPTED` | Built a causal chain from discovering additional tape through damaging repetition, irreversible splicing, stopping, and leaving. |
| 16 | `DRAFT_ACCEPTED` | Produced the complete six-scene script *《停止键》* with no missing scene or placeholder beat. |
| 17 | Intent/causality revision | Removed an audible unknown syllable so the stop occurs before any answer can influence 林然. |
| 18 | Character/dialogue/continuity revision | Corrected the tape splice so removed words cannot reappear during final playback. |
| 19 | `REVISION_ACCEPTED` | Applied both revisions, emitted a revision record, decision diff, and final seven-gate ledger; no equivalent contradiction remained. |

Manual transcript review found no agent turn with more than one material creator-facing question. The per-turn `questions asked` number in the agent log was cumulative rather than per-turn; the response bodies, not that cumulative counter, were used for this check.

## Final artifacts observed

- Complete revised six-scene screenplay: *《停止键》*, approximately 10 minutes, single night, single on-screen character.
- Accepted logline, character engine, dramatic rules, and causal structure.
- Intent/causality revision record.
- Character/dialogue/continuity revision record.
- Decision diff covering the two revisions and all accepted creative constraints.
- Final ledger with all seven gates accepted.

These artifacts existed in the fresh agent context; authored eval fixtures were not used as trial output. They are not represented as a human creator benchmark.

## Pass-condition scoring

| Requirement | Result | Evidence boundary |
|---|---|---|
| At most one material question per turn | Technical pass | Reviewed response bodies for both runs |
| No production/provider references before request | Pass | Per-turn logs named only root Skill and reference 41 |
| Seven gates accepted or rejected | Pass | Final rerun ledger accepted all seven |
| Complete draft, no placeholders | Pass | Six complete scenes in *《停止键》* |
| Two required revision passes | Pass | Two creator-confirmed changes applied and diffed |
| Emotional map optional | Pass | Never loaded or required |
| No silent overwrite | First run fail; rerun pass | First-run semantic remnant prompted the workflow repair; rerun decision diff was clean |
| Real creator and human elapsed evidence | Missing | Creator role was controlled by the implementing agent; no human timing exists |
| Durable verbatim transcript | Missing | Only the reviewed ledger is committed |

## State-design decision

The rerun preserved accepted decisions across 19 agent turns, resumed the earliest unresolved gate correctly, and completed both revision passes without state loss. This evidence does not justify a Python enum, Schema, CLI write command, or persisted state machine. Keep the instruction-first workflow and use the optional workbook when durable or cross-session state is actually needed. Reconsider machine state only after repeated observed loss or ambiguous resumption.

The next valid product-evidence action is one human-led run of `evals/creator-first-trial-protocol.md` with a durable verbatim transcript and measured human elapsed time. Provider-surface classification and cleanup planning remain gated on that evidence.

This checkpoint does not approve a FilmFoundry release; provider-surface removal remains pending.
