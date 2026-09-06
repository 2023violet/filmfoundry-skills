# Voice Passport and Timing Authority

Recurring dialogue needs the same authority discipline as recurring faces.
Create a Voice Passport when a speaker must remain recognizable across shots.
The passport describes the approved voice; the shot still decides whether that
voice owns timing.

Record `voice_id`, voice description, sample asset IDs, accent, pitch, pace,
emotional behavior, test lines, version, drift observations, and evidence
level. Measure speech rate and pauses from the approved voice. Do not invent a
theoretical characters-per-second value and force final dialogue into it.
`UNVERIFIED` is a valid starting evidence level and does not unlock a provider
route.

## Dialogue routes

- `H3_NATIVE_DIALOGUE`: native model audio is the timing authority only after
  that capability has been verified for the current surface/version.
- `EXTERNAL_VOICE_TIMING`: generate and approve the voice track first, then
  derive shot timing from its actual duration and pauses.
- `POST_VO_NO_LIPSYNC`: use when the mouth is not a visual timing constraint,
  such as narration, distant figures, backs, or non-speaking plates.

Every dialogue shot names a `voice_id`, `dialogue_route`, `timing_authority`,
and `speech_intent`. Cross-shot continuity includes voice identity, delivery
pace, pauses, pronunciation, and emotional range, not just visual state.

Use `templates/voice-passport.example.json` for one passport,
`templates/voice-registry.example.json` for a registry, and
`scripts/validate_voice_registry.py` for the registry contract.
