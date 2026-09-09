# 30 · Edit Timeline Contract

## Why this layer exists

Narrative Shots, Generation Units, and Edit Units are different things. Generation-unit edit targets do **not** have to sum to episode runtime because one Select can be held, split, reused, combined with static inserts, sound bridges, deterministic post, or omitted.

But before final Picture Lock, the edit plan must cover **100% of the intended timeline**.

## Required fields

For every timeline block record:
- `episode_id`
- `edit_unit_id`
- `start_seconds`
- `end_seconds`
- `source_type` (`SELECT`, `PARTIAL_SELECT`, `STATIC`, `POST`, `AUDIO_BRIDGE`, etc.)
- `source_ids`
- `timing_authority`
- `status`

## Gates

1. **Rough Edit Coverage:** no unexplained timeline gaps.
2. **Timing Authority Lock:** approved voice/music/dialogue where they own timing.
3. **Final Select Coverage:** every used range points to an approved source.
4. **Picture Lock:** edit timing/order is frozen. Only after this point use the term Picture Lock.

Static/keyframe readiness must use `STATIC_VISUAL_LOCK`, `KF_QC_PASS`, or equivalent terms instead of Picture Lock.


## Picture Lock vs audio finishing

Resolve any audio that is a **picture timing authority** (for example approved VO/dialogue/music cues that determine shot duration) before Picture Lock. However, the **final sound mix**, SFX polish, non-timing-authoritative music finishing, and subtitle export may continue **after Picture Lock** because they should no longer change picture order or duration.
