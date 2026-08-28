# AI 视频全链路 Agent Skill：GitHub 52 Skills 深度蒸馏研究与架构设计 v0.1

**研究日期：** 2026-08-28  
**目标：** 从公开 GitHub Agent Skills、官方 Skills 和可复用生产工作流中，蒸馏出一个真正可用于实际 AI 视频项目的通用 Skill。  
**当前状态：** Research + Architecture Design  
**明确排除：** 不把任何尚未完成、尚未经过真实成片验收的内部项目当作“成功经验”或设计依据。

---

# 1. 研究目标

本研究不回答：

> “MiniMax H3 提示词到底应该写多长？”

真正要回答的是：

> **一个 AI Agent 怎样把用户的故事、广告、MV、短片、产品片或电影创意，稳定地变成可生成、可审查、可修改、可剪辑、可交付的视频生产流程？**

因此目标不是做一个：

```text
minimax-prompt-generator
```

而是做一个更上层的：

```text
generative-film-production
```

它应该能够：

```text
Brief
→ Story / Creative Intent
→ Breakdown
→ Reference Board
→ Asset Lock
→ Shot Design
→ Keyframe Strategy
→ Model-Agnostic Video Spec
→ Model Adapter
→ Generation
→ Continuity
→ Review
→ Selects
→ Edit
→ Audio
→ Captions
→ Final QC
→ Master
```

模型可以换。

工作流不能随着模型一起报废。

---

# 2. 研究方法

## 2.1 不是只看 Star

GitHub 的 Star 是：

**Repository 级别。**

不是每一个 `SKILL.md` 单独拥有 Star。

因此本报告把两类排名分开：

### A. Repository Popularity

反映：

- 社区关注
- 维护活跃
- 传播度
- 生态成熟度

### B. Skill Utility Score

反映我们真正关心的：

- AI 视频直接相关度
- 连续性设计
- 可执行性
- 失败恢复
- 模型可移植性
- 验证机制
- 是否适合真实生产

不能把：

> 172K Star 的通用 Skill 仓库

直接理解成：

> 里面某一个视频 Skill 一定比 100 Star 的专业影视 Skill 强。

---

# 3. 本轮实际阅读范围

本轮实际阅读 / 拆解：

**52 个 Skill。**

来源包括：

```text
machina-exm/film-studio-skills                 7
fralapo/awesome-agent-skills                  10
SamurAIGPT/Generative-Media-Skills            13
remotion-dev/skills                           12
anthropics/skills                              5
Superpowers                                    3
AtlasCloudAI/awesome-seedance...                2
------------------------------------------------
TOTAL                                          52
```

---

# 4. GitHub Repository 热度榜

> Star 数为研究时读取到的 GitHub 仓库数据；会随时间变化。

| 排名 | Repository | Stars | Forks | 价值判断 |
|---:|---|---:|---:|---|
| 1 | `anthropics/skills` | 172,029 | 20,447 | Agent Skill 结构、触发、渐进加载、eval 方法的最高优先级参考 |
| 2 | `remotion-dev/skills` | 4,416 | 501 | 程序化视频、时间线、字幕、渲染、后期工作流的官方级参考 |
| 3 | `SamurAIGPT/Generative-Media-Skills` | 4,173 | 482 | 当前非常完整的多模态生成 Skill 集，图像/视频/剪辑/社媒覆盖广 |
| 4 | `AtlasCloudAI/awesome-seedance-2.5-prompts-skills` | 164 | 9 | 通用视频 Prompt Spec → 模型编译器思想非常强 |
| 5 | `machina-exm/film-studio-skills` | 98 | 17 | Star 不高，但对“影视生产工程化”的直接价值极高 |
| — | `fralapo/awesome-agent-skills` | 0 | 1 | 热度低，但多个 Skill 明确从真实 prompt corpus / 文档 / 书籍中蒸馏，研究价值高 |

### 来源

- https://github.com/anthropics/skills
- https://github.com/remotion-dev/skills
- https://github.com/SamurAIGPT/Generative-Media-Skills
- https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills
- https://github.com/machina-exm/film-studio-skills
- https://github.com/fralapo/awesome-agent-skills

---

# 5. 52 Skills 蒸馏清单

下面不是简单列名字。

每一项只保留：

> **这个 Skill 最值得偷师的那个机制。**

---

## 5.1 Film Studio Skills — 7

### 1. `film-breakdown`

核心：

> 在生成任何 Prompt 前，先把脚本拆成结构化 Shot 数据。

值得蒸馏：

- Scene / Shot ID
- Location
- Character State
- Props
- Dialogue verbatim
- Runtime
- Dramaturgy
- Blocking
- Acting
- Shot size
- Lens
- Camera movement
- Cut / pace / transition

最大价值：

**Prompt 不是剧本拆解器。**

剧本必须先被结构化。

---

### 2. `reference-board`

核心：

> Reference 是 Specification，不是 Inspiration。

每一张参考必须说明：

```text
从这张图取什么？
不取什么？
```

并且存在：

```text
APPROVED
REVISE
REJECTED
```

值得蒸馏：

**Reference Role Binding。**

---

### 3. `asset-passport`

核心：

> 每一个持续出现的角色 / 场景 / 道具只有一个权威 Passport。

例如：

```text
CHAR_001
Canonical Descriptor
Wardrobe
Silhouette
Face
State
Allowed Variants
Forbidden Drift
```

后续 Prompt 不重新描述角色。

而是使用：

```text
CHAR_001
```

+ Canonical Descriptor。

这是角色一致性的核心。

---

### 4. `stress-test`

核心：

> 不要第一张角色图看起来不错就进入视频。

先低成本测试：

- 正面
- 侧面
- 背面
- 中景
- 特写
- 全景
- 强光
- 弱光
- 双人镜头
- 不同角度

关键原则：

> Identity consistency 不是平均分。

如果 10 张里 1 张已经完全不是这个人：

**失败。**

---

### 5. `shot-prompt`

本轮最重要 Skill 之一。

核心 Prompt 不是“基础设定 + 氛围 + 每秒内容”这么简单。

它实际上覆盖：

