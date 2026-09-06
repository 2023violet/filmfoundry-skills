# Model Evidence

Treat provider/model behavior as evidence, not lore. A statement such as “this model understands reference roles,” “ten seconds remain spatially stable,” or “the final second will hold” is not a canonical production rule until the exact provider surface/version has repeated evidence.

## Evidence levels

`UNVERIFIED → OBSERVED_ONCE → REPEATED → PROJECT_VERIFIED → CROSS_PROJECT_VERIFIED`

Only `REPEATED` or stronger evidence should become a default adapter behavior. Keep single observations as hypotheses.

## Behavior observations

v1.2 Model Profiles may record real production observations such as:

- spatial persistence / mid-clip scene reset;
- identity persistence;
- camera instruction adherence;
- edit-hold/deceleration adherence;
- acting amplification;
- hand/prop persistence;
- reference contamination.

Every evidenced observation records source generation IDs, exact context, evidence level, observation, and production consequence. `OBSERVED_ONCE` may justify the next controlled experiment; it may not be marked as a default adapter behavior.

## Capability smoke tests

When a model is central to a project, run the smallest representative tests needed before scaling. For MiniMax H3, the bundled profile expects ten tests covering:

1. single-character I2V micro-motion
2. environment slow camera move
3. keyframe + identity reference
4. keyframe + two characters
5. one Chinese dialogue line
6. fixed camera / no automatic cuts
7. hand + persistent prop
8. reverse-angle continuity
9. mixed instruction language + Chinese dialogue
10. semantic reference-role binding A/B

The tenth test is critical: compare identical references with and without role-language. If the role-language does not produce repeatable improvement, do not depend on it in the adapter.

## Adapter consequence

A model adapter must degrade gracefully:

- **R1 Semantic Role Binding:** only when role binding has repeated-or-stronger evidence.
- **R2 Minimal Reference:** use the smallest sufficient reference pack without depending on nuanced role semantics.
- **R3 Precomposed Keyframe:** move identity/style/location/prop locking upstream into a validated keyframe and give video generation only that frame when multi-reference interference is high.

Unknown means unknown, not unsupported and not supported.
