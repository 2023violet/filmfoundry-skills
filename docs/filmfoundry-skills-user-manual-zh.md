# FilmFoundry Skills 全流程使用手册

> **当前状态：**本手册覆盖从空白创意到剧本修订、再到通用视觉生产准备与外部工具交接的完整使用路径。FilmFoundry v3.0.0 尚未获正式发布批准；Provider 相关旧表面仍待后续独立清理。构建、渲染或静态测试通过不等于创作 Gate、媒体质量或 Release 通过。

FilmFoundry 是一个通用、creator-first 的 Agent Skill。它帮助创作者形成故事、完成剧本、分析和修订文本，并把已经确认的创作决定整理成可交给外部视觉生产工具的资产、镜头和提示词准备材料。

FilmFoundry 不替创作者暗中决定故事，也不负责 Provider 调用、视频生成、下载和审美 QC。这些工作由外部工具和人员完成。

## 手册如何使用

这是一份操作手册，不是第二份规范。发生冲突时，按以下优先级执行：

1. 用户在当前任务中的明确决定；
2. 根 Skill：`skills/generative-film-production/SKILL.md`；
3. 工作模式：`skills/generative-film-production/references/40-work-modes.md`；
4. Creator-First 流程：`skills/generative-film-production/references/41-creator-first-script-workflow.md`；
5. 当前阶段对应的单篇 reference 与 template；
6. 本手册中的解释和示例。

不要一次加载整个 `references/` 目录。先判断当前阶段，再读取最少的必要文件。

---

## 1. 快速开始

### 1.1 安装或加载 Skill

把完整目录 `skills/generative-film-production/` 放入支持 Agent Skills 的工具所要求的位置，或让 Agent 直接读取该目录中的 `SKILL.md`。目录中的 references、templates、scripts 必须保持相对路径不变。

首次会话可使用：

```text
请使用 generative-film-production Skill。先判断当前工作模式和入口状态，只加载本阶段必需的 references。每轮最多问我一个会改变下游结果的实质问题；未经我确认，不要把创意草案写成正式事实，也不要进入 Provider 或视频生成。
```

从空白开始可直接说：

```text
我想写一个 8–12 分钟的短片，但现在没有故事。请从零带我完成。
```

已有材料可直接说：

```text
我有一份故事大纲。请先判断它处于 SEED、OUTLINE 还是 DRAFT，从最早未完成的 Gate 继续；不要让我重做已经成立的部分。
```

### 1.2 每次任务先声明四件事

最好提供：

- 当前材料：空白想法、片段、梗概、大纲、剧本或已确认场景；
- 目标：继续创作、确认决定、准备视觉生产，还是检查就绪状态；
- 约束：片长、格式、语言、受众、必须保留和禁止出现的内容；
- 写入权限：只在对话中讨论，还是允许创建/修改指定文件。

没有提供的事实保持为未知。Agent 可以提出假设供讨论，但不能把假设静默写成 Canon、Runtime 或 Registry 事实。

### 1.3 最短可用操作循环

```text
提出请求
  → Agent 判断 Work Mode 与入口状态
  → 展示已确认事实
  → 只暴露一个最高影响未知项
  → 只问一个问题并等待
  → 用户确认或纠正
  → 进入下一 Gate
  → 完成剧本与两轮修订
  → 用户明确接受后才进入视觉生产准备
```

---

## 2. 选择入口状态与工作模式

入口状态描述“现有故事材料到了哪里”；工作模式描述“这一轮允许做什么”。两者不能互相替代。

### 2.1 四种入口状态

| 入口 | 现场特征 | 起点 |
|---|---|---|
| `BLANK` | 只有创作愿望、时长或模糊感受，没有可用故事 | 从观众体验和核心处境开始 |
| `SEED` | 有一句想法、人物、画面、主题或 premise | 检查 `SEED_ACCEPTED`，再形成 logline |
| `OUTLINE` | 已有事件顺序、梗概或结构，但未形成完整剧本 | 找到最早缺失的角色、规则或因果 Gate |
| `DRAFT` | 已有完整或近完整剧本 | 先保留原意，检查缺失场景、因果、人物和连续性 |

