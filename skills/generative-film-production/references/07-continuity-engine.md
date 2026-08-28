# Continuity Engine

Track continuity as explicit state, not resemblance alone. The ledger records shot IDs, transition type, camera axis, canonical screen-side logic, structured eyelines, asset/wardrobe state, important prop state, light/time state, and the exact handoff.

## Structured reverse-angle fields

For `reverse_angle`, do not compare prose such as `A looks screen right` against `B looks screen left` as literal strings. Record the physical relationship explicitly:

- `camera_axis`: canonical dialogue/action axis; it must not change across the cut.
- `screen_direction`: canonical side map such as `A:left|B:right`; keep this identical across the pair.
- `eyeline_subject`: the person whose look is described in this shot.
- `eyeline_target`: the person/object being looked at.
- `eyeline_screen_direction`: `left`, `right`, or `center`.

A valid dialogue reverse is reciprocal: if shot A records `A -> B / right`, the reverse should record `B -> A / left`. The validator checks reciprocal subject/target and opposite screen direction rather than requiring the human-readable `eyeline` sentence to be identical.

## Stateful continuity fields

Use explicit values, including `none` when a category is intentionally empty:

- `asset_state`: canonical/state-variant IDs currently visible, e.g. `CHAR_A:CANON`.
- `wardrobe_state`: visible wardrobe condition, e.g. `robe:dry`.
- `prop_state`: ownership and persistent prop condition.
- `light_state`: stable lighting state for the moment.
- `time_state`: story time / time-of-day state.

`continuous` transitions require `asset_state`, `wardrobe_state`, `light_state`, and `time_state` on both rows and require equality. `reverse_angle` represents the same story moment, so it also requires these state fields and preserves them across the cut.

## Transition rules

- `continuous`: tail relay is allowed; next initial state must equal prior visible end state, and state fields must match.
- `hard_cut`: no pixel inheritance requirement; preserve only story-state invariants relevant to the intended cut.
- `reverse_angle`: preserve axis, canonical side logic, reciprocal eyelines, prop state, asset/wardrobe state, light, and time; intentionally redesign composition.
- `match_cut`: define the matched feature explicitly.
- `insert`: inherit only stateful prop facts required for recognition.
- `cutaway`: may leave the current axis, but must return with story-state continuity intentionally managed.

Tail-frame chaining across every cut reduces shot freedom and often creates accidental pseudo-continuity. Use it only when physical continuity requires it.
