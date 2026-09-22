# Skill 高效工作流调查与 FilmFoundry 优化基线

**调查日期：** 2026-09-21  
**适用范围：** FilmFoundry Core / 创作者优先剧本工作流 / Skill 执行与决策交互  
**文档性质：** 外部真实工作流调查、问题诊断和 P0/P1 实施基线；不是发布批准，也不是本次对 Skill 行为的直接修改。

## 结论先行

FilmFoundry 当前的主要速度问题，不是缺少规则，而是把所有任务都按“高风险、不可回退、必须逐项对齐”的方式处理了。对于一个可撤销的创意草稿，当前流程会产生以下过程税：

- 每个小问题都触发一次完整的 Gate 对齐；
- 已经可以安全假设的内容被重复询问；
- 规则、参考文件、历史上下文在每一轮都被重新加载；
- 生成、检查、提交和外部交接混在同一条严格路径里；
- 人类决策者看到的不是一个可比较的创作包，而是很多零散确认点。

GitHub 和 Hugging Face 上较成熟的 Agent/Skill 工作流有一个共同方向：**把质量控制从“更多对话步骤”迁移到“更小的上下文、更强的输出契约、更少但更有价值的人类决策，以及可重复的确定性检查”。** 其中最重要的不是让模型更快地连续调用，而是减少不必要的 LLM 调用和人类等待。

本调查建议 FilmFoundry 采用以下目标模型：

> **默认快速探索，按风险升级到严格 Gate；一次交互产出一个小型创作包，而不是审议一个完整流程。**

这不等于取消七个 Gate，也不等于降低质量。七个 Gate 继续作为 Core 合同和验收语义存在，但不应在每个创作草稿阶段都以“逐问、逐轮、逐 Gate”的对话形式出现。低风险草稿应该批量生成、局部自检、明确标记为未提交；高风险的 Canon 变更、对外写入、最终交付和不可逆操作才进入严格路径。

## 1. 调查问题与证据边界

本次调查回答五个问题：

1. 真实公开项目如何组织 Skill、Agent 和工作流，使调用次数较少而产出仍可控？
2. 哪些机制是在“对话前”减少工作，哪些机制是在“输出后”保证质量？
3. 哪些机制可以迁移到 FilmFoundry，而不会破坏创作者优先、Provider-neutral 和人类决策边界？
4. FilmFoundry 当前的慢点属于模型能力问题、Skill 编排问题，还是人类审批边界问题？
5. 如何用一轮小规模验证证明“更快”没有变成“更随意”？

证据分为三类：

| 证据层 | 含义 | 本调查的用法 |
|---|---|---|
| 官方仓库/官方文档 | 项目维护者明确写出的设计规则、接口和示例 | 作为可复用的设计模式，不直接当作 FilmFoundry 的性能证明 |
| 官方教程/参考实现 | 能运行的 Agent 循环、参数、终止条件或脚本 | 用于提取调用上限、检查点和确定性边界 |
| FilmFoundry 本地事实 | 当前 Skill、参考文件、测试和交接记录 | 用于诊断当前摩擦点和定义本地验证 |

需要明确：公开仓库很少提供同一模型、同一提示、同一创作任务的严格速度 A/B 数据。因此本文将外部材料视为**设计证据**，而不是宣称外部项目已经证明 FilmFoundry 会快多少。速度和质量必须由 FilmFoundry 的新鲜上下文试验测量。

## 2. 调查对象与关键发现

### 2.1 OpenAI Codex skill-creator：入口要薄，详细规则按需加载

[OpenAI Codex 的 skill-creator 示例](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)强调：Skill 入口只保留非显而易见的指导，保持任务意图和范围，具体程度要与风险匹配；共享路由放在入口，模式特定的细节放到按需加载的 references；重复、泛化和过度约束会降低模型表现；确定性的重复操作应尽量脚本化并验证。

对 FilmFoundry 的直接启示：

- SKILL.md 只负责判断是否触发、选择工作模式、识别风险和告诉模型加载哪一个参考文件；
- 生成某个剧本阶段时，不应预加载所有视觉、Provider、诊断和历史材料；
- 只要任务是可撤销草稿，就不应自动进入完整生产检查；
- “知道更多规则”不等于“当前回合要执行更多规则”。