判断原则：从最早未完成的 Gate 开始，不让已有可用剧本的创作者返回空白练习。

### 2.2 四种工作模式

完整规则见 `references/40-work-modes.md`。

| 模式 | 何时使用 | 允许 | 不允许 |
|---|---|---|---|
| Creative | 探索、写作、分析、修订、比较方向 | 生成 `CREATIVE_DRAFT`、提出假设、逐门创作 | Provider call、全量验证、写 Canon/Runtime |
| Commit | 用户明确选定或锁定创作方向 | 汇总选择、列出冲突、准备经授权的正式写入 | 静默写入、替用户裁决冲突、调用 Provider |
| Production | 已确认内容转资产、Shot Spec、连续性和外部提示词材料 | 运行相关结构检查，生成通用交接材料 | 把结构通过说成媒体质量通过 |
| Gate | 询问是否 ready、可生成、可交付或可发布 | 执行能力范围内的完整证据检查 | 把 `UNKNOWN`、render 或单次观察判为通过 |

Creative Mode 固定保持：

```text
validators = ()
run_full_validation = false
allow_provider_calls = false
allow_source_writes = false
```

只有用户明确授权写入后，才能对指定文件采取写操作；工作模式本身不是写入授权。

### 2.3 混合请求如何处理

如果请求同时说“帮我想故事并直接生成视频”，先处理最小创作部分，并指出进入 Production 或外部生成前必须满足的边界。不能因为时间紧、领导要求或 Provider 名称出现在请求中，就跳过创作确认。

---

## 3. 从零完成剧本

从零创作必须先加载 `references/41-creator-first-script-workflow.md`。短流程不强制创建文件；长流程、跨会话或用户要求保存进度时，才使用 `templates/script-development-workbook.md`。

### 3.1 七个确认 Gate

| Gate | 必须确认什么 | 典型输出 | 不能偷做什么 |
|---|---|---|---|
| `SEED_ACCEPTED` | 观众体验、格式/长度、核心处境 | seed 摘要 | 直接写完整故事或生产方案 |
| `LOGLINE_ACCEPTED` | 主角、目标、障碍、代价、独特钩子 | 一句因果 logline | 用主题口号代替事件因果 |
| `CHARACTER_ENGINE_ACCEPTED` | want、need、矛盾、受压反应、变化/不变 | 人物发动机 | 只列背景资料，不证明能推动场景 |
| `DRAMATIC_RULES_ACCEPTED` | 视角、世界限制、语气边界、结尾事实 | 戏剧规则清单 | 临近结尾再发明规则或反转 |
| `STRUCTURE_ACCEPTED` | 触发、升级决定、不可逆转折、高潮、回报 | 因果结构 | 用事件罗列代替主角选择 |
| `DRAFT_ACCEPTED` | 完整剧本、无缺失场景、无 placeholder beat | 完整草稿 | 用分场提纲冒充成稿 |
| `REVISION_ACCEPTED` | 意图/因果 pass 与人物/对白/连续性 pass | 修订稿、记录、decision diff | 声称已修改却保留同义残留 |

### 3.2 每一轮的固定形状

Agent 应当：

1. 重述已经接受的事实；
2. 指出当前 Gate；
3. 找出一个最可能推翻下游工作的未知项；
4. 只问一个实质问题；
5. 等待回答，不顺手跨越下一 Gate。

如果创作者卡住，可以提供两到三个真正不同的选择，并给出推荐。选择题仍然只能解决当前一个问题。

### 3.3 可选深度不是默认流程税

- 商业化、变现或系列化目标：按需加载 `references/20-content-market-gate.md` 与 `references/21-market-mvp.md`；
- 多个情绪节点、对白/音乐时间或明确节奏故障：按需加载 `references/39-script-facts-and-emotion.md`；
- 世界观扩写：只在角色选择或结构因果依赖它时进行；
- 情绪 Beat Map：有实际诊断价值时才创建，不作为每个故事的必填表。

