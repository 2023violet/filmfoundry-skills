# Project and Style Profiles

Profiles keep reusable Core contracts separate from project and visual choices. They
are routing and compilation inputs, not a replacement for Canon, Runtime, or Gate.

## Project Profile

Use when the medium, audience, delivery format, target duration, production scope, or
continuity burden affects the workflow. Keep it short and explicit:

```yaml
project_profile:
  project_id: example-project
  medium: narrative_short
  audience: general
  target_duration: 30s
  production_scope: teaser
  continuity_level: high
  delivery_aspect: 9:16
```

Project Profile may select a lighter or deeper route, but it must not create project-
specific branches in Core or override approved story facts.

## Style Profile

Use when the visual language changes. Separate observable style choices from story
facts:

```yaml
style_profile:
  visual_language: cinematic_realism
  palette: muted_warm
  texture: restrained_film_grain
  lighting: motivated_practical
  camera_behavior: observational
  motion_density: low
  composition: balanced
```

For another style, change the profile rather than rewriting the asset, shot, or Gate
contracts. Style may change material, color, texture, lighting, camera behavior, and
motion density; it may not silently change identity, count, blocking, continuity, or
required visible facts.

## Routing rules

- No profile is needed for a one-off creative draft unless the user supplies a delivery
  constraint.
- Create a Project Profile before scaling assets or shots.
- Create a Style Profile before comparing visual variants or compiling a style-sensitive
  prompt.
- Record deliberate profile changes as versioned decisions with provenance.
- Treat missing profile values as `UNKNOWN` or `ASSUMPTION`, never as hidden defaults.

The Core ships JSON examples at
`templates/project-profile.example.json` and
`templates/style-profile.example.json`. When compiling a handoff, pass them with
`--project-profile` and `--style-profile`; the compiler records the values as
inputs and never promotes them to Canon.
