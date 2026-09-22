# Creator-First Script Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one small, complete, project-neutral workflow that can guide a creator from a blank idea through a reviewed script without loading production or provider machinery.

**Architecture:** Keep the first checkpoint instruction-first: one canonical workflow reference plus one optional Markdown workbook, selected by the existing Creative Mode router. Do not add a new Python state machine or schema unless the fresh-context trial proves that the conversational/workbook state is insufficient. Preserve the existing v3 structural foundations, and defer provider-surface removal to a separate plan after this creator path passes its evidence gate.

**Tech Stack:** Markdown Agent Skill, dependency-free Python 3.11, `argparse`, pytest, JSON eval metadata, PowerShell verification.

**Spec:** `CURRENT_HANDOFF.md` (sections “Decision”, “Product boundary”, “Required work before a release decision”, and “New-agent first action”)

## Global Constraints

- FilmFoundry Core remains general, creator-first, provider-neutral, and project-neutral.
- Do not add Wucheng names, paths, counts, fixtures, or status rules to Core.
- Do not restore `filmfoundry_v2`, old schemas, migration commands, or compatibility shims.
- Ask at most one creator-facing question per turn during the from-zero workflow.
- Load only the reference needed for the current creative decision; optional depth remains opt-in.
- Do not load Runtime, media, provider, model-evidence, prompt-compiler, or video-QC references before the creator asks to enter production preparation.
- Script creation must cover seed, logline, character engine, dramatic rules, structure, draft, and revision.
- Emotional mapping is conditional, not mandatory process tax.
- Static tests and authored fixtures prove contracts only; they do not prove creator speed, model obedience, script quality, or product acceptance.
- Keep version `3.0.0`; do not create or push a tag, GitHub Release, or publication artifact in this checkpoint.
- Preserve dirty worktrees and unrelated user changes. Stop before editing if the live worktree differs from the plan handoff state.

---

## Evidence Behind This Plan

- `skills/generative-film-production/references/01-creative-brief.md` is 11 lines and assumes a concept is already eligible for a brief.
- `skills/generative-film-production/references/02-story-breakdown.md` is 7 lines and starts by converting existing prose into shot candidates.
- `filmfoundry/modes.py` currently loads Production Philosophy and AI-native production design in the default Creative profile.
- `filmfoundry/modes.py` currently lets Gate Mode advertise `provider-smoke`, `media-audit`, and `allow_provider_calls=True`; that debt is real but is not removed in this plan.
- `evals/evals.json` contains 26 production-oriented single-turn cases and no complete blank-idea script journey.
- Building the current Creator Read Model against the repository’s `empty-project` fixture yields no navigation actions and only production-oriented unknown metrics. The renderer is therefore not a substitute for a creator workflow.
- The current deterministic baseline is 299 passing tests at commit `ea2885d74338c847dd54e5f9f3f392c131aee2ca`.

## File Structure

**Create**

- `skills/generative-film-production/references/41-creator-first-script-workflow.md` — the canonical multi-turn creative process and gates.
- `skills/generative-film-production/templates/script-development-workbook.md` — optional durable state for a creator who wants a saved artifact.
- `tests/test_creator_first_script_workflow.py` — static and routing contracts for the new entry path.
- `evals/creator-first-trial-protocol.md` — pre-registered fresh-context procedure and human acceptance rubric.
- `evals/fixtures/baseline/E27-from-zero-script-entry.md` — deliberately weak authored scorer fixture.
- `evals/fixtures/golden/E27-from-zero-script-entry.md` — authored contract example, explicitly not benchmark evidence.
- `docs/reports/2026-09-10-creator-first-fresh-context-trial.md` — actual trial transcript summary and evidence; create only after the trial runs.

**Modify**

- `skills/generative-film-production/SKILL.md` — make blank-idea script creation the first creative route.
- `skills/generative-film-production/references/01-creative-brief.md` — accept a creator-approved seed/logline rather than assuming production eligibility.
- `skills/generative-film-production/references/02-story-breakdown.md` — separate story structure from later shot engineering.
- `skills/generative-film-production/references/40-work-modes.md` — define the creator workflow as Creative Mode’s default script path.
- `skills/generative-film-production/templates/creative-brief.md` — capture dramatic intent before production fields.
- `filmfoundry/modes.py` — route blank-idea/story/script requests to the new workflow with a minimal reference set.
- `tests/test_creative_modes.py` — protect the minimal routing behavior.
- `tests/test_skill_contract.py` — require the new reference/template and creator-first entry language.
- `evals/evals.json` — add one single-turn entry guardrail without presenting it as a multi-turn benchmark.
- `tests/test_eval_schema.py` — update the exact eval count and validator-output assertion from 26 to 27.
- `evals/README.md` — distinguish the new authored guardrail from the fresh-context multi-turn trial.
- `README.md` — describe the implemented checkpoint without claiming release readiness.
- `docs/README.md` — index the creator workflow and trial protocol as current user/evidence material.
- `docs/filmfoundry-v3.md` — add the creator entry before the technical production guide.
- `docs/ai-video-production-guide-zh.md` — point blank-idea users to the creator workflow; retain it as production-stage guidance.
- `CHANGELOG.md` — record the creator-first checkpoint under Unreleased.
- `pyproject.toml` — replace the stale “Production-oriented” description with the creator-first product boundary.
- `tests/test_repo_metadata.py` — lock the revised package description and the still-paused release status.

