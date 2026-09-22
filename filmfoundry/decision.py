"""Human-facing decision projections derived from the Creator Read Model.

The decision brief is a presentation layer. It never creates Canon facts and
does not replace the Creator Snapshot or navigation contracts.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .creator_read_model import CreatorReadModel


DecisionStatus = Literal["ACTION_REQUIRED", "READY_FOR_REVIEW", "EVIDENCE_INCOMPLETE"]


@dataclass(frozen=True)
class CreatorDecisionOption:
    option_id: str
    label: str
    consequence: str
    recommended: bool


@dataclass(frozen=True)
class CreatorDecisionBrief:
    """Compact decision projection for a human reviewer.

    This view is deliberately explicit about whether it has a derived action
    or only enough evidence to request human review. It must not imply that a
    technical validation result is creative approval.
    """

    schema_version: Literal["creator-decision-brief.v1"]
    project_id: str
    phase: str
    status: DecisionStatus
    question: str
    recommendation: str
    options: tuple[CreatorDecisionOption, ...]
    locked_facts: tuple[str, ...]
    open_risks: tuple[str, ...]
    next_action: str
    evidence_refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "phase": self.phase,
            "status": self.status,
            "question": self.question,
            "recommendation": self.recommendation,
            "options": [
                {
                    "option_id": option.option_id,
                    "label": option.label,
                    "consequence": option.consequence,
                    "recommended": option.recommended,
                }
                for option in self.options
            ],
            "locked_facts": list(self.locked_facts),
            "open_risks": list(self.open_risks),
            "next_action": self.next_action,
            "evidence_refs": list(self.evidence_refs),
        }


def _metric_facts(model: CreatorReadModel) -> tuple[str, ...]:
    metric_labels = {
        "assets.total": "资产数量",
        "production_units.total": "制作单元数量",
        "character_media.missing": "缺失的角色媒体数量",
        "generation.total": "已生成单元数量",
        "select.total": "已选片数量",
    }
    facts: list[str] = [
        f"项目阶段：{model.snapshot.overview.phase}",
        f"当前权威：{model.snapshot.overview.current_authority}",
    ]
    if model.snapshot.overview.historical_authority:
        facts.append(f"存在历史参考：{model.snapshot.overview.historical_authority}")
    for metric in model.snapshot.metrics:
        if metric.value is not None and metric.data_status == "KNOWN":
            facts.append(f"{metric_labels.get(metric.metric_id, metric.metric_id)}：{metric.value}")
    return tuple(facts)


def _risk_reasons(model: CreatorReadModel) -> tuple[str, ...]:
    risks = [
        f"{blocker.blocker_id}：{blocker.reason}"
        for blocker in model.snapshot.blockers
    ]
    risks.extend(
        f"{conflict.conflict_id}：{conflict.reason}"
        for conflict in model.snapshot.conflicts
    )
    risks.extend(
        f"{coverage.coverage_id}：{coverage.reason or '来源覆盖不完整'}"
        for coverage in model.snapshot.coverage
        if coverage.data_status != "KNOWN"
    )
    return tuple(dict.fromkeys(risks))


def _evidence_refs(model: CreatorReadModel) -> tuple[str, ...]:
    refs: list[str] = []
    action = model.navigation.primary_action
    if action:
        refs.extend(ref.source_id for ref in action.provenance.source_refs)
    for blocker in model.snapshot.blockers:
        refs.extend(ref.source_id for ref in blocker.provenance.source_refs)
    for conflict in model.snapshot.conflicts:
        refs.extend(ref.source_id for ref in conflict.provenance.source_refs)
    return tuple(dict.fromkeys(refs))


def _action_summary(action: object) -> str:
    rule_id = getattr(action, "rule_id", None)
    entity_id = getattr(action, "entity_id", None) or "当前对象"
    if rule_id == "creator.navigation.lifecycle.next":
        return f"镜头 {entity_id} 还没有完成进入下一制作阶段所需的前置条件"
    if rule_id == "creator.navigation.previous_observed_state":
        return f"镜头 {entity_id} 的连续性前置观察状态还没有记录"
    if rule_id == "creator.navigation.source_coverage":
        return f"来源 {entity_id} 目前不可读取或覆盖不完整"
    if rule_id == "creator.navigation.authority_conflict":
        return "当前权威来源与历史映射存在冲突"
    if rule_id == "creator.navigation.asset.media":
        return f"资产 {entity_id} 的媒体状态需要复核"
    return str(getattr(action, "reason", "当前动作需要复核"))


def _human_prerequisite(action: object) -> str:
    rule_id = getattr(action, "rule_id", None)
    if rule_id == "creator.navigation.lifecycle.next":
        return "完成下一制作阶段所需的前置检查"
    if rule_id == "creator.navigation.previous_observed_state":
        return "记录前一镜头的实际观察状态"
    if rule_id == "creator.navigation.source_coverage":
        return "让声明来源可读取并可解析"
    prerequisites = getattr(action, "prerequisites", ())
    return str(prerequisites[0]) if prerequisites else "解决当前首要问题"


def build_creator_decision_brief(model: CreatorReadModel) -> CreatorDecisionBrief:
    """Build a deterministic, evidence-bound decision view.

    The default options describe operational next steps only. Creative
    alternatives and their artistic trade-offs must be supplied by the
    creator-first workflow, never inferred from production metadata.
    """

    action = model.navigation.primary_action
    risks = _risk_reasons(model)
    evidence_incomplete = any(coverage.data_status != "KNOWN" for coverage in model.snapshot.coverage)
    if evidence_incomplete:
        question = "是否先补齐证据和来源，再批准进入下一阶段？"
        recommendation = "先补齐或解释未决证据；技术渲染通过不等于创作或外部媒体通过。"
        options = (
            CreatorDecisionOption(
                "RESOLVE_EVIDENCE",
                "补齐证据后再审",
                "保留当前事实边界，减少把 UNKNOWN 当成通过的风险。",
                True,
            ),
            CreatorDecisionOption(
                "HUMAN_REVIEW",
                "带着风险进入人工评审",
                "允许人明确接受风险，但不改变 Core 状态或来源事实。",
                False,
            ),
        )
        status: DecisionStatus = "EVIDENCE_INCOMPLETE"
        next_action = "resolve the listed evidence risks"
    elif action is not None:
        prerequisite = _human_prerequisite(action)
        summary = _action_summary(action)
        question = f"是否先处理当前首要问题：{summary}？"
        recommendation = f"先{prerequisite}，再继续其他并行工作。"
        options = (
            CreatorDecisionOption(
                "RESOLVE_PRIMARY",
                "处理当前首要问题",
                f"满足当前导航前置条件：{prerequisite}。",
                True,
            ),
            CreatorDecisionOption(
                "REVIEW_BOUNDARY",
                "交由来源所有者复核",
                f"保持当前状态不变；复核边界：{action.support_boundary}。",
                False,
            ),
        )
        status = "ACTION_REQUIRED"
        next_action = prerequisite
    elif risks:
        question = "是否先补齐证据和来源，再批准进入下一阶段？"
        recommendation = "先补齐或解释未决证据；技术渲染通过不等于创作或外部媒体通过。"
        options = (
            CreatorDecisionOption(
                "RESOLVE_EVIDENCE",
                "补齐证据后再审",
                "保留当前事实边界，减少把 UNKNOWN 当成通过的风险。",
                True,
            ),
            CreatorDecisionOption(
                "HUMAN_REVIEW",
                "带着风险进入人工评审",
                "允许人明确接受风险，但不改变 Core 状态或来源事实。",
                False,
            ),
        )
        status = "EVIDENCE_INCOMPLETE"
        next_action = "resolve the listed evidence risks"
    else:
        question = "是否批准当前快照进入下一阶段？"
        recommendation = "当前没有推导出的阻塞动作；请由创作者或决策者确认下一阶段。"
        options = (
            CreatorDecisionOption(
                "APPROVE_NEXT_STAGE",
                "批准进入下一阶段",
                "不改变已有事实，只推进到下一个已声明阶段。",
                True,
            ),
            CreatorDecisionOption(
                "HOLD_FOR_REVIEW",
                "保持当前阶段",
                "保留当前快照，等待额外创作判断或资料。",
                False,
            ),
        )
        status = "READY_FOR_REVIEW"
        next_action = "record the human decision before changing stage"

    return CreatorDecisionBrief(
        "creator-decision-brief.v1",
        model.snapshot.project_id,
        model.snapshot.overview.phase,
        status,
        question,
        recommendation,
        options,
        _metric_facts(model),
        risks,
        next_action,
        _evidence_refs(model),
    )


__all__ = [
    "CreatorDecisionBrief",
    "CreatorDecisionOption",
    "DecisionStatus",
    "build_creator_decision_brief",
]
