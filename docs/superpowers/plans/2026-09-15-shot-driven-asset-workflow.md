# Shot-Driven Asset Workflow Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace mandatory asset-wide stress testing with a shot-driven asset workflow that creates only the character, location, prop, wardrobe, and state references required by the approved shot scope.

**Architecture:** Keep identity references as reusable baselines. Derive scene and state assets from a shot requirement matrix, and bind every derived asset to one or more actual shots or generation units. Make stress tests optional, risk-triggered diagnostics rather than a default stage.

**Tech Stack:** Markdown Skill references, CSV/JSON templates, Python contract tests, pytest, PowerShell verification.

**Spec:** Official Higgsfield workflow evidence: [Academy](https://higgsfield.ai/academy), [Cinema Studio help](https://higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio), and [studio pipeline guide](https://www.higgsfield.company/blog/how-studios-scale-ai-video-production).

## Global Constraints

- FilmFoundry remains provider-neutral and project-neutral.
- No changes to downstream project Canon or production files.
- Character identity sheets remain reusable identity baselines, not proof of every possible action.
- Derived state references must have an explicit shot or generation-unit binding.
- Optional diagnostics must never become a release prerequisite without a documented risk reason.
- Existing provenance, continuity, Select, and Gate semantics remain intact.

---

### Task 1: Record external workflow evidence and design principles

**Files:**
- Create: `docs/reports/2026-09-15-shot-driven-workflow-research.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: official Academy, Cinema Studio help, and studio pipeline pages.
- Produces: cited evidence table and migration principles for later Skill edits.

- [ ] **Step 1: Write the evidence table** with source URL, observed workflow, and transferable principle.
- [ ] **Step 2: State the decision** that references are prepared before generation, while actual state references are selected per shot.
- [ ] **Step 3: Add the report to `docs/README.md` under Evidence and history.**
- [ ] **Step 4: Run `git diff --check`.**

### Task 2: Introduce a shot requirement matrix

**Files:**
- Create: `skills/generative-film-production/templates/shot-requirement-matrix.md`
- Modify: `skills/generative-film-production/references/06-shot-engineering.md`
- Modify: `skills/generative-film-production/references/04-asset-passport.md`

**Interfaces:**
- Consumes: approved Shot Plan and Asset Passport identities.
- Produces: a per-shot record of required characters, locations, props, wardrobe, state, and optional visual controls.

- [ ] **Step 1: Define matrix columns**: `shot_id`, `generation_unit_id`, `characters`, `locations`, `props`, `wardrobe_or_state`, `reference_inputs`, `new_asset_needed`, `risk_reason`.
- [ ] **Step 2: Define the rule** that an identity sheet is created once per recurring identity, while a derived state asset is created only when a listed shot needs a visual authority that Prompt text alone cannot carry.
- [ ] **Step 3: Define the handoff order**: identity baselines → scene assets → shot-specific state assets → prompt compilation.
- [ ] **Step 4: Add one concrete fictional example without project-specific Canon.**

### Task 3: Reclassify asset stress testing as optional and risk-triggered

**Files:**
- Modify: `skills/generative-film-production/SKILL.md`
- Modify: `skills/generative-film-production/references/05-asset-stress-test.md`
- Modify: `skills/generative-film-production/references/25-character-reference-system.md`
- Modify: `skills/generative-film-production/templates/character-reference-sheet.md`

**Interfaces:**
- Consumes: shot requirement matrix and declared production risks.
- Produces: `OPTIONAL_DIAGNOSTIC` guidance with explicit trigger conditions and no default action checklist.

- [ ] **Step 1: Remove the unconditional core invariant requiring every recurring asset to be stress-tested before video.**
- [ ] **Step 2: Replace the default route with shot-driven routing: create the next required scene asset after identity approval.**
- [ ] **Step 3: Preserve stress tests only for a declared high-risk combination such as identity plus difficult lighting, complex hand interaction, or a state the selected route cannot express reliably.**
- [ ] **Step 4: Require each diagnostic output to name the affected shot IDs and the decision it informs.**
- [ ] **Step 5: Remove mandatory generic action lists from the character reference template.**

### Task 4: Add contract tests for shot-driven asset scope

**Files:**
- Modify: `tests/test_skill_contract.py`
- Create: `tests/test_shot_requirement_matrix_contract.py`

**Interfaces:**
- Consumes: updated reference and template text.
- Produces: deterministic checks that prevent regression to unconditional asset testing.

- [ ] **Step 1: Add a failing test** requiring the Skill route to mention shot requirement matrices and optional risk-triggered diagnostics.
- [ ] **Step 2: Add a failing test** rejecting wording that makes generic character action tests mandatory.
- [ ] **Step 3: Add a passing fixture test** confirming every derived state entry has at least one shot or generation-unit binding.
- [ ] **Step 4: Run `python -m pytest tests/test_skill_contract.py tests/test_shot_requirement_matrix_contract.py -q`.**
- [ ] **Step 5: Run the full `python -m pytest -q`.**

### Task 5: Reconcile user documentation and migration guidance

**Files:**
- Modify: `docs/filmfoundry-skills-user-manual-zh.md`
- Modify: `docs/ai-video-production-guide-zh.md`
- Modify: `docs/README.md`

**Interfaces:**
- Consumes: the new routing and test contracts.
- Produces: consistent Chinese documentation that teaches identity → scene → shot state → prompt → generation.

- [ ] **Step 1: Replace the old default sequence that outputs an asset stress-test package.**
- [ ] **Step 2: Add the shot-driven sequence and explain when a diagnostic is justified.**
- [ ] **Step 3: Add a migration note for existing projects with already-created identity sheets.**
- [ ] **Step 4: Run link checks, `git diff --check`, and the full test suite.**

### Task 6: Review release and downstream boundaries

**Files:**
- Modify: `CURRENT_HANDOFF.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: all prior tasks and test evidence.
- Produces: an explicit unreleased change entry and a handoff note that downstream projects are not modified.

- [ ] **Step 1: Record the optimization as unreleased; do not change the version or tag.**
- [ ] **Step 2: Record that the current project workflow correction is methodological and does not rewrite any downstream project assets.**
- [ ] **Step 3: Run package build and clean extraction commands from `AGENTS.md`.**
- [ ] **Step 4: Review the complete diff and leave the plan execution checkpoint for user review.**
