```json
{
  "prompt_id": "EP01_SH001_P01",
  "prompt_type": "I2V",
  "production_unit": "EP01_SH001_G01",
  "visual_fact": "The watcher is in profile at the inn entrance.",
  "output_profile": "VIDEO_SOURCE_NATIVE",
  "start_state": "Lantern dark; watcher frame right.",
  "end_state": "Lantern lit; watcher turns once toward it.",
  "subjects": ["CHAR_SHENYE"],
  "dominant_action": "One turn toward the lantern.",
  "camera": "One slow push in.",
  "continuity_locks": ["wardrobe", "screen direction"],
  "references": [{"slot": "character", "asset_id": "CHAR_SHENYE", "role": "identity", "controls": "face and wardrobe", "does_not_control": "motion timing"}],
  "forbidden": ["extra characters", "camera orbit"],
  "acceptance": ["single action", "stable identity"]
}
```

## visual_fact

The watcher is in profile at the inn entrance.

## output_profile

VIDEO_SOURCE_NATIVE

## start_state

Lantern dark; watcher frame right.

## end_state

Lantern lit; watcher turns once toward it.

## subjects

CHAR_SHENYE

## dominant_action

One turn toward the lantern.

## camera

One slow push in.

## continuity_locks

Wardrobe and screen direction.

## references

The character reference controls face and wardrobe, not motion timing.

## forbidden

Extra characters and camera orbit.

## acceptance

Single action and stable identity.
