# Lab notebook

Append-only. One dated entry per step that ran something or made a decision: what ran (run ids),
cost, key numbers, decisions and why.

## 2026-10-24 — repo setup and plumbing (kickoff steps 1–2)

**Repo.** Removed the nine sprint experiments unrelated to Q1.2; kept `llm-cartel/`, `util/`,
`literature/` and the root files unchanged. New code lives in `seat_swap/` (uv project, path deps
on `llm-cartel` and `util`, zero upstream edits). `upstream` remote added, fetch-only.

**Orientation (step 1).** Upstream `run_game.py`/`branch_game.py` have no notes, no shock, no
lookalike, no dry-run/max-calls; agents are stateless; the chat template is applied server-side;
the price parser is loose (falls back to any number on the last line). Decision: own game loop in
`seat_swap/`, reusing `OligopolyGame` (market maths, P0 prefix, product info) and `ChatProvider`.

**Prompt.** PLANS/INSIGHTS wording verbatim from Fish, Gonczarowski & Shorrer, arXiv:2404.00806v2,
Appendix E (E.1 P0 files clause, E.2.1 template). Deviations from Fish, kept deliberately:
- market table oldest round first under "MARKET DATA" (upstream LLMCartel layout); Fish lists
  newest first under "MARKET_DATA" — one-line switch if wanted;
- prefix sent as the system message (upstream split); Fish's appendix shows one block.
Round convention: round t = t-th LLM decision; synthetic warm-up near Nash is Round 0; window =
last 100 rounds, which is what a newcomer inherits as "history".

**Logging (step 2).** Contract implemented; `rendered_prompt` is null on OpenRouter (server
applies the template) and exact on vLLM `/v1/completions`; `rendered_prompt_local` (Qwen3-8B
tokenizer @ b968826d) always logged. Strict parser, one retry, failures counted, no price ever
filled in. `--max-calls` counts every attempt (SDK retries disabled). 17 offline tests pass.
Cost so far: $0 (no completion calls).

**Decided.** Model prices are rounded to 2 dp before the market (as upstream), so the market is
computed at the price both tables show; `raw_completion` keeps the original.

**Open.** In a shock, is the forced seat's LLM still called and its notes updated? Parked; needed
before Phase B (`shock_calls_llm` has no default).
