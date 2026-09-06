# Audio

Treat dialogue, voice-over, ambience, foley/SFX, music, and captions as separate reviewable layers even when a video model can synthesize native audio. Native audio is a capability, not automatically the final mix or timing authority.

For recurring speakers, load `18-voice-passport.md`. Every dialogue unit names a dialogue route and timing authority:

- native model dialogue only when verified for the exact model surface/version;
- approved external voice track when voice identity, pace, or lip-sync consistency matters;
- post VO when visible mouth timing is not required.

Lock verbatim dialogue before lip-sync work. If external voice owns timing, approve/generate that voice first, measure its actual duration and pauses, then write second-level timing. Do not pre-allocate an arbitrary short window and later force final speech into it.

Review language, speaker identity, delivery pace, intelligibility, sync, ambience continuity, and music edit separately.


## Picture Lock boundary

Timing-authoritative voice/dialogue/music must be measured before Picture Lock when it can change picture duration. Final SFX and final mix may finish after Picture Lock as long as they cannot reopen picture timing/order.
