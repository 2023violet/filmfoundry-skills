# Shot Engineering

Design the shot before compiling language. Required thinking is physical: who is where, what changes, where the camera is, what lens relationship is intended, how the camera moves through space, what the stage must visibly land on, and which consequences persist.

Separate three IDs:

- **Narrative Shot** (`SH014`): story/edit meaning; does not change when generation is split.
- **Generation Unit** (`SH014_G01`): smallest unit submitted to a generative model; may split when risk is high.
- **Edit Unit** (`SH014_E01_SELECT`): approved whole source or selected source range entering the timeline.

v1.2 also separates **generation duration** from **edit target duration**. A 10-second provider source may legitimately feed a 5-second edit unit if the selected contiguous range passes the shot goal and quality bar.

Prefer one dominant action. Composite camera motion is acceptable only when it behaves as one coherent physical move. When continuity matters, include axis, screen direction, structured eyeline, and persistent prop/state facts. When a character must visibly look at a narrative target, set `eyeline_critical` and define the subject/target/direction even if the shot is not a reverse angle.

Use `../templates/shot-card.md`. For v1.2 projects, apply `references/19-adaptive-spec.md` and validate structured JSON with `../scripts/validate_shot_spec.py`.
