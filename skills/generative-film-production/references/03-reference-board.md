# Reference Board

A reference is a specification input. Every reference record needs:

```yaml
ref_id: REF_001
controls: face identity
does_not_control: wardrobe, background, lighting
status: approved
```

Prefer the smallest sufficient reference pack. Extra references are not free context: they can compete, leak backgrounds, duplicate people, or confuse roles. Reject references whose unwanted attributes are more salient than the property they are meant to control.
