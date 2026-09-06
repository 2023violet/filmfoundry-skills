# Voice Passport and Timing Authority

Recurring dialogue needs the same authority discipline as recurring faces. Create a Voice Passport when a speaker must remain recognizable across shots.

Record provider/model, voice reference, apparent age, pitch/texture, baseline energy, measured speech-rate ranges, pause style, pronunciation notes, and forbidden delivery. Measure speech rate from the approved voice; do not invent a theoretical characters-per-second value and force final dialogue into it.

## Dialogue routes

- `H3_NATIVE_DIALOGUE`: native model audio is the timing authority only after that capability has been verified for the current surface/version.
- `EXTERNAL_VOICE_TIMING`: generate/approve the voice track first, then derive shot timing from its actual duration and pauses.
- `POST_VO_NO_LIPSYNC`: use when the mouth is not a visual timing constraint, such as narration, distant figures, backs, or non-speaking plates.

Every dialogue shot names a `voice_id`, `dialogue_route`, `timing_authority`, and `speech_intent`. Cross-shot continuity includes voice identity and delivery pace, not just visual state.

Use `templates/voice-registry.example.json` and `scripts/validate_voice_registry.py`.
