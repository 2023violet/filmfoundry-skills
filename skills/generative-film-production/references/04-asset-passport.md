# Asset Passport

Create one authoritative passport for every recurring character, product, important prop, vehicle, creature, or location. Store visible invariants, canonical descriptor, approved references, version/hash evidence, and allowed state variants.

State changes are explicit variants such as `CHAR_A_DRY` → `CHAR_A_WET`; do not silently mutate canon or fight a contradictory canon reference with prompt text. A variant parents the canon directly. A new reference is proposed, stress-tested, versioned, hashed, and then promoted; it never silently replaces the authority record.

Use three asset classes to control process cost:

- **CANONICAL:** recurring identity/geometry/location authority; locked versions need a real SHA-256.
- **GENERIC:** repeatable background language without fixed individual identity, such as villagers/crowd wardrobe language.
- **EPHEMERAL:** one-off props or extras that do not need persistent authority. If persistence becomes important, promote the asset rather than pretending an ephemeral item is locked.

Use `../templates/asset-passport.md`, `../templates/asset-registry.example.csv`, and the asset-registry validator.
