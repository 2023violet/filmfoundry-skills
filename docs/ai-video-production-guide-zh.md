# FilmFoundry AI 视频全流程操作指南

本指南面向第一次做 AI 视频、又希望以后能重复生产的团队。它说明每一步该读什么、写什么、校验什么，以及哪些事情必须交给外部工具或人工完成。FilmFoundry 是生产契约和证据层，不是图片/视频/声音生成器。

## 如何使用这套 Skill

把 `skills/generative-film-production/` 安装到你所使用的 Agent Skills 目录后，在每个工作会话的第一条任务中明确说明：

```text
使用 generative-film-production。当前阶段是“建立角色资产”/“拆镜头”/“编译 H3 Prompt”等，请按 Skill 路由只读取本阶段需要的 references，并把输出写入指定项目目录。
```

不要把整套 references 一次性粘进对话。让 Agent 先读取项目入口和 Runtime，再按阶段加载一到三篇 reference；这样可以减少旧状态、模型经验和当前镜头事实混在一起。每次让 Agent 修改文件时，要求它返回：改动文件、校验命令、校验结果、仍未验证的假设。

Skill 的职责边界可以这样理解：

| 你要解决的问题 | Skill/工具负责 | 仍需你或外部工具完成 |
|---|---|---|
| 故事、镜头和资产是否说清楚 | 模板、字段、引用和状态校验 | 创作取舍、Canon 裁决 |
| Prompt 是否结构完整 | metadata、章节、reference role、lint、编译 | 模型是否真的遵守 |
| 图片/视频/声音是否生成 | Provider payload、能力证据记录、项目适配器 | 登录、API/网页操作、下载和媒体处理 |
| 画面是否好看、身份是否稳定 | QC 表和可回填证据 | 人工播放、比较、审美判断 |
| 是否能交付发布 | 时间线、音频、字幕、编码检查入口 | NLE、编码器、平台上传和发布数据 |

## 先理解四个原则

1. **先确定要拍什么，再写 Prompt。** Prompt 只是已决定内容的编译结果。
2. **每个事实只保留一个权威来源。** Canon 管故事，Registry 管资产，Shot Spec 管镜头，Prompt Markdown 管创作载荷，Runtime 管状态，媒体文件只承担实体内容。
3. **控制项按风险启用。** 不是每个角色都要三视图五表情，不是每个镜头都要空间地图或预演。
4. **证据等级和愿望分开。** `UNVERIFIED` 可以指导实验，不能解锁默认路线；`OBSERVED_ONCE` 只能说明一次观察。

## 0. 建立工作区

从项目根 `README.md` 和 `00_入口与规则` 开始。确认 Runtime 中的资产、生产状态、依赖、模型证据、画幅、时间线和后期状态。新图片、视频、Prompt 和测试记录先进入 `09_新生成产出/`，通过审查后再提升到生产目录。

FilmFoundry 独立工作区可以先执行：

```text
python -m filmfoundry init --root <workspace>
python -m filmfoundry validate --root <workspace> --format json
python -m filmfoundry index --root <workspace>
```

项目适配器使用（由项目自己提供，不属于 FilmFoundry Core）：

```text
python <project-adapter>/scripts/validate_workspace.py --root <project>
python <project-adapter>/scripts/audit_media.py --root <project>
python <project-adapter>/scripts/build_indexes.py --root <project>
```

先检查是否触碰 `99_归档`；它只读，不能移动、改名或重写。

### 推荐的单镜头文件流

以一个需要人物和场景连续性的镜头为例，文件关系应是：

```text
Asset Passport / Registry
        ↓ asset_id + sha256
Visual Control Plan ──→ Shot Spec
        ↓                  ↓
Prompt Markdown ───────→ Provider payload
                              ↓ 外部生成
Generation record → Select + QC → Observed State → Edit Timeline
```

一个可执行的目录可以是：

```text
03_分集生产/EP01_某集/03_镜头工程/EP01_SH001.json
03_分集生产/EP01_某集/04_视觉控制/EP01_SH001_VC.json
03_分集生产/EP01_某集/05_Prompt/EP01_SH001_P01.md
05_生成与模型验证/生成日志/EP01_SH001_G01.json
05_生成与模型验证/Select_QC/EP01_SH001_SELECT_01.json
06_后期与交付/时间线/EP01_EDIT001.json
```

文件名可以使用中文显示名，但 JSON/CSV 中的 `asset_id`、`shot_id`、`generation_unit_id` 和 `prompt_id` 必须稳定、唯一、ASCII。文件改名不应产生新的机器身份。

## 1. 立项与市场判断

如果项目要做连载、涨粉或商业化，先读 `references/20-content-market-gate.md` 和 `21-market-mvp.md`。写清楚目标观众、点击理由、前三秒钩子、兑现、追更理由、三十集引擎、变现假设和最便宜的可发布 MVP。没有这些答案时，状态应保持 `MVP_ONLY`、`TRAFFIC_EXPERIMENT` 或 `NO_GO`，不要直接批量做资产。

