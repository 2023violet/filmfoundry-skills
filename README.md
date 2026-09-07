# FilmFoundry Skills

**v2.1 core:** provider-neutral contracts, visual-control validation, compilation, and evidence APIs.

The v1.3.3 metadata remains available as the compatibility baseline. See
`docs/filmfoundry-v2.md` and `docs/filmfoundry-v2-support-matrix.md` for the
v2 boundary and adapter responsibilities.

**Repository:** `filmfoundry-skills`  
**Primary skill:** `generative-film-production`  
**Version:** 2.2.0

开始使用：阅读[AI 视频全流程操作指南](docs/ai-video-production-guide-zh.md)。评分与边界见[全面评分报告](docs/reports/2026-09-07-filmfoundry-skills-v2.1-score.md)。

Compatibility baseline: **Version:** 1.3.3 (immutable checkpoint; current package metadata is 2.2.0).

FilmFoundry Skills is a production-oriented Agent Skill suite for AI filmmaking. v1.2.0 keeps one end-to-end skill and adds a **Content-Market-First** front end so audience-growth and monetization projects validate who watches, why they click, what the hook/payoff/follow engine is, whether thirty episodes are sustainable, what can monetize, and what the cheapest real MVP is **before** FilmFoundry pays the full production cost.
FilmFoundry Skills v1.3.3 keeps the **format-agnostic visual-planning and edit-timeline layer** and hardens state alignment between Shot Specs and visual-control assets. Storyboards, first/last frames, keyframes, character sheets, scene sheets, and model-specific prompts are optional control artifacts chosen by production risk; none of them is the parent workflow.


## Status

| Layer | Status |
|---|---|
| Repository / Skill contract tests | **Static/TDD verified after release verification** |
| Content Market Gate / runtime / shot / Select validators | **Deterministic validators included** |
| Keyframe and provider structural prompt gates | **Deterministic lint only; not model obedience evidence** |
| Authored eval fixtures | **Harness demonstrations only; not agent benchmark results** |
| Fresh-context no-skill vs with-skill Agentic benchmark | **Pending** |
| Real provider/model smoke tests | **Project-specific; not fabricated by this package** |
| Real market MVP evidence | **Project-specific; not fabricated by this package** |
| Real multi-project production validation | **Pending** |

## Core idea

> **Market before production. Spec before prompt. Evidence before trust. Runtime before memory.**

Commercial/creator route:

```text
Idea
→ Content Market Gate
→ Cheapest publishable MVP
→ Market Evidence Review
→ Production Approval
→ Creative Brief
→ Story / Asset / Shot Engineering
→ Visual Control Gate (only when required)
→ Model Profile + Adapter
→ Generation
→ Full or Partial Select
→ Observed State
→ Edit / Audio / Final QC
```

Non-market work such as a client-locked commission, pure art piece, portfolio study, or model-capability test may explicitly bypass the market gate with a recorded reason.

## What changed in 1.3.3

- Made CSV validators BOM-safe with `utf-8-sig`, including Asset Registry, aggregate Project Runtime asset loading, Selects Log, and Continuity Ledger. This fixes a real production integration failure where a valid Excel/Windows-style UTF-8 BOM made the first CSV header appear as `\ufeffasset_id`.
- Added regression tests proving both standalone Asset Registry validation and aggregate Project Runtime validation accept BOM-prefixed registries.
- No Canonical Shot Spec or provider behavior semantics changed.

## What changed in 1.3.2

- Added **Visual Control State Alignment**: an approved keyframe can be a partial authority and must not be used as a start/end frame when its visible state conflicts with the Shot Spec.
- Added a state-audit template for comparing expected initial/end state against observed visual-control state before provider submission.
- Clarified that **proxy smoke tests do not directly unlock a production route** when the production shot has different prop/location/state conditions.
- Hardened First/Last guidance: authority pairs should isolate the intended transition and must not silently change unrelated locked states.
- Corrected Picture Lock sequencing: timing-authoritative audio must be resolved before Picture Lock, while final SFX/music mix and subtitle export may finish after Picture Lock when they cannot change picture timing.