1. Scene context
2. Exact character count
3. One action
4. Reference descriptors
5. Spatial map
6. 180° line
7. First-frame blocking
8. Lens
9. Physical camera placement
10. Camera path
11. Action timing
12. Physics
13. Persistent consequences
14. Lighting
15. Audio
16. Acting
17. Style
18. Color ratio
19. Quality bar
20. Failure conditions

非常重要的原则：

> **One action per clip。**

另外：

> 每次失败后只修改一行，而不是整段 Prompt 推倒重写。

---

### 6. `setup`

核心：

在开始项目之前先确定：

- 有什么模型
- 支持哪些输入
- 单 Clip 长度
- 输出目录
- 资产策略

蒸馏：

**Capability Discovery before Production。**

---

### 7. `studio-init`

核心：

生产目录隔离：

```text
assets/
generations/
selects/
edit/
color/
sound/
master/
docs/
```

最重要规则：

> Editor 只看 SELECTS。

不要让：

```text
v01
v02
v03
failed
almost-good
test-final
```

全部进入剪辑区。

---

# 5.2 fralapo Skills — 10

---

### 8. `seedance-prompts`

来源作者称其从约 195 个 Prompt 中提炼。

核心结构：

```text
Style
Duration
Scene
Timecoded Shot List
Technical / Negative
```

重要经验：

- 一张参考图一个明确目的
- identity ref / camera ref / audio ref 分开
- 15 秒约 3 Shot 是舒服区
- 不要在一个 Shot 塞太多 micro-details
- Extension 的开始状态必须接上前段结束状态

---

### 9. `image-gen-prompts`

作者称其从约 18,900 个图像 Prompt 中提炼。

通用图像结构：

```text
Subject
Action
Wardrobe
Environment
Lighting
Camera/Lens
Style
Format
Preserve
Negative
```

最值得蒸馏：

> 图像编辑必须有 Preserve Clause。

例如：

```text
Preserve exactly:
face
hair
wardrobe
body proportions
camera perspective
background architecture
```

---

### 10. `creative-director`

核心不是 Prompt。

而是：

# Router

根据任务加载：

```text
copywriter
idea-generator
creative-leader
visionary
evaluator
```

重要启示：

> 一个大型 Skill 不应该把所有知识写在根 SKILL.md。

应该：

```text
Router
→ 按需读取 specialist reference
```

---

### 11. `video-editor`

从多个专业剪辑 breakdown 中蒸馏。

North Star：

```text
Retention
Audience Experience
Edit serves idea
```

剪辑原则：

- Hard Cut 是默认
- J Cut / L Cut 用于对白连续
- Transition 必须有动机
- Show, don't tell
- 一个画面一个主要焦点
- 先修上游素材，再用剪辑补救

重要启示：

**AI 生完 Clip 并不等于视频完成。**

---

### 12. `ffmpeg`

重要机制：

- Diagnose before convert
- `ffprobe` 先看事实
- stream copy vs transcode
- filtergraph
- deterministic post

启示：

> 裁切、转码、拼接、音轨处理这种确定性任务，不要浪费生成模型。

---

### 13. `social-algorithm`

重要机制：

- Hook
- Camera variety
- Visual metaphor
- Trailer-style progression
- Audience-first

用于：

短视频 / 广告 / 社交分发。

---

### 14. `awesome-readme`

虽然不是视频 Skill，但它的方法论值得蒸馏：

```text
DISCOVER
→ CLASSIFY
→ SELECT
→ DRAFT
→ AUDIT
→ VERIFY
→ WRITE
```

启示：

> 不要根据固定模板强行生成所有章节。

只加载任务需要的部分。

---

### 15. `llm-wiki`

核心：

> Compile, don't retrieve.

结构：

```text
raw/       原始不可变
wiki/      编译后的知识
schema     规则
log        审计轨迹
```

对 AI 视频 Skill 的启示：

应建立：

```text
model_profiles/
production_lessons/
failure_patterns/
```

每做一个真实项目后：

不是“下次靠记忆”。

而是把经验编译进模型 Profile。

---

### 16. `marketing-mba`

最值得吸收：

> Precision on “for who” is a feature.

进入广告 / 商业片之前必须定义：

```text
Audience
Need
Outcome
Position
```

而不是直接开始“酷炫生视频”。

---

### 17. `public-speaking-persuasion`

关键故事结构：

```text
Situation
Desire
Conflict
Change
Result
```

以及：

> Point X：作品结束后，希望观众做什么 / 理解什么？

这是 Creative Brief 的重要前置字段。

---

# 5.3 Generative-Media-Skills — 13

---

### 18. `muapi-cinema-director`

Prompt 公式：

```text
Shot Type
+ Subject / Action
+ Environment
+ Lighting
+ Camera Movement
+ Lens Effect
```

关键：

Camera 要物理可解释。

不要写：

```text
cinematic dynamic amazing camera
```

而应该写：

```text
camera at waist height,
3 meters from subject,
85mm lens,
slow dolly forward 1 meter
```

---

### 19. `muapi-product-video-ad-maker`

核心：

```text
Hero Image
→ Approval
→ Animate
```

不要直接：

```text
产品描述 → 视频
```

先静态验收再动。

---

### 20. `muapi-ai-clipping`

长视频后期流水线：

```text
Transcribe
→ Rank
→ Dedupe
→ Select
→ Crop
```

Highlight 判断：

- Hook
- Emotional peak
- Conflict
- Revelation
- Quotable line
- Story peak
- Practical value

---

### 21. `muapi-social-media-video`

非常接近完整生成流程：

```text
Brand Files
→ Storyboard
→ Reference Images
→ Director Brief
→ Generate
```

关键：

> 抽象形容词要翻译成技术摄影语言。

---

### 22. `muapi-ugc-video-factory`

三阶段：

```text
Prompt
→ Hero Image
→ I2V
```

多 Shot 广告：

> 每一 Shot 分别做 hero frame + clip。

不是一次让模型做整条广告。

---

### 23. `muapi-seedance-2`

Prompt 层级：

```text
Scene
Subject
Action
Camera
Audio
Pacing / Style
```

并明确：

> 顺序很重要。

Reference 要写用途。