### 3.4 从结构到完整剧本

短片在 `STRUCTURE_ACCEPTED` 后可一次写出完整剧本。长片或长剧按创作者接受的段落分批写，每一批携带简短的已确认决定摘要。

成稿至少应检查：

- 每个主要场景是否改变目标、关系、信息、风险或可选行动；
- 主角的升级是否由决定推动，而非连续偶然；
- 不可逆转折是否真的关闭旧选择；
- 高潮是否兑现人物与主题，而非用新信息逃避；
- 结尾是否满足已确认的 ending facts；
- 是否仍有“之后补”“待定”“此处发生冲突”等 placeholder。

### 3.5 两轮修订与 decision diff

第一轮检查意图与因果：

- 影片想让观众经历什么；
- 每个结果是否有可见原因；
- 人物选择是否被巧合、额外危机或信息隐藏替代；
- 结尾是否兑现而非减轻核心代价。

第二轮检查人物、对白与连续性：

- want/need/contradiction 是否在动作中出现；
- 对白是否重复画面已经表达的内容；
- 时间、地点、道具、知识状态和动作结果是否连续；
- 删除或改动的事实是否在后文意外复活。

标记 `REVISION_ACCEPTED` 前，逐项把“接受的修订决定”与最终稿对照。不能只搜索原句；还要检查同义、软化或改写后的残留。

---

## 4. 从现有材料继续

### 4.1 已有故事片段或 premise

先分类为 `SEED`，说明哪些事实是用户提供、哪些仍是开放项。不要自动补齐人物过去、世界历史或结局。

推荐请求：

```text
这是我的 premise。请保留原始意图，先判断离 LOGLINE_ACCEPTED 还缺哪个最关键事实；这一轮只问一个问题。
```

### 4.2 已有大纲

通常从 `CHARACTER_ENGINE_ACCEPTED`、`DRAMATIC_RULES_ACCEPTED` 或 `STRUCTURE_ACCEPTED` 中最早的缺口开始。读取 `references/02-story-breakdown.md`，但不要提前拆镜头。

优先检查：

- 事件是否由人物选择连接；
- 是否存在可删除而不影响任何状态的场景；
- 转折是否只靠新人物或新规则突然出现；
- 高潮是否由主角完成；
- 结尾是否回应开场承诺。

### 4.3 已有剧本

读取 `references/39-script-facts-and-emotion.md` 与 `references/02-story-breakdown.md`。先区分：

- 已确认事实；
- 角色主观理解；
- 审稿人的推断；
- 真正的因果或连续性故障；
- 单纯的审美偏好。

推荐请求：

```text
请分析这份完整剧本。先列出已确认的剧本事实，再指出一个最影响因果或人物选择的问题；不要直接重写全文，也不要把个人口味说成硬错误。
```

### 4.4 Revision 请求

修订前先明确“必须保留什么”和“希望改变什么”。任何会改变结局、人物核心动机、视角或世界规则的修改都需要用户确认，不能作为润色静默发生。

---

## 5. 保存进度与跨会话恢复

### 5.1 什么时候使用 Workbook

使用 `templates/script-development-workbook.md`，当且仅当：

- 创作跨越多个会话；
- 决策数量已难以可靠记忆；
- 用户明确要求保存进度；
- 多人需要接手同一剧本；
- 需要保留接受和拒绝的修订历史。

短创作不要为了“流程完整”强制生成 Workbook。

### 5.2 每次结束前记录什么

- Entry state；
- 当前 Gate；
- 已接受的事实和 creator decision；
- 被拒绝的方案；
- 唯一 open question；
- 剧本或草稿位置；
- 已完成与未完成的修订 pass。

### 5.3 新会话如何恢复

```text
请读取这份 Script Development Workbook。先复述所有已接受 Gate 和唯一 open question，不要重新提问已经确认的决定；发现矛盾时只报告，不要静默选择一边。
```

