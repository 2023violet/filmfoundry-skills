# FilmFoundry documentation

This index separates current instructions from historical evidence. The repository is in a creator-first product reset; the local technical RC is not approved for publication.

## Current user documents

- [FilmFoundry Skills 全流程使用手册](filmfoundry-skills-user-manual-zh.md) — 从安装、四种入口和七个创作 Gate，到视觉生产准备、外部交接与验证的公开第一入口。
- [Creator-first script workflow](../skills/generative-film-production/references/41-creator-first-script-workflow.md) — the current starting point for a blank idea, outline, or draft.
- [Creator-first trial protocol](../evals/creator-first-trial-protocol.md) — the fresh-context product-evidence procedure.
- [FilmFoundry v3 technical guide](filmfoundry-v3.md) — documents the implemented v3 contracts and CLI. It is not yet the approved creator onboarding flow.
- [FilmFoundry v3 support matrix](filmfoundry-v3-support-matrix.md) — states what the current code can represent and validate, including deprecated product surfaces that still need removal.
- [AI video production guide (Chinese)](ai-video-production-guide-zh.md) — production-stage reference used after a script or stable section is accepted.
- [FilmFoundry 通用化重构规范 v1](filmfoundry-generalization-spec-zh.md) — 设计项目、风格、Provider 与 Core 边界的通用化规范；文档仍是设计基线，P0/P1 的最小实现已落地，但未构成发布批准。
- [Project / Style Profiles](../skills/generative-film-production/references/42-project-style-profiles.md) — 当前最小项目与风格输入契约。
- [Provider-neutral Handoff](../skills/generative-film-production/references/43-provider-neutral-handoff.md) — Core 到外部工具之间的稳定交接边界。
- [Failure Diagnosis](../skills/generative-film-production/references/44-failure-diagnosis.md) — 按可见事实和最窄失败层定位问题。
- [Human Decision Layer](../skills/generative-film-production/references/45-human-decision-layer.md) — 把创作事实投影为决策者可读的当前问题、推荐、取舍、风险和下一步。
- [Execution Evidence](../skills/generative-film-production/references/46-execution-evidence.md) — 记录执行预算、交互成本和严格/自适应 fresh-context A/B 结果；不是普通创作必读流程。

## Evidence and history

- [Skill 高效工作流调查与 FilmFoundry 优化基线](reports/2026-09-21-skills-efficiency-workflow-investigation-zh.md) — 基于 GitHub/Hugging Face 官方 Skill、Agent 和工作流资料的速度/质量调查；提出自适应车道、决策预算和 P0/P1 验证方案，作为 2026-09-22 已落地优化的历史设计基线。
- `reports/` contains dated reviews and verification evidence. A report describes what was true at that checkpoint; it is not the current product decision.
- `superpowers/` contains implementation plans and historical handoffs. These are repository history, not newcomer instructions.
- `filmfoundry-v2.2-user-guide.md` is historical and excluded from the active release archive.

The repository-level source of truth for current work is `CURRENT_HANDOFF.md`. It intentionally stays outside the distributable Skill archive so release artifacts contain user-facing documentation rather than local branch administration.
