# Model Profile v1.2

Record provider behavior for the exact product surface/version. Do not promote wording assumptions into workflow facts.

## Identity
- Model ID:
- Provider:
- Product surface:
- Version/build:
- Tested date:
- Verification status:

## Reference-role binding
- Evidence level: `UNVERIFIED / OBSERVED_ONCE / REPEATED / PROJECT_VERIFIED / CROSS_PROJECT_VERIFIED`
- Evidence IDs:

## Prompt language strategy
- Instruction language:
- Dialogue language:

## Smoke tests
Record attempts/passes/fails and verdicts for the model-specific smoke plan.

## Behavior observations
For every real production observation record:

- Capability: e.g. `spatial_persistence`, `identity_persistence`, `camera_hold`, `acting_amplification`
- Context: exact route/duration/reference pattern
- Evidence level
- Source generation IDs
- Observation
- Production consequence
- `default_adapter_behavior: true/false`

`OBSERVED_ONCE` is a hypothesis, not a default. Only `REPEATED` or stronger may set `default_adapter_behavior: true`.

## Production summary
- Verified strengths:
- Verified weaknesses:
- Timing behavior:
- Identity behavior:
- Reference behavior:
