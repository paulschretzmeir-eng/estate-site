<!-- Generated: concise, actionable local guidance for AI coding agents -->
# Copilot / AI Agent Instructions

Purpose: help an automated coding agent quickly become productive in this repository.

- **Quick repo shape**: single Python entrypoint at `main.py`. There is no dependency manifest (no `requirements.txt` or `pyproject.toml`). Treat this as a small single-file app unless new structure is explicitly approved.

- **How to run locally**: run the entrypoint to sanity-check changes.

  ```bash
  python main.py
  ```

- **Where to look first**: open `main.py` to find the program entrypoint and primary logic. Use that file as the authoritative implementation until the project grows.

- **Editing rules for AI agents**:
  - Make focused, minimal patches. Prefer edits that change a single responsibility (e.g., fix a function, add a small helper).
  - When adding runtime dependencies, also add a `requirements.txt` and document the reason in the PR.
  - Add or update `README.md` when you introduce new top-level components or run steps.

- **Testing & verification**:
  - There are no tests discovered. After making code changes, run `python main.py` and manually exercise the changed behavior.
  - If you add tests, place them under `tests/` and use `pytest` (include `pytest` in `requirements.txt`).

- **Project-specific patterns discovered**:
  - Single-file structure: prefer keeping related helpers in the same module unless complexity justifies extracting a package.
  - No CI/test manifest detected: assume manual verification is expected.

- **When to ask the human**:
  - Before adding major structure (new packages, service components, or external services).
  - Whenever adding persistent state or external integrations (databases, message queues).

- **Documentation & PR guidance**:
  - Keep PRs small and explain runtime steps to reproduce locally (commands to run `main.py`, env variables if any).
  - If you add files, include short docstrings and a one-line note in `README.md`.

If anything above is incomplete or you want the agent to follow different conventions, tell me which area to expand or change.
