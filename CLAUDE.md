# CLAUDE.md — Cartel Re-forms (Apart AI Collusion Sprint, Track 1, Q1.2)

**Read `docs/working_model.md` first.** It holds every project rule: roles (PI / coordinator / coder),
what to do after each task, when to decide vs ask, the fixed economics, the design, the logging
contract, git conventions, the run policy (spend guard rails) and the current decisions.

Each session, also read `docs/status.md` (where things stand) and the end of `docs/log.md`.

Non-negotiables, in short (full versions in the working model):
- Run from the repo root: `uv run --project seat_swap python -m seat_swap.<module>`.
- Secrets live in `compute.env` (gitignored); never print, log or commit keys.
- Never overwrite a run directory; commit before a live run (dirty-tree guard).
- Stop and ask before changing what a seller sees, a metric, threshold, pass rule or arm, or
  before spending above the run policy.
- Commits: conventional, one line, **no trailers of any kind**.
