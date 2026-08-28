# FilmFoundry Skills v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build a production-oriented, model-agnostic AI filmmaking Agent Skill repository whose primary skill turns briefs and scripts into validated shot specifications, model-specific prompts, continuity decisions, retry plans, and post-production handoffs.

**Architecture:** The public repository is `filmfoundry-skills`; the primary installable skill is `generative-film-production`. The root SKILL.md is a compact router. Heavy production knowledge lives in references, deterministic checks live in Python validators, model/provider details live in adapters, and evals are stored separately so the skill can be benchmarked against a no-skill baseline.

**Tech Stack:** Markdown/YAML skill documents, Python 3.11+ standard library, pytest, JSON/CSV templates, git.

**Spec:** `docs/superpowers/specs/2026-08-28-filmfoundry-skills-design.md`

## Global Constraints

- Repository/public suite name: `filmfoundry-skills` / “FilmFoundry Skills”.
- Primary skill name: `generative-film-production`.
- Root SKILL.md must remain below 500 lines and use progressive disclosure.
- Canonical production decisions are model-agnostic; model dialect belongs only in adapters.
- Default narrative timing grammar is stages + observable end states; second-level timing requires an external hard constraint.
- Every recurring asset uses a single authoritative passport and explicit state variants.
- Every reference has a positive role and a `does_not_control` boundary.
- Every generative clip has one dominant action unless a route-specific profile explicitly permits more.
- Retries change one hypothesized variable at a time and preserve generation lineage.
- Deterministic post-production work must not be delegated to generative video when ordinary editing can perform it reliably.
- Agentic benchmark results must never be claimed unless a fresh external runner actually executed the baseline and with-skill cases.

---

### Task 1: Repository Contract RED/GREEN

**Files:**
- Create: `tests/test_skill_contract.py`
- Create: `skills/generative-film-production/SKILL.md`
- Create: required reference/template/adapter paths listed by the contract test

**Interfaces:**
- Consumes: repository filesystem.
- Produces: an installable Agent Skill directory with valid frontmatter and progressive-disclosure layout.

- [x] Step 1: Write contract tests first for name/description, line budget, required sections, required referenced files, and forbidden placeholder markers.
- [x] Step 2: Run `pytest tests/test_skill_contract.py -q`; verify RED because SKILL.md and dependencies do not exist.
- [x] Step 3: Implement the minimal root skill and required files.
- [x] Step 4: Re-run contract test; verify GREEN.
- [x] Step 5: Commit as `feat: add generative film production skill contract`.

### Task 2: Canonical Shot Spec Validator

**Files:**
- Create: `tests/test_validate_shot_spec.py`
- Create: `skills/generative-film-production/scripts/validate_shot_spec.py`
- Create: `skills/generative-film-production/templates/shot-spec.example.json`

**Interfaces:**
- Produces: `validate_shot_spec(data: dict) -> list[str]` and CLI exit 0/1.

- [x] Step 1: Write failing tests for required identifiers, dominant action, initial/end state, conditional camera axis, reference role boundaries, and timing granularity.
- [x] Step 2: Run targeted pytest; verify expected failures.
- [x] Step 3: Implement minimal validator using standard library only.
- [x] Step 4: Run targeted and full tests; verify GREEN.
- [x] Step 5: Commit as `feat: validate canonical shot specifications`.

### Task 3: Asset Registry Validator

**Files:**
- Create: `tests/test_validate_asset_registry.py`
- Create: `skills/generative-film-production/scripts/validate_asset_registry.py`
- Create: `skills/generative-film-production/templates/asset-registry.example.csv`

**Interfaces:**
- Produces: `validate_rows(rows: list[dict[str, str]]) -> list[str]` and CSV CLI.

- [x] Step 1: Write failing tests for unique asset IDs, canonical descriptor, state ownership, reference role, and anti-role.
- [x] Step 2: Verify RED.
- [x] Step 3: Implement minimal validator.
- [x] Step 4: Verify GREEN and full regression suite.
- [x] Step 5: Commit as `feat: validate asset registry invariants`.

### Task 4: Prompt Linter

