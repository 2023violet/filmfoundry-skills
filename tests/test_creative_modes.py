from __future__ import annotations

from filmfoundry.modes import (
    LANE_FAST,
    LANE_RECOVERY,
    LANE_STANDARD,
    LANE_STRICT,
    MODE_COMMIT,
    MODE_CREATIVE,
    MODE_GATE,
    MODE_PRODUCTION,
    mode_output_contract,
    reference_profile,
    route_request,
)


def test_ambiguous_idea_routes_to_lightweight_creative_mode():
    decision = route_request("先给我三个 hook 和一个中文视频 prompt 草案，不要生成文件")

    assert decision.mode == MODE_CREATIVE
    assert decision.run_full_validation is False
    assert decision.allow_provider_calls is False
    assert decision.allow_source_writes is False
    assert decision.lane == LANE_FAST
    assert decision.risk_level == "R0"
    assert decision.budget.max_blocking_decisions == 1
    assert decision.budget.max_internal_steps == 4
    assert "CREATIVE_DRAFT" in decision.output_labels
    assert "OPEN" in decision.output_labels
    assert "DEFERRED" in decision.output_labels
    assert "NOOP" in decision.output_labels
    assert "DEFERRED_CHECK" in decision.output_labels
    assert "references/41-creator-first-script-workflow.md" in decision.references
    assert "references/00-production-philosophy.md" not in decision.references
    assert "references/22-ai-native-content-design.md" not in decision.references
    assert "references/09-prompt-compiler.md" not in decision.references


def test_explicit_commit_routes_without_provider_or_full_gate():
    decision = route_request("把这个方向定下来并写入正式剧本")

    assert decision.mode == MODE_COMMIT
    assert decision.run_full_validation is False
    assert decision.allow_provider_calls is False
    assert decision.allow_source_writes is False
    assert decision.lane == LANE_STANDARD
    assert decision.risk_level == "R1"
    assert decision.budget.max_internal_steps == 6
    assert "COMMIT_SUMMARY" in decision.output_labels


def test_production_prompt_request_loads_production_checks_only():
    decision = route_request("把这个镜头编译成可用的 provider payload")

    assert decision.mode == MODE_PRODUCTION
    assert decision.run_full_validation is False
    assert decision.allow_provider_calls is False
    assert set(decision.validators) == {"runtime", "state", "asset", "dependency"}
    assert "references/09-prompt-compiler.md" in decision.references
    assert decision.lane == LANE_STANDARD
    assert decision.risk_level == "R1"


def test_provider_neutral_handoff_request_enters_production_and_loads_human_decision_reference():
    decision = route_request("把第3个镜头整理成 Provider-neutral handoff，供导演评审")

    assert decision.mode == MODE_PRODUCTION
    assert decision.goal == "SINGLE_SHOT_PROMPT"
    assert "references/45-human-decision-layer.md" in decision.references


def test_release_readiness_routes_to_gate_mode():
    decision = route_request("这个项目现在是否 ready，可以发布验收吗？")

    assert decision.mode == MODE_GATE
    assert decision.run_full_validation is True
    assert decision.allow_provider_calls is False
    assert "provider-smoke" not in decision.validators
    assert "media-audit" not in decision.validators
    assert "handoff" in decision.validators
    assert decision.lane == LANE_STRICT
    assert decision.risk_level == "R2"
    assert decision.budget.max_internal_steps == 10


def test_explicit_strict_and_recovery_lanes_are_visible_in_routing():
    strict = route_request("请严格逐项检查这个创作方向", explicit_mode="creative")
    recovery = route_request("请做失败诊断并恢复这个 handoff", explicit_mode="production")

    assert strict.lane == LANE_STRICT
    assert strict.risk_level == "R2"
    assert recovery.lane == LANE_RECOVERY
    assert recovery.risk_level == "R1"
    assert recovery.budget.max_internal_steps == 5


def test_explicit_mode_is_deterministic_and_profiles_are_immutable_tuples():
    decision = route_request("随便说点什么", explicit_mode="creative")

    assert decision.mode == MODE_CREATIVE
    assert isinstance(reference_profile(MODE_CREATIVE), tuple)
    assert isinstance(mode_output_contract(MODE_GATE), tuple)


def test_creator_reference_selection_distinguishes_script_development_from_visual_artifacts():
    creator_cases = {
        "Please help me develop this outline.": False,
        "I have a seed and need help developing it.": False,
        "Please rewrite this screenplay.": True,
        "Please analyze this existing draft.": True,
        "Analyze my rough draft.": True,
        "请修改这份初稿。": True,
        "请修改这份初稿，然后做分镜。": True,
        "Rewrite my rough draft, then make a storyboard.": True,
        "Create a draft, then make a storyboard.": False,
        "我有一个想法，帮我完善一下。": False,
        "请帮我完善这个人物弧光。": False,
    }
    for request, needs_script_facts in creator_cases.items():
        decision = route_request(request)
        assert decision.mode == MODE_CREATIVE
        assert decision.references[0] == "references/41-creator-first-script-workflow.md"
        assert ("references/39-script-facts-and-emotion.md" in decision.references) is needs_script_facts

    for request in (
        "Design a character reference image.",
        "Create a storyboard for this approved scene.",
        "Rewrite this provider prompt draft.",
        "Rewrite this prompt draft.",
        "修改这份提示词草稿。",
        "请为这个已确认场景制作故事板。",
        "帮我做角色视觉创意和参考图。",
        "Design character reference images based on this approved script.",
        "Edit storyboard from script.",
        "Revise storyboard from script.",
        "Analyze storyboard from script.",
        "Improve shot plan from screenplay.",
        "Write a storyboard from the script.",
    ):
        assert "references/41-creator-first-script-workflow.md" not in route_request(request).references

    for request in (
        "Create a logline, then make a storyboard.",
        "Develop the character arc, then create a character reference image.",
    ):
        assert "references/41-creator-first-script-workflow.md" in route_request(request).references

    market = route_request("Develop a commercial series story from a blank idea.")
    assert market.references[:3] == (
        "references/20-content-market-gate.md",
        "references/21-market-mvp.md",
        "references/41-creator-first-script-workflow.md",
    )