如果 Workbook 与用户本轮明确决定冲突，以用户本轮决定为准，并记录变更原因。不要为了恢复方便新增 Python 状态机；只有反复出现状态丢失、恢复歧义或跨会话失败时，才单独设计机器状态契约。

---

## 6. 确认创作决定

Creative Mode 的输出默认是 `CREATIVE_DRAFT`。完成七个 Gate 不自动修改项目文件，也不等于进入 Production。

### 6.1 进入 Commit Mode

用户需要明确表达类似：

```text
我确认这个 logline、人物发动机、戏剧规则、结构和修订稿。请进入 Commit Mode，先给出将写入的内容和目标文件，不要调用 Provider。
```

Commit Mode 应返回：

- `COMMIT_SUMMARY`：准备确认的决定；
- `CANON_CONFLICT`：与已有权威来源直接冲突的内容；
- `DEFERRED_CHECK`：属于 Production/Gate 的后续检查；
- 目标文件与预期变更；
- 是否仍需要单独的写入授权。

### 6.2 写入权限

“我选 A”只确认创作方向，不等于授权修改磁盘文件。“把确认稿写入指定文件”才是写入授权。不得修改未被用户指定的下游 Canon、Runtime、Registry、资产或归档。

---

## 7. 剧本确认后的视觉生产准备

只有剧本、选定场景或稳定段落被接受，或用户明确要求处理已有稳定材料时，才进入本阶段。

### 7.1 推荐顺序

```text
已确认剧本
  → Creative Brief
  → Story Development and Breakdown
  → 资产与 reference roles
  → Sequence / Shot Engineering
  → 连续性与状态
  → 可选 Visual Control
  → Canonical Shot Spec
  → 通用 Prompt/外部交接包
```

### 7.2 Creative Brief

读取 `references/01-creative-brief.md`，使用 `templates/creative-brief.md`。记录观众体验、格式与长度、premise、accepted logline、人物变化、戏剧规则、结尾承诺和硬约束。

Delivery specifications 只有在确实约束写作或视觉准备时才填写。商业项目才需要 Market Gate；艺术短片或客户已锁定项目可明确标记适用边界，而不是编造市场证据。

### 7.3 Story Development and Breakdown

读取 `references/02-story-breakdown.md`。这里负责因果结构、场景职责和剧本修订，不负责镜头细节。

每个场景至少说明：

- 叙事目标；
- 谁做了什么决定；
- 哪个状态发生变化；
- 为什么下一场因此发生；
- 与高潮或 payoff 的关系。

### 7.4 资产与引用权威

 recurring 人物、产品、地点或重要道具使用 `references/04-asset-passport.md` 和 `templates/asset-passport.md`。引用图先按 `references/03-reference-board.md` 声明角色：

- `controls`：它真正控制什么；
- `does_not_control`：它不能证明什么；
- 版本、来源和哈希；
- 可见状态是否与目标场景一致。

不要因为有一张漂亮参考图，就假设它同时控制身份、服装、空间、动作、镜头和最终画质。

### 7.5 Shot Engineering

读取 `references/06-shot-engineering.md` 与按需的 `references/19-adaptive-spec.md`。一个生成单元保持一个 dominant action 和一个 observable end state。

Canonical Shot Spec 的核心包括：

- narrative goal；
- generation unit；
- generation duration 与 edit target duration；
- 人物、地点、道具和初始状态；
- dominant action 与事件顺序；
- observable end state；
- shot size、composition、camera move；
- reference bindings；
- failure risks 与 quality bar。

对话、反打、重要道具、连续动作、精确时间或关键视线只在适用时增加条件字段，不让所有镜头背负同一套字段税。

### 7.6 连续性

读取 `references/07-continuity-engine.md`。先写计划状态，外部生成并选定素材后再记录 observed state；下一镜头以 Select 的真实出点状态为依据，而不是以原计划或整段生成的最后一帧为依据。