---

### 24. `muapi-ad-creative`

核心：

```text
Phase A：Hero Concept
↓ approval
Phase B：平台扩展
```

启示：

> 先冻结创意方向，再 fan-out。

---

### 25. `muapi-nano-banana`

重要原则：

# No Keyword Soup

用逻辑关系表达：

```text
Subject
+ Action
+ Context
+ Composition
+ Lighting
+ Style
```

并描述物理关系：

```text
光从哪个方向来
照到什么
反射到哪里
```

---

### 26. `muapi-youtube-shorts`

平台 preset 模式：

```text
shorts
tiktok
reels
feed
```

说明我们自己的 Skill 也应该：

> 核心 Workflow 不变，Delivery Adapter 按平台变化。

---

### 27. `muapi-instagram-post`

核心：

- Single focal point
- format-aware
- 有已有 subject 时优先 edit / reference，而非重生

---

### 28. `muapi-youtube-thumbnail`

先做：

```text
Composition Plan
```

再生图。

重要：

> 图像模型不可靠的文字，放到 Post。

视频同理。

---

### 29. `muapi-logo-creator`

虽然不是视频，但提供了优秀的：

```text
Design Specification
before generation
```

不要让模型边想结构边生成。

---

### 30. `muapi-ui-design`

同样强调：

```text
Tokens
Hierarchy
Components
Constraints
```

启示：

> 视频也应该有 Production Tokens / Visual DNA，而不是每镜重新写风格形容词。

---

# 5.4 Remotion Official Skills — 12

---

### 31. `remotion-best-practices`

Router Skill。

把不同需求路由到：

```text
create
markup
interactivity
captions
maps
multimedia
render
studio
docs
upgrade
```

再次证明：

**高质量 Skill 应采用模块化 progressive disclosure。**

---

### 32. `remotion-captions`

字幕不是 Prompt 文本。

是结构化数据。

启示：

```text
caption generation
caption timing
caption rendering
```

应该与生成视频分离。

---

### 33. `remotion-create`

创建 Composition 与渲染分开。

重要设计思想：

> Build ≠ Render。

---

### 34. `remotion-markup`

所有动画受：

```text
frame
time
interpolation
```

控制。

这提醒我们：

> 能由确定性时间线完成的动画，不需要生成模型猜。

---

### 35. `remotion-multimedia`

先读取：

- duration
- dimensions
- media facts

启示：

**Inspect metadata before processing。**

---

### 36. `remotion-render`

Render 是独立终端步骤。

---

### 37. `remotion-interactivity`

非常好的工程原则：

> 保持视频编辑结构“可编辑”，不要过度抽象到 Studio 无法操作。

我们自己的 Pipeline 也必须输出：

```text
editable intermediate artifacts
```

而不是只有最终 MP4。

---

### 38. `remotion-studio`

Preview 是正式 Workflow 的一环。

不是生成完直接 export。

---

### 39. `remotion-maps`

关键模式：

> 先选择一个 technique，再只加载那个 technique。

说明：

Prompt / 模型 Adapter 也应该这样工作。

---

### 40. `remotion-docs`

重要：

> 查当前文档，不依赖记忆中的旧 API。

未来模型参数变化时：

Skill 必须支持 Model Profile 更新。

---

### 41. `remotion-saas`

说明视频工作流最终可以产品化为：

```text
input form
→ editable preview
→ render
```

---

### 42. `remotion-upgrade`

重要工程原则：

- preserve existing changes
- inspect current state
- exact version compatibility
- verify after upgrade

对生产 Skill 同样成立。

---

# 5.5 Anthropic Official Skills — 5

---

### 43. `skill-creator`

这是我们写自己的 Skill 必须服从的重要来源。

核心流程：

```text
Capture Intent
→ Draft
→ Create Realistic Evals
→ Run WITH Skill
→ Run BASELINE
→ Compare
→ Grade
→ Iterate
→ Expand Eval Set
```

核心结构：

```text
SKILL.md
references/
scripts/
assets/
```

并明确推荐：

> SKILL.md 尽量 <500 行。

其余知识按需读取。

---

### 44. `brand-guidelines`

最重要机制：

> Style 不能只有形容词。

应该变成 Token：

```text
Color
Typography
Scale
Fallback
Rules
```

映射到电影：

```text
Color palette
contrast
lighting ratio
lens family
texture
motion character
```

---

### 45. `canvas-design`

重要：

```text
Visual Philosophy
→ Visual Execution
```

并强调：

> 第二遍优化不是继续加东西，而是优化已有结构。

对视频生成非常重要。

---

### 46. `algorithmic-art`

最值得吸收：

- parameterized
- seeded
- reproducible
- controlled variation

映射到 AI 视频：

> 每次生成必须知道“哪些变量变了”。

否则 Retry 没有学习价值。

---

### 47. `slack-gif-creator`

虽然场景不同，但它有非常好的：

```text
Platform constraints
→ Build
→ Validate
```

并提供 validators。

我们自己的 Skill 也必须有：

```text
Prompt Linter
Shot Validator
Asset Registry Validator
```

---

# 5.6 Superpowers — 3

---

### 48. `writing-skills`

核心：

> Skill 是可复用流程，不是某个项目的长 Prompt。

要求：

- clear trigger
- reusable
- progressive disclosure
- references separated
- test before trust

---

### 49. `test-driven-development`

核心：

```text
RED
→ GREEN
→ REFACTOR
```

映射到 Skill：

```text
baseline fails
→ skill changes behavior
→ regression tests
```

---

### 50. `brainstorming`

核心：

> 先把架构设计说清楚并确认，再写实现。

这就是本报告为什么先给出 Skill Architecture，而不是现在直接把一个未经测试的 `SKILL.md` 包装成“完成品”。

---

# 5.7 Atlas Video Skills — 2

---

### 51. `universal-video-prompt-skill`

这是本轮最重要来源之一。

核心思想：

# Spec ≠ Prompt

先写：

```text
Model-Agnostic Video Spec
```

再：

```text
Compile → Seedance
Compile → Veo
Compile → Kling
Compile → MiniMax
...
```

它把信息分成三类：

