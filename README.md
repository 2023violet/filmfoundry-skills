# FilmFoundry Skills

**Repository:** `filmfoundry-skills`  
**Primary skill:** `generative-film-production`  
**Version:** 1.0.1

FilmFoundry Skills is a production-oriented Agent Skill suite for AI filmmaking. Its first skill separates creative intent, recurring-asset identity, shot engineering, continuity, model capabilities, prompt compilation, generation retries, editing, audio, and QC so that changing a video model does not require rebuilding the production method.

## Why the public name is different from the skill ID

`FilmFoundry Skills` is the umbrella project and GitHub repository name. The installable skill uses the descriptive ID `generative-film-production` so agents can discover it from ordinary requests such as “make an AI short film”, “keep this character consistent”, “write a Kling/Veo/Seedance/MiniMax prompt”, or “fix continuity between these shots”.

The name `filmfoundry-skills` was checked against GitHub repository search on 2026-08-28 and returned no repository match at that time. GitHub names are global only within an owner namespace, so this is a collision check, not a reservation.

## Status

| Layer | Status |
|---|---|
| Repository/Skill contract tests | **Static verified** |
| Shot-spec, asset, prompt, continuity validators | **Static verified** |
| Eval metadata and deterministic fixture harness | **Static verified** |
| Fresh-context no-skill vs with-skill Agentic benchmark | **Pending** |
| Real multi-project production validation | **Pending** |

The authored files in `evals/fixtures/` are **not agent benchmark results**. They exist only to prove the deterministic eval scorer behaves correctly. Do not cite fixture scores as evidence that the skill improves a model.

## Core idea

> **Spec before prompt.**

A prompt is the compiled output of upstream production decisions. FilmFoundry keeps those decisions in reusable artifacts:

```text
Creative Brief
→ Story Breakdown
→ Reference Board
→ Asset Passport + Stress Test
→ Canonical Shot Spec
→ Continuity Ledger
→ Model Adapter / Model Profile
→ Compiled Prompt
→ Controlled Generation Loop
→ Selects
→ Edit / Audio / Captions
→ Final QC
```

## Repository layout

```text
filmfoundry-skills/
├── skills/
│   └── generative-film-production/
│       ├── SKILL.md
│       ├── references/
│       │   └── adapters/
│       ├── templates/
│       └── scripts/
├── evals/
│   ├── evals.json
│   ├── fixtures/
│   └── README.md
├── scripts/
├── tests/
└── docs/superpowers/
```

## Install

Copy `skills/generative-film-production/` into the Agent Skills directory used by your runtime. Common runtimes recognize a `SKILL.md` directory; exact installation paths vary by host.

The skill itself has no Python runtime dependency. The validators use Python 3.11+ standard library only.

## Validate the repository

```bash
python -m pytest -q
python skills/generative-film-production/scripts/validate_shot_spec.py \
  skills/generative-film-production/templates/shot-spec.example.json
python skills/generative-film-production/scripts/validate_asset_registry.py \
  skills/generative-film-production/templates/asset-registry.example.csv
python scripts/validate_evals.py evals/evals.json
```

## Agentic evals

The 12 cases in `evals/evals.json` test decisions that commonly fail in generative-video workflows: overstuffed clips, recurring-character locking, unlabeled references, dialogue axis, I2V over-description, timing granularity, lip-sync clocks, reverse-angle continuity, persistent props, exact generated text, Selects discipline, and the transition from generation to finishing.

Run each case twice in a fresh context—without and with the skill—using the same model and settings. Keep human visual/production judgment separate from machine-readable signal assertions. See `evals/README.md`.

## Design sources

The v1 architecture was distilled from 52 public/official Agent Skills and production references, including Anthropic Skills, Remotion Skills, Atlas universal-video/Seedance skills, Film Studio Skills, Generative Media Skills, and additional corpus-derived skills. The research/design record is preserved under `docs/superpowers/specs/`.

## License

MIT. See `LICENSE`.