重点检查：

- 人物身份、服装和可见伤痕；
- 道具持有者、位置与状态；
- 时间、天气、光线；
- 轴线、screen side 与 reciprocal eyeline；
- 动作接续和 selected out-point。

### 7.7 可选 Visual Control

只有 Shot Spec 留下昂贵的可见歧义时，才读取 `references/36-visual-control-decision-tree.md` 选择最小控制物：角色、地点、空间、比例、物理提示、预演、关键帧或首尾帧。

Visual Control Plan 是交接约束，不是 Provider 能力证明。静态图通过也不能证明运动、节奏、接缝、对白同步或最终审美通过。

### 7.8 Prompt 准备

读取 `references/08-video-spec.md`、`references/09-prompt-compiler.md` 和必要的通用 adapter。Prompt 是已确认 Spec 的编译输出，不是重新发明故事的地方。

Prompt 至少保持：

- 单一主要动作；
- 清晰初始状态和结束状态；
- 必要的主体、环境、镜头与运动；
- 可追踪的 reference role；
- 与已确认 Shot Spec 一致；
- 不声称未经证据验证的模型能力。

---

## 8. 外部工具交接

FilmFoundry 的主动责任到“通用、可审查、可追踪的视觉生产准备包”为止。

### 8.1 可交付给外部工具的内容

- 已确认剧本与 revision record；
- Creative Brief；
- Sequence Plan；
- Asset Passport 与 Registry；
- reference roles 与 Visual Control Plan；
- Canonical Shot Spec / Shot Card；
- Continuity Ledger；
- 编译后的通用 Prompt 或 Provider-neutral payload；
- 明确的未知项、风险和人工检查清单。

### 8.2 外部环节负责什么

Provider 调用、视频生成、下载和审美 QC 由外部工具与人员负责，还包括：

- 登录、凭证和 API/Web 操作；
- 提交任务、排队、重试和成本控制；
- 下载、转码和媒体文件管理；
- 实际播放、节奏、身份稳定、动作可信度和视听审美判断；
- NLE 剪辑、混音、字幕、编码、上传与发布。

FilmFoundry 可以定义需要回填的证据字段，但不能把外部执行结果伪装成本地已完成事实。

### 8.3 回填外部结果

当外部工具返回生成结果后，只记录可验证事实：任务 ID、工具/版本、输入版本、时间、输出文件、人工观察、Select 区间和失败类型。

一次成功只能是 `OBSERVED_ONCE`。只有作用域一致且证据足够时，才能提高证据等级；不能把单个镜头推广为 Provider 的永久能力。

---

## 9. 验证与证据边界

### 9.1 结构验证

在仓库根目录运行：

```powershell
python -m pytest -q
python scripts/validate_evals.py evals/evals.json
git diff --check
```

按产物运行相应 validator，例如：

```powershell
python skills/generative-film-production/scripts/validate_content_market_gate.py <market-gate.json>
python skills/generative-film-production/scripts/validate_asset_registry.py <asset-registry.csv>
python skills/generative-film-production/scripts/validate_shot_spec.py <shot-spec.json>
python skills/generative-film-production/scripts/validate_axis_registry.py <axis-registry.json>
python skills/generative-film-production/scripts/validate_voice_registry.py <voice-registry.json>
python skills/generative-film-production/scripts/validate_model_profile.py <model-profile.json>
python skills/generative-film-production/scripts/validate_production_state.py <production-state.json>
```

validator 通过只说明字段、状态和引用关系满足确定性契约，不证明创意质量、可拍性、Provider 服从、媒体质量或发布就绪。

### 9.2 路由检查

```powershell
python -m filmfoundry route --request "我想从零写一个十分钟短片" --format json
```

预期是 Creative Mode、creator workflow 优先、零 validator、零 Provider call、零 source write。

### 9.3 构建与 clean extraction