**Explicitly untouched in this plan**

- Provider adapters, provider evidence, generation/video schemas, lifecycle truncation, CLI `compile`, provider-specific references/scripts, and video-QC removal. These require a separate keep/generalize/delete plan after the creator workflow trial.
- `filmfoundry/creator_read_model.py` and renderer code. The new creator path must work before another dashboard expansion is considered.

---

### Task 1: Lock the creator-first contract with failing tests

**Files:**

- Create: `tests/test_creator_first_script_workflow.py`
- Modify: `tests/test_creative_modes.py`
- Modify: `tests/test_skill_contract.py`

**Interfaces:**

- Consumes: `filmfoundry.modes.route_request(request: str, explicit_mode: str | None = None) -> ModeDecision`
- Produces: a static contract for `references/41-creator-first-script-workflow.md`, `templates/script-development-workbook.md`, and the minimal blank-script reference profile.

- [ ] **Step 1: Confirm the implementation worktree is safe**

Run:

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

Expected: `main`, no worktree entries, and both revisions equal the reviewed handoff revision or a later explicitly accepted revision. If not, preserve the worktree and re-evaluate this plan against the live state without resetting or cleaning.

- [ ] **Step 2: Create the failing workflow contract tests**

Create `tests/test_creator_first_script_workflow.py` with:

```python
from pathlib import Path

from filmfoundry.modes import MODE_CREATIVE, route_request


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "generative-film-production"
WORKFLOW = SKILL / "references" / "41-creator-first-script-workflow.md"
WORKBOOK = SKILL / "templates" / "script-development-workbook.md"


def test_blank_idea_routes_to_creator_workflow_without_production_references():
    decision = route_request("我只有一个模糊想法，请从零带我完成一个短片剧本")

    assert decision.mode == MODE_CREATIVE
    assert decision.references[0] == "references/41-creator-first-script-workflow.md"
    assert "references/40-work-modes.md" in decision.references
    forbidden = ("video-spec", "prompt-compiler", "model-evidence", "runtime-contract")
    assert not any(token in reference for reference in decision.references for token in forbidden)
    assert decision.validators == ()
    assert decision.allow_provider_calls is False
    assert decision.allow_source_writes is False


def test_creator_workflow_defines_the_complete_path_and_interaction_limits():
    text = WORKFLOW.read_text(encoding="utf-8")
    lower = text.lower()

    for stage in (
        "SEED_ACCEPTED",
        "LOGLINE_ACCEPTED",
        "CHARACTER_ENGINE_ACCEPTED",
        "DRAMATIC_RULES_ACCEPTED",
        "STRUCTURE_ACCEPTED",
        "DRAFT_ACCEPTED",
        "REVISION_ACCEPTED",
    ):
        assert stage in text
    assert "one question per turn" in lower
    assert "optional depth" in lower
    assert "fresh-context" in lower


def test_optional_workbook_matches_the_creator_workflow_gates():
    text = WORKBOOK.read_text(encoding="utf-8")

    for heading in (
        "## Seed",
        "## Logline",
        "## Character engine",
        "## Dramatic rules",
        "## Structure",
        "## Draft",
        "## Revision",
    ):
        assert heading in text
    assert "Creator decision" in text
    assert "Open question" in text
```

- [ ] **Step 3: Extend existing tests without adding duplicate test cases**

In `test_ambiguous_idea_routes_to_lightweight_creative_mode()` in `tests/test_creative_modes.py`, add:

```python
assert "references/41-creator-first-script-workflow.md" in decision.references
assert "references/00-production-philosophy.md" not in decision.references
assert "references/22-ai-native-content-design.md" not in decision.references
```

In `REQUIRED_REFERENCES` and `REQUIRED_TEMPLATES` in `tests/test_skill_contract.py`, add:

