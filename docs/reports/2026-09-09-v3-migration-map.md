# FilmFoundry v3 Migration Map

Date: 2026-09-09

## Pre-migration snapshots

### FilmFoundry release

| Path | SHA-256 at inventory |
|---|---|
| `filmfoundry/contracts.py` | `D7F49C8BFD9DEBE1E66F8BE9AA3F124774838BD28EAAE95C4EA2FFF31B0165AB` |
| `filmfoundry/cli.py` | `B19A1ED4F713FB58C00C113F6BB5D97A9880155D7BE9FE2A890F6FD975DD8695` |
| `filmfoundry/modes.py` | `F11F76A0F72119E01A8767217D8C8EE3A18DE703B68F1E54069758DBBC08A303` |
| `filmfoundry/render.py` | `E717BCC45AABFB14E41851FAFD68C4F810D4F23BB8D2F2CDB766908523915582` |
| `pyproject.toml` | `526CF018F94597556158F4BE6437A9D3FD40E90A2639543B66107DD84DE1672F` |
| `tests/fixtures/v23/creator-read-model/smoke-project/workspace-manifest.v3.json` | `E586259630318E1D1FAC78D7F25FCF78C8D1A3AE35F1B8080F17C3251443E6B4` |

### Wucheng project

| Path | SHA-256 at inventory |
|---|---|
| `07_运行时/RUNTIME/project-runtime.json` | `ABD2B319ECFE9C81C6977069A6289F13DA959CDD9AD5994AF55F21E84ADAACF9` |
| `08_工具与技能/README.md` | `FCD273FB8DF4C264E8C0808FBA11E06353D6DE4C44C287385C473C9A5E342DD8` |
| `08_工具与技能/索引.md` | `F85A89FFF6940C8E0AE8A671AF5D19760A9AFD85B9338C4893DCB8FED96A22FB` |
| `08_工具与技能/雾城项目适配器/scripts/build_creator_catalog.py` | `CAA745A771A21C3CE0B38BC34659EDB9BE0EB5167B9DF1D119BBC7CB0E2F5398` |
| `README.md` | `F66CF6C74979064E729A0ACAB53218D5FF73FABDC5AB54D7B4D38FDBF1A3C972` |
| `01_项目治理/当前状态/CURRENT_HANDOFF_v1.9.3.md` | `BB209028F0144F37FF1F516D88232869172EB29F5ACBCAE1E13558C39E7D4824` |
| `SHA256SUMS.txt` | `A4BF1469525EF509D6955D1C60EDC1A3804705EEEB760457A523A9A881B8352F` |

## Migration table

| Surface | Current state | v3 action | Owner |
|---|---|---|---|
| Workspace manifest | v3 version, loose adapter range | enforce `>=3.0.0,<4.0.0` | FilmFoundry Core |
| Active v2 tests/fixtures | still discoverable by pytest/search | move to historical tree or remove from active suite without touching archive | FilmFoundry Core |
| Wucheng projection | external media paths; missing `runtime_status` | copy verified media, write sentinels, project active state as `DRAFT`, retain history | Wucheng adapter |
| Wucheng Runtime | active metadata says v2.0.0 | write v3 metadata and keep old values under history | Wucheng project |
| Wucheng handoff/docs | current pointer says v1.9.3 and mixed v2 references | create v3 handoff and update active navigation | Wucheng project |
| Work modes | Python routing only | add `ff route` and benchmark evidence | FilmFoundry Core |
| Renderer | render-manifest.v1 and bare tables | static v2 dashboard with coverage, warnings, blockers, current/history labels | FilmFoundry Core |
| Packaging | wheel only contains Python package | add clean skill zip and extraction checks | FilmFoundry Core |
| Release | no RC tag | run all gates, create local `v3.0.0-rc1` only after evidence | Release owner |

## Safety boundaries

- Do not modify `99_归档`.
- Do not reset, checkout, or clean either dirty worktree.
- Do not add Wucheng identifiers or branching to FilmFoundry Core.
- Do not restore `filmfoundry_v2` or a permanent migration command.
- Keep the RC reversible until human creator review is complete.