```powershell
$env:SOURCE_DATE_EPOCH = "0"
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir .dist
python scripts/build_release_artifacts.py --out .dist
Remove-Item Env:SOURCE_DATE_EPOCH -ErrorAction SilentlyContinue
python scripts/check_clean_extraction.py --wheel .dist/filmfoundry_skills-3.0.0-py3-none-any.whl --archive .dist/filmfoundry-skills-v3.0.0.zip
```

这些命令验证制品边界和可复现结构，不批准 Gate、Tag、GitHub Release 或正式发布。

### 9.4 `UNKNOWN` 与 `INVALID`

- `UNKNOWN`：缺少证据，不能判成功，也不一定说明内容错误；
- `INVALID`：已违反明确契约，必须修复后再继续；
- render 成功：只说明只读展示产物生成成功；
- authored fixture：只用于守护行为或 scorer，不是真实 fresh-context 创作速度；
- reference-loading benchmark：只测本地文件数量、字节与加载耗时，不是 LLM 创作耗时。

---

## 10. 可直接执行的 Runbook

### Runbook A：从空白完成短片剧本

1. 发出固定开场请求；
2. 确认 `BLANK` 与 Creative Mode；
3. 每轮只回答当前一个问题；
4. 逐个确认七个 Gate；
5. 在 `STRUCTURE_ACCEPTED` 后要求完整剧本；
6. 确认 `DRAFT_ACCEPTED`；
7. 分别完成两轮修订；
8. 检查 decision diff 后确认 `REVISION_ACCEPTED`；
9. 需要保存时才写 Workbook 或剧本文件；
10. 不自动进入 Production。

开场提示词：

```text
我想写一部 8–12 分钟的中文短片，现在没有故事。请按 Creator-First 流程从 BLANK 开始，每轮只问一个会改变下游结果的问题。所有选择由我确认；完成结构后写完整剧本，再做意图/因果和人物/对白/连续性两轮修订。剧本接受前不要加载生产、Runtime、Provider 或视频 QC。
```

### Runbook B：修订已有初稿

1. 提供完整初稿和必须保留项；
2. 判断 `DRAFT`，加载 workflow、Story Breakdown 与 Script Facts；
3. 先列剧本事实，不立即重写；
4. 找出一个最高影响问题；
5. 用户确认修订目标；
6. 完成因果 pass；
7. 完成人物/对白/连续性 pass；
8. 输出最终稿、修订记录和 decision diff。

提示词：

```text
这是我的完整初稿。必须保留：[列出内容]。请从 DRAFT 入口继续，先总结已确认事实和最关键的一个问题，不要一次给我整份重写。所有改变结局、人物动机、视角或世界规则的修订先征求确认。
```

### Runbook C：商业内容或系列化概念

1. 先说明商业、变现或系列化目标；
2. 在 Creator workflow 前加载 Market Gate；
3. 明确受众、点击理由、三秒 hook、payoff、follow reason、系列引擎和最小 MVP；
4. 市场假设保持假设；
5. 没有真实 MVP 证据时不得声称 `PRODUCTION_APPROVED`；
6. Market Gate 只决定是否值得扩大投入，不替代故事创作。

提示词：

```text
我要开发一个可连续更新的短片系列。请先执行 Content Market Gate，再进入 Creator-First 剧本流程。市场结论必须区分假设与真实证据，不要因为题材完整就判定有市场。
```

### Runbook D：稳定剧本转视觉生产准备

1. 明确哪一版剧本或场景已接受；
2. 创建/核对 Creative Brief；
3. 完成场景职责与 Sequence Plan；
4. 识别 recurring assets；
5. 给引用材料声明 controls/does_not_control；
6. 拆 Narrative Shot、Generation Unit 和 Edit Unit；
7. 写 Adaptive Canonical Shot Spec；
8. 按风险增加连续性、空间、比例、物理、关键帧或声音控制；
9. 编译通用 Prompt 和外部交接清单；
10. 验证结构后交给外部工具，不在 FilmFoundry 内宣称生成完成。

提示词：