```python
"references/41-creator-first-script-workflow.md",
```

and:

```python
"templates/script-development-workbook.md",
```

In `test_root_skill_stays_compact_and_routes_by_stage()`, add `"Creator-first script workflow"` to the required tokens.

- [ ] **Step 4: Run the focused tests and verify the intended red state**

Run:

```powershell
python -m pytest -q tests/test_creator_first_script_workflow.py tests/test_creative_modes.py tests/test_skill_contract.py
```

Expected: failures for the missing reference/template, missing root-skill route language, and current production-heavy Creative reference profile. Any unrelated failure must be investigated before continuing.

- [ ] **Step 5: Commit only the contract tests**

```powershell
git add tests/test_creator_first_script_workflow.py tests/test_creative_modes.py tests/test_skill_contract.py
git commit -m "test: define creator-first script workflow contract"
```

---

### Task 2: Write the smallest complete creator workflow

**Files:**

- Create: `skills/generative-film-production/references/41-creator-first-script-workflow.md`
- Create: `skills/generative-film-production/templates/script-development-workbook.md`
- Modify: `skills/generative-film-production/references/01-creative-brief.md`
- Modify: `skills/generative-film-production/references/02-story-breakdown.md`
- Modify: `skills/generative-film-production/templates/creative-brief.md`

**Interfaces:**

- Consumes: Creative/Commit separation from `references/40-work-modes.md`.
- Produces: a human-readable stage sequence and optional saved workbook; no machine schema and no source mutation.

- [ ] **Step 1: Write the canonical workflow reference**

Create `references/41-creator-first-script-workflow.md` with these required sections and rules:

```markdown
# Creator-First Script Workflow

Use this path when the creator starts from a blank idea, a fragment, a premise, an outline, or an existing draft. The goal is a reviewed script, not production setup.

## Interaction contract

- Ask one question per turn. Choose the unanswered question that can invalidate the most downstream work.
- If the creator is stuck, offer two or three materially different options plus a recommendation; do not manufacture weak choices.
- Summarize the accepted decision before moving to the next gate.
- Keep alternatives as `CREATIVE_DRAFT`; only creator-approved choices cross an `*_ACCEPTED` gate.
- Do not load Runtime, assets, provider adapters, model evidence, prompt compilation, or video QC during this path.
- The workbook is optional depth. Use it only when the creator wants durable state or the script spans enough turns that decisions may be lost.

## Entry state

Classify the supplied material as `BLANK`, `SEED`, `OUTLINE`, or `DRAFT`. Start at the earliest unresolved gate; never force a creator with a usable draft back through blank-idea exercises.

## Required gates

1. `SEED_ACCEPTED` — audience experience, format/length, and the core situation are clear enough to explore.
2. `LOGLINE_ACCEPTED` — protagonist, goal, obstacle, stakes, and distinguishing hook form one causal sentence.
3. `CHARACTER_ENGINE_ACCEPTED` — the protagonist’s want, need, contradiction, pressure response, and change/non-change can drive scenes.
4. `DRAMATIC_RULES_ACCEPTED` — point of view, world constraints, tone boundary, and non-negotiable ending facts are explicit.
5. `STRUCTURE_ACCEPTED` — the inciting change, escalating decisions, irreversible turn, climax, and payoff form a causal chain.
6. `DRAFT_ACCEPTED` — a complete draft exists with no missing scenes or placeholder beats.
7. `REVISION_ACCEPTED` — at least one intent/causality pass and one character/dialogue/continuity pass have been reviewed by the creator.

## Stage loop

For the current gate: show the accepted facts, expose one blocking unknown, ask one question, then wait. After the answer, either accept the gate or explain the single remaining contradiction. Do not silently rewrite accepted decisions.

Draft short work as a complete script after structure approval. Draft long work in creator-approved sections, carrying forward a concise decision recap. Revision preserves the creator’s intent unless the creator explicitly changes it.

## Optional depth

- Load Content Market Gate only for audience-growth, monetization, or repeatable-series goals.
- Build a formal Emotional Beat Map only when several beats, dialogue/music timing, or a diagnosed pacing problem makes it useful.
- Expand worldbuilding only when a story decision depends on it.
- Enter visual-production preparation only after the creator accepts the script or explicitly asks to work on an already stable section.

## Completion and handoff

Report the accepted logline, character engine, dramatic rules, structure, revision decisions, unresolved questions, and the script location if the creator authorized a write. Label the result `CREATIVE_DRAFT` until Commit Mode records creator approval. A completed fresh-context trial is product evidence; an authored fixture or local reference-loading measurement is not.
```

- [ ] **Step 2: Create the optional workbook**

