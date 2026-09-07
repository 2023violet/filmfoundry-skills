# Production Ledger 与条件门禁

账本是追加式生产记录。资产、Prompt、Generation、Select、QC 和 Timeline 的每个状态变化都记录输入哈希、参数、成本状态、失败原因和决策。成本未知写 `UNKNOWN`，不估算。

使用 `ff requirements` 判断当前镜头需要的资料。基础契约始终必需；三视图、Beat Map、Topology、Look Bible、Scale、Physics 和 Previs 按复用、复杂度和连续性风险触发。选择 `NOT_APPLICABLE` 时必须写理由。
