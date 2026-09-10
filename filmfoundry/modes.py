"""Deterministic work-mode routing for the creator-to-production boundary."""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal


MODE_CREATIVE = "CREATIVE"
MODE_COMMIT = "COMMIT"
MODE_PRODUCTION = "PRODUCTION"
MODE_GATE = "GATE"
WorkMode = Literal["CREATIVE", "COMMIT", "PRODUCTION", "GATE"]

_MODE_ALIASES: dict[str, WorkMode] = {
    "creative": MODE_CREATIVE,
    "创作": MODE_CREATIVE,
    "commit": MODE_COMMIT,
    "确认": MODE_COMMIT,
    "production": MODE_PRODUCTION,
    "生产": MODE_PRODUCTION,
    "gate": MODE_GATE,
    "验收": MODE_GATE,
}

_SCRIPT_DEVELOPMENT_ACTION_RE = re.compile(
    r"(?:写|创作|开发|完善|修改|修订|分析|重写|构思|塑造).{0,20}(?:故事|剧本|初稿|草稿|梗概|大纲|情节|人物|角色)|"
    r"(?:故事|剧本|初稿|草稿|梗概|大纲|情节|人物|角色).{0,20}(?:开发|完善|修改|修订|分析|重写)|"
    r"\b(?:develop|write|create|revise|rewrite|analyze|analyse|edit|improve|finish)\b.{0,24}"
    r"\b(?:story|script|screenplay|outline|premise|logline|plot|draft|character)\b",
    re.IGNORECASE,
)
_STRONG_SCRIPT_DEVELOPMENT_ACTION_RE = re.compile(
    r"(?:写|创作|开发|完善|修改|修订|分析|重写|构思)(?:一下)?(?:这个|这份|我的)?"
    r"(?:故事|剧本|初稿|草稿|梗概|大纲|情节|人物弧光|人物动机|角色弧光)|"
    r"\b(?:develop|write|create|revise|rewrite|analyze|analyse|edit|improve|finish)\s+"
    r"(?:(?:a|an|the|this|my|our)\s+)?"
    r"(?:story|script|screenplay|outline|premise|logline|plot|"
    r"(?:(?:rough|first|existing)\s+)?draft|character arc|character motivation|character backstory)\b",
    re.IGNORECASE,
)
_CREATOR_SCRIPT_RE = re.compile(
    r"从零|空白|模糊想法|"
    r"(?:我)?(?:有|只有|目前有).{0,8}(?:想法|创意|故事片段|种子|梗概|大纲|初稿|草稿|剧本)|"
    r"人物(?:弧光|动机|塑造|小传|开发)|"
    r"\b(?:i have|i've got|start(?:ing)? with)\b.{0,24}\b(?:idea|seed|fragment|premise|outline|draft|story|script|screenplay)\b|"
    r"\b(?:hooks?|blank (?:idea|page)|story fragment|character arc|character motivation)\b|"
    r"\b(?:story|script|screenplay|outline|premise|logline|plot|draft|character)\b.{0,24}"
    r"\b(?:development|revision|rewrite|analysis)\b",
    re.IGNORECASE,
)
_VISUAL_ARTIFACT_RE = re.compile(
    r"故事板|分镜|角色(?:参考|视觉|设定图)|参考图|提示词|提示语|"
    r"\b(?:storyboard|character reference|reference image|visual reference|shot plan|shot spec|asset|prompt)\b",
    re.IGNORECASE,
)
_EXISTING_SCRIPT_RE = re.compile(
    r"已有(?:剧本|初稿|草稿)|现有(?:剧本|初稿|草稿)|"
    r"(?:分析|修改|修订|重写)(?:这个|这份|我的)?(?:剧本|初稿|草稿)|"
    r"\bexisting\s+(?:script|screenplay|draft)\b|\b(?:script|screenplay)\s+draft\b|"
    r"\b(?:analyze|analyse|revise|rewrite)\s+(?:(?:this|my|the|an)\s+)?"
    r"(?:(?:existing|rough|first)\s+)?(?:script|screenplay|draft)\b",
    re.IGNORECASE,
)


def _is_creator_script_request(request: str) -> bool:
    if _VISUAL_ARTIFACT_RE.search(request) and not (
        _STRONG_SCRIPT_DEVELOPMENT_ACTION_RE.search(request) or _CREATOR_SCRIPT_RE.search(request)
    ):
        return False
    return bool(_SCRIPT_DEVELOPMENT_ACTION_RE.search(request) or _CREATOR_SCRIPT_RE.search(request))

_PROFILE_REFERENCES: dict[WorkMode, tuple[str, ...]] = {
    MODE_CREATIVE: (
        "references/40-work-modes.md",
    ),
    MODE_COMMIT: (
        "references/01-creative-brief.md",
        "references/02-story-breakdown.md",
        "references/39-script-facts-and-emotion.md",
    ),
    MODE_PRODUCTION: (
        "references/06-shot-engineering.md",
        "references/08-video-spec.md",
        "references/09-prompt-compiler.md",
        "references/19-adaptive-spec.md",
        "references/23-controllability-budget.md",
    ),
    MODE_GATE: (
        "references/13-qc.md",
        "references/14-failure-recovery.md",
        "references/15-runtime-contract.md",
        "references/16-model-evidence.md",
        "references/29-capability-scoped-model-gates.md",
        "references/30-edit-timeline-contract.md",
    ),
}