```text
GLOBAL
LOCKS
TIME
```

更重要的是：

# Verifiability

不要写：

```text
保持一致
氛围紧张
镜头高级
```

改成：

```text
Stage 结束时角色左手仍拿着杯子
眉毛收紧
嘴唇闭合
呼吸加快
前景叶片失焦、人物脸清晰
```

如果一条要求：

> 输出后无法检查，

就无法 Debug。

---

### 52. `seedance-2-5-skill`

非常重要的纠偏：

> “首尾帧”不等于所有镜头都应该把上一条视频尾帧当下一条首帧。

只有：

```text
uninterrupted action
```

才适合 tail relay。

如果是：

```text
hard cut
reverse angle
new location
insert
match cut
```

应该独立设计。

另外它明确指出：

### 时间粒度不是越细越好

三档：

```text
None
Stages + End States
Second-level
```

默认：

# Stages + End States

只有：

- 音乐卡点
- 对口型
- 固定品牌露出时刻
- 必须精确 handoff

才使用逐秒时间轴。

这是对“每一秒全部写死”方案非常重要的纠正。

---

# 6. 针对 AI 视频生产的 Skill 实用排行榜

下面不是 Star 排名。

这是针对：

> **“做真实 AI 视频项目”**

的综合评分。

评分：

```text
AI 视频直接相关度             25%
生产控制 / 连续性            25%
可移植性                     15%
验证 / Debug 能力            15%
来源可信度 / 方法依据        10%
维护 / 社区信号              10%
```

---

| 排名 | Skill | 分数 | 为什么值得优先学 |
|---:|---|---:|---|
| 1 | Atlas `universal-video-prompt-skill` | 96 | 把“视频规格”和“模型 Prompt”彻底分开，是跨模型长期可用架构 |
| 2 | Machina `shot-prompt` | 95 | 最像真正摄影导演执行单，空间、光学、动作、物理、音频、失败条件完整 |
| 3 | Machina `asset-passport` | 94 | 解决 AI 视频最根本的角色/场景持续一致问题 |
| 4 | Machina `stress-test` | 93 | 在昂贵视频生成前低成本发现角色失真 |
| 5 | Atlas `seedance-2-5-skill` | 92 | Route Selection、End State、Transition Continuity 思路非常成熟 |
| 6 | fralapo `seedance-prompts` | 91 | 从真实 Prompt corpus 中总结 Reference、时间码、连续性模式 |
| 7 | Machina `film-breakdown` | 90 | 把创作问题先变成结构化镜头工程问题 |
| 8 | Machina `reference-board` | 89 | Reference Role / Anti-reference 是高价值机制 |
| 9 | Samur `muapi-seedance-2` | 88 | Prompt hierarchy 和多 Reference 使用很实用 |
| 10 | fralapo `video-editor` | 87 | 补齐“生成之后怎么办”，防止只会生 Clip 不会做片 |
| 11 | fralapo `image-gen-prompts` | 86 | Keyframe / edit consistency 很有价值 |
| 12 | Samur `muapi-cinema-director` | 85 | 把运镜转成物理摄影参数 |
| 13 | Samur `muapi-social-media-video` | 84 | Storyboard→Ref→Director Brief→Video 链路完整 |
| 14 | Remotion `remotion-markup` | 84 | 将可确定的后期从生成模型中剥离 |
| 15 | Anthropic `skill-creator` | 83 | 决定我们自己的 Skill 是否真的能验证、迭代 |
| 16 | Remotion `remotion-best-practices` | 82 | Router + modular knowledge 的好样板 |
| 17 | fralapo `creative-director` | 81 | 多 Specialist Router 模式 |
| 18 | Machina `studio-init` | 80 | Selects-only、版本、生产目录非常实用 |
| 19 | fralapo `ffmpeg` | 79 | 确定性视频处理应该留给确定性工具 |
| 20 | Samur `muapi-product-video-ad-maker` | 78 | 静态 approval → animate 的 gate 非常正确 |

---

# 7. 本轮最重要的结论

研究这些 Skill 后，最明显的结论是：

# “更长的 Prompt”不是答案。

优秀 Skill 真正反复出现的是：

```text
更少歧义
更少并发动作
更清晰 Reference 角色
更明确 End State
更严格资产锁定
更小的生成单元
更可靠的验证
更可控的 Retry
更强的后期分工
```

---

# 8. 对“每秒写清楚”的纠正

这是本轮研究后必须修改的观点。

旧思路：

```text
0-1 秒
1-2 秒
2-3 秒
3-4 秒
...
```

看起来非常精确。

实际上：

**不是所有镜头都适合。**

Atlas 的模型无关 Video Skill 明确区分：

## A. None

适合：

- 单一连续动作
- 氛围镜头
- 一镜到底

只写事件顺序。

---

## B. Stages + End States

适合：

**绝大多数叙事镜头。**

例如：

```text
Stage 1:
角色走到桌前。

End state:
角色停在桌子左侧，
右手距离地图约 10cm，
地图仍闭合。

Stage 2:
角色展开地图。

End state:
地图完全铺平，
左手压住左下角，
右手停在地图中央。
```

这比：

```text
第 2.3 秒抬手
第 2.8 秒碰地图
```

更容易生成，也更容易 QC。

---

## C. Second-Level

只有外部硬约束才使用：

- lip-sync
- VO
- 音乐节拍
- 固定 logo reveal
- reference handoff

---

# 9. 我们自己的 Skill 不应该是“超级 Prompt”

如果最终写成：

```text
一个 1500 行 SKILL.md
+
一个巨型万能 Prompt
```

这次研究就失败了。

正确设计应该是：

# Router + Production Modules + Model Adapters + Validators

---

# 10. Proposed Skill Name

建议：

```text
generative-film-production
```

而不是：

```text
minimax-video
```

也不是：

```text
ai-video-prompt
```

因为它应该负责：

**从创意到 Master 的全链路。**

---

# 11. Skill Package Architecture v0.1

