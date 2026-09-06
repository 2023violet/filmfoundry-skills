# 31 · Visual Control State Alignment

## Purpose

An approved image can be beautiful, canonical, and still be the **wrong state for a provider input**. This layer checks whether the visible state in a keyframe, First frame, Last frame, or board actually matches the Shot Spec role assigned to it.

## Core rule

**Asset approval is not the same as route-state approval.** A keyframe may be a partial authority. For example, it may correctly control location geometry while the lantern, wardrobe state, door state, or character pose does not match the required start state.

Before provider submission compare:
- expected initial/end state from the Canonical Shot Spec;
- observed visual state in the control asset;
- which fields the asset is authoritative for;
- which mismatches require a targeted repair, deterministic composite, different route, or dynamic handoff from a prior Select.

## First/Last discipline

A First/Last pair should isolate the intended dominant transition. If the pair changes the door **and** lantern state **and** camera framing, then the test is multi-variable and cannot cleanly prove the intended transition. It may still be useful as a stress test, but label it as a proxy/stress test rather than direct production-route evidence.

## Partial authority examples

- A locked environment frame can control the restored wall while not controlling a character's lantern state.
- A relight frame can control hand/lantern geometry after ignition while being invalid as an OFF start frame.
- A wide composition master can control location and screen direction while not controlling final 9:16 framing.

## Proxy smoke rule

A provider smoke test with proxy inputs proves only the behavior actually observed on those inputs. It does **not** automatically unlock a production route whose shot-specific prop/location/state contract differs. Use the proxy to decide whether a targeted route pilot is worth paying for.

## Exit condition

A provider route may leave preflight only when every visual authority required by that route is state-matched for the fields it claims to control, or the mismatch is explicitly handled by a deterministic/hybrid edit plan.
