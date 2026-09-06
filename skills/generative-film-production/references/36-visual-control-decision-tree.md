# 36 - Visual Control Decision Tree

## Decision order

Start with the approved Shot Spec and ask which visible fact is most expensive
to leave ambiguous:

```text
SHOT SPEC
  |
  +-- recurring identity or costume? --> Character Reference
  |
  +-- recurring location or geometry? --> Location Reference
  |                                      + Spatial Map if relations matter
  |
  +-- size relationship must read? --> Scale Reference
  |
  +-- material response changes the beat? --> Physics Cue
  |
  +-- start/end physical states differ? --> First/Last or state-matched keyframe
  |
  +-- camera/blocking remains ambiguous? --> Previsualization
  |
  +-- framing depends on lens behavior? --> Lens result with visible outcome
  |
  +-- no material continuity risk? --> No extra control artifact
```

Choose the smallest artifact that resolves the actual risk. A Visual Control
Plan can bind several optional controls to one production unit, but empty or
irrelevant controls should remain absent.

## Gate sequence

1. Name the control problem and the expected visible result.
2. Bind only the assets and relations required by that problem.
3. Record `controls` and `does_not_control` for each authority.
4. Compare visible start/end state with the Shot Spec.
5. Check provider evidence for the selected route and capability.
6. Run human review where the result is aesthetic, physical, or otherwise not
   structurally provable.
7. Record the result and evidence level before promoting a route.

`UNVERIFIED` means the control can describe intent but cannot unlock a default
provider behavior. `OBSERVED_ONCE` can support a controlled pilot and remains
scoped to the observed surface and inputs. Keep the plan, provider payload,
and evidence record as separate artifacts.

Use `templates/visual-control-plan.example.json` as the binding artifact and
the focused templates for each selected control.
