# MiniMax H3 Evidence Smoke Tests

Use this plan when an H3 product surface/version is new, changed, or still marked `UNVERIFIED`. These tests collect provider evidence; they do **not** prove general H3 behavior beyond the exact surface/version tested.

## Test discipline

- Freeze the exact endpoint/product surface, visible settings, duration, aspect ratio, model version label, and input assets.
- Use the smallest representative clips possible.
- Change one variable in A/B comparisons.
- Record attempts, passes, failures, raw observations, and artifacts in the Model Profile.
- Do not promote a behavior to a default adapter rule from a single attractive output.

Evidence remains `UNVERIFIED` until a test is actually run. Use the project evidence ladder: `UNVERIFIED → OBSERVED_ONCE → REPEATED → PROJECT_VERIFIED → CROSS_PROJECT_VERIFIED`.

## TEST_H3_01 — Single-character I2V micro-motion

Question: does one approved keyframe preserve identity during restrained motion?

Hold camera and scene simple. Evaluate face, age, wardrobe, anatomy, unwanted pose drift, and automatic cuts.

## TEST_H3_02 — Environment slow camera

Question: can H3 perform one slow camera move without terrain/architecture morphing?

Use a static environment keyframe and one slow push or slide. Evaluate geometry persistence and camera compliance.

## TEST_H3_03 — Keyframe + identity reference

Question: does adding one identity reference improve recurring-character identity relative to keyframe-only I2V?

Run A/B with the same keyframe, prompt, settings, and seed behavior where available:
- A: keyframe only
- B: keyframe + identity reference

## TEST_H3_04 — Keyframe + two characters

Question: can H3 preserve two identities, exact character count, and screen sides?

Keep actions minimal. Reject character merging, swaps, duplicates, or axis drift.

## TEST_H3_05 — Chinese dialogue

Question: how well does the exact tested surface handle one short Chinese spoken line?

Evaluate wording, pronunciation, lip behavior, identity stability, and whether dialogue degrades motion/camera compliance.

## TEST_H3_06 — Fixed camera / no automatic cut

Question: does an explicit fixed-camera, one-shot instruction prevent reframing or auto-cutting?

Use one small subject action and inspect the full clip, not just first/last frames.

## TEST_H3_07 — Hand + persistent prop

Question: can a character interact with one canonical prop while its geometry and ownership remain stable?

Record hand anatomy, prop deformation, disappearance, duplication, and ownership changes.

## TEST_H3_08 — Reverse angle

Question: can an independently composed reverse angle preserve axis, reciprocal eyelines, identity, wardrobe, and prop state without blindly chaining the prior tail frame?

Use an Axis Registry entry as authority.

## TEST_H3_09 — Mixed-language prompt

Question: does the tested surface reliably follow structured instructions when control prose and Chinese dialogue use different languages?

Compare against the best single-language control if practical. Record instruction omissions and dialogue-language errors.

## TEST_H3_10 — Reference Role Binding A/B

This is the critical test for **Reference Role Binding** semantics.

Use the exact same references and generation settings.

**A — unlabeled/minimally labeled references**

Provide the references without semantic ownership prose.

**B — explicit semantic roles**

For every pointer, state both a positive role and a boundary, for example:

```text
@图1 controls composition only; does_not_control motion.
@图2 controls geography only; does_not_control composition.
```

Compare at minimum:
- intended face/identity adherence
- wardrobe/prop adherence when applicable
- background/composition contamination
- cross-reference interference

Only enable adapter mode `R1` when repeated A/B evidence shows a stable advantage. Otherwise keep the behavior `UNVERIFIED`/insufficient and use `R2` Minimal Reference or `R3` Precomposed Keyframe.

## Recording result

For each test store:

```yaml
test_id:
model_version:
product_surface:
input_asset_versions:
prompt_version:
attempts:
passes:
fails:
observations:
verdict: UNVERIFIED | VERIFIED | PARTIAL | FAIL
artifacts:
```

A smoke-test verdict is model evidence, not a film-quality score. Visual storytelling, acting quality, pacing, audio mix, and editability still require human review.