Create `templates/script-development-workbook.md` with:

```markdown
# Script Development Workbook

- Project:
- Entry state: `BLANK` / `SEED` / `OUTLINE` / `DRAFT`
- Format and target length:
- Current gate:
- Creator decision:
- Open question:

## Seed

- Intended audience experience:
- Core situation:
- Distinguishing element:
- Gate: `OPEN` / `SEED_ACCEPTED`

## Logline

- Protagonist:
- Goal:
- Obstacle:
- Stakes:
- Hook:
- Accepted logline:
- Gate: `OPEN` / `LOGLINE_ACCEPTED`

## Character engine

- Want:
- Need:
- Contradiction:
- Pressure response:
- Change or deliberate non-change:
- Gate: `OPEN` / `CHARACTER_ENGINE_ACCEPTED`

## Dramatic rules

- Point of view:
- World constraints:
- Tone boundary:
- Ending facts:
- Gate: `OPEN` / `DRAMATIC_RULES_ACCEPTED`

## Structure

- Inciting change:
- Escalating decisions:
- Irreversible turn:
- Climax:
- Payoff:
- Gate: `OPEN` / `STRUCTURE_ACCEPTED`

## Draft

- Script path or inline draft:
- Missing scenes or placeholders: none
- Creator decision:
- Gate: `OPEN` / `DRAFT_ACCEPTED`

## Revision

- Intent and causality findings:
- Character and dialogue findings:
- Continuity findings:
- Accepted changes:
- Rejected changes:
- Open question:
- Gate: `OPEN` / `REVISION_ACCEPTED`
```

- [ ] **Step 3: Reframe the existing creative references**

Replace `references/01-creative-brief.md` with:

```markdown
# Creative Brief

Use after `SEED_ACCEPTED` or `LOGLINE_ACCEPTED`. The brief records creator-approved dramatic intent; it does not force production setup.

Capture intended audience experience, format and target length, premise, accepted logline, protagonist change or deliberate non-change, dramatic rules, ending promise, and hard constraints. Add delivery specifications only when they already constrain the writing.

For audience-growth, monetization, or repeatable-series work, load `20-content-market-gate.md` before expensive scale. A market hypothesis is conditional context, not a substitute for the story.

Mark `BRIEF_LOCKED` only when two writers would understand the same protagonist, central pressure, causal direction, tone boundary, and ending promise.

Use `../templates/creative-brief.md`.
```

Replace `references/02-story-breakdown.md` with:

```markdown
# Story Development and Breakdown

Build a causal story before designing shots. Resolve the inciting change, the protagonist's escalating decisions, the irreversible turn, the climax choice, and the payoff. Every major scene must change a goal, relationship, knowledge state, risk, or available choice.

For an existing draft, identify missing causes, repeated beats, passive turns, unsupported character decisions, and scenes whose removal changes nothing. Preserve deliberate ambiguity; do not confuse missing causality with mystery.

Use hook, conflict/question, escalation, payoff, and follow/cliffhanger only when the chosen format needs them. Do not force a series engine onto a self-contained work.

After `STRUCTURE_ACCEPTED`, write the draft. Load `06-shot-engineering.md` only after the script or selected section is accepted for visual-production preparation.
```

Replace the top of `templates/creative-brief.md` with:

```markdown
# Creative Brief

- Project:
- Entry source: `SEED_ACCEPTED` / `LOGLINE_ACCEPTED` / existing brief
- Intended audience experience:
- Format and target length:
- Premise:
- Accepted logline:
- Protagonist change or deliberate non-change:
- Dramatic rules:
- Ending promise:
- Market Gate ID / decision: optional unless commercial or repeatable-series work
- Hard constraints:
- Delivery specifications: optional until production preparation
- Gate status: `DRAFT` / `BRIEF_LOCKED`
```

- [ ] **Step 4: Run the document contract tests**

```powershell
python -m pytest -q tests/test_creator_first_script_workflow.py::test_creator_workflow_defines_the_complete_path_and_interaction_limits tests/test_creator_first_script_workflow.py::test_optional_workbook_matches_the_creator_workflow_gates
```

Expected: 2 tests pass. The routing and root-Skill token tests remain intentionally red until Task 3.

- [ ] **Step 5: Commit the workflow reference and templates**

```powershell
git add skills/generative-film-production/references/41-creator-first-script-workflow.md skills/generative-film-production/templates/script-development-workbook.md skills/generative-film-production/references/01-creative-brief.md skills/generative-film-production/references/02-story-breakdown.md skills/generative-film-production/templates/creative-brief.md
git commit -m "feat: add creator-first script workflow"
```

