# 25 - Character Reference System

## Principle

Character reference cost must scale with **recurrence, identity risk, costume
continuity, and shot diversity**. Three views and five expressions are useful
tools, not universal mandatory deliverables.

## Suggested tiers

- **Core recurring identity:** face close-up plus front body; add back body,
  turnaround, expressions, costume details, or state variants when the approved
  shot plan actually needs them.
- **Secondary recurring identity:** usually face plus body is enough until an
  episode introduces new angles or acting range.
- **Ephemeral identity:** one stable reference may be enough.
- **Generic extras:** lock visual language, not individual faces.

The `character-reference.example.json` template makes the authority boundary
explicit with `face_closeup_asset_id`, `front_body_asset_id`,
`back_body_asset_id`, `headless_body_strategy`, `controls`, and
`does_not_control`. A headless body reference or neutral-gray identity
background may be a useful experiment, but both remain unverified practices
until the exact provider surface has evidence.

## Reference roles

Each character reference must say what it controls and does not control.
Character sheets control identity and the stated costume/body facts. They do
not control camera, environment, lighting, action, or story state unless a
separate authority frame explicitly precomposes those facts.

## Production test

Stress-test only the angles/actions that the next approved production scope
will use. Avoid building a complete model sheet for a character who does not
yet appear. Record failures as evidence and change one variable per retry.
Before provider use, check that the selected reference's visible state matches
the Shot Spec and the Visual Control Plan.