如果是客户锁定、纯艺术、作品集或模型测试，使用显式 `BYPASS`，写明原因。

输出：Creative Brief、市场门记录、MVP 评价标准。

## 2. Canon 与剧本

读取 `references/01-creative-brief.md`、`02-story-breakdown.md` 和项目 Canon。先锁定人物目标、冲突、信息揭示、场景变化和结尾状态，再拆成 Narrative Beat。不要在这一步写模型品牌、镜头参数或“电影感”形容词。

输出：Series/ Episode Bible、锁稿剧本、Beat 表、Canon 冲突清单。

门禁：Canon 冲突没有裁决前，不建立新的权威资产。

## 3. 资产 Passport 与参考图

读取 `04-asset-passport.md`、`05-asset-stress-test.md`、`25-character-reference-system.md`、`26-location-reference-system.md`。给每个会跨镜头复现的人物、场景、道具分配稳定 ASCII `asset_id`，中文放 `display_name` 和文件名。

### 角色最小路径

1. 只为当前镜头需要的角色建立面部近景和身体参考。
2. 需要大景或背面时再加正面/背面全身。
3. 去头全身、灰色无杂物背景、湿身/受伤/换装等作为可选实验变量。
4. 局部修复记录 `mask_regions`、源图哈希、修复图哈希和人工 QC，不要整张重生覆盖原 Canon。
5. 注册 Registry，记录尺寸、比例、模式、透明通道、状态和 `controls/does_not_control`。

### 声音 Passport

需要跨镜头保持声音时，建立 `voice_id`、描述、样本、口音、音高、语速、情绪行为、测试台词、版本和漂移观察。读取 `18-voice-passport.md`。真正的声音文件由外部工具生成，时长和停顿确认后才能成为 timing authority。

### 场景 Passport

优先锁定门、柱子、灯、台阶等可识别锚点，并登记相机侧和光源方向。3/4 视角是可选实验，不是硬规则。场景参考不自动控制人物身份、表演或镜头运动。

输出：Asset Passport、Registry、角色/声音/场景参考图、资产压力测试记录。

## 4. 拆镜头：Narrative Shot → Generation Unit → Edit Unit

读取 `06-shot-engineering.md` 和 `19-adaptive-spec.md`。每个镜头写：

- `shot_id`、`generation_unit_id`、`edit_unit_ids`；
- 生成源时长和剪辑目标时长；
- 叙事目标、一个主动作、地点、起始状态、可观察结束状态；
- 景别、构图、相机位置/高度/路径/速度/停止；
- 转场、引用绑定、失败风险和质量标准。

只有镜头确实需要时才填写对白、反打轴线、eyeline、道具持续性、连续动作 handoff、逐秒硬时钟。生成 10 秒不代表成片必须使用 10 秒；先看是否有可用的连续 `PARTIAL_SELECT`。

运行：

```text
python -m filmfoundry validate --root <workspace> --stage shot --format json
```

## 5. 选择视觉控制计划

读取 `references/36-visual-control-decision-tree.md`。先问“哪个可见事实最怕出错”：

| 风险 | 采用 |
|---|---|
| 角色身份/服装 | Character Reference |
| 场景几何/同地点变化 | Location Reference + Spatial Map |
| 巨人与人物比例 | Scale Reference，写可见参照关系 |
| 液体、重物、布料响应 | Physics Cue，写力/重量/惯性/重力/结果 |
| 多人站位或复杂空间 | Previsualization |
| 视野和景别理解不稳定 | Lens Result，同时写 FOV 和画面结果 |
| 无明显连续性风险 | 不建立额外控制 |

每项参考都写 `controls` 和 `does_not_control`。计划本身仍是意图，不能绕过 Shot state alignment、Provider Evidence 或 Runtime 状态机。

## 6. 编写 Prompt Markdown

读取 `08-video-spec.md`、`09-prompt-compiler.md`、`23-controllability-budget.md` 和对应 Provider adapter。Prompt 顶部写 JSON metadata fence，正文按固定章节写：`visual_fact`、`output_profile`、`start_state`、`end_state`、`subjects`、`dominant_action`、`camera`、`continuity_locks`、`references`、`forbidden`、`acceptance`。

每个 reference 必须有 `slot`、`asset_id`、`role`、`controls`、`does_not_control`。写结果和可观察动作，少写泛化的“真实、电影感、8K 全部都要”。镜头只保留一个主运动；物理动作说明材料怎样受力并产生什么可见结果。

校验并编译：

```text
python -m filmfoundry validate --root <workspace> --stage prompt --format json
python -m filmfoundry compile --prompt <prompt.md> --provider minimax-h3 --out <payload.txt>
python -m filmfoundry compile --prompt <prompt.md> --visual-control <plan.json> --provider minimax-h3 --out <payload.txt> --format json
```

编译器只读取 Prompt 和视觉控制计划，输出 payload、引用槽和输入哈希，不回写 Canon、Prompt 或 Registry。

## 7. 选 Provider 与做小样

