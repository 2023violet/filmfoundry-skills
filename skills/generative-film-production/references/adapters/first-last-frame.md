# First / Last Frame Adapter

Use start/end frames for one shot that must begin and land on specific visible states. The pair does not imply that every film cut should inherit the prior tail. Ensure the requested motion can plausibly connect the two frames within the supported duration.


## v1.3.2 State-alignment hardening

Before treating a frame or pair as provider authority, verify it is **state-matched** to the Shot Spec for every field it claims to control. A proxy smoke test or partial-authority frame cannot directly unlock a production route when shot-specific state differs.
