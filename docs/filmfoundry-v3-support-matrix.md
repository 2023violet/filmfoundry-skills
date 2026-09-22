# FilmFoundry v3 Support Matrix

> **Status — product reset:** This matrix records the current technical implementation. External provider execution, returned-media evidence, and video-quality gates remain outside the Skill; the Core boundary is the Provider-neutral handoff.

| Area | Status | Boundary |
|---|---|---|
| Workspace, asset, shot, prompt, state, graph contracts | CONTRACTED | Core validates structure and references. |
| Visual Control Plan and visual-control stage | CONTRACTED | Core binds optional controls and reports structural failures; Shot Spec remains unchanged. |
| Character, voice, and location reference records | CONTRACTED | Templates define authority fields; media quality and identity consistency remain separate gates. |
| Spatial Map | CONTRACTED | Subject, anchor, distance, facing, screen direction, camera side, and light direction are explicit facts. |
| Visible scale relation | CONTRACTED | The plan can record a visible subject/reference-object relation; provider obedience still needs evidence. |
| Physics result cues | HUMAN_REVIEW | Force, material, weight, inertia, gravity, and observable result are representable; realism is not structurally proven. |
| Previsualization route | UNVERIFIED | A short establishment pass may help some routes; no provider capability is assumed. |
| Lens/FOV guidance with visible result | HUMAN_REVIEW | Numeric FOV must be paired with an observable framing result. |
| Provider-neutral handoff compilation | CONTRACTED | Core emits deterministic handoff sections; an external adapter may translate them. |
| Image/video/audio provider execution | EXTERNAL_REQUIRED | Requires the selected external provider. |
| NLE, encoding, publishing | EXTERNAL_REQUIRED | Core records evidence only. |
| Visual quality, identity consistency, aesthetic Select/QC | HUMAN_REVIEW | Structural validation cannot prove quality. |
| Neutral-gray identity background causal benefit | UNVERIFIED | Requires a controlled A/B experiment. |
| Headless body reference causal benefit | UNVERIFIED | Requires a controlled comparison on the exact provider surface. |
| Three-quarter location view causal benefit | UNVERIFIED | Requires a controlled comparison; geometry remains a human review concern. |
| Small-team operating mode | DOCUMENTED | Progressive references reduce handoffs without relaxing authority or evidence gates. |

Statuses describe the repository boundary. `CONTRACTED` means the fact can be
represented and checked structurally; it does not mean a provider will follow
it. `UNVERIFIED` practices remain experimental, and `HUMAN_REVIEW` results
require a reviewer before promotion.
