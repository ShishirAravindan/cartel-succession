# seat_swap

Sprint Track 1, Q1.2: once two LLM pricing agents sustain high prices and punish defection,
does replacing one seller break the cartel, and does the newcomer need the inherited history
(price table, PLANS/INSIGHTS notes, or both) to re-form it?

Builds on `../llm-cartel` (market maths, P0 prompt, `ChatProvider`) and `../util`
(`poseidon_compute`, inference routing) without modifying them; see `UPSTREAM_CHANGES.md`.

```bash
uv sync --project seat_swap                                   # or ./setup.sh from the repo root
uv run --project seat_swap python -m pytest seat_swap/tests -q
uv run --project seat_swap python -m seat_swap.show_prompt --seat 1 --round 10    # read a prompt
uv run --project seat_swap python -m seat_swap.run --dry-run --rounds 5           # zero API calls
uv run --project seat_swap python -m seat_swap.run --rounds 30 --max-calls 80     # live (OpenRouter)
```

Always run from the repo root with `python -m seat_swap.<module>` (the package has a
`logging.py`, which would shadow the stdlib if `seat_swap/` itself were on `sys.path`).

| file | role |
|---|---|
| `prompts.py` | `NotesOligopoly` (Fish et al. PLANS/INSIGHTS prompt) and the strict parser |
| `render.py` | Qwen3 chat template, tokenizer pinned (Qwen3-14B) |
| `providers.py` | OpenRouter chat, vLLM `/v1/completions`, scripted sellers |
| `game.py` | game loop: retries, call budget, shocks, snapshots |
| `logging.py` | run-directory writer (logging contract) |
| `run.py` | CLI for one main-line game |

Raw logs go to `seat_swap/runs/<run_id>/` (gitignored; never overwritten). Curated tables and
figures derived from them go in `seat_swap/results/`. Live runs refuse a dirty working tree, so
each run's recorded git sha is the code that produced it.

## Provenance labels in the code

Comments and report headers cite the project's internal work orders ("Kickoff NN") and sections of the
pre-registered plan ("plan §N", `docs/plan.md` as frozen at each `prereg-*` tag). "PI" marks a design decision
made in the project's review step before a run. The kickoffs map to experiment families and tags as follows:

| kickoff | what it set up | paper | tag |
|---|---|---|---|
| 03 | positive-control diagnostics for instructed pairs | Appendix B.2 | |
| 05 | planted design: the numeric rule with forgiveness, the newcomer pilot | §3.2, Appendix B.2 | |
| 06 | main experiment on Set A, base gate, discipline probe | §3–4, Appendix B.3, B.5 | `prereg-p1` |
| 07 | Set B replication with the Notes arm | §3–4 | `prereg-p1b` |
| 08 | other newcomer models (Qwen3-8B, gpt-oss-20b) | Appendix D.3 | `prereg-p23`, `prereg-p23b` |
| 09 | template notes, post-hoc outcomes and paper figures | §4, Appendix D.2 | `prereg-p1c` |
