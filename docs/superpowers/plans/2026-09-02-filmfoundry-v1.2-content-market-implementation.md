# FilmFoundry Skills v1.2.0 Content-Market-First Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the single `generative-film-production` skill so commercial AI-video projects validate content-market fit and cheap MVP evidence before expensive scale, while adding partial-select, source-vs-edit-duration, eyeline-critical, and model-observation contracts learned from real Pilot production.

**Architecture:** Keep one skill. Add a project-level Content Market Gate and MVP loop in front of the existing production engine; leave the generation-unit lifecycle intact. Extend deterministic contracts only where runtime truth is valuable: market gate, v1.2 shot duration/eyeline rules, partial Selects, and model behavior observations.

**Tech Stack:** Markdown Agent Skill files; Python 3.11+ standard library validators; JSON/CSV runtime artifacts; pytest.

**Spec:** `docs/superpowers/specs/2026-09-02-filmfoundry-v1.2-content-market-design.md`

## Global Constraints

- Primary skill remains exactly `generative-film-production`.
- Commercial/creator growth work uses `CONTENT MARKET GATE → MVP → Production`; non-market work may bypass only with an explicit reason.
- Do not hard-code volatile platform payout or algorithm thresholds.
- `PARTIAL_SELECT` is a disposition, never a generation-unit runtime state.
- `OBSERVED_ONCE` provider evidence must not become default adapter behavior.
- v1.1 runtime manifests/specs remain accepted.
- Python validators use standard library only.
- New production behavior follows TDD: failing test first, then minimal implementation.

---

### Task 1: Content Market Gate Contract

**Files:**
- Create: `tests/test_v120_content_market_gate.py`
- Create: `skills/generative-film-production/scripts/validate_content_market_gate.py`
- Create: `skills/generative-film-production/templates/content-market-gate.example.json`
- Create: `skills/generative-film-production/templates/content-market-gate.md`
- Create: `skills/generative-film-production/templates/market-mvp-report.md`
- Modify: `skills/generative-film-production/scripts/validate_project_runtime.py`
- Modify: `skills/generative-film-production/templates/project-runtime.example.json`

**Interfaces:**
- Consumes: project goal and market-gate JSON.
- Produces: `validate_content_market_gate(data) -> list[str]`; v1.2 runtime commercial-goal gate enforcement.

- [ ] Write tests for required market questions, explicit bypass, `MVP_ONLY`, and `PRODUCTION_APPROVED` evidence rules.
- [ ] Run the new tests and verify they fail because the validator does not exist / v1.2 runtime behavior is absent.
- [ ] Implement the minimal market-gate validator and v1.2 runtime integration.
- [ ] Add published v1.2 example/template files.
- [ ] Run focused tests and the legacy runtime tests; confirm compatibility.

### Task 2: v1.2 Shot Controllability Contract

**Files:**
- Create: `tests/test_v120_shot_spec.py`
- Modify: `skills/generative-film-production/scripts/validate_shot_spec.py`
- Modify: `skills/generative-film-production/templates/shot-spec.example.json`
- Modify: `skills/generative-film-production/references/19-adaptive-spec.md`
- Modify: `skills/generative-film-production/references/17-keyframe-engineering.md`

**Interfaces:**
- Produces v1.2 fields `generation_duration_seconds`, `edit_target_duration_seconds`, `eyeline_critical` conditional checks.

- [ ] Write failing tests for positive numeric durations, edit duration <= generation duration, and eyeline-critical requirements.
- [ ] Run focused tests and verify expected failure.
- [ ] Implement minimal adaptive validation while preserving v1.1 behavior.
- [ ] Publish a v1.2 example spec.
- [ ] Run focused plus legacy shot-spec tests.

### Task 3: Partial Select / Clip Salvage Contract

**Files:**
- Create: `tests/test_v120_partial_select.py`
- Create: `skills/generative-film-production/scripts/validate_selects_log.py`
- Modify: `skills/generative-film-production/scripts/validate_production_state.py`
- Modify: `skills/generative-film-production/templates/selects-log.csv`
- Modify: `skills/generative-film-production/templates/production-state.example.json`
- Modify: `skills/generative-film-production/templates/qc-report.md`

**Interfaces:**
- Produces: `validate_select_rows(rows) -> list[str]`; selection object with `FULL_SELECT|PARTIAL_SELECT` and time range.

- [ ] Write failing tests for valid partial range, invalid ranges, full-select constraints, and production-state selected range requirements.
- [ ] Run tests and verify RED.
- [ ] Implement validator and production-state support without adding a runtime state.
- [ ] Update published templates.
- [ ] Run focused tests and legacy production-state/runtime tests.