---

### Task 3: Make Creative Mode select the workflow without production machinery

**Files:**

- Modify: `filmfoundry/modes.py`
- Modify: `skills/generative-film-production/SKILL.md`
- Modify: `skills/generative-film-production/references/40-work-modes.md`

**Interfaces:**

- Consumes: request text and the existing four-mode boundary.
- Produces: `ModeDecision.references` with `references/41-creator-first-script-workflow.md` first for blank/story/script requests, `validators=()`, `allow_provider_calls=False`, and `allow_source_writes=False`.

- [ ] **Step 1: Reduce the Creative baseline and add a creator-request matcher**

In `filmfoundry/modes.py`, make the Creative profile:

```python
MODE_CREATIVE: (
    "references/40-work-modes.md",
),
```

Add near the mode aliases:

```python
_CREATOR_SCRIPT_RE = re.compile(
    r"从零|空白|想法|创意|故事|剧本|梗概|人物|情节|hook|idea|story|script|premise|logline|character|plot|draft|revise",
    re.IGNORECASE,
)
_EXISTING_SCRIPT_RE = re.compile(
    r"已有剧本|现有剧本|分析剧本|修改剧本|修订剧本|existing script|script draft|revise|rewrite",
    re.IGNORECASE,
)
```

- [ ] **Step 2: Replace the Creative request expansion logic**

Use this behavior inside `_references_for_request()`:

```python
references = list(reference_profile(mode))
normalized = request.lower()
if mode == MODE_CREATIVE and _CREATOR_SCRIPT_RE.search(request):
    references.insert(0, "references/41-creator-first-script-workflow.md")
if mode in {MODE_CREATIVE, MODE_COMMIT} and _EXISTING_SCRIPT_RE.search(request):
    if "references/39-script-facts-and-emotion.md" not in references:
        references.append("references/39-script-facts-and-emotion.md")
if mode == MODE_CREATIVE and any(token in normalized for token in ("商业", "变现", "系列", "market", "monetiz")):
    references[0:0] = [
        "references/20-content-market-gate.md",
        "references/21-market-mvp.md",
    ]
return tuple(dict.fromkeys(references))
```

Do not add a creator-stage enum, persisted workflow state, CLI write command, or schema in this checkpoint.

- [ ] **Step 3: Add the root Skill entry route**

In `SKILL.md`, place a `## Creator-first script workflow` section before production invariants. It must state:

```markdown
When the creator has a blank idea, fragment, premise, outline, or draft, load `references/41-creator-first-script-workflow.md` first. Ask one question per turn and advance only the earliest unresolved creator gate. Do not load production, Runtime, provider, model-evidence, or video-QC references until the script is accepted or the creator explicitly asks for production preparation.
```

Replace the frontmatter description with:

```yaml
description: Use when creating or revising scripts, developing stories and characters, or preparing assets, images, prompts, and shot plans for external visual-production tools.
```

Add this product boundary immediately after the overview:

```markdown
FilmFoundry owns script creation, analysis, revision, and visual-production preparation. External tools and people own provider calls, video generation, downloads, and aesthetic video QC.
```

Add this row to “Route by current stage”:

```markdown
| Blank idea, story fragment, outline, or draft needing development | `references/41-creator-first-script-workflow.md`; load `01`, `02`, or `39` only when its stage requires them |
```

Keep the root Skill under 500 lines and remove any nearby statement that makes provider execution or video QC a Core responsibility. Do not perform the repository-wide provider cleanup in this task.

- [ ] **Step 4: Reconcile the Work Modes reference**

Update Creative Mode in `references/40-work-modes.md` to name the creator workflow as the default script path and state that a blank project requires a creator question, not Runtime initialization. Keep Commit Mode as a separate authorization boundary.

- [ ] **Step 5: Run the routing and Skill tests**

```powershell
python -m pytest -q tests/test_creator_first_script_workflow.py tests/test_creative_modes.py tests/test_skill_contract.py tests/test_v3_clean_break_contract.py
```

Expected: all focused tests pass. Existing Gate tests may still document deprecated provider debt; do not weaken or silently delete them in this plan.

- [ ] **Step 6: Commit routing and Skill entry changes**

```powershell
git add filmfoundry/modes.py skills/generative-film-production/SKILL.md skills/generative-film-production/references/40-work-modes.md
git commit -m "feat: route blank ideas through creator workflow"
```

---

### Task 4: Add honest guardrails and a fresh-context acceptance protocol

**Files:**

