# Asset Passport

Create one authoritative passport for every recurring character, product,
important prop, vehicle, creature, or location. Store visible invariants,
canonical descriptors, approved references, version/hash evidence, and allowed
state variants.

The passport answers **what the asset is**. A Visual Control Plan answers
**which facts this production unit needs the asset to control**. Keep those
records separate so a face reference does not silently become a camera,
location, physics, or story-state authority.

State changes are explicit variants such as `CHAR_A_DRY` -> `CHAR_A_WET`; do
not silently mutate canon or fight a contradictory canon reference with prompt
text. A variant parents the canon directly. A new reference is proposed,
stress-tested, versioned, hashed, and then promoted; it never silently
replaces the authority record.

Use three asset classes to control process cost:

- **CANONICAL:** recurring identity/geometry/location authority; locked versions
  need a real SHA-256.
- **GENERIC:** repeatable background language without fixed individual
  identity, such as villagers/crowd wardrobe language.
- **EPHEMERAL:** one-off props or extras that do not need persistent authority.
  If persistence becomes important, promote the asset rather than pretending an
  ephemeral item is locked.

For every reference, record both `controls` and `does_not_control`. When a
reference is bound to a shot or Visual Control Plan, compare its visible state
with the Shot Spec before provider submission. A locked asset can still be the
wrong start or end state for a particular route.

Use `../templates/asset-passport.md`,
`../templates/asset-registry.example.csv`, the asset-registry validator, and
`../templates/visual-control-plan.example.json` when a production unit needs
explicit character, location, scale, physics, previs, or lens controls.