```text
generative-film-production/
│
├── SKILL.md
│
├── references/
│   │
│   ├── 00-production-philosophy.md
│   ├── 01-creative-brief.md
│   ├── 02-story-breakdown.md
│   ├── 03-reference-board.md
│   ├── 04-asset-passport.md
│   ├── 05-asset-stress-test.md
│   ├── 06-shot-engineering.md
│   ├── 07-continuity-engine.md
│   ├── 08-video-spec.md
│   ├── 09-prompt-compiler.md
│   ├── 10-generation-loop.md
│   ├── 11-editing.md
│   ├── 12-audio.md
│   ├── 13-qc.md
│   ├── 14-failure-recovery.md
│   │
│   └── adapters/
│       ├── generic-t2v.md
│       ├── generic-i2v.md
│       ├── first-last-frame.md
│       ├── multi-reference-video.md
│       ├── storyboard-to-video.md
│       ├── seedance.md
│       ├── minimax-h3.md
│       ├── veo.md
│       ├── kling.md
│       └── image-generation.md
│
├── templates/
│   ├── creative-brief.md
│   ├── production-bible.md
│   ├── asset-passport.md
│   ├── asset-registry.csv
│   ├── shot-card.md
│   ├── continuity-ledger.csv
│   ├── generation-log.csv
│   ├── selects-log.csv
│   └── qc-report.md
│
├── scripts/
│   ├── validate_asset_registry.py
│   ├── validate_shot_spec.py
│   ├── prompt_lint.py
│   └── continuity_lint.py
│
└── evals/
    ├── evals.json
    └── README.md
```

---

# 12. 根 SKILL.md 只负责路由

根 Skill 不应该塞满摄影词汇。

它只负责判断：

```text
用户现在在什么阶段？
缺什么？
下一步是什么？
应该加载哪个 reference？
是否达到 Gate？
```

例如：

```text
用户给故事
→ read creative-brief
→ read story-breakdown

用户已经有角色图
→ read asset-passport
→ read asset-stress-test

用户要生成某一 Shot
→ read shot-engineering
→ read continuity-engine
→ read video-spec
→ read target model adapter

用户拿到视频问为什么失败
→ read qc
→ read failure-recovery

用户准备剪成片
→ read editing
→ read audio
```

---

# 13. 全链路正式 Workflow

---

## STAGE 0 — Capability Discovery

先问清楚：

```text
图像模型？
视频模型？
音频模型？
是否支持 multi-ref？
是否支持 first/last frame？
最大时长？
支持原生音频？
支持视频参考？
Reference 上限？
分辨率？
```

输出：

```text
MODEL_PROFILE
```

如果不知道：

**不得凭经验假设。**

---

## STAGE 1 — Creative Brief

必须明确：

```text
Audience
Format
Duration
Purpose
Point X
Platform
Story / Message
Emotional arc
Style intent
Delivery specs
```

Gate：

```text
BRIEF_LOCKED
```

---

## STAGE 2 — Story Breakdown

把内容转换成：

```text
Sequence
Scene
Shot
```

每一 Shot 定义：

```text
Narrative Goal
One Dominant Action
Duration Range
Characters
Location
Props
Dialogue
Edit Intent
```

Gate：

```text
BREAKDOWN_LOCKED
```

---

## STAGE 3 — Reference Board

每一个 Reference 必须拥有 Role。

例如：

```text
REF_001
controls:
  face identity
does_not_control:
  clothing
  lighting
```

或者：

```text
REF_007
controls:
  location architecture
does_not_control:
  time of day
```

同时维护：

```text
ANTI_REFERENCE
```

Gate：

```text
REFERENCE_BOARD_APPROVED
```

---

## STAGE 4 — Asset Passport

每个持续出现资产：

```text
CHARACTER
LOCATION
PROP
PRODUCT
VEHICLE
CREATURE
```

只有一个 Canonical Passport。

状态变化：

```text
CHAR_A_DRY
CHAR_A_WET
```

应作为明确 State Variant。

不要悄悄改变 Canon。

Gate：

```text
ASSET_LOCKED
```

---

## STAGE 5 — Stress Test

在真正生成视频前：

对持续资产做便宜的静态测试。

例如角色：

```text
CU front
CU 3/4
profile
medium
full body
back
harsh light
low light
two-shot
wide environment
```

通过：

```text
10/10 identity hold
```

再进入视频。

---

## STAGE 6 — Shot Engineering

这里不是写 Prompt。

先写：

# Canonical Shot Spec

---

# 14. Canonical Shot Spec

建议字段：

```yaml
shot_id:
scene_id:
duration_target:
narrative_goal:
dominant_action:

characters:
  - asset_id:
    state:
    start_position:
    end_position:

location:
props:

screen_direction:
camera_axis:
eyelines:

initial_state:
end_state:

shot_size:
lens:
camera_position:
camera_height:
camera_angle:
camera_support:
camera_move:
camera_path:
camera_stop:

action_stages:
  - stage:
    visible_action:
    end_state:

physics:
persistent_consequences:

acting:
lighting:
color:
audio:
dialogue_verbatim:

edit_in:
edit_out:
transition_type:

reference_roles:
failure_risks:
quality_bar:
```

---

# 15. 为什么 Canonical Shot Spec 比 Prompt 更重要

因为它可以被编译成：

```text
MiniMax H3 Prompt
Seedance Prompt
Veo Prompt
Kling Prompt
Wan Prompt
```

而不是每换模型：

> 整套导演逻辑重写一次。

---

# 16. 三层 Prompt Spec

采用 Atlas 最优秀的设计：

---

## GLOBAL

控制整个 Shot / Clip：

```text
film type
scene
visual DNA
camera principle
overall action
```

---

## LOCKS

不能漂移：

```text
identity
character count
reference role
wardrobe
prop state
screen direction
continuity
audio source
must preserve
```

---

## TIME

只写：

```text
stage
observable action
observable end state
```

只有硬约束才加秒数。

---

# 17. End State 是核心中的核心

错误：

```text
保持角色一致。
```

不可验证。

正确：

```text
Stage 2 end state:

CHAR_A remains on frame left.
His left hand still holds the cup.
The cup is upright.
His right hand rests on the table.
CHAR_B remains seated frame right.
Neither character has crossed the camera axis.
```

这可以：

```text
看
检查
打分
Debug
```

---

