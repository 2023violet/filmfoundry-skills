# FilmFoundry 通用化重构规范 v1（设计稿）

**状态：** 设计稿，未构成发布批准或行为变更。

**目的：** 让 FilmFoundry 能够服务不同项目、媒介、视觉风格和外部生成工具，同时避免把任何一个下游项目的规则写入 Core。

## 1. 目标与非目标

### 目标

- 同一套核心语义可用于电影、短视频、广告、MV、纪录片、动画、游戏过场和动态海报。
- 项目差异通过项目配置表达，风格差异通过风格配置表达，Provider 差异通过外部适配器表达。
- 所有生成资产、Prompt 和镜头计划保持可追溯、可审查、可回滚。
- 保留现有 Provenance、Continuity、Select、Shot Spec 和 Gate 语义。
- 在缺少具体 Provider 时，仍能输出可交接的 Provider-neutral 生产资料。

### 非目标

- 不承诺任意模型都能生成相同结果。
- 不把平台热度、视觉美学或创作者速度写成 Core 保证。
- 不在 Core 中维护具体项目 Canon、角色名、镜头数量或下游 Runtime。
- 不把某一种风格的惯例提升为所有项目的硬性 Gate。

## 2. 四层边界

### 2.1 Core Contracts

Core 只定义跨项目稳定的事实和关系：

- 创作目标与受众；
- 故事状态和版本；
- 角色、地点、道具和状态的身份；
- 镜头中的主体、动作、空间、摄影和时间关系；
- 连续性、Provenance、Select、Gate 和人工确认；
- 资产之间的依赖和派生关系。

Core 不包含项目名、Provider 名、具体风格名或某一种资产生产惯例。

### 2.2 Project Profile

Project Profile 描述当前交付任务，不改变 Core 语义。建议字段：

```yaml
project_profile:
  project_id: example-project
  medium: narrative_short
  audience: general
  target_duration: 30s
  production_scope: teaser
  continuity_level: high
  delivery_aspect: 9:16
```

`medium`、`production_scope` 和 `continuity_level` 用于路由深度、风险和输出格式，不用于创建项目专用分支。

### 2.3 Style Profile

Style Profile 描述可替换的视觉语言：

```yaml
style_profile:
  visual_language: cinematic_realism
  palette: muted_warm
  texture: restrained_film_grain
  lighting: motivated_practical
  camera_behavior: observational
  motion_density: low
  composition: balanced
```

风格参数只影响表现层。身份、空间、动作、连续性和可追溯要求仍由 Core 控制。

### 2.4 Provider Adapter

Core 输出 Provider-neutral 的 Shot Spec、资产需求和 Prompt 中间表示。Provider Adapter 负责把中间表示转换为某个工具的语法、参数和调用方式。

Provider Adapter 不得改变：

- 主体身份；
- 镜头意图；
- 连续性约束；
- Provenance 链；
- Gate 结论。

## 3. 通用工作流路由

入口先判断创作目标，而不是默认进入完整电影流程：

| 目标 | 最小路径 |
|---|---|
| 从零创意 | premise → logline → characters → structure |
| 已有剧本 | script analysis → revision → production preparation |
| 短视频试片 | hook → beat map → keyframes → motion prompt → end-frame check |
| 场景资产 | shot demand matrix → location identity → shot-bound derivatives |
| 风格探索 | style profile → controlled variants → human select |
| 单镜头 Prompt | Shot Spec → references → constraints → handoff prompt |

路由必须允许用户在达到目标后停止，不得为了完整性强制进入后续阶段。

## 4. 资产与镜头的通用契约

### 4.1 资产类型

资产类型是可扩展标签，不是固定生产清单：

- identity reference；
- location reference；
- prop reference；
- state reference；
- lighting reference；
- composition reference；
- motion reference；
- shot keyframe。

一个文件可以承担多个标签，但每个用途必须明确记录。

### 4.2 镜头驱动原则

- 先从 Shot Spec 提取可见需求，再决定是否需要资产。
- 每个派生资产至少绑定一个 `shot_id` 或 `generation_unit_id`。
- 没有镜头需求的泛化动作测试不是默认 Gate。
- 只有 Prompt 和基础引用不足以控制关键可见事实时，才生成状态图、姿态图或视觉控制图。
- Stress Test 只在存在明确风险、且基础引用和 Prompt 无法消除风险时触发。

### 4.3 参考图责任分级

每张参考图必须声明主要责任：身份、空间、道具、光线、构图、动作、风格或关键帧。探索性四宫格、六宫格或九宫格默认只能作为探索证据，不能自动视为严格几何连续性证据。

## 5. 可见事实质量模型

质量评估不使用单一“好看/不好看”结论，而按镜头需求检查：

1. 身份是否可辨认；
2. 主体与场景是否处于同一空间；
3. 比例、接触、遮挡、焦点和光线是否可信；
4. 动作是否可读且符合镜头意图；
5. 风格是否符合 Style Profile；
6. 与前后镜头的方向、位置和状态是否连续；
7. 是否存在足以阻止交付的 Provider 或生成风险。

“相对最佳”只能表示候选选择，不能替代人工批准或 Gate 通过。

## 6. 失败诊断顺序

当结果不理想时，按以下顺序定位，不要直接重写全部 Prompt：

1. Shot Spec 是否清楚；
2. 参考图的责任是否混用；
3. 主体与场景的空间关系是否可观察；
4. 身份锚点是否不足；
5. 风格变量是否漂移；
6. 运镜、动作和光线是否超出当前方法的控制能力；
7. 是否需要换参考、拆镜头或增加专用状态资产；
8. 最后才考虑更换 Provider 或调整参数。

## 7. 验证矩阵

通用化不能只在一个电影项目中验证。至少准备五个最小案例：

- 写实怀旧叙事短片；
- 中国古画或壁画活化；
- 现代产品广告；
- 动画或插画风格；
- 纪录片或历史照片活化。

每个案例验证：

- 路由是否正确；
- 是否产生多余资产；
- Prompt 是否保留风格与项目边界；
- 资产是否可追溯；
- 是否发生项目规则泄漏；
- 是否能在没有 Provider 专属知识时完成外部交接。

## 8. 实施顺序

### P0：边界清理

- 从活跃 Skill、API、测试和文档中清理 Provider 执行与证据责任；
- 建立 Project Profile 和 Style Profile 的最小表示；
- 把项目专用规则移出 Core；
- 保留现有 Provenance、Continuity、Select、Shot Spec 和 Gate 语义。

### P1：工作流增强

- 增加创作目标路由；
- 增加参考图责任标签；
- 增加失败诊断矩阵；
- 增加 Provider-neutral Prompt 中间表示；
- 建立五类项目、多风格回归案例。

### P2：按真实需求扩展

- 平台适配；
- 风格分析；
- 自动风险预测；
- 多人协作与版本审计；
- Provider Adapter 集合。

P2 不应在 P0、P1 的真实创作者验证前大规模开发。

## 9. 受理标准

这份规范只有在以下证据具备后才可转为实施基线：

- 至少一个空白项目完成创作者流程试用；
- 至少三个不同媒介或风格案例完成路由验证；
- 没有发现项目 Canon 泄漏到 Core；
- Provider-neutral 输出可被外部工具或人工直接使用；
- 现有确定性测试、打包和清洁提取仍通过；
- 人工确认、Gate 和 Provenance 的语义未被削弱。

在此之前，本文件是设计稿，不是发布承诺。
