# MiniMax H3 Adapter

Use the Canonical Shot Spec as authority and compile only capabilities confirmed for the exact MiniMax H3 endpoint/product surface available to the user. Do not hard-code undocumented reference counts, native-audio behavior, duration ceilings, language preference, timing precision, edit-hold precision, or acting stability into the canonical workflow.

## Evidence gate

Before scaling a project around H3, create a dated Model Profile and follow `minimax-h3-smoke-tests.md`. For an unfamiliar surface/version, run the smallest representative smoke tests needed to answer the production risks. The profile enumerates ten tests: single-character micro-motion, environment slow camera, KF+identity, KF+two-character, Chinese dialogue, fixed-camera/no-cut, hand+prop persistence, reverse angle, mixed-language prompt following, and semantic reference-role A/B.

`controls identity only` is a candidate adapter syntax, not a proven H3 capability. Do not depend on it until repeated A/B evidence shows it improves adherence.

## Reference modes

- **R1 Semantic Role Binding:** use only with `REPEATED` or stronger role-binding evidence.
- **R2 Minimal Reference:** default when H3 accepts multiple references but nuanced role semantics are unverified; use the approved keyframe plus the smallest identity/prop set.
- **R3 Precomposed Keyframe:** use when multi-reference interference is high; lock appearance/location/props upstream in a validated keyframe and give H3 one primary visual reference.

For I2V, prioritize one camera logic, one dominant motion/performance task, persistence, expensive locks, and minimal acting change over re-describing the entire start frame. Compile exactly one actual generation duration plan.

## Source-vs-edit strategy

Do not assume the full provider duration must become the edit. If the route offers a ten-second source and the shot only needs a stable five-second beat, set that distinction in the canonical spec and review for a valid contiguous range. A later source failure can become a `PARTIAL_SELECT` only when the selected range independently satisfies narrative, continuity, identity, and quality requirements.

Do not assume precise late deceleration/hold or subtle acting intensity will obey prose unless the exact H3 surface has repeated evidence. If the Model Profile records camera over-push, acting amplification, spatial resets, or another tendency, adapt only at the evidence level allowed by `16-model-evidence.md`.

## Structural prompt contract

Compiled H3 prompts use nine sections:

`REFERENCE BINDING → GLOBAL SHOT → LOCKS → CAMERA → ACTION STAGES + END STATES (or hard TIMING) → ACTING → PHYSICS / PERSISTENCE → AUDIO → FAILURE CONSTRAINTS`

Use `scripts/h3_prompt_lint.py` before generation. The linter validates FilmFoundry structure; it does not claim the model will obey the prompt.
