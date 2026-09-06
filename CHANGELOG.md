# Changelog

## 1.3.3 — 2026-09-06

- Hardened CSV ingestion for UTF-8 BOM (`utf-8-sig`) across asset registry, aggregate runtime asset loading, selects log, and continuity ledger validators.
- Added regression coverage for BOM-prefixed Asset Registry files in standalone and aggregate Project Runtime validation.
- This is a validator interoperability fix; production semantics remain unchanged from v1.3.2.

## 1.3.2 — 2026-09-06

- Added visual-control state-alignment guidance and audit template.
- Clarified partial-authority semantics for keyframes and First/Last frames.
- Added the rule that proxy smoke evidence cannot directly unlock a production route when shot-specific state differs.
- Clarified First/Last tests should isolate the intended state change rather than bundle unrelated prop/camera changes.
- Corrected Picture Lock sequencing relative to final sound/mix/subtitle finishing.

## 1.3.1 — 2026-09-06

- Corrected v1.3.0 over-specialization: visual planning is now format-agnostic and applies to any AI-video production style.
- Added `references/24-visual-planning-layer.md`, `25-character-reference-system.md`, `26-location-reference-system.md`, `27-storyboard-keyframe-planning.md`, `28-visual-plan-qc.md`, `29-capability-scoped-model-gates.md`, and `30-edit-timeline-contract.md`.
- Added generic templates for character/location reference sheets, storyboard boards, sequence plans, and edit-timeline ledgers.
- Defined capability-scoped model evidence gates so unrelated provider tests do not block a route that has enough local evidence.
- Reserved Picture Lock for final edit timing/state; static assets use Static Visual Lock / Keyframe Lock terminology.
- Updated the runtime validator so `READY_FOR_VIDEO` can be authorized by an explicit capability-scoped `provider_route_gate`; an unverified route still blocks release.

## 1.3.0 — 2026-09-05

- Added `references/24-comic-adaptation.md` with guidance for converting short-form mystery scripts into board-driven AI comic / 漫剧 episodes.
- Added `references/25-character-design-sheets.md`, `references/26-scene-design-sheets.md`, `references/27-four-panel-storyboards.md`, and `references/28-board-qc.md`.
- Added reusable templates: `templates/character-design-sheet.md`, `templates/scene-design-sheet.md`, `templates/four-panel-board.md`, and `templates/episode-board-plan.md`.
- Expanded the root skill routing so teams can load comic / storyboard references just-in-time without polluting the main film-production flow.
- Clarified that storyboard panels are planning anchors and do not automatically equal one final edited shot each.
- Added tests covering the published v1.3.0 comic/storyboard references and templates.

## 1.2.0 — 2026-09-02

- Added Content Market Gate and Market MVP contracts before expensive commercial/creator production scale.
- Added explicit `NO_GO`, `TRAFFIC_EXPERIMENT`, `MVP_ONLY`, `PRODUCTION_APPROVED`, and `BYPASS` decisions with validated real-evidence requirements for Production approval.
- Added AI-native content-design and controllability-budget references to prioritize narrative engine, hook/payoff/follow logic, minimal generative burden, and model-evidence-aware prompt control.
- Split generated source duration from edit target duration in v1.2 shot specs.
- Added `eyeline_critical` conditional validation for narrative target shots outside reverse-angle workflows.
- Added traceable `PARTIAL_SELECT` ranges and Select-log validation; downstream observed state is taken from the selected out-point.
- Added Model Profile behavior observations with source generation IDs and evidence-level gating; `OBSERVED_ONCE` cannot be promoted to a default adapter behavior.
- Updated QC, failure recovery, editing, H3 adapter guidance, runtime contract, and primary skill routing from real Pilot lessons without fabricating provider guarantees.
- Expanded authored adversarial eval definitions from 18 to 26; they remain harness demonstrations, not agent benchmark evidence.
- v1.1 runtime manifests/specs remain accepted by the updated validators.

## 1.1.0 — 2026-09-01

- Added an executable project-runtime contract: production state, dependencies, axis registry, voice registry, model profile, and aggregate runtime validation.
- Added Narrative Shot / Generation Unit / Edit Unit separation and a 12-state generation-unit lifecycle.
- Upgraded asset governance with canonical/generic/ephemeral classes, version/hash authority, and explicit state-variant rules while retaining v1.0.1 registry compatibility.
- Upgraded shot validation to adaptive conditional contracts for dialogue, reverse angles, important prop interaction, continuous handoffs, and second-level timing authority.
- Added keyframe-engineering guidance and a structural keyframe prompt linter so invalid start states are rejected before expensive I2V.
- Expanded the MiniMax H3 adapter with evidence-gated R1/R2/R3 reference strategies, a 10-test model-profile schema, mixed-language testing, and semantic reference-role A/B validation.
- Added Voice Passport / dialogue-route / timing-authority guidance so approved external voice can own timing when required.
- Added H3 nine-section prompt linting, single-duration compilation checks, retry-budget guidance, and observed-state writeback before downstream readiness.
- Model-specific smoke results, fresh-context agentic benchmark results, and real multi-project validation remain separate evidence gates and are not fabricated by this release.

## 1.0.1 — 2026-08-28

- Hardened shot-spec transition validation, unique reference bindings, and sequential action-stage IDs.
- Enforced canonical asset authority: CANON assets cannot have parents and variants must parent a CANON directly.
- Hardened continuity checks for screen direction, structured reciprocal eyelines, asset/wardrobe/light/time state, and continuous handoffs.
- Extended prompt linting for Chinese second-level timestamps, `REF_*` role binding, case-insensitive I2V routing, and conflicting multi-move camera paths.
- Updated published templates and regression contracts to match the hardened validators.
- Fresh-context agentic benchmark and real multi-project production validation remain separate evidence gates.

## 1.0.0 — 2026-08-28

- Introduced the FilmFoundry Skills repository and `generative-film-production` primary skill.
- Added model-agnostic Creative Brief → Asset Passport → Canonical Shot Spec → Continuity → Prompt Compiler workflow.
- Added generic and named model adapters for T2V, I2V, first/last-frame, multi-reference, storyboard-to-video, Seedance, MiniMax H3, Veo, Kling, and image generation.
- Added deterministic validators for shot specs, asset registries, compiled prompts, and adjacent-shot continuity.
- Added 12 agentic eval definitions plus deterministic fixture/scoring smoke harness.
- Static/TDD verification is part of v1. Fresh-context agentic benchmark and real multi-project production validation remain separate evidence gates.
