# Controllability Budget

A prompt has more words than a video model has independent control channels. Do not confuse textual specificity with reliable control.

## Spend control on the expensive truths

For ordinary I2V, prioritize in roughly this order:

1. identity / count / required visible state;
2. narrative target and eyeline when critical;
3. fixed geography / prop persistence;
4. one dominant action;
5. one primary camera intent;
6. minimal acting change;
7. lighting continuity;
8. optional micro-environment motion.

If the model cannot satisfy all requested behavior, optional smoke, foliage motion, elaborate timing prose, and decorative adjectives should lose before identity, geography, eyeline, and narrative action.

## Generation duration is not edit duration

A provider may offer ten seconds while the edit only needs five. v1.2 therefore separates `generation_duration_seconds` from `edit_target_duration_seconds`.

Treat the generated clip as source material unless the route has evidence for exact full-duration performance. Review the whole clip and promote the best contiguous range when that range alone satisfies the shot goal and quality bar.

`PARTIAL_SELECT` is not cheating; it is normal editing when traceable. Record the source in/out range and write observed state at the selected out-point.

## Do not over-time ordinary motion

Without an external timing authority, prefer event order or a few stages. Do not expect a model to obey “8–9 seconds decelerate, 9–10 seconds hold” merely because it is written precisely. If repeated model evidence proves such control, an adapter may use it. Until then, plan edit handles and choose a usable range.

## Acting amplification

If a model profile records that subtle acting tends to amplify over time, adapt with evidence-based choices: lower initial intensity, shorten the useful edit target, reduce camera motion, or select an earlier range. Do not encode this as a universal provider fact after one clip.
