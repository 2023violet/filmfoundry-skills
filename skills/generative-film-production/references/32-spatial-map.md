# 32 - Spatial Map

## Purpose

Use a Spatial Map when continuity depends on where subjects, props, lights, or
the camera are relative to stable anchors. It turns "keep the geography
consistent" into inspectable relationships.

Each relation records:

- `subject_id`: the moving or framed entity;
- `anchor_id`: a stable person, prop, landmark, or location asset;
- `relation`: beside, in front of, behind, inside, or another visible relation;
- `distance`: a qualitative or measured range;
- `facing`: the subject's facing direction;
- `screen_direction`: the direction retained in the frame;
- `camera_side`: the side of the axis from which the shot is viewed;
- `light_direction`: the relevant key or practical light direction.

## When to use one

Add a map when a reverse angle, entrance/exit, same-location payoff, handoff,
or prop interaction would fail if the relative positions drifted. A simple
single-subject shot may not need one.

Map only the relationships that carry story or edit risk. Do not turn every
background detail into a locked coordinate system. If a relation changes, name
the transition and record the intended end state in the Shot Spec.

## Preflight

1. Confirm every ID resolves to a current asset, Shot Spec subject, or declared
   anchor.
2. Confirm reciprocal relations do not contradict each other.
3. Confirm all reverse-angle views stay on the intended camera side.
4. Confirm screen direction and eyeline agree with the narrative target.
5. Confirm light direction and required location anchors survive the delivery
   crop.

The map represents spatial intent. It does not prove that a provider will
preserve the relation. Record provider results in the evidence register and
keep `UNVERIFIED` behavior out of a default route.

Use `templates/spatial-map.example.json` for the standalone artifact and bind
it through `templates/visual-control-plan.example.json` when several visual
controls belong to one production unit.
