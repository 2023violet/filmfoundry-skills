# 24 · Visual Planning Layer

## Purpose

Visual planning is an **optional control layer** between shot engineering and provider prompting. It applies to any AI-video format: 3D animation, 2D animation, photoreal, ad, short drama, MV, documentary-style fiction, comic-like motion, or hybrid editing.

## Core rule

Do not choose a storyboard format first. Choose the **control problem** first.

| Control problem | Preferred artifact |
|---|---|
| Identity/composition already solved | single approved keyframe |
| Start/end physical state matters | first + last authority frames |
| Same location must persist across shots | continuity board / location anchor board |
| A micro-sequence has several visually distinct beats | storyboard / sequence board |
| Exact text/symbol is the only change | deterministic post, no storyboard required |
| Simple T2V concept with low continuity risk | no visual board may be required |

A 2×2 or 3×2 grid is only a convenient review surface. **Panel count is not final shot count, and grid count is not episode duration.**

## Visual Planning Unit

When useful, assign a `visual_plan_id` to a Narrative Beat or Generation Unit. It can contain 1, 2, 4, 6, or more anchors. The planning artifact is not automatically a provider input; the selected Model Adapter decides whether the provider receives one frame, two frames, multiple references, or none.

## Exit condition

A visual plan is successful when it removes the expensive ambiguity that would otherwise be left to the video model.
