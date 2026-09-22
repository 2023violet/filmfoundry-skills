# Keyframe Engineering

A video model should not be asked to rescue a bad visual start state. For I2V, treat approved keyframes as a production gate between the Canonical Shot Spec and video generation.

## Keyframe routes

- **Fresh composition:** new scene, new time, or establishing frame.
- **Continuity-informed:** use prior observed state without necessarily copying the prior tail frame.
- **Reverse angle:** rebuild composition from axis, eyelines, location, and character authority; do not use the previous tail as composition master.
- **Insert:** isolate a prop/hand/detail as its own composition.
- **State variant:** use the correct visible state asset rather than prompting against a contradictory canon reference.

## Keyframe compiler contract

A compiled keyframe prompt should contain:

`REFERENCE BINDING → SHOT / UNIT → VISUAL STYLE → CHARACTER LOCK → LOCATION LOCK → PROP LOCK → SHOT SIZE + PHYSICAL CAMERA → COMPOSITION → BLOCKING → ACTION MOMENT → ACTING → LIGHTING → CONTINUITY INPUT → MUST PRESERVE → FAILURE CONSTRAINTS`

`ACTION MOMENT` is one still moment, not a timeline. Do not leak multi-stage video instructions into the keyframe prompt.

## Eyeline-critical keyframes

Identity correctness is not enough when the shot narrative depends on a character looking at a place, person, prop, screen, or off-screen event. Set `eyeline_critical: true` and explicitly define subject, target, and screen direction. QC the visible relation **subject → target** before aesthetics.

A frame-right character whose narrative target is frame-left but whose eyes/face point frame-right is a keyframe failure even if the image is beautiful. Repair upstream; do not expect I2V text to reverse a contradictory start frame reliably.

## Keyframe QC

Review identity, character count, state variant, wardrobe, prop state, location geometry, narrative target/eyeline, axis, screen side, composition, acting, anatomy/hands, lighting, and edit continuity. Reject before video generation on identity swaps, wrong state variants, wrong count, wrong eyeline/side logic, key prop errors, or architecture redesign.

### Shot Spec alignment and subject–scene integration

Before visual review, compare the compiled frame against the approved Shot Spec's
initial state, shot size, camera move, action moment, and reference bindings. Record
any intentional deviation as a human decision; do not silently replace a state with a
more convenient portrait composition.

For a frame that places a character into a location, run a subject–scene integration
pass in addition to identity review. Check that the subject and environment share a
plausible common light (direction, relative exposure, and color), coherent scale and
occlusion, compatible focus/depth characteristics, and believable contact with
surfaces, glass, props, or openings. Check the requested action moment, not only a
clear face. If these checks fail, the frame is not an approved keyframe.

The best-of-batch candidate is only the relative best until it passes the same
approval bar as a standalone candidate. A batch may have no approved frame.

Use `scripts/keyframe_prompt_lint.py` before expensive I2V generation.


## v1.3.2 State-alignment hardening

Before treating a frame or pair as provider authority, verify it is **state-matched** to the Shot Spec for every field it claims to control. A proxy smoke test or partial-authority frame cannot directly unlock a production route when shot-specific state differs.
