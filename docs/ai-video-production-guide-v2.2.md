# AI 视频生产全流程指南（FilmFoundry v2.2）

FilmFoundry 管理生产事实、资产身份、Prompt、状态、证据和引用关系；图片、视频、声音生成以及 NLE 仍在外部工具完成。

## 每次创作的顺序

1. 从项目入口读取 Canon、Runtime 和支持矩阵。
2. 固化剧本文件哈希，创建 Script Analysis；明确事实来源，`INFERRED` 不得直接写入 Canon。
3. 创建 Production Ledger；每次生成、失败、重试、选择和 QC 都追加事件。
4. 运行 `ff requirements`，只为当前镜头准备被触发的工件。
5. 为复用角色建立面部近景、正面全身、背面全身；按风险补状态变体、去头全身和局部蒙版。
6. 有对白时建立 Voice Passport；有复杂空间时建立 Scene Topology、Spatial Map 和 Coverage Set。
7. 多场景或跨时间天气时建立 Look Bible 和 Palette/Lighting State。
8. 创建 Emotional Beat Map，标记叙事功能、情绪方向、音乐意图和对白密度。
9. 创建 Visual Control Plan 与 Shot Spec，运行结构校验和 Preflight。
10. 使用 `ff compile` 生成 Provider payload；检查输入哈希和能力快照。
11. 在外部 Provider 生成，保存原始设置、generation ID 和输出媒体。
12. 回填 Generation、Select、QC 和 Observed State；失败重试必须写明改变的变量。
13. 以 Prompt Compliance、Identity、Spatial、Scale、Physics、Camera、Editability、Aesthetic 分层复核。
14. 覆盖 Edit Timeline，最后处理音频、字幕、编码、交付和发布证据。

## 什么时候必须做什么

- 账本、Registry、稳定 ID、哈希、引用和 QC：全项目强制。
- 角色跨镜头复用、转身、全身或服装连续性：三视图包必需。
- 多 Beat、对白、旁白或音乐节点：Emotional Beat Map 必需。
- 多人走位、追逐、反打或跨镜头空间连续：Scene Topology/Spatial Map 必需。
- 室内跨房间行动：Floor Plan 信息必需。
- 多场景、时间或天气变化：Look Bible 必需。
- 巨物、比例差异或材料运动：Scale Reference/Physics Cue 必需。
- 位置经常漂移或多人复杂站位：Previs 推荐，是否保留进最终剪辑由人工决定。

灰色背景、3/4 场景、去头全身图、FOV 数字和物理描述是可验证的控制策略或实验变量，不是模型质量保证。

## 常用命令

```text
ff init --root <path>
ff requirements --policy <policy.json> --facts <facts.json> --artifacts <artifacts.json> --format json
ff validate --root <path> --stage all
ff compile --prompt <prompt.md> --visual-control <plan.json> --provider <provider> --out <payload.txt>
ff ledger validate --ledger <ledger.json>
ff audit --root <path> --kind all
```

遇到生成失败，先在账本记录失败原因和输入哈希，再只改变一个主要变量。不要把一次成功升级为默认 Provider 能力；证据按 `UNVERIFIED → OBSERVED_ONCE → REPEATED → PROJECT_VERIFIED` 晋级。
