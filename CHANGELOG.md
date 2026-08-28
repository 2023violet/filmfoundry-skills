# Changelog

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
