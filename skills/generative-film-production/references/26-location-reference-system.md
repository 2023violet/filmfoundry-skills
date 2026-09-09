# 26 - Location Reference System

## Principle

A location reference exists to preserve **spatial logic**, not to create a
beautiful concept-art collection. The location record describes geometry and
light anchors; a Spatial Map records subject-to-anchor relationships for a
specific production unit.

## Minimum authority depends on shot needs

A recurring or geometry-critical location may need:

- a hero master;
- one or more directional or three-quarter anchors;
- entrance/exit landmarks;
- clue/prop positions;
- camera-side and 180-degree-axis facts;
- lighting/weather state variants.

A one-off low-risk background may need only one approved frame. A three-quarter
view may expose useful geometry, but its benefit remains an unverified creative
practice until the route has evidence.

The `location-reference.example.json` template records
`preferred_view`, `anchor_objects`, `camera_side`, `light_sources`,
`geometry_controls`, and `does_not_control`. Keep final crop, actor identity,
and motion behavior outside the location authority unless explicitly bound by a
separate control artifact.

## Same-location rule

If the story payoff depends on "the same place changed," the before/after images
must share identifiable anchors. Atmosphere similarity alone is insufficient.
Add `spatial-map.example.json` when the shot depends on where a subject, prop,
light, or camera sits relative to those anchors.

## Aspect-ratio note

A location master may be wider than the delivery format, but it is not
automatically a final framing authority. Delivery-format preflight must prove
the required crop and composition.
