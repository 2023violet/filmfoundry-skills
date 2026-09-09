# Model-Agnostic Video Spec

Sort promptable decisions into three scopes:

- **GLOBAL:** whole clip—film type, scene, visual DNA, director premise, camera principle.
- **LOCKS:** identity, count, reference roles, wardrobe/state, prop ownership, axis/direction/eyeline, audio source, must-preserve facts.
- **TIME:** ordered stages, one primary change per stage, observable end state, and only genuine hard clocks.

A line belongs in the narrowest scope that still governs it correctly. Rewrite unverifiable intent as visible evidence. If it cannot be checked after generation, it cannot be debugged reliably.

v1.2 distinguishes **generation duration** from **edit target duration**. The provider source may be longer than the contiguous footage the edit needs. Do not overburden the provider with a perfect full-duration choreography when the shot only needs a stable usable window.

Load `23-controllability-budget.md` when a prompt is becoming long, timing-dense, or behaviorally overloaded.
