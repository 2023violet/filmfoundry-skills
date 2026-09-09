# FilmFoundry Skills v3.0 User Guide

FilmFoundry v3 is a provider-neutral contract layer for AI video production.
It makes creative decisions inspectable and compilable without claiming that a
provider, model, editor, or human reviewer has completed the work.

The v3 core owns Workspace Manifest, Asset Registry, Canonical Shot Spec,
Prompt Markdown metadata, lifecycle transitions, reference graphs, and
Provider Evidence. Project adapters own local paths, display names,
credentials, provider APIs, media downloads, and runtime aggregation.

```text
python -m filmfoundry init --root <workspace>
python -m filmfoundry validate --root <workspace> --format json
python -m filmfoundry index --root <workspace>
python -m filmfoundry route --request "<request>" --format json
python -m filmfoundry compile --prompt <prompt.md> --provider <adapter> --out <payload.txt>
python -m filmfoundry render --root <workspace> --out <render-dir> --format json
```

Markdown is the human authoring authority. JSON and CSV are machine state
authority. Media bytes remain the entity; the registry records measured size,
mode, alpha, profile, and SHA-256. The declared archive boundary is read-only
and never changed by the core package. One-time migration tooling belongs to a
consuming project and is not part of the v3 runtime.

Structural validation cannot prove image quality, model obedience, market
performance, audio quality, or publishability. Those remain adapter evidence
or human review gates.

## Visual-control workflow

1. Resolve the Shot Spec and identify the visible fact that would be expensive
   to leave ambiguous.
2. Use `references/36-visual-control-decision-tree.md` to select the smallest
   control artifact. Use `templates/visual-control-plan.example.json` when
   several controls belong to one production unit.
3. Bind current Asset Registry IDs and state the `controls` and
   `does_not_control` boundary for every reference.
4. Validate the workspace with
   `python -m filmfoundry validate --root <workspace> --stage visual-control`.
5. Compare the visible start/end state with the Shot Spec. Resolve a mismatch
   before provider submission, or record the deterministic/hybrid handoff.
6. Compile with `--visual-control` only after the plan is structurally valid.
   Compilation appends deterministic control sections and records the plan
   hash; it does not mutate the Markdown authoring source.
7. Record provider output, human review, and evidence level separately. An
   `UNVERIFIED` or `OBSERVED_ONCE` result remains scoped to the tested route.

## Artifact guide

| Need | Start with |
|---|---|
| Recurring identity | `templates/character-reference.example.json` |
| Recurring voice/timing | `templates/voice-passport.example.json` |
| Recurring location | `templates/location-reference.example.json` |
| Subject/anchor geography | `templates/spatial-map.example.json` |
| Visible size relationship | scale entries in `visual-control-plan.example.json` |
| Physical motion result | `templates/physics-cues.example.json` |
| Blocking or camera ambiguity | `templates/previsualization.example.json` |
| Lens/framing result | `lens_result` in `visual-control-plan.example.json` |
| Route selection | `references/36-visual-control-decision-tree.md` |

The controls are optional. A simple shot can remain on the core Shot Spec
workflow, while a recurring or state-sensitive shot can opt into only the
facts that carry continuity risk.