# 18. Reference Role Binding

不能再写：

```text
参考图1
参考图2
参考图3
```

必须：

```text
REF_A:
controls identity only.
Do not inherit background or lighting.

REF_B:
controls costume and body silhouette.
Do not use facial identity.

REF_C:
controls location architecture.
Do not use people visible in the image.

REF_D:
controls camera motion only.
Do not inherit appearance.
```

这是多参考视频的核心。

---

# 19. 连续性 Engine

连续性不能只靠：

```text
last frame → next shot
```

必须根据 Transition Type 判断。

---

## Uninterrupted Action

可以：

```text
prior tail
→ next start
```

---

## Hard Cut

不要继承上一帧。

保持：

```text
screen direction
eyeline
prop state
time
lighting continuity
```

即可。

---

## Reverse Angle

保持：

```text
180° axis
eyeline
character positions
```

但重新设计画面。

---

## Match Cut

匹配：

```text
shape
motion direction
color
composition
```

不需要上一尾帧。

---

## Insert

独立生成。

---

# 20. Model Adapter

Canonical Spec 绝不直接发送给所有模型。

先：

```text
MODEL_PROFILE
```

再 Compiler。

---

## Example: I2V Adapter

因为画面已经由首帧定义：

Prompt 重点：

```text
Motion
Camera
Timing
Acting
Physics
Audio
End State
```

不要重复 500 字描述：

```text
角色穿什么衣服
场景有几个柱子
```

除非它们是高风险 Lock。

---

## Example: T2V Adapter

必须补：

```text
appearance
scene
composition
lighting
```

因为没有图像承担这些信息。

---

## Example: Multi-Reference Adapter

必须：

```text
每张 Reference 一个 Role
```

并根据模型 Reference 数限制自动降级。

优先级：

```text
Identity
>
Key Prop
>
Scene
>
Style
```

---

# 21. “负向 Prompt”冲突怎么解决

GitHub 研究中出现两种观点：

### 流派 A

明确 Negative：

```text
no text
no morph
no duplicate
```

### 流派 B

尽量转换成 Positive / Verifiable Constraints：

不要：

```text
don't change hand
```

而写：

```text
left hand remains wrapped around the same cup
through the final frame
```

我们自己的 Skill 不站死某一边。

Canonical Spec 存：

```text
must_preserve
failure_risks
```

Model Adapter 决定：

```text
Positive constraints
or
Negative section
or
Both
```

根据真实 Model Profile。

---

# 22. Generation Loop

第一次生成：

```text
GEN_v01
```

失败后：

不要：

> “再抽一张试试。”

必须写：

```text
Failure:
CHAR_A left hand releases prop too early.

Hypothesis:
Stage 2 has two competing hand actions.

Change:
remove second hand gesture.

Everything else:
unchanged.
```

然后：

```text
GEN_v02
```

---

# 23. Single Variable Retry

这是从 Film Studio + Algorithmic Art + TDD 共同蒸馏出的原则。

每轮只改变：

```text
one variable
```

例如：

```text
camera move
or
action count
or
reference pack
or
stage timing
```

否则无法知道：

> 为什么变好 / 为什么变差。

---

# 24. Failure Budget

同一个 Shot 如果连续失败：

```text
3 次
```

先诊断。

```text
5 次
```

必须考虑：

- 减少动作
- 固定机位
- 减少 Reference
- 拆 Clip

超过：

```text
10 次左右
```

不应该继续同 Prompt 抽卡。

应该重新设计 Shot。

---

# 25. QC 顺序

必须按照：

```text
1 Identity
2 Character count
3 Locks
4 End State
5 Anatomy / Prop
6 Spatial continuity
7 Camera
8 Motion quality
9 Audio
10 Editability
```

如果：

```text
Identity FAIL
```

就没必要继续评价：

> 镜头光影是不是 9.5 分。

直接 Reject。

---

# 26. Selects Only

生产目录：

```text
generations/
  shot_001/
    v01
    v02
    v03

selects/
  SH001_SELECT.mp4
```

Final Edit：

只能读取：

```text
selects/
```

---

# 27. 生成模型与后期模型职责分离

以下事情优先 Post：

```text
字幕
精确文字
Logo
标准转场
Cross Dissolve
Fade
简单 Push
简单 Zoom
音量自动化
J Cut
L Cut
精确时间轴
裁切
拼接
变速
色彩匹配
```

不要为了：

> 一个淡入淡出

重新花一次视频生成费用。

---

# 28. Audio Pipeline

声音拆分：

```text
Dialogue
Voice Over
Ambience
Foley / SFX
Music
```

不要把：

> “有氛围的音乐 + 对白 + 脚步 + 风 + 鸟叫”

一句塞给视频模型后就当成 Final Mix。

即使模型有 Native Audio：

也应该把音频当成：

```text
可独立验收 Layer。
```

---

# 29. 我们 Skill 的核心设计原则

最终保留 18 条：

1. **Spec before prompt**
2. **Brief before shot**
3. **One authoritative passport per recurring asset**
4. **Reference is a specification**
5. **Every reference has one explicit role**
6. **Stress-test recurring assets before video**
7. **One dominant action per generative clip**
8. **Physical camera language beats vague camera adjectives**
9. **Stages + visible end states are the default timing grammar**
10. **Second-level timing only when externally constrained**
11. **Continuity is state + axis + direction + prop logic, not blindly tail-frame chaining**
12. **Canonical Shot Spec is model-agnostic**
13. **Prompt is compiled by a model adapter**
14. **Failure risks compile differently per model**
15. **Change one variable per retry**
16. **Editor receives selects only**
17. **Deterministic post belongs to deterministic tools**
18. **Every real project feeds verified lessons back into model profiles**

---

# 30. 这套 Skill 和传统 Prompt 模板最大的区别

传统：

```text
用户故事
↓
LLM 写一个“超级详细 Prompt”
↓
视频模型
↓
抽卡
```

我们设计的：

```text
User Intent
↓
Creative Brief
↓
Story Breakdown
↓
Reference Board
↓
Asset Passport
↓
Stress Test
↓
Shot Spec
↓
Continuity Check
↓
Route Selection
↓
Model Profile
↓
Prompt Compiler
↓
Generation
↓
Structured Review
↓
Controlled Retry
↓
Select
↓
Edit / Audio / Caption / Color
↓
Master QC
```

