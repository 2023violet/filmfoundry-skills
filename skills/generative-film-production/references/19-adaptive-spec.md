# Adaptive Shot Spec

Completeness means every applicable requirement is explicit—not that every shot copies the same thirty fields and fills irrelevant ones with `none`.

## Always required

Every v1.2 generation unit identifies its narrative shot, generation-unit ID, **generation duration**, **edit target duration**, narrative goal, one dominant action, location, initial state, observable end state, shot size, composition, camera move, action stages/event order, transition, reference bindings, failure risks, and quality bar.

The edit target may be shorter than the generated source. This is intentional: providers generate source material; the edit promotes a valid contiguous `FULL_SELECT` or `PARTIAL_SELECT`.

## Conditional layers

- **Recurring characters present:** character IDs/states, wardrobe, acting, identity authority.
- **Dialogue present:** `voice_id`, `dialogue_route`, `timing_authority`, `speech_intent`.
- **Reverse angle:** axis, canonical screen-side logic, structured reciprocal eyelines.
- **Eyeline-critical shot:** `eyeline_critical: true`, subject, target, screen direction—even if it is not a reverse angle.
- **Important prop interaction:** canonical prop ID, initial state, end state, persistence.
- **Continuous action:** continuity source, prior observed state, visible handoff state.
- **Second-level timing:** hard timing constraint and explicit timing authority.

Use the loosest schema that still makes the actual risk testable. Generic extras and one-off ephemeral props should not be promoted into canonical assets unless persistence matters.

The v1.2 validator keeps legacy v1.0.1/v1.1 specs readable while enforcing v1.2 duration separation and conditional eyeline rules when used.
