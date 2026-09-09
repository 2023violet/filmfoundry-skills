# Runtime Contract

Use a project runtime when a generative production has multiple recurring assets, generation units, dependencies, retries, or handoffs. Markdown explains intent; runtime files hold current facts.

## Runtime artifacts

- `project-runtime.json` points to every authoritative runtime file.
- `content-market-gate.json` is required in v1.2 runtime for commercial/series project goals.
- `production-state.json` records each generation unit's lifecycle state and selected artifacts.
- `asset-registry.csv` records canonical, generic, and ephemeral asset authority.
- `axis-registry.json` records reusable camera-axis and reciprocal eyeline rules.
- `voice-registry.json` records locked voice identity and measured speech-rate evidence.
- `dependency-graph.json` separates design readiness from upstream runtime dependencies.
- `model-profile.json` records dated model evidence and optional behavior observations.

The bundled validators use JSON/CSV so the skill remains Python-standard-library-only. YAML may be used in another host only if that host converts it into the same data contract before validation.

## Project market state is not shot runtime state

Commercial/series work follows a project-level gate:

`IDEA → MARKET_GATE_RESOLVED → MVP_READY → MVP_TESTING → MVP_EVALUATED → PRODUCTION_APPROVED`

This is separate from generation-unit lifecycle. An MVP may create generation units before Production approval; the point is to avoid scaling expensive canon/shot volume until market evidence exists.

## State is not dependency

A unit can be design-ready while runtime-blocked by an upstream Select, axis, asset, or voice. Store these separately.

The canonical generation-unit lifecycle remains:

`DRAFT → SPEC_RESOLVED → PREFLIGHT_PASS → READY_FOR_KF → KF_GENERATED → KF_QC_PASS → READY_FOR_VIDEO → VIDEO_GENERATED → VIDEO_QC_PASS → SELECT → OBSERVED_STATE_RECORDED → EDIT_READY`

`PARTIAL_SELECT` is **not** a runtime state. It is a selection disposition inside `video.selected`. A Select is not edit-ready until observed state is written at the selected out-point.

## Runtime preflight

Before generation, validate the manifest and hard dependencies. A runtime may initialize with an unverified model profile, but a generation unit must not reach `READY_FOR_VIDEO` on model folklore alone.

For v1.2 commercial/series project goals, the runtime manifest must point to a valid Content Market Gate. Use:

```bash
python scripts/validate_content_market_gate.py templates/content-market-gate.example.json
python scripts/validate_project_runtime.py templates/project-runtime.example.json
```