## What changed in 1.3.1

- Corrected the visual-planning layer to be **AI-video format agnostic**: comic, 3D animation, photoreal, ads, shorts, MV, and hybrid workflows share the same production architecture.
- Added a generic **Visual Planning Layer**: use a single keyframe, first/last pair, storyboard board, continuity board, or no board at all according to the control problem.
- Added **capability-scoped provider gates** so a shot may enter a pilot when its required model behaviors are evidenced, without waiting for unrelated global model tests.
- Added an **Edit Timeline Contract**: Generation Units do not have to add up to final runtime, but every final episode must have explicit 100% timeline coverage before Picture Lock.
- Clarified that **Picture Lock is an edit state**, not a synonym for static asset/keyframe readiness.
- Added generic character/location reference-system templates that scale asset cost by recurrence and continuity risk instead of requiring three views/five expressions for every person.

## 1.3.0 — superseded design note

The short-lived 1.3.0 draft over-specialized the new visual-planning layer around comic / 漫剧 production. v1.3.1 retracts that specialization and preserves only the generally useful ideas: optional boards, reusable reference sheets, and board-level QC.

## What changed in 1.2.0

- Added a validated **Content Market Gate** for audience-growth, monetization, and repeatable-series projects.
- Added `NO_GO`, `TRAFFIC_EXPERIMENT`, `MVP_ONLY`, `PRODUCTION_APPROVED`, and explicit `BYPASS` decisions.
- Added a low-cost Market MVP loop with predeclared success criteria and dated evidence IDs.
- Added AI-native content-design guidance: narrative engine before worldbuilding, strong hook/payoff/follow logic, and production-fit design.
- Split provider source duration from required edit duration: `generation_duration_seconds` vs `edit_target_duration_seconds`.
- Added traceable `PARTIAL_SELECT` support so a valid contiguous range can be used even when unused source footage fails later.
- Added eyeline-critical shot/keyframe contracts to catch beautiful but narratively misdirected character frames.
- Added model `behavior_observations` with evidence levels and source generation IDs; `OBSERVED_ONCE` cannot become a default adapter rule.
- Added a controllability-budget reference to reduce long-prompt over-control, timing density, camera overload, and acting overload.
- Updated QC to separate Prompt Compliance, Narrative Fitness, Identity/Continuity, Visual Quality, and Editability.
- Expanded the adversarial eval suite from 18 to **26** cases.

## Repository layout

```text
filmfoundry-skills/
├── skills/generative-film-production/
│   ├── SKILL.md
│   ├── references/
│   │   └── adapters/
│   ├── templates/
│   └── scripts/
├── evals/
├── scripts/
├── tests/
└── docs/
```

## Install

Copy `skills/generative-film-production/` into the Agent Skills directory used by your runtime. Validators use Python 3.11+ standard library only; runtime templates use JSON/CSV so validation does not require PyYAML.

## Validate

```bash
python -m pytest -q
python skills/generative-film-production/scripts/validate_content_market_gate.py \
  skills/generative-film-production/templates/content-market-gate.example.json
python skills/generative-film-production/scripts/validate_project_runtime.py \
  skills/generative-film-production/templates/project-runtime.example.json
python skills/generative-film-production/scripts/validate_shot_spec.py \
  skills/generative-film-production/templates/shot-spec.example.json
python skills/generative-film-production/scripts/validate_selects_log.py \
  skills/generative-film-production/templates/selects-log.csv
python scripts/validate_evals.py evals/evals.json
```

## Evidence boundary

Static tests prove the package and deterministic contracts, not audience demand, video quality, provider obedience, or profitability. A prompt linter cannot prove a provider follows the prompt. An authored eval fixture is not a benchmark run. A Content Market Gate hypothesis is not market validation. Real dated publishing evidence and real model generations remain separate evidence layers.

## License

MIT. See `LICENSE`.