### 2.2 Anthropic Skills：短入口、清晰触发、输出契约和按需资源

Anthropic 的 [Skills 仓库](https://github.com/anthropics/skills)展示了一种清晰的分层：每个 Skill 自包含，入口描述作用域和触发条件，详细模板、脚本和示例按需要读取。

[skill-development 指南](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md)特别强调入口要精简，详细内容放在 references；先在真实任务中观察 Skill 哪里迟缓或失效，再针对性修改，而不是预先增加更多规则。其示例 Skill 还有几个稳定模式：

- 入口先说明“什么时候用、什么时候不用”；
- 用小型决策表把任务类型映射到工作方式；
- 用输出契约替代反复口头确认；
- 用脚本完成可重复的结构检查、格式化和计算；
- 只有选定的资源才进入当前任务。

[xlsx Skill](https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md)是一个典型的短入口：它把范围、方法选择、输出质量要求和常见失败集中写清楚，把复杂操作交给引用脚本。它没有要求模型在每次单元格编辑前与用户完成一轮形式对齐。

[doc-coauthoring Skill](https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md)更直接地说明了“分阶段不等于强制长流程”：用户可以选择完整协作流程，也可以选择自由创作；只有在长文档和高不确定性任务中才逐节精修；读者测试被放在文档基本成形之后，而不是每个段落之后。

对 FilmFoundry 的启示是：应把“严格剧本审议”作为一种工作模式，而不是所有请求的默认交互协议。

### 2.3 Hugging Face smolagents：减少 LLM 调用，确定性函数优先

Hugging Face 的 [smolagents building good agents](https://github.com/huggingface/smolagents/blob/main/docs/source/en/tutorials/building_good_agents.md)把核心经验写得非常直接：**尽可能减少 LLM 调用次数**；能用确定性函数完成的事情不要交给 Agent；把相关工具组合起来，避免为了一个小动作多次来回；为工具提供清晰的输入输出和错误信息。

其 [Agent 参考文档](https://huggingface.co/docs/smolagents/reference/agents)把几个速度和可靠性控制项公开成参数：

- `max_steps`：限制一次任务允许的 Agent 步数；
- `planning_interval`：只在需要时周期性规划，不是每一步都重新规划；
- `final_answer_checks`：输出前运行确定性检查；
- memory/replay：保存已完成步骤，恢复时不重复成功工作；
- tool calling 的并行能力：多个互不依赖的工具调用可以并行。

[Agents Course 教程](https://huggingface.co/learn/agents-course/unit1/tutorial)使用有限的 `max_steps` 和最小工具集来构造可运行示例，这说明“有上限的 Agent”比“允许无限解释和尝试”更适合生产流程。

对 FilmFoundry 的启示：

1. 创作请求应该有明确的最大澄清问题数、最大内部步骤数和停止条件；
2. 角色卡、场景表、连续性清单等重复校验应当是本地确定性检查，不应变成一串 LLM 对话；
3. 一次请求中的互不依赖选项可以成组生成，而不是逐个请求；
4. 已确认事实应进入上下文卡或状态快照，下一轮不应重新确认。

### 2.4 GitHub Agentic Workflows：确定性预处理，便宜分支优先，高价值才升级

GitHub 的 [Agentic Workflows](https://github.github.com/gh-aw/about/)把确定性的 GitHub Actions 与 Agent 推理组合在一起：触发、权限、工具和沙箱由机器控制，Agent 只处理需要判断、调查或生成的部分。

[Deterministic Agentic Patterns](https://github.github.com/gh-aw/guides/deterministic-agentic-patterns/)给出了适合迁移到 FilmFoundry 的成本分层：先做确定性预计算、过滤和上下文压缩；高频、低价值、已知或重复情况走廉价分支；只有歧义大、价值高的情况才使用更强推理。

[IssueOps 模式](https://github.github.com/gh-aw/patterns/issue-ops/)还明确加入 `noop`：当没有安全动作或没有必要动作时，工作流可以显式地不行动，而不是为了“完成一次流程”继续调用 Agent。

对 FilmFoundry 的启示：

- 剧本任务先分类为“探索、修订、提交、外部交接”；
- 先读取最小上下文卡并做规则检查，再调用模型；
- 不需要修改 Canon 时，允许 `DRAFT_ONLY` 或 `DEFERRED`；
- 不确定但不影响当前草稿时，记录为待定，不把它强行升级为用户问题；
- 高成本或不可逆 Provider 操作必须单独确认。

### 2.5 LangGraph：只在高风险节点中断，人类批准后恢复

LangGraph 的 [checkpointer 机制](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/checkpointers.mdx)支持在步骤边界保存状态，从而实现恢复、人工介入、时间旅行和故障后继续。其 [Human-in-the-loop 文档](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/human-in-the-loop.mdx)使用条件 `when` 决定是否中断：安全调用可以自动继续，只有需要审批、编辑或拒绝的动作才暂停；暂停后带着原状态恢复，而不是从头再跑。

对 FilmFoundry 的启示是：**人工决策边界应该绑定动作风险，而不是绑定每一个生成步骤。** 生成三个可撤销的 Logline 草案不需要人类逐项批准；将其中一个写入 Canon、生成外部资产或宣布交付完成才需要批准。

### 2.6 OpenAI Cookbook：小阶段、验收条件、真实证据和复盘

[OpenAI Cookbook 的 Codex 迭代工作流示例](https://github.com/openai/openai-cookbook/blob/main/examples/codex/iterating-development-workflows-with-codex.md)强调：仓库是事实源；把计划拆成有边界的小阶段；每个阶段写清依赖、非目标、预期文件和验收方式；在实际任务中观察摩擦，再做下一轮改进。

其中两个原则适合 FilmFoundry：

- 只记录会影响范围、实现、验证、安全或未来决策的事实；
- 让模型提供观察到的测试/验证证据，而不是用一份巨大流程文件替代证据。

这支持“短上下文 + 明确输出 + 可复查证据”，不支持“把所有可能的规则都放进每一轮对话”。

## 3. 跨项目共性：高效且高质量的工作流到底做了什么

| 共性原则 | 外部证据 | 对 FilmFoundry 的翻译 |
|---|---|---|
| 入口轻量 | Codex skill-creator、Anthropic skill-development | SKILL.md 负责路由，不承担全部知识库 |
| 按需加载 | Codex skill-creator、Anthropic Skills | 一次只加载当前 Gate/模式需要的参考文件 |
| 任务分层 | GitHub Agentic Workflows、Anthropic doc-coauthoring | 探索、标准修订、严格提交使用不同路径 |
| 少调用模型 | smolagents | 合并相关问题、减少重复澄清和重复规划 |
| 确定性检查 | smolagents、GitHub Agentic Workflows | 连续性、字段、格式、状态检查交给脚本/规则 |
| 步数与预算上限 | smolagents `max_steps`、Agent tutorial | 设置最大问题数、内部步骤数、时间预算 |
| 只在高风险动作中断 | LangGraph HITL | Canon、外部写入、最终交付才需要批准 |
| 可恢复状态 | LangGraph checkpointer、smolagents memory | 记录已确认事实和中间产物，不重复启动 |
| 无动作是合法结果 | GitHub IssueOps | `NOOP` / `DEFERRED` 不是失败，而是安全终止 |
| 输出契约代替仪式 | Anthropic xlsx、smolagents final checks | 先规定交付字段，再做一次集中检查 |
| 真实任务复盘 | OpenAI Cookbook、Anthropic skill-development | 以新鲜上下文的耗时、问题数、修订次数反馈 Skill |

### 3.1 “高质量”不是“更多步骤”

外部项目共同把质量拆成三个部分：

1. **输入质量**：最小但明确的任务、范围和事实上下文；
2. **过程约束**：工具接口、状态、权限、步数、风险中断；
3. **输出验证**：确定性检查、最终答案检查、读者测试、人工确认。

FilmFoundry 当前较强的是 Core 语义、Provenance、Gate 和人类决策展示；缺口是把这三部分在执行层分离。现在许多“过程约束”以人类对话仪式呈现，因此速度损失被错误地归因于质量要求。

### 3.2 “更多 Agent”不是默认答案

smolagents 的多 Agent 文档也把专业分工限定在真正需要的任务上。对于一个普通 Logline 或人物关系修订，增加多个代理只会增加上下文交接和协调成本；只有当任务可以并行、职责真正独立、结果需要互相审查时，才值得引入多 Agent。

FilmFoundry 当前应优先减少流程调用和重复确认，而不是引入更多角色型 Agent。

## 4. FilmFoundry 当前慢点诊断

当前工作流的 creator-first 方向是正确的：它先保护创作者意图，再逐步确认故事事实、角色、戏剧规则、结构和草稿。问题出在**统一执行协议过于严格**，不是七个 Gate 的语义本身错误。

结合当前 [creator-first script workflow](../../skills/generative-film-production/references/41-creator-first-script-workflow.md)、[工作模式](../../skills/generative-film-production/references/40-work-modes.md) 和 [人类决策层](../../skills/generative-film-production/references/45-human-decision-layer.md)，主要摩擦如下：

### 4.1 所有请求都被当作高风险请求

“先问一个关键问题”在防止 AI 自说自话时很有价值，但当用户已经给出明确方向，或只是要三种可撤销创意草案时，每次仍只推进一个问题，会造成不必要的等待。应区分：

- 影响 Canon、连续性和后续生产的决定；
- 只影响本轮草稿的可撤销选择；
- 可以暂时未知、以后再补的事实。

### 4.2 Gate 语义与 Gate 对话被混为一体

Gate 作为“是否可提交”的语义边界必须保留；但 Gate 不应要求每次生成一小段文本都完成一次正式审议。探索阶段可以生成 `CREATIVE_DRAFT`，同时附带假设、未决项和检查结果；只有提交或升级时才变成已接受事实。

### 4.3 问题粒度太细，缺少小型创作包

用户通常希望看到一组可比较的方向，而不是分别回答“主题是什么、主角是谁、目标是什么”。对于低风险任务，模型可以在一轮内生成 3 个 Logline、一个简短角色冲突表和每个方向的代价说明，再请用户选择或改写。这样人类决策仍然存在，但决策对象更接近创作，而不是流程确认。

### 4.4 规则阅读成本可能高于任务本身

Provider、视觉风格、失败诊断和生产交接是必要的边界，但写剧本第一稿时不一定需要加载。入口路由必须先判断当前请求属于剧本探索、剧本修订、视觉准备还是外部交接，然后只加载一条相关参考链。

### 4.5 缺少可见的成本上限和终止条件

当前严格流程表达了“必须对齐”，但没有同样显式地表达“最多问几次、最多内部迭代几次、什么时候先交付一个可用版本”。没有上限，模型容易用更多解释和确认来降低自己的不确定性，最终把成本转移给创作者。

## 5. 建议的目标模型：自适应三车道

建议保留当前严格模式，同时增加按风险选择的执行车道。车道是执行协议，不是新的项目分支，也不改变 Core 合同。

### 5.1 Fast / Sprint：可撤销探索

适用：空白想法、Logline 变体、人物动机候选、场景版本、对白试写、风格试探、结构选项。

行为：

- 默认不改 Canon，不承诺最终连续性；
- 一次读取最小上下文卡；
- 可在一轮内批量生成 3 个左右选项或一个小型创作包；
- 最多提出一个阻塞性问题，非阻塞信息记录为 `OPEN` 或 `DEFERRED`；
- 结果显式标记为 `CREATIVE_DRAFT`；
- 通过确定性检查后直接交付，不等待逐项 Gate 批准。

### 5.2 Standard / Balanced：可比较的中等风险修订

适用：用户已有方向但希望形成角色卡、剧情梗概、短场次或一轮结构修订。

行为：

- 把相邻决策合并成一个小阶段，例如“种子 + Logline”或“角色 + 冲突规则”；
- 输出事实、假设、风险和建议选择；
- 将多个问题压缩成一个决策包，而不是每个问题单独等待；
- 允许一轮自检和一次局部修订；
- 只有当变更会影响已确认 Canon 或下游交付时才停下来确认。

### 5.3 Strict / Gate：提交、交接和不可逆动作

适用：把草稿写入 Canon、宣布阶段接受、生成最终剧本交付、对外工具调用、Provider handoff、重大连续性变更。

行为：

- 维持当前严格的事实、连续性、Provenance、Gate 和人类决策卡；
- 只展示仍需决策的项目；
- 通过 checkpointer/状态快照恢复，不从头重问；
- 外部写入和不可逆动作必须有明确的人类批准。

### 5.4 Recovery：失败和矛盾诊断

适用：质量检查失败、角色动机矛盾、连续性冲突、需求变更或 Provider-neutral 交接失败。

行为：

- 只读取失败层所需的证据；
- 按最窄原因修复，不重新执行完整创作流程；
- 失败诊断和创作重写分开，避免模型用重写掩盖不确定性。

## 6. 决策预算：什么时候直接做，什么时候问人

可以为每个请求计算一个轻量风险等级，而不是把“有未知项”直接等同于“必须提问”。建议使用以下四个因素：

- **可逆性**：草稿可随时丢弃，还是写入固定事实；
- **影响范围**：只影响一个段落，还是影响角色、结构、连续性和后续镜头；
- **外部副作用**：是否写文件、调用 Provider、消耗预算或对外发布；
- **歧义价值**：不同理解是否会导致完全不同的创作方向。

| 等级 | 典型请求 | 行为 |
|---|---|---|
| R0 | 生成候选、改写一句话、尝试一种场景语气 | 直接执行；最多记录假设 |
| R1 | 角色卡、短梗概、结构变体、局部连续性修订 | 批量执行；集中展示取舍；必要时只问一个问题 |
| R2 | 提交 Canon、最终接受、外部调用、重大连续性改变 | 严格 Gate；先展示人类决策卡并等待批准 |

决策规则应当是：

1. 能安全假设且可撤销，就先做并显式标记假设；
2. 多个方向都合理，就一次生成可比较选项，不为每个选项分别发问；
3. 只要会产生不可逆影响或改变已确认事实，就暂停并询问；
4. 仅仅“还不知道”但不阻塞当前草稿时，使用 `OPEN` / `DEFERRED`，不要强制创作者立即决定；
5. 没有安全动作时，允许返回 `NOOP`，说明原因和下一步触发条件。

## 7. 推荐的快速交互协议

### 7.1 目标流程

```text
用户请求
  ↓
识别目标 + 车道 + 风险等级
  ↓
读取最小上下文卡
  ↓
批量生成一个小型创作包
  ↓
运行确定性/局部质量检查
  ↓
交付结果、假设、未决项和一个必要决策
  ↓
只有在提交或高风险动作时进入 Strict Gate
```

### 7.2 一轮快速创作包的最小结构

```text
目标：本轮要帮助创作者做什么
输出：2–4 个可比较选项或一个短版本
已知事实：直接来自上下文或用户
假设：本轮为了继续而暂定的内容
风险：会影响哪些后续决定
检查：已自动检查的规则
下一步：只列一个必要的人类决定；没有则写 NOOP
状态：CREATIVE_DRAFT / OPEN / DEFERRED / READY_FOR_GATE
```

这个结构将“方便 AI 看”的状态字段，转换为“决策者能看懂”的创作结果。人类不必阅读完整内部过程，只需看到选项、差异、代价和下一步。

### 7.3 例：从零开始的首次请求

当前严格路径可能需要分别确认主题、主角、目标、阻力、结局方向和结构。快速路径可以先问一次高价值问题，例如受众或情绪承诺，然后在同一轮返回：

- 3 个 Logline 方向；
- 每个方向的主角欲望、核心障碍和情绪代价；
- 一句说明“继续这个方向会锁定什么”；
- 尚未决定的内容；
- 让创作者选择、合并或直接改写的单一入口。

这仍然保留创作者的主导权，但把决策对象从六个孤立问题变成三个可比较的创作方向。选定方向后，才进入 Standard 或 Strict。

## 8. 如何在加速时保持质量

### 8.1 把质量放到输出契约和检查器

每个车道都要有不同的输出契约：

- Fast：创意清晰、差异可见、假设标记、无 Canon 写入；
- Standard：事实/假设分离、角色因果完整、结构约束满足、可局部修订；
- Strict：Gate 条件、Provenance、连续性、交付格式和人类批准齐全。

输出契约比“请再次确认你是否确认”更可靠，因为它可以由人和脚本共同检查。

### 8.2 确定性检查优先

适合脚本或规则检查的内容包括：

- 必填字段、状态值、枚举和格式；
- 角色名、场景编号、时间地点是否一致；
- 已确认事实是否被无意改写；
- Shot/Scene 引用是否存在；
- Provider-neutral 数据是否符合 schema；
- `CREATIVE_DRAFT` 是否误写入正式 Canon。

LLM 应该把时间用于创意判断、取舍和语言，而不是重复数数、查字段和确认状态。

### 8.3 只在动作风险处做人类审批

人类应该看得到并决定：

- 故事方向和价值取舍；
- 影响后续的角色/结构选择；
- 进入 Canon 的内容；
- 外部成本、Provider、最终交付和不可逆写入。

人类不必审批：

- 可随时丢弃的草稿；
- 模型已经按已知事实生成的多个版本；
- 已有确定性检查器覆盖的格式和状态转换。

### 8.4 用状态快照避免重复对齐

每轮输出都应保存一个小型上下文卡，至少包含：

- 已接受事实；
- 当前工作车道和风险等级；
- 当前草稿引用；
- 未决项和延期项；
- 最近一次检查结果；
- 下一步触发条件。

下一次请求从这个快照继续，而不是再次从完整历史中寻找“用户到底确认了什么”。

## 9. FilmFoundry 的 P0 / P1 实施建议

本次用户要求明确不展开 P2，因此本文只列 P0 和 P1；P2 不纳入当前调查后的实施承诺。

### P0：降低交互过程税，保留现有质量边界

1. 在 `41-creator-first-script-workflow.md` 中增加 Fast / Standard / Strict / Recovery 车道和 R0/R1/R2 风险路由。
2. 把“每轮只能问一个问题”改为“每轮最多一个阻塞性决策；可比较的非阻塞决策合并为一个创作包”。
3. 明确 `CREATIVE_DRAFT`、`OPEN`、`DEFERRED`、`READY_FOR_GATE`、`NOOP` 的状态语义。
4. 增加最小上下文卡模板，规定已确认事实、假设、风险、检查和下一步。
5. 将相邻 Gate 组织成小阶段，不改变七 Gate 的 Core 语义：
   - Seed + Logline：快速建立方向；
   - Character + Dramatic Rules：建立因果和取舍；
   - Structure + Draft：在方向已选时形成可读版本；
   - Revision + Acceptance：保留严格路径。
6. 在入口处明确“何时不要加载”视觉、Provider、交接和历史参考。
7. 保持 Canon、Provider handoff、外部写入和最终交付继续走 Strict Gate。

### P1：让速度可测量、可回归

1. 为 Fast/Standard/Strict 记录：墙钟时间、用户轮数、澄清问题数、内部步骤数、参考文件数、草稿修订次数、最终接受次数和返工原因。
2. 增加一次 fresh-context A/B：同一提示和模型分别执行当前 Strict 路径与自适应路径。
3. 将质量评分拆为创作维度，而不是只看流程是否完成：主题/承诺清晰度、角色因果、结构可读性、连续性、创作者控制感、决策者可读性。
4. 给每个车道设置可调上限：最大澄清问题数、最大内部步骤数、最大自动修订轮数和时间预算；达到上限时输出当前结果和明确的继续选项。
5. 在人类决策层中显示“这是草稿还是已提交事实”，避免加速后出现状态误读。
6. 以复盘结果为依据调整规则；不要因为一次成功案例就永久放宽 Strict Gate。

## 10. 验证设计：证明快了，而且没有变差

### 10.1 A/B 方案

| 项目 | A：当前严格路径 | B：自适应路径 |
|---|---|---|
| 输入 | 同一份空白项目请求 | 同一份空白项目请求 |
| 模型和工具 | 固定 | 固定 |
| 路由 | 七 Gate 逐步对齐 | Fast → Standard → Strict 按风险升级 |
| 记录 | 墙钟时间、轮数、问题数、返工 | 同左，增加车道和升级原因 |
| 质量评估 | 人类决策者盲评 | 人类决策者盲评 |
| 状态安全 | 检查是否错误写入 Canon | 同样检查 |

### 10.2 建议指标

速度指标：

- 首个可比较创作包的墙钟时间；
- 首个可用剧本片段的用户轮数；
- 澄清问题数和重复确认数；
- 每个任务的 LLM 调用/内部步骤数；
- 加载的参考文件数量和上下文规模。

质量指标：

- 主题和情绪承诺是否清晰；
- 角色欲望、障碍和行动是否形成因果；
- 结构是否满足任务要求；
- 是否产生新矛盾或破坏已确认事实；
- 创作者是否能快速指出“选哪个、改什么、为什么”；
- 决策者是否能区分事实、假设、风险和下一步。

安全指标：

- 未经批准的 Canon 写入次数必须为零；
- 未经批准的外部调用次数必须为零；
- 需要严格审批的动作是否都正确升级；
- 恢复时是否重复询问已经确认的事实；
- `NOOP`/`DEFERRED` 是否被正确解释为安全状态而非失败。

“更快”的目标应先写成可验证假设，而不是承诺固定分钟数。例如：在相同输入下，Fast 车道应明显减少首次可比较输出的等待和问题数，同时不增加事实冲突、未授权写入和后续返工。具体阈值应在首次 fresh-context 基线之后设定。

## 11. 不应采用的“加速”方式

- 删除 Provenance、连续性和人类决策层；这会把速度换成不可追溯的返工。
- 让模型默认把草稿写入 Canon；这会破坏创作者的可逆探索空间。
- 把所有 Gate 合并成一个模糊的大提示；这会隐藏失败层，降低诊断能力。
- 只增加模型上下文或更换更强模型；如果流程仍然逐问，过程税仍在。
- 引入多 Agent 处理每个小问题；协调成本通常高于收益。
- 用自然语言反复检查字段、数量和状态；这些应该由确定性检查器完成。
- 取消所有提问；在高风险、不可逆或重大价值取舍处，人类决策仍然必须可见。
- 用静态测试或作者编写的 fixture 宣称“创作者速度已经提升”；必须使用新鲜上下文和真实人类耗时。

## 12. 最终建议

FilmFoundry 下一阶段不应继续增加更多强制流程，而应实施一层很薄的自适应路由：

1. 先判断请求是探索、修订、提交、交接还是恢复；
2. 再按可逆性、影响范围、外部副作用和歧义价值选择车道；
3. Fast/Standard 车道批量产出创作包，使用假设、未决项和确定性检查保持质量；
4. Strict 车道只守住 Canon、交付、外部工具和不可逆动作；
5. 让状态快照、`NOOP`、`DEFERRED` 和最大步骤数成为正式合同；
6. 用 fresh-context A/B 验证速度、质量和安全，而不是凭感觉放宽规则。

最重要的交互变化可以概括为一句话：

> **一个问答不应该做成七个 Gate 的完整审议；应该是一次小型创作冲刺，加上一个可选的必要决策点。**

这样既能让 Skill 更易用、更通用，也能保留 FilmFoundry 当前最有价值的能力：创作者拥有方向权，事实可以追溯，高风险动作有人类确认，失败可以定位和恢复。

## 参考来源

以下均为截至 2026-09-21 可访问的官方仓库或官方文档。它们用于提取工作流模式，不代表 FilmFoundry 已经获得相同的性能结果。

- [OpenAI Codex skill-creator sample](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)
- [OpenAI Cookbook：Iterating development workflows with Codex](https://github.com/openai/openai-cookbook/blob/main/examples/codex/iterating-development-workflows-with-codex.md)
- [Anthropic Skills repository](https://github.com/anthropics/skills)
- [Anthropic Claude Code：skill-development](https://github.com/anthropics/claude-code/blob/main/plugins/plugin-dev/skills/skill-development/SKILL.md)
- [Anthropic xlsx Skill](https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md)
- [Anthropic doc-coauthoring Skill](https://github.com/anthropics/skills/blob/main/skills/doc-coauthoring/SKILL.md)
- [Hugging Face smolagents：Building good agents](https://github.com/huggingface/smolagents/blob/main/docs/source/en/tutorials/building_good_agents.md)
- [Hugging Face smolagents Agent reference](https://huggingface.co/docs/smolagents/reference/agents)
- [Hugging Face Agents Course：smolagents tutorial](https://huggingface.co/learn/agents-course/unit1/tutorial)
- [GitHub Agentic Workflows：About](https://github.github.com/gh-aw/about/)
- [GitHub Agentic Workflows：Deterministic agentic patterns](https://github.github.com/gh-aw/guides/deterministic-agentic-patterns/)
- [GitHub Agentic Workflows：IssueOps](https://github.github.com/gh-aw/patterns/issue-ops/)
- [LangGraph：Human-in-the-loop](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/human-in-the-loop.mdx)
- [LangGraph：Checkpointers](https://github.com/langchain-ai/docs/blob/main/src/oss/langgraph/checkpointers.mdx)