```text
这版剧本已经确认。请进入 Production Mode，把第 3 场整理为通用视觉生产准备包：先做场景职责、资产与 reference role，再拆 Shot Spec、连续性和必要的 Visual Control，最后输出供外部工具使用的 Prompt。不要调用 Provider，不要生成或下载媒体。
```

---

## 11. 常见错误与处理

| 错误 | 为什么不行 | 正确处理 |
|---|---|---|
| 空白请求直接给完整故事 | 静默替创作者越过所有 Gate | 从 `BLANK` 的一个高影响问题开始 |
| 一次列十几个问题 | 让关键选择互相污染，创作者负担过高 | 每轮最多一个实质问题 |
| 已有剧本仍从 seed 重做 | 丢弃现有成果 | 找最早未完成 Gate |
| 商业分析成为所有项目必选 | 把条件深度变成流程税 | 只有商业/系列化目标才加载 |
| 情绪图成为默认产物 | 静态格式不能替代故事需要 | 只有节奏/对白/音乐问题需要时创建 |
| Creative Mode 初始化 Runtime | 空白创作不需要生产状态 | 保持零验证、零写入 |
| “我选 A”被当作写文件授权 | 创作确认不等于磁盘写入 | 单独确认目标文件和写入动作 |
| Scene Breakdown 直接拆镜头 | 因果尚未稳定就固化制作 | 先场景职责，再 Shot Engineering |
| Prompt 中重新发明故事 | Prompt 无法成为可靠编译产物 | 回到被接受的 Brief/Spec |
| 引用图控制一切 | 一张图通常只有部分权威 | 写 controls/does_not_control |
| 单次生成成功成为模型规则 | 一次观察不可泛化 | 记录 `OBSERVED_ONCE` 与完整作用域 |
| render 成功被写成 Gate 通过 | render 不验证内容与外部行为 | 单独执行 Gate 证据审查 |
| 测试失败就放宽断言 | 掩盖真实契约回归 | 查根因并只修被证实的问题 |
| 修订记录说已删除但正文仍有同义残留 | 形式完成，实际未执行决定 | 在 `REVISION_ACCEPTED` 前做 decision diff |

遇到冲突时：展示冲突的两个来源、说明各自权威范围、只问用户一个裁决问题。不要偷偷合并成第三种说法。

---

## 12. 阶段完成检查表

### 剧本创作完成

- [ ] 入口状态已正确识别；
- [ ] 每轮最多一个实质问题；
- [ ] 七个 Gate 均由创作者确认或明确拒绝；
- [ ] 完整剧本无缺失场景和 placeholder beat；
- [ ] 已完成意图/因果修订；
- [ ] 已完成人物/对白/连续性修订；
- [ ] 最终稿通过 decision diff；
- [ ] 未静默覆盖创作者选择；
- [ ] 未提前加载生产或 Provider machinery。

### 视觉生产准备完成

- [ ] 使用的是明确接受的剧本/场景版本；
- [ ] Creative Brief 与场景职责一致；
- [ ] recurring assets 有明确权威；
- [ ] references 声明 controls/does_not_control；
- [ ] 每个 Generation Unit 只有一个 dominant action；
- [ ] 初始状态和 observable end state 明确；
- [ ] 条件字段只在适用时启用；
- [ ] 连续性以上一个 Select 的 observed state 为依据；
- [ ] Prompt 可追溯到 Shot Spec；
- [ ] 外部未知项和人工检查清单已列出。

### 外部交接完成

- [ ] Provider/API 凭证未写入 Skill 产物；
- [ ] 未把外部生成、下载或播放审查伪装成已完成；
- [ ] 每个输出能追溯到输入版本与创作决定；
- [ ] `UNKNOWN` 没有被当成通过；
- [ ] `OBSERVED_ONCE` 没有被泛化；
- [ ] 发布、Tag、Release 仍由独立授权和证据 Gate 决定。

完成当前阶段后停止。只有用户明确提出下一阶段，才继续加载新的 references 或执行新的工作模式。
