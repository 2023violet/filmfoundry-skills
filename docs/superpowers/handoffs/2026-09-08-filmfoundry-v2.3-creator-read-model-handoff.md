# FilmFoundry v2.3.0 Creator Read Model 接手文档

> **历史文档：**本文只保留 v2.3 阶段证据，已被仓库根目录 `CURRENT_HANDOFF.md` 取代。不要据此继续旧 RC 路线或把雾城项目作为 Core 设计对象。

> 本文用于下一次对话接手当前实现。它记录事实、已完成工作、未完成工作和可复现命令，不把计划目标误写成已交付功能。

## 当前结论

这项工作没有“卡死”，但也没有完成整个 v2.3.0 计划。当前已经完成了 v2.3 数据基础的前四个阶段：基线与规格、来源目录、类型化 Creator Snapshot、导航与术语。下一阶段是 P0.5 视觉原型门禁；正式 HTML/Markdown/SVG Renderer、`ff render`、雾城适配器、打包和最终验收尚未完成。

当前分支为 `codex/filmfoundry-v2.3-creator-read-model`，基于 v2.2.0 提交 `941fcda99506427a521d1ff20252bf7544114ea3`。最新代码提交为 `89a42e9`（Creator Navigation 合约修复）。在写入本文前，工作树只有 SDD 执行报告更新；本文本身是新增的接手文档。此前未改动产品源文件、媒体或归档内容。

## 十几个小时主要做了什么

### 1. 先建立可恢复的执行边界

- 读取并执行 `superpowers:subagent-driven-development`、TDD、代码复核和完成前验证规则。
- 建立执行账本：`.superpowers/sdd/2026-09-08-filmfoundry-v2.3-creator-read-model/progress.md`
- 固定基线、分任务提交、每个任务独立测试和独立复核，避免在长任务中丢失上下文。
- 扫描任务之间共享的接口和文件，明确了历史来源不得覆盖当前来源、Task 5 必须先于正式 Renderer 等裁决。

### 2. 完成 Source Catalog

新增来源目录、路径基准和 Parser Registry 相关实现，解决了：

- `WORKSPACE_ROOT` 与 `RUNTIME_DIR` 两种路径解析；
- 工作区越界；
- `99_归档` 作为活跃来源；
- 同一 `source_kind + scope` 的多个 `CURRENT`；
- 缺失来源、未知 Schema 和不支持的解析器；
- Windows/POSIX/中文路径测试。

这一步的难点不是读取 JSON，而是要明确“谁是当前权威、谁只是历史对照”，并且不能让 Core 根据雾城项目名写特殊分支。

### 3. 完成 Typed Creator Snapshot

新增不可变的类型化读模型实体和确定性序列化，包含：

- `CreatorSourceRef`、`CreatorProvenance`、`CreatorMetric`；
- Overview、Narrative、Emotion、Asset、Shot、Continuity、Blocker、Conflict、Coverage；
- `declared_state` 与文件系统观察到的 `observed_readiness` 分离；
- `KNOWN`、`UNKNOWN`、`INVALID` 的覆盖状态；
- 当前来源与历史生产映射并存时的 `AUTHORITY_MISMATCH`；
- 聚合统计只纳入已成功解析且属于选定权威集合的来源。

冻结的雾城夹具已经证明边界事实：75 条资产、19 条历史生产单元、21 个缺失角色媒体、0 条 Generation、0 条 Select。这里的 21 个缺失是读模型对登记状态与物理文件的差异呈现，不是恢复图片。

### 4. 完成 Navigation 与 Terminology

新增：

- 中文优先、英文回退、未知值保留原值的版本化术语注册表；
- `CreatorNavigation` 与 `CreatorReadModel`；
- 从 Snapshot 单向推导行动的规则；
- 行动按 `priority → severity → entity_id → action_id` 稳定排序；
- 首要行动与同优先级可并行行动；
- 来源不可读、权威冲突、硬阻塞、条件制品缺失、Observed State、生命周期和建议行动；
- 每个行动的 `rule_id`、前置条件、支持边界和非空来源 Provenance；
- `creator-navigation.v1.json` 与 `creator-read-model.v1.json`。

独立复核发现了六组问题，已在最新修复提交中处理：硬严重度优先级、连续性边的生命周期门禁、空 Provenance、防止术语映射被修改、导航/读模型 Schema、支持边界术语覆盖。Task 4 的独立修复复审仍需在下一步确认并写入账本，不能只凭实现者报告宣布验收。

## 当前验证证据

本次接手前重新执行了以下命令：

```text
python -m pytest -q
295 passed in 16.54s

python -m compileall -q filmfoundry_v2
exit 0

git diff --check
通过（仅提示 SDD 报告的换行风格）

git diff -- 99_归档
空
```

历史任务证据中还包括：Task 2 原有 234 条测试保持通过；Task 3 聚焦夹具与契约 47 条通过；Task 4 修复后的聚焦测试 61 条通过。最新全套测试以本文件上方的 295 条为准。

## 为什么会耗时这么久

难点主要在架构语义和证据要求，不在代码量本身：

