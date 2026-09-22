# FilmFoundry Skills

FilmFoundry Skills is a general, creator-first toolkit for developing scripts and preparing visual production. It must work across projects; Wucheng is a downstream consumer, never a Core design branch.

**Repository:** `filmfoundry-skills`  
**Primary skill:** `generative-film-production`  
**Version:** 3.0.0

## Current status

The repository has a local v3 technical RC and passing deterministic tests, but it is **not approved for publication**. The creator-first workflow, adaptive execution lanes with soft budgets, and Provider-neutral handoff are implemented; fresh-context product evidence remains a release blocker.

Blank-idea script work starts with `references/41-creator-first-script-workflow.md`; production references remain deferred until the creator accepts the script or explicitly requests production preparation.

The local `v3.0.0-rc1` tag is evidence of the earlier technical checkpoint only. It has not been pushed and must not be treated as product acceptance.

| Surface | Current evidence |
|---|---|
| Static contracts and deterministic validators | Verified locally |
| Creator Read Model and renderer | Verified structurally |
| Human Decision Brief and `Decision` view | Added; structural rendering verified |
| Adaptive execution lanes and soft budgets | Implemented; route and CLI metadata verified |
| Authored fixtures | Demonstrations, not an agent benchmark |
| Creator-first workflow contract | Implemented and deterministically verified |
| Fresh-context creator trial | Agentic product evidence pending |
| Provider-neutral Core boundary | Verified structurally; external adapter execution remains out of scope |
| Provider-specific removal | Active execution removal completed; historical field classification pending |
| Multi-project creator validation | Not requested in this pass |

## Product boundary

FilmFoundry should help a creator:

1. turn an idea into a premise, logline, characters, dramatic rules, structure, draft, and revision;
2. analyze an existing script, including emotion, causality, continuity, and production risk;
3. prepare assets, images, prompts, and shot plans when the script is ready.

External tools and people own video-provider calls, generation, downloads, and aesthetic video QC. FilmFoundry emits a Provider-neutral handoff and does not run provider clients or smoke gates; historical evidence fields remain for external traceability only.

## What remains valuable

The v3 clean-break namespace, path safety, `UNKNOWN` / `INVALID` semantics, provenance, state alignment, deterministic serialization, Creator data model, and the Creative / Commit / Production / Gate boundary remain useful foundations. They do not by themselves prove that the Skill is pleasant or fast to create with.

## Development

```powershell
python -m pytest -q
$env:SOURCE_DATE_EPOCH = "0"
python -m pip wheel . --no-deps --no-build-isolation --wheel-dir .dist
python scripts/build_release_artifacts.py --out .dist
Remove-Item Env:SOURCE_DATE_EPOCH -ErrorAction SilentlyContinue
python scripts/check_clean_extraction.py --wheel .dist/filmfoundry_skills-3.0.0-py3-none-any.whl --archive .dist/filmfoundry-skills-v3.0.0.zip
git diff --check
```

`ff render` is read-only. Its `decision` view summarizes evidence-bound actions and risks for a human reviewer; it is not a creative approval, Gate decision, or proof of provider behavior, market performance, or visual quality.

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

Start with the [Chinese full-workflow user manual](docs/filmfoundry-skills-user-manual-zh.md), then use [the documentation index](docs/README.md) for technical and evidence references. Repository history is recorded in [CHANGELOG.md](CHANGELOG.md); it is not an active compatibility promise.

## Release rule

Do not publish a v3 release until all of the following are true:

- Provider-neutral compilation and external adapter boundaries remain intact;
- a concise from-zero script-creation workflow is implemented;
- at least one fresh-context creator completes a real script with it and records friction honestly;
- deterministic tests and clean extraction pass again;
- the release commit and tag point to the exact reviewed contents.

## License

MIT. See [LICENSE](LICENSE).