_OUTPUT_LABELS: dict[WorkMode, tuple[str, ...]] = {
    MODE_CREATIVE: ("CREATIVE_DRAFT", "ASSUMPTION", "DEFERRED_CHECK", "HARD_CANON_CONFLICT"),
    MODE_COMMIT: ("COMMIT_SUMMARY", "CANON_CONFLICT", "DEFERRED_CHECK"),
    MODE_PRODUCTION: ("PRODUCTION_ARTIFACT", "VALIDATION_RESULT", "DEFERRED_CHECK"),
    MODE_GATE: ("GATE_RESULT", "BLOCKER", "ACTION"),
}

_VALIDATORS: dict[WorkMode, tuple[str, ...]] = {
    MODE_CREATIVE: (),
    MODE_COMMIT: ("canon-conflict",),
    MODE_PRODUCTION: ("runtime", "state", "asset", "dependency"),
    MODE_GATE: ("runtime", "state", "asset", "dependency", "provider-smoke", "media-audit"),
}


@dataclass(frozen=True)
class ModeDecision:
    """The minimum execution contract selected for one user request."""

    mode: WorkMode
    reason: str
    references: tuple[str, ...]
    validators: tuple[str, ...]
    output_labels: tuple[str, ...]
    run_full_validation: bool
    allow_provider_calls: bool
    allow_source_writes: bool


def _normalize_mode(value: str | None) -> WorkMode | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    try:
        return _MODE_ALIASES[normalized]
    except KeyError as exc:
        raise ValueError(f"unsupported work mode: {value}") from exc


def reference_profile(mode: WorkMode) -> tuple[str, ...]:
    """Return the immutable minimum reference set for a work mode."""
    if mode not in _PROFILE_REFERENCES:
        raise ValueError(f"unsupported work mode: {mode}")
    return _PROFILE_REFERENCES[mode]


def mode_output_contract(mode: WorkMode) -> tuple[str, ...]:
    """Return labels that keep drafts, facts, and gate results distinguishable."""
    if mode not in _OUTPUT_LABELS:
        raise ValueError(f"unsupported work mode: {mode}")
    return _OUTPUT_LABELS[mode]


def _references_for_request(mode: WorkMode, request: str) -> tuple[str, ...]:
    references = list(reference_profile(mode))
    normalized = request.lower()
    if mode == MODE_CREATIVE and _is_creator_script_request(request):
        references.insert(0, "references/41-creator-first-script-workflow.md")
    if mode in {MODE_CREATIVE, MODE_COMMIT} and _EXISTING_SCRIPT_RE.search(request):
        if "references/39-script-facts-and-emotion.md" not in references:
            references.append("references/39-script-facts-and-emotion.md")
    if mode == MODE_CREATIVE and any(
        token in normalized for token in ("商业", "变现", "系列", "commercial", "market", "monetiz", "series")
    ):
        references[0:0] = [
            "references/20-content-market-gate.md",
            "references/21-market-mvp.md",
        ]
    return tuple(dict.fromkeys(references))


def _detected_mode(request: str) -> tuple[WorkMode, str]:
    normalized = request.lower()
    if re.search(r"验收|发布|上线|ready|release|audit|全量校验|是否能生成|can (?:we|i) generate", normalized):
        return MODE_GATE, "readiness or release language requests a complete gate"
    if re.search(r"定下来|写入.*剧本|转成正式|敲定|commit|lock|finali[sz]e|make official", normalized):
        return MODE_COMMIT, "the user is committing a selected creative direction"
    if re.search(r"payload|编译|shot spec|生产.*(?:prompt|提示词)|可用.*(?:prompt|提示词)", normalized):
        return MODE_PRODUCTION, "the user requests a production artifact or compiled payload"
    return MODE_CREATIVE, "the request is exploratory or does not ask for production readiness"


def route_request(request: str, *, explicit_mode: str | None = None) -> ModeDecision:
    """Select the lightest safe mode without performing validation or I/O."""
    if not isinstance(request, str):
        raise TypeError("request must be a string")
    mode = _normalize_mode(explicit_mode)
    reason = "explicit mode selected by the user"
    if mode is None:
        mode, reason = _detected_mode(request)
    return ModeDecision(
        mode=mode,
        reason=reason,
        references=_references_for_request(mode, request),
        validators=_VALIDATORS[mode],
        output_labels=mode_output_contract(mode),
        run_full_validation=mode == MODE_GATE,
        allow_provider_calls=mode == MODE_GATE,
        allow_source_writes=False,
    )


__all__ = [
    "MODE_COMMIT",
    "MODE_CREATIVE",
    "MODE_GATE",
    "MODE_PRODUCTION",
    "ModeDecision",
    "WorkMode",
    "mode_output_contract",
    "reference_profile",
    "route_request",
]