- Modify: `evals/evals.json`
- Create: `evals/fixtures/baseline/E27-from-zero-script-entry.md`
- Create: `evals/fixtures/golden/E27-from-zero-script-entry.md`
- Modify: `tests/test_eval_schema.py`
- Modify: `evals/README.md`
- Create: `evals/creator-first-trial-protocol.md`

**Interfaces:**

- Consumes: the single-turn eval schema and the multi-turn workflow gates.
- Produces: one authored routing guardrail plus a separate human-run, fresh-context acceptance record.

- [ ] **Step 1: Add one single-turn authored guardrail**

Append this exact object to the `evals` array in `evals/evals.json`:

```json
{
  "id": "E27-from-zero-script-entry",
  "name": "Start a blank script with one creator question",
  "prompt": "我想写一个八到十二分钟的短片，但目前只有想创作的愿望，没有故事、人物或世界观。请从零带我完成，不要假装我已经有制作方案。",
  "expected_output": "The agent should identify the blank entry state, explain that it will guide the creator one decision at a time, and ask exactly one high-leverage question about the intended audience experience or core situation. It must not initialize production machinery.",
  "assertions": [
    {
      "type": "contains_all",
      "text": "Identifies the blank Creative entry state",
      "terms": ["BLANK", "CREATIVE_DRAFT"]
    },
    {
      "type": "not_contains",
      "text": "Does not initialize production machinery",
      "terms": ["Runtime", "provider", "Shot Spec", "视频生成"]
    },
    {
      "type": "human",
      "text": "The response asks exactly one material creator-facing question and waits instead of inventing the story."
    }
  ]
}
```

Create `evals/fixtures/baseline/E27-from-zero-script-entry.md` with:

```markdown
<!-- Authored scorer fixture; not a fresh-context agent result. -->

Initialize Runtime, create a Shot Spec, choose a provider, prepare assets, and start 视频生成 before deciding the story.
```

Create `evals/fixtures/golden/E27-from-zero-script-entry.md` with:

```markdown
<!-- Authored scorer fixture; not a fresh-context agent result. -->

CREATIVE_DRAFT

Entry state: BLANK. 我会一次只推进一个创作决定，并在你确认后再进入下一步。

你希望观众看完这部短片后，最主要地感受到什么？
```

- [ ] **Step 2: Update exact eval-count assertions**

In `tests/test_eval_schema.py`, rename the first test to `test_eval_file_has_twenty_seven_realistic_cases`, change the count assertion to 27, and change the validator-output assertion to:

```python
assert "27 evals" in result.stdout
```

- [ ] **Step 3: Write the multi-turn trial protocol**

Create `evals/creator-first-trial-protocol.md` with this pre-registered scenario and acceptance table:

```markdown
# Creator-First Fresh-Context Trial Protocol

## Fixed start

Open a genuinely fresh agent context with the current FilmFoundry Skill and no project Runtime. Use: “我想写一个 8–12 分钟的短片，但现在没有故事。请从零带我完成。”

Record model/version, reasoning setting, references loaded each turn, elapsed human time, agent turns, creator interventions, accepted gates, and the final artifacts. Reference-loading time is not creator completion time.

## Pass conditions

| Requirement | Evidence |
|---|---|
| At most one material question per agent turn | Full transcript review |
| No production/provider references before explicit production request | Per-turn reference log |
| All seven creator gates are either accepted or explicitly rejected by the creator | Gate ledger |
| Complete draft has no missing scene or placeholder beat | Draft review |
| Revision includes intent/causality and character/dialogue/continuity checks | Revision record |
| Emotional map appears only when the story or creator needs it | Transcript and artifact list |
| Creator choices are not silently overwritten | Decision-diff review |

Any missing transcript, reference log, creator intervention record, or final draft makes the result `INSUFFICIENT_EVIDENCE`, not pass.
```

- [ ] **Step 4: Clarify evidence boundaries in the eval README**

State that E27 is a single-turn authored guardrail. State that only a completed run of `creator-first-trial-protocol.md` can supply the current multi-turn product evidence, and even that one run does not prove creator speed or broad market fit.

- [ ] **Step 5: Run deterministic eval verification**

```powershell
python scripts/validate_evals.py evals/evals.json
python -m pytest -q tests/test_eval_schema.py tests/test_eval_fixtures.py
```

Expected: `PASS: 27 evals schema-valid`; authored golden fixtures pass machine assertions; the suite still labels them as non-benchmark evidence.

- [ ] **Step 6: Commit the eval guardrail and trial protocol**

```powershell
git add evals/evals.json evals/fixtures/baseline/E27-from-zero-script-entry.md evals/fixtures/golden/E27-from-zero-script-entry.md tests/test_eval_schema.py evals/README.md evals/creator-first-trial-protocol.md
git commit -m "test: add creator-first trial protocol"
```

