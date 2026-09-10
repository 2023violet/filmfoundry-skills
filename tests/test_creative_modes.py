from __future__ import annotations

from filmfoundry.modes import (
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
    assert "CREATIVE_DRAFT" in decision.output_labels
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
    assert "COMMIT_SUMMARY" in decision.output_labels


def test_production_prompt_request_loads_production_checks_only():
    decision = route_request("把这个镜头编译成可用的 provider payload")

    assert decision.mode == MODE_PRODUCTION
    assert decision.run_full_validation is False
    assert decision.allow_provider_calls is False
    assert set(decision.validators) == {"runtime", "state", "asset", "dependency"}
    assert "references/09-prompt-compiler.md" in decision.references


def test_release_readiness_routes_to_gate_mode():
    decision = route_request("这个项目现在是否 ready，可以发布验收吗？")

    assert decision.mode == MODE_GATE
    assert decision.run_full_validation is True
    assert decision.allow_provider_calls is True
    assert "provider-smoke" in decision.validators
    assert "media-audit" in decision.validators


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
    ):
        assert "references/41-creator-first-script-workflow.md" not in route_request(request).references

    market = route_request("Develop a commercial series story from a blank idea.")
    assert market.references[:3] == (
        "references/20-content-market-gate.md",
        "references/21-market-mvp.md",
        "references/41-creator-first-script-workflow.md",
    )
