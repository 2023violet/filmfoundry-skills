# Provider-neutral Handoff

FilmFoundry first emits a provider-neutral handoff. It is the stable boundary between
creative/production decisions and an external generation tool.

## Required sections

```text
REFERENCE BINDING
PROJECT / STYLE PROFILE
SHOT / GENERATION UNIT
SUBJECTS AND IDENTITY LOCKS
LOCATION AND SPATIAL LOCKS
PROP / STATE LOCKS
DOMINANT ACTION
CAMERA AND COMPOSITION
LIGHTING AND PHYSICAL CUES
CONTINUITY INPUT
OBSERVABLE END STATE
MUST PRESERVE
FAILURE CONSTRAINTS
ACCEPTANCE CHECKS
```

Each statement must be traceable to the Shot Spec, a profile, a reference, or a
declared assumption. Do not add provider folklore while compiling the handoff.

## Adapter boundary

An external adapter may translate section names, syntax, parameters, reference slots,
duration limits, and known evidence-backed quirks for one exact provider surface. It may
not change narrative intent, identity, state, continuity, quality bar, or Gate status.

If the provider surface or behavior is unknown, keep it `UNKNOWN` and deliver the
neutral handoff. Do not fabricate support from a model name, a single attractive
output, or a generic prompt convention.

## Handoff status

- `DRAFT`: creative or production decisions are incomplete.
- `SPEC_RESOLVED`: the neutral handoff is internally consistent.
- `EXTERNAL_ADAPTER_REQUIRED`: provider syntax is needed but not yet selected.
- `HUMAN_REVIEW`: external output exists but has not passed the relevant checks.
- `READY_FOR_EXTERNAL_TOOL`: the handoff and required references are approved for the
  requested external operation.

These statuses do not replace existing Runtime or Gate states.