### Task 4: Model Behavior Observation Evidence

**Files:**
- Create: `tests/test_v120_model_observations.py`
- Modify: `skills/generative-film-production/scripts/validate_model_profile.py`
- Modify: `skills/generative-film-production/templates/model-profile.example.json`
- Modify: `skills/generative-film-production/templates/model-profile.md`
- Modify: `skills/generative-film-production/references/16-model-evidence.md`

**Interfaces:**
- Produces validated `behavior_observations` with evidence level and source generation IDs.

- [ ] Write failing tests that require source IDs above UNVERIFIED and reject unknown evidence levels.
- [ ] Verify RED.
- [ ] Implement minimal validation and example observations structure.
- [ ] Run focused and legacy model-profile/runtime tests.

### Task 5: Market-First and Controllability Guidance

**Files:**
- Create: `skills/generative-film-production/references/20-content-market-gate.md`
- Create: `skills/generative-film-production/references/21-market-mvp.md`
- Create: `skills/generative-film-production/references/22-ai-native-content-design.md`
- Create: `skills/generative-film-production/references/23-controllability-budget.md`
- Modify: `skills/generative-film-production/SKILL.md`
- Modify: `skills/generative-film-production/references/00-production-philosophy.md`
- Modify: `skills/generative-film-production/references/01-creative-brief.md`
- Modify: `skills/generative-film-production/references/02-story-breakdown.md`
- Modify: `skills/generative-film-production/references/08-video-spec.md`
- Modify: `skills/generative-film-production/references/09-prompt-compiler.md`
- Modify: `skills/generative-film-production/references/10-generation-loop.md`
- Modify: `skills/generative-film-production/references/11-editing.md`
- Modify: `skills/generative-film-production/references/13-qc.md`
- Modify: `skills/generative-film-production/references/14-failure-recovery.md`
- Modify: `skills/generative-film-production/references/adapters/minimax-h3.md`

**Interfaces:**
- Skill routes commercial projects to Gate/MVP before costly production; provider guidance treats generated duration as source material when appropriate and permits traceable partial selection.

- [ ] Update guidance to implement the approved architecture and YAGNI market MVP behavior.
- [ ] Add explicit content-market questions and AI-native short-form production-fit heuristics without hard-coding genre profitability.
- [ ] Add prompt-control budget and “best contiguous segment” guidance.
- [ ] Add QC separation: prompt compliance, narrative fitness, identity/continuity, visual quality, editability.
- [ ] Add eyeline checks before aesthetics.

### Task 6: v1.2 Agentic Evals and Repository Contracts

**Files:**
- Create: `tests/test_v120_repo_contract.py`
- Modify: `tests/test_eval_schema.py`
- Modify: `evals/evals.json`
- Add: `evals/fixtures/baseline/E19...E26...md`
- Add: `evals/fixtures/golden/E19...E26...md`
- Modify: `evals/README.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `pyproject.toml`

**Interfaces:**
- Repository metadata publishes version 1.2.0 and 26 eval cases.

- [ ] Write failing repository-contract tests for new references/scripts/templates/version and 26 eval cases.
- [ ] Verify RED.
- [ ] Add eight adversarial evals: market gate, MVP restraint, no-monetization MVP-only, partial salvage, over-control, eyeline-critical, one-observation overgeneralization, and 30-episode engine.
- [ ] Add authored baseline/golden fixtures and update metadata/docs.
- [ ] Run eval schema/scoring and repository-contract tests.

### Task 7: Full Verification and Release Package

**Files:**
- Create: `docs/reports/2026-09-02-filmfoundry-v1.2.0-verification.md`
- Create archive: `/mnt/data/filmfoundry-skills-v1.2.0.zip`

**Interfaces:**
- Produces final independently extractable delivery archive.

- [ ] Run `python -m pytest -q` fresh and record exact pass count.
- [ ] Run published validators against all v1.2 example files.
- [ ] Run `python scripts/validate_evals.py evals/evals.json`.
- [ ] Scan for stale `1.1.0` metadata where v1.2.0 is required and for placeholder markers.
- [ ] Write verification report with evidence boundary: static/TDD verified, provider obedience not fabricated.
- [ ] Create zip with one top-level `filmfoundry-skills/` directory.
- [ ] Extract the zip into a clean directory and rerun the full pytest suite and published validators from the extracted copy.
- [ ] Compare archive file list against source tree and report final checksum.