1. **权威冲突不能靠猜。** 当前故事、历史生产状态、Registry 声明和物理文件可能互相矛盾，读模型必须并列呈现并保留来源。
2. **要保持旧版本不变。** v1.3.3 和 v2.2 的接口、Schema、测试和 Wucheng 资产边界都要保留，新增能力只能通过独立派生层接入。
3. **每个任务都有 TDD 和复核循环。** Task 2 和 Task 3 的复核分别发现了多个重要问题，修复后还要重新跑聚焦测试、全套测试、编译和归档边界检查。
4. **当前代码要跨项目。** Core 不能写死雾城目录或项目 ID；雾城知识必须延迟到 Adapter。
5. **计划要求可追溯和确定性。** 行动、指标、冲突、覆盖率都要能回到路径和 JSON Pointer，默认输出还必须可重复。

因此，这个计划属于“中高难度的架构扩展”，不是无法完成的重写。已经完成的四个任务证明基础抽象是可行的；剩余工作中，真正耗时的部分会是视觉原型可用性、Renderer 安全与确定性、CLI 退出码、雾城真实只读接入和最终跨层验收。

## 已完成提交

从基线到当前的主要提交如下：

```text
becc43c  v2.3 基线、规格和证据
2eceaf3  基线文档修复
720d540  v2.3 夹具和 RED 合约
038ef84  RED 合约加固
56789f3  Creator Source Catalog
b3dfcd6  Source Catalog 首轮修复
3bfc32a  Source Catalog 复核修复
2c91082  Typed Creator Snapshot
b6d58d3  Snapshot 报告和补充
bf78a9d  Snapshot 语义修复
071ae3f  历史生产覆盖修复
275195f  Creator Navigation 与 Terminology
89a42e9  Navigation 合约复核修复
```

不要重做这些任务，也不要把 `HEAD~1` 当成 Task 4 的完整 diff；需要复核时使用账本记录的 Task BASE 和 review package。

## 尚未完成的任务

### Task 4 收尾

- 确认独立复审报告已生成并为 PASS；
- 将 Task 4 complete、复审结果和最新测试数字写入 `progress.md`；
- 处理 SDD 报告的工作树变更，保持代码提交边界清楚。

### Task 5：P0.5 视觉原型门禁（下一步）

必须使用真实、已验证的雾城 `CreatorReadModel`，禁止手工伪造页面数据。先做三个原型：Overview、Emotional Map、Shot Board，生成桌面和移动截图并检查：

- 30 秒内找到项目阶段、当前权威、最大阻塞；
- 10 秒内判断离散情绪趋势；
- 一眼看到 21 个缺失角色媒体；
- 分清故事 v3 与 19 个历史生产单元；
- 找到首要行动和并行行动；
- 无文字重叠、溢出、空白 SVG 或不可读内容。

如果原型不通过，只修改 Presenter/视觉层，不改 Snapshot、Runtime、Registry、Canon 或媒体。

### Task 6–11

- Task 6：共享 Presenter、六个正式视图、HTML/Markdown/SVG、安全媒体链接；
- Task 7：`ff render`、稳定退出码、确定性输出和 `render-manifest.json`；
- Task 8：雾城只读 Adapter，输出到 `09_新生成产出/creator-dashboard/`；
- Task 9：通用 Smoke Project 验证无雾城分支；
- Task 10：Skill、文档、README、CHANGELOG、v2.3.0 包和 ZIP；
- Task 11：全量验收，只有通过后才可更新 Runtime 工具指针，并且只允许创建本地 `v2.3.0-rc1`，不能推送、合并或创建最终 `v2.3.0` 标签。

## 下一轮启动命令

在新对话开始时，先进入仓库并执行：

```powershell
Set-Location 'D:\study\Software\filmfoundry-skills-v2-release'
git status --short --branch
git log --oneline -5
Get-Content -Raw '.superpowers\sdd\2026-09-08-filmfoundry-v2.3-creator-read-model\progress.md'
Get-Content -Raw 'docs\superpowers\plans\2026-09-08-filmfoundry-v2.3-creator-read-model.md'
```

然后：

1. 读取本接手文档和 Task 4 复审报告；
2. 若 Task 4 复审 PASS，按计划生成 Task 5 brief；
3. 用真实 Wucheng Source Catalog 构建 Read Model；
4. 先做原型和截图，过门禁后才进入正式 Renderer；
5. 每个任务继续执行“实现 → 聚焦测试 → 全量回归 → 独立复核 → 提交”。

## 不可违反的边界

- 不恢复已删除的角色图片；
- 不调用付费 Higgsfield 或 H3 生成；
- 不修改 Wucheng Canon、Registry、状态、媒体哈希、Generation、Select 或 `99_归档`；
- 不把历史生产映射显示成当前故事事实；
- 不把 `UNKNOWN` 当成零或成功；
- 不在 Core 或 Renderer 中写 Wucheng 项目特例；
- 不宣称 `CREATOR_REVIEWED` 或 `CREATOR_VALIDATED`，除非完成计划规定的人工证据。

## 对“这个计划困难吗”的直接回答

困难，但属于可控的工程难度。已有部分不是概念草图，而是通过测试、类型、Schema、来源和提交边界固定下来的基础层。后续最容易返工的不是 Python 语法，而是把当前故事、历史状态和文件实况错误合并，或先做漂亮页面再发现页面依据的数据不可信。只要坚持“先来源目录和 Snapshot，再 Presenter，再渲染器；先原型门禁，再正式 UI”的顺序，剩余工作可以分阶段完成，不需要推翻当前实现。
