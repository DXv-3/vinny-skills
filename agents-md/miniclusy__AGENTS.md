# AGENTS.md — Build Rules for mini-clusy

1. **Read this file before editing.**
2. **Run tests after every layer.** Fix failures before proceeding.
3. **All state-mutating actions route through `AutonomyGate`.** No bypass paths.
4. **Never write secrets** to notebook JSON, logs, or the action log.
5. **Keep the mock provider deterministic** and fully offline.
6. **Use the interfaces in `interfaces.py`** for new providers, memory backends, transports, or registries.
7. **Profile-copy isolation is mandatory** for browser code.
8. **Persist plans as first-class data** via `store.save_plan()`.
9. **Append to the action log** for every gated decision.
10. **Prefer stdlib + pinned deps.** Add new dependencies to `pyproject.toml` and README.