---

### Task 5: Reconcile public documentation and metadata without claiming release

**Files:**

- Modify: `README.md`
- Modify: `docs/README.md`
- Modify: `docs/filmfoundry-v3.md`
- Modify: `docs/ai-video-production-guide-zh.md`
- Modify: `CHANGELOG.md`
- Modify: `pyproject.toml`
- Modify: `tests/test_repo_metadata.py`

**Interfaces:**

- Consumes: the implemented creator workflow and still-open provider-removal debt.
- Produces: one honest public status: creator workflow implemented as a checkpoint, product release still paused.

- [ ] **Step 1: Write a failing metadata assertion**

Add this assertion inside `test_readme_uses_public_suite_and_repo_name()`:

```python
pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
assert 'description = "Creator-first script development and visual-production preparation Skills"' in pyproject
```

Add to `test_readme_distinguishes_verified_static_tests_from_pending_agentic_benchmark()`:

```python
assert "provider-specific removal" in text and "pending" in text
assert "fresh-context" in text
```

Run:

```powershell
python -m pytest -q tests/test_repo_metadata.py
```

Expected: the description assertion fails before metadata is updated.

- [ ] **Step 2: Update active documentation**

Apply these exact content anchors consistently:

- Add to `README.md`: “Blank-idea script work starts with `references/41-creator-first-script-workflow.md`; production references remain deferred until the creator accepts the script or explicitly requests production preparation.” Keep separate status rows for `Creator-first workflow contract`, `Fresh-context creator trial`, and `Provider-specific removal`.
- Add to `docs/README.md`: “Creator-first script workflow — the current starting point for a blank idea, outline, or draft” and “Creator-first trial protocol — the fresh-context product-evidence procedure.”
- Add to `docs/filmfoundry-v3.md`: “FilmFoundry starts with script creation or revision. It prepares generic visual-production handoffs only after the creative direction is accepted; provider calls and generated-media QC remain external.”
- Add to the status banner in `docs/ai-video-production-guide-zh.md`: “空白创意请先使用 `skills/generative-film-production/references/41-creator-first-script-workflow.md`；本指南从剧本确认后的视觉生产准备开始。”
- Add under Unreleased in `CHANGELOG.md`: bullets for the seven-gate creator workflow, optional workbook, minimal Creative routing, and fresh-context trial protocol.
- In `pyproject.toml`, set `description = "Creator-first script development and visual-production preparation Skills"`.

Do not change the version, tag language, release state, or historical changelog entries.

- [ ] **Step 3: Run metadata and link checks**

```powershell
python -m pytest -q tests/test_repo_metadata.py tests/test_v3_active_surface.py tests/test_skill_contract.py
```

Expected: all tests pass, active documentation remains project-neutral, and reports/superpowers history remain outside the release archive.

- [ ] **Step 4: Commit the public documentation checkpoint**

```powershell
git add README.md docs/README.md docs/filmfoundry-v3.md docs/ai-video-production-guide-zh.md CHANGELOG.md pyproject.toml tests/test_repo_metadata.py
git commit -m "docs: make creator workflow the public entry"
```

---

### Task 6: Run the fresh-context trial and stop at the evidence gate

**Files:**

- Create: `docs/reports/2026-09-10-creator-first-fresh-context-trial.md`
- Modify after a failed trial only: the smallest workflow/routing/test files implicated by transcript evidence.

**Interfaces:**

- Consumes: `evals/creator-first-trial-protocol.md` and the current Skill package.
- Produces: a factual `PASS`, `FAIL`, or `INSUFFICIENT_EVIDENCE` report and the decision whether an instruction-first workflow is sufficient.

- [ ] **Step 1: Run the trial in a genuinely fresh context**

Use the fixed start prompt and record every required field from the protocol. Do not use authored fixtures as the run output, do not preload a project Runtime, and do not treat the local reference-loading benchmark as creator elapsed time.

- [ ] **Step 2: Score the transcript against every pass condition**

The report must separate:

- observed facts from reviewer inference;
- workflow failures from script-taste disagreements;
- required creator interventions from unnecessary process friction;
- useful optional emotional mapping from mandatory process tax;
- static verification from the fresh-context evidence.

If the agent asks multiple material questions, loads production machinery early, skips a required gate, leaves an incomplete draft, or silently overwrites a creator decision, mark the trial `FAIL` and repair only the evidenced workflow defect before rerunning in another fresh context.

- [ ] **Step 3: Decide whether Python workflow state is justified**

