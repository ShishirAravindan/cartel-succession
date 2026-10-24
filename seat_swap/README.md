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
