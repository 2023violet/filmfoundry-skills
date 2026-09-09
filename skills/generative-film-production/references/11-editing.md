# Editing

Editing consumes approved Selects only. A Select may be a whole source (`FULL_SELECT`) or a traceable contiguous range (`PARTIAL_SELECT`). Raw generation folders never become the timeline contract.

For a partial Select, record source generation ID, filename, in/out seconds, source duration, selected duration, and why excluded footage is not needed. Downstream continuity uses the state visible at the selected out-point, not the raw source clip end.

Use hard cuts by default; use J/L cuts for motivated audio continuity; use transitions only when they express a relationship or hide a necessary seam. Move deterministic fades, dissolves, wipes, crop/reframe, exact speed changes, assembly, and layout to post when a generator adds no unique value. Preserve edit handles around selected clips when possible.

Use `../scripts/validate_selects_log.py` when maintaining a structured Selects CSV.