- Keep the instruction-first design if the transcript preserves accepted decisions and completes the path without state loss.
- Propose a separate design/spec for Python or Schema state only if the transcript shows repeatable state loss, ambiguous resumption, or cross-session handoff failure that the optional workbook cannot solve.
- Do not add a state machine merely because the current Creator Read Model exists.

- [ ] **Step 4: Write and review the trial report**

The report must include the exact model/settings, transcript location, references loaded, turn count, human elapsed time, intervention count, gate results, artifact list, failures, and the instruction-first/stateful decision. End with: “This checkpoint does not approve a FilmFoundry release; provider-surface removal remains pending.”

- [ ] **Step 5: Commit the evidence only if it is complete**

```powershell
git add docs/reports/2026-09-10-creator-first-fresh-context-trial.md
git commit -m "docs: record creator-first fresh-context trial"
```

If evidence is incomplete, do not commit a pass claim; preserve the raw transcript and record `INSUFFICIENT_EVIDENCE`.

---

### Task 7: Verify the checkpoint and prepare the next independent plan

**Files:**

- Inspect: all changed files
- Create after the creator trial passes: `docs/superpowers/plans/2026-09-10-provider-boundary-cleanup.md`

**Interfaces:**

- Consumes: creator workflow implementation plus fresh-context evidence.
- Produces: a verified creator-workflow checkpoint and a go/no-go decision for provider-boundary planning; it does not produce a release.

- [ ] **Step 1: Run the full deterministic suite**

```powershell
python -m pytest -q
git diff --check
```

Expected: 302 tests pass if Task 1 adds exactly the three tests specified above and no other test functions are added. Treat the actual collected count as authoritative and explain any difference; do not edit tests merely to force the expected number.

- [ ] **Step 2: Run the repository validators and reference-loading measurement**

```powershell
python scripts/validate_evals.py evals/evals.json
python scripts/benchmark_work_modes.py --format json
```

Expected: 27 evals are schema-valid, all Creative references exist, and the measurement remains explicitly scoped to bytes/reference loading only. Do not convert its milliseconds into an LLM or creator speed claim.

- [ ] **Step 3: Build and verify clean extraction**

```powershell
$env:SOURCE_DATE_EPOCH = "0"
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir .dist
python scripts/build_release_artifacts.py --out .dist
Remove-Item Env:SOURCE_DATE_EPOCH -ErrorAction SilentlyContinue
python scripts/check_clean_extraction.py --wheel .dist/filmfoundry_skills-3.0.0-py3-none-any.whl --archive .dist/filmfoundry-skills-v3.0.0.zip
```

Expected: build and clean extraction pass. This proves packaging and archive boundaries only, not a release Gate.

- [ ] **Step 4: Review the exact diff and live Git state**

```powershell
git status --short --branch
git diff --stat origin/main...HEAD
git log --oneline --decorate -8
```

Expected: only creator-workflow, routing, eval, documentation, metadata, tests, and the factual trial report changed. No provider cleanup, legacy compatibility, downstream project files, tag, or release mutation appears.

- [ ] **Step 5: Open the next planning gate**

Only after the fresh-context trial passes, classify every active provider-related match as:

- `KEEP_GENERIC_HANDOFF` — generic shot/prompt/asset preparation that ends before external execution;
- `GENERALIZE` — useful planning semantics coupled to provider naming or video lifecycle;
- `DELETE_ACTIVE` — provider execution, capability evidence ingestion, smoke gates, named adapters, generation tracking, or aesthetic video QC owned externally;
- `KEEP_HISTORY_ONLY` — dated reports and historical tests excluded from active artifacts.

Use that inventory to write the separate provider-boundary cleanup plan. Do not delete files during classification, and do not mark v3.0 approved until that second plan, another full verification pass, and an exact release diff are complete.

---

## Plan Self-Review

- **Spec coverage:** The plan covers the first required handoff action: a complete from-zero script path, minimal context, one question per turn, optional depth, fresh-context evidence, and honest release status.
- **Scope boundary:** Provider cleanup is deliberately separated because it spans Skill instructions, Python APIs, CLI, schemas, tests, templates, and docs and can be reviewed independently from creator-workflow quality.
- **No speculative state engine:** A Python/schema workflow state is conditional on transcript evidence, avoiding an unproven abstraction.
- **Evidence integrity:** Static tests, authored eval fixtures, reference-loading measurements, fresh-context evidence, packaging, and release approval remain separate claims.
- **Compatibility:** No v2 namespace, schema, migration, or long-term compatibility layer is introduced.
- **Project neutrality:** No downstream project names or assets are required by the workflow or trial.
