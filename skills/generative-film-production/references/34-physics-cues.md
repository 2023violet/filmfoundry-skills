# 34 - Physics Cues

## Purpose

Physics cues describe the visible response that makes an action credible. They
are compact production instructions, not a simulation claim.

For each important interaction, state:

- `material`: what is moving or being contacted;
- `force`: the source and direction of the force;
- `weight`: how heavy the subject should appear;
- `inertia`: delay, resistance, or momentum;
- `gravity`: the persistent downward or hanging behavior;
- `observable_result`: the single result a reviewer must be able to see.

Prefer a concrete result over a stack of adjectives. "A wet coat drags behind
the turn and settles after the body stops" is more reviewable than "realistic
cinematic motion."

## Use one cue per risky interaction

Add physics cues for doors, cloth, hair, loose debris, liquid, heavy props,
falls, impacts, or other interactions whose failure changes the story. Keep
the dominant action singular and describe the consequence that must persist
into the next cut.

Separate authored intent from observed behavior. A human reviewer may mark a
result as plausible or failing, but a cue alone cannot prove material realism
or unlock a provider route. Register experiments when the behavior matters to
production.

## Preflight

- The force has a visible source.
- The material response matches the stated weight and inertia.
- Gravity affects the result where it should.
- The observable result is one clear acceptance check.
- Unverified provider behavior remains a warning or blocked route according to
  the selected capability gate.

Use `templates/physics-cues.example.json` for standalone cues and bind the
array through `templates/visual-control-plan.example.json`.
