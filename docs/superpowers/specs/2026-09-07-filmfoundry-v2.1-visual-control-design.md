# FilmFoundry v2.1 Visual Control Extension

## Purpose

FilmFoundry v2.1 adds provider-neutral artifacts for facts that materially affect visual continuity: character references, voice passports, location references, spatial maps, scale evidence, physical motion cues, previsualization and lens results.

The extension does not claim that a provider will follow these controls. Structural requirements are errors. Unverified creative practices are warnings and must earn higher evidence levels through recorded experiments and human review.

## Boundaries

- Core Shot Spec remains unchanged; a project links a visual-control artifact through a namespaced extension.
- Provider adapters compile and validate payloads, but network execution remains external.
- Prompt Markdown and Canon remain authoring authorities. Generated payloads cannot write back to either.
- Stable machine identifiers use ASCII. Projects may use localized display names and filenames.
- Archive boundaries declared by the workspace manifest are read-only.

## Contracts

`VisualControlPlan` binds one production unit to optional character, location, space, scale, physics, previs and lens controls. Every referenced asset remains accountable to the Asset Registry. The artifact is strict: unknown fields are rejected except under `project:<name>` and `provider:<name>` extension namespaces.

Alignment validates that Shot start/end state and camera-side facts do not conflict with the plan. It does not advance lifecycle state or bypass Provider Evidence.

Compilation appends visual facts in a deterministic order and records both the plan hash and source prompt hash. Lens controls include an observable framing result; numeric FOV alone is insufficient guidance.

## Evidence

Gray backgrounds, headless body references, 3/4 location views, previsualization, FOV guidance and physics wording enter the register as `UNVERIFIED` or `HUMAN_REVIEW`. A single reviewed result can become `OBSERVED_ONCE`; it cannot establish default capability or unlock a production route.

## Compatibility

FilmFoundry v1.3.3 remains an immutable compatibility checkpoint. v2.1 extends the v2 package and CLI without changing legacy fixtures or provider-specific behavior. Wucheng consumes the extension through its project adapter while preserving Canon, Runtime state, media entities and `99_归档`.