---

# 31. Skill 的触发范围

应该在用户说类似：

```text
帮我做 AI 视频
帮我做短片
把这个故事做成视频
给我设计分镜
给 Kling 写 Prompt
给 Veo 写 Prompt
用 MiniMax 生成视频
做角色一致的视频
怎么保持镜头连续
这个 AI 视频为什么一直失败
帮我做广告片
帮我做 MV
帮我做产品视频
```

时触发。

---

# 32. Skill 不应该自动做什么

不要默认：

- 一上来生成 30 个 Shot
- 一上来写所有 Prompt
- 强制所有镜头逐秒时间轴
- 强制所有镜头首尾帧
- 强制所有项目同一工作流
- 强制一个视频模型
- 把所有 Reference 都塞进 Prompt
- 失败后无脑重复生成

---

# 33. Router Decision Tree

```text
START
│
├── 用户只有想法？
│      └── Creative Brief
│
├── 有脚本？
│      └── Story Breakdown
│
├── 有人物/场景图？
│      └── Asset Passport + Stress Test
│
├── 有完整资产？
│      └── Shot Engineering
│
├── 有 Shot Spec？
│      └── Route Select
│
├── 指定视频模型？
│      ├── Yes → load adapter
│      └── No  → recommend route by capability
│
├── 已经生成失败？
│      └── QC + Failure Recovery
│
├── 已经有完整 Clips？
│      └── Editing + Audio
│
└── 已完成时间线？
       └── Final QC
```

---

# 34. 我们自己的通用 Prompt Compiler

最终不是固定模板。

Compiler 根据 Route 输出。

---

## I2V Example Output Grammar

```text
[REFERENCE BINDING]
[GLOBAL SHOT]
[LOCKS]
[CAMERA]
[ACTION STAGES]
[VISIBLE END STATES]
[ACTING]
[PHYSICS]
[AUDIO]
[MODEL-SPECIFIC CONSTRAINTS]
```

---

## T2V Example Output Grammar

```text
[SUBJECT]
[ENVIRONMENT]
[COMPOSITION]
[LIGHT]
[GLOBAL SHOT]
[CAMERA]
[ACTION STAGES]
[END STATES]
[AUDIO]
[CONSTRAINTS]
```

---

## Multi-Reference Example

```text
REF_1 controls identity only.
REF_2 controls wardrobe only.
REF_3 controls location architecture only.

Do not inherit REF_1 background.
Do not inherit REF_3 people.
```

然后才写 Shot。

---

# 35. Eval / Benchmark 设计

按照 Anthropic `skill-creator` 和 TDD 原则：

不能：

> 写完 Skill，然后觉得“看起来很专业”就算完成。

至少建立下面 12 个 Eval。

---

## Eval 01 — Monster Prompt

输入：

> 用户要求一个 12 秒视频里完成 6 个复杂动作。

期望：

Skill 不直接写 12 秒超级 Prompt。

应该建议拆 Shot / Stage。

---

## Eval 02 — Recurring Character Not Locked

输入：

> 用户有一张主角照片，要直接做 20 个镜头。

期望：

Skill 先要求 / 建立：

```text
Asset Passport
+
Stress Test
```

---

## Eval 03 — Too Many References

输入：

> 用户提供 8 张参考图片，没有说明用途。

期望：

Skill 不全部使用。

先给每张图分配：

```text
Reference Role
```

然后选最小必要集。

---

## Eval 04 — Cross-Axis Dialogue

输入：

> 两个人对话，用户要求多个机位。

期望：

Skill 明确：

```text
180° axis
screen direction
eyeline
```

---

## Eval 05 — I2V Over-description

输入：

> 已有完整首帧，但用户让 Prompt 再写 500 字服装背景。

期望：

Skill 将 Prompt 压缩到：

```text
motion
camera
acting
timing
locks
end state
```

---

## Eval 06 — Timing Granularity

输入：

> 单一人物缓慢走向窗边，没有音乐、对白或卡点。

期望：

**不要逐秒硬编码。**

使用：

```text
event order
or stages + end states
```

---

## Eval 07 — Lip Sync

输入：

> 第 7 秒必须说出品牌名。

期望：

切换到 second-level timing。

---

## Eval 08 — Continuity Cut

输入：

> Shot A 正面，Shot B 反打。

期望：

不要盲目使用 A 尾帧作为 B 首帧。

保持：

```text
axis
eyeline
positions
prop state
```

---

## Eval 09 — Generation Failure

输入：

> 手里的杯子连续三次消失。

期望：

Skill：

- 定位 failure
- 改为 visible persistent state
- 只改相关行
- 不整段重写

---

## Eval 10 — Generated Text

输入：

> 广告里要出现完全正确的长中文说明文字。

期望：

优先：

```text
Post-production overlay
```

而不是押宝视频模型。

---

## Eval 11 — Generation Folder Chaos

输入：

> 已生成 14 个版本，准备剪片。

期望：

建立：

```text
SELECT
```

剪辑只读取 Select。

---

## Eval 12 — Final Assembly

输入：

> 所有 Clip 已经完成。

期望：

进入：

```text
Continuity
Edit
Audio
Caption
Color
Final QC
```

而不是继续生图 / 生视频。

---

# 36. 可自动验证的 Assertions

未来 `prompt_lint.py` 可以检查：

```text
是否有 shot_id
是否有 dominant_action
是否引用未定义 asset
每个 reference 是否有 role
是否有 initial_state
是否有 end_state
是否有 camera axis（需要时）
是否一个 Clip 存在多个互相冲突 camera moves
是否 dialogue 被改写
是否 generation retry 记录 change
是否 Select 已登记
```

---

# 37. 人工视觉 Eval

有些事情无法靠代码完全判断：

```text
动作自然
表演细腻
镜头节奏
电影感
构图美感
情绪是否正确
```

必须保留：

```text
Human Qualitative Review
```

不能为了“量化”而假装它们是客观数值。

---

