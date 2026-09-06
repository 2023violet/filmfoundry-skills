# 29 · Capability-Scoped Model Gates

## Problem

A global “model passed everything” gate is often too expensive and logically wrong. A fixed-camera single-character I2V shot does not need evidence for multi-character dialogue, reverse angles, or complex first/last transitions.

## Rule

Gate each Generation Unit by the **capabilities its route actually requires**.

Example capability IDs:
- `FIXED_CAMERA_STABILITY`
- `IDENTITY_MICROMOTION`
- `HAND_PROP_PERSISTENCE`
- `FIRST_LAST_STATE_TRANSITION`
- `MULTI_REFERENCE_IDENTITY`
- `DIALOGUE_LIPSYNC`

A provider can have a broad Model Profile while individual units consume only a subset.

## Evidence levels

- `UNVERIFIED`: route blocked except explicit smoke test.
- `OBSERVED_ONCE`: pilot-only, not a global default.
- `REPEATED_LOCAL`: eligible for the scoped route in this project.
- `STRONG`: reusable default for the same provider surface/version within stated limits.

## Pilot rule

A pilot may start when **all capabilities required by that pilot route** meet the project’s minimum evidence level. Unrelated tests can remain pending.

## Change rule

Changing provider surface/version invalidates only the capabilities whose evidence may no longer transfer; do not rewrite story/shot canon because the model changed.


## v1.3.2 State-alignment hardening

Before treating a frame or pair as provider authority, verify it is **state-matched** to the Shot Spec for every field it claims to control. A proxy smoke test or partial-authority frame cannot directly unlock a production route when shot-specific state differs.
