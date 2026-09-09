# Generation Loop

Log each submission: generation ID, narrative shot, generation unit, model/profile version, compiled prompt hash/version, input asset IDs/versions, source generation for extensions, status, disposition, and observed state writeback.

Treat queued/processing work as the same job; resume it rather than silently resubmitting. After completion, inspect dependencies before generating downstream chains.

## Review the source before deciding to retry

Review full playback with timestamps. A late failure does not automatically invalidate an earlier contiguous range. If a range alone satisfies the narrative goal, quality bar, and downstream continuity needs, promote it as `PARTIAL_SELECT`, record source in/out, and write observed state at the selected out-point. Do not regenerate merely to make unused source footage perfect.

If no valid range exists, retries are experiments: state one failure, one evidence-based hypothesis, one changed variable, and which variables remain fixed. Use a practical retry budget: attempts 1–3 are normal controlled diagnosis; attempts 4–5 require simplification of action/reference/camera/dialogue burden; a sixth repeated failure blocks the current route and triggers a split or route redesign instead of blind sampling.

Promote only approved full or partial outputs to Selects, then write their observed state before declaring downstream continuity ready.