先读取 `16-model-evidence.md`、`29-capability-scoped-model-gates.md` 和对应 adapter。检查准确的 Provider surface、版本、参考数量、First/Last、音频、时长、画幅、语言、身份和手/道具行为证据。未知能力保持未知。

对某个项目的 H3 当前切片：

```text
python <project-adapter>/scripts/build_visual_control_plan.py --root <project> --out <plan.json>
python <project-adapter>/scripts/prepare_h3_vertical_slice.py --root <project> --visual-control <plan.json> --out <handoff.json>
```

当前参数固定为 5 秒、768P、adaptive、`NONE`。这一步只生成执行卡，不调用付费 Provider。

## 8. 外部生成与记录

外部工具执行后必须保存 generation ID、Provider/版本、Prompt 哈希、输入资产 ID、参数、输出媒体哈希和观察状态。新媒体先放 `09_新生成产出/review`。不要只凭聊天窗口截图宣布成功。

首轮失败时，先判断是否已经有满足剪辑目标的连续范围；有则记录 `PARTIAL_SELECT`。必须重试时只改一个与失败假设相关的变量，保留其他输入不变。

## 9. Select、QC 与观察状态

编辑只接收通过审查的 FULL/PARTIAL Select。QC 分开记录 Prompt Compliance、Identity、Spatial Continuity、Scale、Physics、Camera、Editability 和 Aesthetic。状态按顺序推进：

```text
DRAFT → SPEC_RESOLVED → PREFLIGHT_PASS → READY_FOR_KF → KF_GENERATED
→ KF_QC_PASS → READY_FOR_VIDEO → VIDEO_GENERATED → VIDEO_QC_PASS
→ SELECT → OBSERVED_STATE_RECORDED → EDIT_READY
```

`KF_QC_PASS` 不等于完整 Start/End Authority；先做 Visual Control State Alignment。`OBSERVED_ONCE` 不得提升成默认模型能力。

回填 H3 外部材料（由项目适配器执行）：

```text
python <project-adapter>/scripts/ingest_h3_evidence.py --root <project> --mp4 <raw.mp4> --screenshot <settings.png> --generation-id <id> --out <evidence.json>
```

该脚本只记录哈希、参数和 `OBSERVED_ONCE`，不会自动 PASS、重试或解锁 E01/E02。

## 10. 剪辑、音频、字幕与发布

读取 `11-editing.md`、`12-audio.md` 和 `30-edit-timeline-contract.md`。用 Edit Unit 覆盖最终时间线；文本、字幕、标准转场和精确时序尽量放确定性后期。声音 timing authority 确认后再锁画面。最终交付还要做目标 9:16/画幅、音频、字幕、编码、文件命名和发布证据检查。

FilmFoundry 可以记录这些事实和证据，但不会替你操作 NLE、编码器或发布平台。

## 11. 每镜头最小检查清单

- Canon/Shot 状态是否已锁定？
- 资产是否有稳定 ID、真实哈希和正确 Profile？
- 参考槽是否写清 controls 与 does_not_control？
- 起始/结束状态是否与输入图一致？
- 是否真的需要空间图、尺度、物理或预演？
- Prompt 是否只有一个主动作和清楚的可观察结果？
- Provider 能力是否有相同 surface/version 证据？
- 生成时长是否和剪辑目标分开？
- 是否记录 generation、Select、QC 和 observed state？
- 最终镜头是否覆盖时间线、声音、字幕、画幅和交付要求？

## 12. 项目当前推荐顺序

先用项目已有的锁定资产和 routed units 做一条技术切片，不改 Canon、不重做全套角色表。为一个代表性测试建立最小视觉控制计划，拿到真实 MP4、设置截图和 generation ID 后，登记一次观察，再决定是否扩大测试矩阵。任何路线升级都等待对应证据和 state alignment。

## 13. 第一次创作的可复制清单

第一次不要试图做完整一集。选择一个 5 秒左右、一个主体、一个地点、一个动作的镜头，按下面顺序完成：

1. 写一页 Creative Brief，给镜头一个明确的叙事目的。
2. 为需要复用的人物和场景建立最小 Passport，并确认 Registry 路径和哈希。
3. 写一个 Shot Spec，只保留一个主动作和清楚的起始/结束状态。
4. 如果身份、空间或物理事实容易漂移，再建立 Visual Control Plan；否则不要增加控制项。
5. 写 Prompt Markdown，逐项绑定 references，并执行 `validate`。
6. 读取 Provider 的准确能力证据；没有证据就把它当作实验路线。
7. 编译 payload，保存输入哈希；由外部工具生成一次。
8. 将原始输出放入 `09_新生成产出/review`，记录 generation ID 和媒体哈希。
9. 人工播放并填写 QC；必要时选择连续 `PARTIAL_SELECT`，再回填 observed state。
10. 只有 Select、状态、音频 timing 和时间线覆盖都满足后，才把镜头交给后期。

任何一步失败都先回到最靠近失败事实的上游修复。不要因为一次失败就同时更换角色图、Prompt、模型、时长和镜头运动，否则无法知道哪一个变量造成改善。
