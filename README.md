# FilmFoundry Skills

FilmFoundry Skills is a general, creator-first toolkit for developing scripts and preparing visual production. It must work across projects; Wucheng is a downstream consumer, never a Core design branch.

**Repository:** `filmfoundry-skills`  
**Primary skill:** `generative-film-production`  
**Version:** 3.0.0

## Current status

The repository has a local v3 technical RC and passing deterministic tests, but it is **not approved for publication**. A real from-zero script-creation trial showed that the current Skill is still too production-oriented: it can route a creative request, but it does not yet provide a concise, reusable script-creation workflow.

The local `v3.0.0-rc1` tag is evidence of the earlier technical checkpoint only. It has not been pushed and must not be treated as product acceptance.

| Surface | Current evidence |
|---|---|
| Static contracts and deterministic validators | Verified locally |
| Creator Read Model and renderer | Verified structurally |
| Authored fixtures | Demonstrations, not an agent benchmark |
| Fresh-context agentic benchmark | Pending |
| Real from-zero creator trial | Product acceptance pending |
| Provider-specific removal | Pending |
| Multi-project creator validation | Pending |

## Product boundary

FilmFoundry should help a creator:

1. turn an idea into a premise, logline, characters, dramatic rules, structure, draft, and revision;
2. analyze an existing script, including emotion, causality, continuity, and production risk;
3. prepare assets, images, prompts, and shot plans when the script is ready.

External tools and people own video-provider calls, generation, downloads, and aesthetic video QC. The active implementation still contains older H3/provider execution and evidence surfaces; those are deprecated product debt and must be removed before release.

## What remains valuable

The v3 clean-break namespace, path safety, `UNKNOWN` / `INVALID` semantics, provenance, state alignment, deterministic serialization, Creator data model, and the Creative / Commit / Production / Gate boundary remain useful foundations. They do not by themselves prove that the Skill is pleasant or fast to create with.

## Development

```powershell
python -m pytest -q
python scripts/build_release_artifacts.py --out .dist
python scripts/check_clean_extraction.py --wheel .dist/filmfoundry_skills-3.0.0-py3-none-any.whl --archive .dist/filmfoundry-skills-v3.0.0.zip
git diff --check
```

`ff render` is read-only. A successful render is not a Gate decision and does not prove provider behavior, market performance, or creative quality.

## Repository map

```text
filmfoundry-skills/
├── filmfoundry/                         # Python contracts and CLI
├── skills/generative-film-production/  # Primary Agent Skill
├── schemas/                             # Active schemas
├── evals/                               # Authored guardrail fixtures
├── tests/                               # Deterministic regression tests
├── docs/                                # User docs and repository evidence
├── CURRENT_HANDOFF.md                   # Current repository handoff
└── CHANGELOG.md                         # Version history
```

Start with [the documentation index](docs/README.md). Repository history is recorded in [CHANGELOG.md](CHANGELOG.md); it is not an active compatibility promise.

## Release rule

Do not publish a v3 release until all of the following are true:

- provider-specific execution/evidence responsibilities are removed from the active Skill, code, tests, and user docs;
- a concise from-zero script-creation workflow is implemented;
- at least one fresh-context creator completes a real script with it and records friction honestly;
- deterministic tests and clean extraction pass again;
- the release commit and tag point to the exact reviewed contents.

## License

MIT. See [LICENSE](LICENSE).