# 38. Model Profile 是长期护城河

每一次真实使用后记录：

```yaml
model: ...
mode: I2V

strengths:
  - ...

weaknesses:
  - ...

reference_limit:
timing_behavior:
identity_behavior:
camera_behavior:
audio_behavior:

effective_patterns:
  - ...

failed_patterns:
  - ...

verified_on:
  - project / test id
```

以后：

Skill 不再：

> 凭网上经验猜。

而是：

> 先读已验证 Model Profile。

---

# 39. 本研究发现的三个“看起来正确但其实危险”的做法

---

## 39.1 Prompt 越长越好

错误。

真正应该追求：

# Information Density

不是字数。

---

## 39.2 每秒写得越细越好

错误。

容易：

- fragment motion
- 模型为了追 timestamp 制造停顿
- 丢动作
- 自动切镜

默认：

```text
Stages + End States
```

更可靠。

---

## 39.3 所有镜头都上一镜尾帧接下一镜

错误。

只适合：

```text
Continuous action / extension
```

电影硬切、反打、插入、Match Cut：

应该设计 continuity，而不是复制画面。

---

# 40. 本 Skill 的真正“核心 Prompt”

不是一段 Prompt。

是：

# Canonical Shot Spec

以及：

# Prompt Compiler

这是本次 52 Skills 蒸馏后最重要的架构决策。

---

# 41. 为什么不现在把“最终 Skill”直接写完

因为那会违反我们刚刚研究到的最重要 Skill Engineering 方法：

Anthropic 官方 Skill Creator 的正确流程是：

```text
Intent
→ Design
→ Draft
→ Eval
→ Baseline Comparison
→ Iterate
```

而不是：

```text
读完资料
→ 写一个 1000 行 SKILL.md
→ 宣布 Production Ready
```

目前已经完成：

```text
[✓] Intent
[✓] GitHub Research
[✓] 52 Skills Distillation
[✓] Architecture Design
[✓] Eval Design
```

尚未执行：

```text
[ ] Architecture Approval
[ ] SKILL.md Implementation
[ ] References Implementation
[ ] Templates
[ ] Validators
[ ] Baseline Eval
[ ] With-Skill Eval
[ ] Compare
[ ] Refactor
[ ] v1.0 Package
```

---

# 42. 下一阶段正式交付物

架构确认后，下一轮应直接生成一个完整可安装目录：

```text
generative-film-production/
```

以及：

```text
generative-film-production_v1.0.zip
```

至少包含：

```text
SKILL.md
14+ reference modules
model adapters
templates
validators
12+ evals
README
CHANGELOG
```

而不是再交付：

> “一份更详细的提示词教程”。

---

# 43. 最终结论

这次 GitHub 研究后，方向发生了一个根本变化。

我们原来在问：

> **怎样把 Prompt 写得更细，让视频模型听话？**

真正成熟的答案是：

> **不要让 Prompt 同时承担导演、分镜、资产管理、连续性、摄影、表演、音频、版本管理和 QC。**

应该把这些决策拆成可验证的生产对象：

```text
Creative Brief
Asset Passport
Reference Role
Shot Spec
Continuity Ledger
Model Profile
Compiled Prompt
Generation Log
Select
QC
```

Prompt 只是最后的：

# 编译产物。

这才有可能让同一套方法：

```text
今天用 MiniMax
明天用 Seedance
后天用 Veo
以后换新的模型
```

仍然成立。

---

# 44. 推荐进入 v1.0 的设计

**推荐批准当前架构：**

```text
generative-film-production
=
Router
+
Production Workflow
+
Canonical Shot Spec
+
Continuity Engine
+
Prompt Compiler
+
Model Adapters
+
Generation Log
+
Post Pipeline
+
Validators
+
Evals
```

设计批准后：

**下一步不再讨论方法论。**

直接进入：

# SKILL v1.0 Implementation + TDD / Eval

---

# Appendix A — 主要 GitHub Sources

## Official / High Signal

- https://github.com/anthropics/skills
- https://github.com/remotion-dev/skills
- https://github.com/SamurAIGPT/Generative-Media-Skills
- https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills
- https://github.com/machina-exm/film-studio-skills
- https://github.com/fralapo/awesome-agent-skills

## Especially Important Individual Skills

- https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills/tree/main/skills/universal-video-prompt-skill
- https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills/tree/main/skills/seedance-2-5-skill
- https://github.com/machina-exm/film-studio-skills/tree/main/skills/shot-prompt
- https://github.com/machina-exm/film-studio-skills/tree/main/skills/asset-passport
- https://github.com/machina-exm/film-studio-skills/tree/main/skills/stress-test
- https://github.com/machina-exm/film-studio-skills/tree/main/skills/reference-board
- https://github.com/machina-exm/film-studio-skills/tree/main/skills/film-breakdown
- https://github.com/fralapo/awesome-agent-skills/tree/main/skills/seedance-prompts
- https://github.com/fralapo/awesome-agent-skills/tree/main/skills/image-gen-prompts
- https://github.com/fralapo/awesome-agent-skills/tree/main/skills/video-editor
- https://github.com/SamurAIGPT/Generative-Media-Skills
- https://github.com/remotion-dev/skills
- https://github.com/anthropics/skills/tree/main/skills/skill-creator

---

# Appendix B — Evidence Policy

本报告对来源做以下区分：

### 官方仓库

例如：

```text
anthropics/skills
remotion-dev/skills
```

用于：

- Skill 结构
- 工程方法
- 官方生态使用规范

### Corpus-Distilled Skills

用于：

- 总结 recurring patterns
- Prompt 结构
- Editing patterns

如果仓库作者声明：

```text
195 prompts
18,900 prompts
multi-million-dollar production
```

本报告仅把它视作：

> **仓库作者的来源/经验声明。**

不把它自动当作独立验证事实。

### 我们自己的 v1.0

只有经过：

```text
baseline
+
with-skill eval
+
real project trial
+
regression
```

之后，

才允许标记：

```text
Production Validated
```

否则只标记：

```text
Draft
Experimental
Evaluated
```

---

**END OF RESEARCH & ARCHITECTURE DESIGN v0.1**
