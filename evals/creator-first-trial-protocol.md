# Creator-First Fresh-Context Trial Protocol

## Fixed start

Open a genuinely fresh agent context with the current FilmFoundry Skill and no project Runtime. Use: “我想写一个 8–12 分钟的短片，但现在没有故事。请从零带我完成。”

Record model/version, reasoning setting, references loaded each turn, elapsed human time, agent turns, creator interventions, accepted gates, and the final artifacts. Reference-loading time is not creator completion time.

## Pass conditions

| Requirement | Evidence |
|---|---|
| At most one material question per agent turn | Full transcript review |
| No production/provider references before explicit production request | Per-turn reference log |
| All seven creator gates are either accepted or explicitly rejected by the creator | Gate ledger |
| Complete draft has no missing scene or placeholder beat | Draft review |
| Revision includes intent/causality and character/dialogue/continuity checks | Revision record |
| Emotional map appears only when the story or creator needs it | Transcript and artifact list |
| Creator choices are not silently overwritten | Decision-diff review |

Any missing transcript, reference log, creator intervention record, or final draft makes the result `INSUFFICIENT_EVIDENCE`, not pass.