**Files:**
- Create: `tests/test_prompt_lint.py`
- Create: `skills/generative-film-production/scripts/prompt_lint.py`

**Interfaces:**
- Produces: `lint_prompt(text: str, route: str = "generic") -> list[str]`.

- [x] Step 1: Write failing tests for unverifiable intent phrases, unnamed references, contradictory timing, keyword soup, and missing observable end state for staged prompts.
- [x] Step 2: Verify RED.
- [x] Step 3: Implement bounded heuristics with explainable messages.
- [x] Step 4: Verify GREEN and full suite.
- [x] Step 5: Commit as `feat: add prompt linting guardrails`.

### Task 5: Continuity Linter

**Files:**
- Create: `tests/test_continuity_lint.py`
- Create: `skills/generative-film-production/scripts/continuity_lint.py`
- Create: `skills/generative-film-production/templates/continuity-ledger.example.csv`

**Interfaces:**
- Produces: `validate_transition(prev: dict, nxt: dict) -> list[str]`.

- [x] Step 1: Write failing tests distinguishing continuous action from hard cut/reverse angle/match cut and enforcing axis/eyeline/prop-state continuity where appropriate.
- [x] Step 2: Verify RED.
- [x] Step 3: Implement minimal transition-aware rules.
- [x] Step 4: Verify GREEN and regression suite.
- [x] Step 5: Commit as `feat: validate transition-aware continuity`.

### Task 6: Production References and Adapters

**Files:**
- Create: `references/01-creative-brief.md` through `references/14-failure-recovery.md`
- Create: adapters for generic T2V, I2V, first-last-frame, multi-reference, storyboard-to-video, Seedance, MiniMax H3, Veo, Kling, and image generation.

**Interfaces:**
- Consumes: root router decisions and Canonical Shot Spec.
- Produces: bounded model-specific compilation guidance without provider-specific assumptions leaking into canonical data.

- [x] Step 1: Extend contract tests to require every adapter and high-value invariant.
- [x] Step 2: Verify RED for missing content.
- [x] Step 3: Write concise references/adapters, preserving measured-vs-assumed model-profile rules.
- [x] Step 4: Verify GREEN.
- [x] Step 5: Commit as `docs: add production modules and model adapters`.

### Task 7: Eval Suite and Deterministic Eval Harness

**Files:**
- Create: `evals/evals.json`
- Create: `evals/README.md`
- Create: `tests/test_eval_schema.py`
- Create: `scripts/validate_evals.py`
- Create: `evals/fixtures/baseline/*.md`
- Create: `evals/fixtures/golden/*.md`

**Interfaces:**
- Produces: 12 realistic agentic eval prompts with expected outcomes and a deterministic schema validator. Fixture scoring demonstrates harness behavior only; it is not represented as a real LLM benchmark.

- [x] Step 1: Write failing schema tests before eval files exist.
- [x] Step 2: Verify RED.
- [x] Step 3: Implement 12 evals covering overstuffed clips, asset locking, reference roles, axis continuity, I2V verbosity, timing granularity, lip sync, reverse angle, persistent props, exact text/post, selects-only, and final assembly.
- [x] Step 4: Implement validator and fixture smoke tests.
- [x] Step 5: Verify GREEN.
- [x] Step 6: Commit as `test: add agentic eval suite and harness`.

### Task 8: Documentation, Packaging, and Verification

**Files:**
- Create: `README.md`, `CHANGELOG.md`, `LICENSE`, `pyproject.toml`
- Create: `.github/workflows/test.yml`
- Create: distribution zip under `.dist/` during packaging only.

**Interfaces:**
- Produces: a GitHub-ready repository and installable ZIP.

- [x] Step 1: Add README with truthful status labels: static/TDD verified vs external agentic benchmark pending.
- [x] Step 2: Add CI running pytest and validators.
- [x] Step 3: Run `pytest -q` and all example validators.
- [x] Step 4: Run placeholder scan, SKILL.md line count, `git status --short`, and package integrity check.
- [x] Step 5: Commit as `chore: prepare FilmFoundry Skills v1.0 package`.
