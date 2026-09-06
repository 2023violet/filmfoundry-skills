# FilmFoundry Skills v2.0

FilmFoundry v2 is a provider-neutral contract layer for AI video production.
It makes creative decisions inspectable and compilable without claiming that a
provider, model, editor, or human reviewer has completed the work.

The v2 core owns Workspace Manifest, Asset Registry, Canonical Shot Spec,
Prompt Markdown metadata, lifecycle transitions, reference graphs, and
Provider Evidence. Project adapters own local paths, Chinese display names,
credentials, provider APIs, media downloads, and runtime aggregation.

```text
python -m filmfoundry_v2 init --root <workspace>
python -m filmfoundry_v2 validate --root <workspace> --format json
python -m filmfoundry_v2 index --root <workspace>
python -m filmfoundry_v2 compile --prompt <prompt.md> --provider <adapter> --out <payload.txt>
python -m filmfoundry_v2 audit --root <workspace> --kind all
python -m filmfoundry_v2 migrate --root <workspace> --from 1.x --dry-run
```

Markdown is the human authoring authority. JSON and CSV are machine state
authority. Media bytes remain the entity; the registry records measured size,
mode, alpha, profile, and SHA-256. `99_归档` is inventory-only and never
changed by the core migration planner.

Structural validation cannot prove image quality, model obedience, market
performance, audio quality, or publishability. Those remain adapter evidence or
human review gates.
