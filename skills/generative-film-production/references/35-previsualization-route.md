# 35 - Previsualization Route

## Purpose

Previsualization is an optional route for resolving spatial, camera, timing,
or blocking ambiguity before expensive final generation. It may be a short
establishment pass, a board of reviewed anchors, a blocking video, or a simple
camera/subject diagram.

Previsualization is a planning or review artifact by default. It does not
automatically become a final shot, a provider input, or a production Select.
The selected adapter and the evidence register decide whether a provider route
can consume it.

## Choose the smallest route

- **No previs:** use when the Shot Spec already resolves the control problem.
- **Single anchor:** use for one composition, identity, or eyeline decision.
- **First/Last pair:** use when two physical states must be authoritative.
- **Short establishment pass:** use when location, blocking, or camera path is
  the expensive ambiguity.
- **Board or diagram:** use when several beats need human comparison without
  paying for a final clip.

Record the purpose, production unit, state alignment, initial state, end state,
observable result, review status, and what the artifact does not control. Keep
route assumptions explicit. A short establishment pass does not prove that the
same provider will preserve every downstream identity, prop, or physics
condition.

## Lens result

When framing depends on lens behavior, record `fov_degrees` or
`focal_length_mm` together with an `observable_framing` result. "40 degrees"
alone is not a reviewable framing contract; state what remains visible, how
perspective reads, and whether the intended crop holds.

## Review gate

Review spatial persistence, screen direction, eyeline, state, camera motion,
and crop against the Shot Spec. If the previs is only a proxy smoke test, label
it `UNVERIFIED` or `OBSERVED_ONCE` and keep production-route approval separate.
Do not multiply panels or previs duration into final shot count or episode
runtime.

Use `templates/previsualization.example.json` for a standalone record and bind
it under `previsualization` in `templates/visual-control-plan.example.json`.
