# Generation Loop

Log each submission: generation ID, logical shot/stage, model/profile version, compiled prompt hash/version, reference IDs, source generation for extensions, status, and disposition.

Treat queued/processing work as the same job; resume it rather than silently resubmitting. After completion, inspect dependencies before generating downstream chains.

Retries are experiments: state one failure, one hypothesis, one changed variable, and the expected visible improvement. If repeated controlled attempts fail, redesign the shot rather than escalating randomness.
