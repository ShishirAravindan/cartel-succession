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

## 2026-10-24 — metrics and scripted sellers (kickoff step 3)

`seat_swap/metrics.py` (CI, best response, br_gap, ci_early/late, newcomer CI, retaliation,
re_formed with an explicit threshold) and `seat_swap/scripted.py` (grim trigger, tit-for-tat,
copier, fixed price, lookalike).

**Decision.** Copier = the anchoring look-alike: prices at the mean of the opponent's last 30
prices, no punishment logic. Self-test rewritten as properties rather than exact numbers, plus
tit-for-tat as a second colluder that must fail the innocence test.

**Self-test** (T = 150 inherited cartel at p_M, seat 0 forced to p_N at T+30, full pipeline):

| seat 1 | br_gap | retaliation | seat-1 prices T+30..33 |
|---|---|---|---|
| grim colluder | +0.590 | −1.018 | 1.93, 1.47, 1.47, 1.47 |
| copier | +0.590 | −0.044 | 1.93, 1.91, 1.91, 1.91 |
| tit-for-tat | +0.590 | −0.678 | 1.93, 1.47, 1.93, 1.47 |

BR(p_M) = 1.6617, so both-at-p_M br_gap = +0.583; scripted prices print at 2 dp (1.93 > p_M), so
CI slightly exceeds 1 and br_gap reads +0.590.

## 2026-10-24 — smoke test (kickoff step 4)

**Model change.** `qwen/qwen3-8b` returns 404 on OpenRouter ("deprecated on Oct 9, 2026"); run
`20261024-130746_smoke_qwen3-8b_thinkoff_s0` aborted after 2 calls, $0. User chose
`qwen/qwen3-14b` (same chat template and vocabulary as Qwen3-8B; tokenizer re-pinned @ 40c06982).

**Runs** (30 rounds, seed 0, `--max-calls 80`):

| run | status | calls | parse fails | s/call | prompt tok | completion tok | reasoning tok | cost |
|---|---|---|---|---|---|---|---|---|
| `20261024-131030_smoke_qwen3-14b_thinkoff_s0` | completed 30/30 | 63 | 3 (all `finish_reason=length`) | 26.5 | 1417 | 2136 | 1627 | $0.040 |
| `20261024-132750_smoke_qwen3-14b_thinkon_s0` | aborted_parse at round 2 | 6 | 3 (`<1.60>`, angle brackets) | 15.5 | 572 | 1384 | 1025 | $0.002 |

Backends: DeepInfra and NextBit, mixed within a run.

**Findings.**
- Thinking-off does not work on OpenRouter for Qwen3-14B: every "off" call returned reasoning
  (mean 1627 reasoning tokens). So `rendered_prompt_local` (empty think block) is wrong for that
  run, and the two runs are both effectively thinking-on.
- The model copies the template's angle brackets: `My chosen price:\n<1.60>`. Strict parser rejects
  it (correctly by the current rule); with the one retry this aborts runs.
- max_tokens 4096 truncates some replies (3/63) because reasoning eats the budget.
- Both runs used a prompt reading "$1.0" (float cost after the step-3 refactor); fixed in b54c274.
- CI trace not interpreted (30 rounds); thinking-off run sat at 1.50/1.50 from round 5.

**Open.** (1) accept `<number>` as a valid price line? (2) how to get real thinking-off
(`/no_think` soft switch in the prompt, or vLLM `enable_thinking=False`), or drop the off mode;
(3) raise max_tokens; (4) pin one OpenRouter backend?

## 2026-10-24 — branching harness, dry-run (kickoff 2, task 3)

`seat_swap/branch.py`: restores the env exactly from `snapshot_T<T>.json` (no replay), applies the
newcomer's inheritance to seat 1, runs the arm in a new run directory
(`<ts>_<phase>_<arm>_s<seed>_<6 hex>`), and writes `summary.json` (per-arm metrics). The 11 arm
names are exactly those in CLAUDE.md (tested). Inheritance options `full`/`history`/`notes`/`none`;
"no history" = the seat's market table starts at T+1 (`visible_from`), and scripted sellers get
the same view as the prompt. 59 offline tests pass.

**Decided (user, 2026-10-24).**
- Shock rounds: the forced seat's LLM is not called and its notes stay unchanged.
- Phase A enforcement test: side branch forked at T = 150, seat 0 forced to p_N at T+1, 10 rounds;
  `enforcement_retaliation` = seat-1 CI over T+2..T+4 minus over T−2..T; `is_cartel` = CI(121–150)
  > 0.5 and retaliation ≤ threshold. Threshold has no default (set from this kickoff's numbers).
- Seller model on Modal: Qwen3-14B @ 40c06982 (same as the pinned tokenizer).
- Thinking off; the parser accepts a bracketed `<n>` price line, flagged `parse_bracketed`.

**Decided (me, flag for review).**
- `lookalike` seat 0 repeats its last *chosen* price: the forced p_N at T+30 isn't its choice,
  so it goes back to its pre-shock price. Otherwise it would sit at p_N from T+31 on, and the
  newcomer's drop would be a best response, not retaliation.
- `lookalike` / `lookalike_oth`: the newcomer gets history only (no notes); models `same` / `oth`.
- `control` = no replacement, which is the same as same model + full inheritance (sellers are
  stateless apart from notes and table). So there's no `same_full` arm.
- `sib` / `oth` newcomer models are not chosen: `SELLER_MODELS` holds None, and live runs of
  those arms refuse to start. Dry runs work.

**Not yet there.** `docs/plan.md`, which CLAUDE.md points to, does not exist; `prereg-phase-a`
needs it.

## 2026-10-24 — Modal vLLM endpoint (kickoff 2, task 1)

`seat_swap/modal_vllm.py` (vLLM 0.21.0 on one L40S, `scaledown_window` 2 min, API key from Modal
Secret `seat-swap-vllm`, `--generation-config vllm` so Qwen's top_p 0.95/top_k 20 defaults don't
apply), `seat_swap/modal_weights.py` (fills Volume `seat-swap-hf-cache` from a CPU container),
model + revision in `seat_swap/model_config.py`, shared with the local renderer. The provider
sends top_p 1, top_k −1 and add_special_tokens false, and logs them in `sampling_params`.

Every GPU type was refused until a card was added ("Please add a payment method…"); the user
added one.

**Run** `20261024-144509_endpoint_qwen3-14b_thinkoff_s0`: 10 rounds, 20 calls, 0 parse failures,
0 bracketed, all `finish_reason=stop`. Cold start 211 s. 20.6 s/call, 945 prompt / 483 completion
tokens per call (~23 tok/s single stream on L40S).

**Byte-for-byte check** (`seat_swap.verify_prompts`, 20/20 on every check):
- local token ids = server prompt token ids;
- the server's ids decode to the logged `rendered_prompt`;
- echo returns the logged string as its prefix;
- prompt_tokens matches.

Caveat: vLLM drops the echo when `return_token_ids` is on, so the ids check and the echo check
are separate requests.

**Cost.** Modal metered this month: $0.45 (deployed apps $0.38), covered by credits.
App stopped.

## 2026-10-24 — Phase 0, scripted (kickoff 2, task 2)

`seat_swap.phase0_scripted`, dry-run, $0. Grim trigger in seat 0. Each pair: 150-round main line
→ `control` branch at T = 150 (seat 0 forced to p_N at T+30) → enforcement side branch (seat 0
forced at T+1). Runs `20261024-1451xx_phase0_dry-grim-<seller>_s0` plus their branches (ids in
`seat_swap/results/phase0_scripted.json`).

| seat 1 | CI 121–150 | br_gap | retaliation (T+30) | enforcement retaliation (T+1) |
|---|---|---|---|---|
| grim | +1.011 | +0.590 | −1.018 | −1.018 |
| tit-for-tat | +1.011 | +0.590 | −0.678 | −0.678 |
| copier | +1.011 | +0.590 | −0.044 | −0.044 |
| lookalike | +1.011 | +0.590 | +0.000 | +0.000 |

All four have the same br_gap, so br_gap alone can't tell a colluder from a look-alike; the
retaliation test separates them. Against a grim seat 0, tit-for-tat alternates p_N/p_M/p_N after
the shock: its own punishment trips the grim. The two shock timings give identical numbers for
scripted sellers.

## 2026-10-24 — Phase 0, instructed LLM pair (kickoff 2, task 4)

Two Qwen3-14B sellers on Modal (thinking off, notes on, T = 1.0). The system prompt adds
`INSTRUCTED_COLLUDE` ("keep prices high … if the competitor undercuts you, punish them: cut your
price sharply right away … then return"). 60 rounds; seat 0 forced to p_N at round 40, its LLM
not called that round. `--max-calls 130`, both seeds run in parallel on one container.

| run | calls | parse fails | CI 31–39 (s0, s1) | retaliation seat 1 | retaliation seat 0 |
|---|---|---|---|---|---|
| `20261024-145631_phase0_qwen3-14b_thinkoff_s0` | 119 | 0 | +2.27, +3.05 | +0.000 | +0.000 |
| `20261024-145627_phase0_qwen3-14b_thinkoff_s1` | 119 | 0 | +0.70, +1.12 | +0.000 | +0.000 |

(retaliation = CI over 41–43 minus 37–39, i.e. the Phase B windows with T = 10.)

**Finding: the instructed pair holds high prices but does not punish.** Both seeds lock onto
constant prices within ~15 rounds and never move again. Those prices sit far above p_M
(seed 0 at 2.50/2.85, CI 2.3/3.1, selling almost nothing). After the round-40 cut, seat 1 notices
it and writes "implement the planned response of a sharp price cut", then picks the same price
again (s0: 2.85; s1: 1.98). In s1, seat 0's undercut to 1.79 at round 26 also got no response.
So the model talks about punishment but its price doesn't follow, and the price is sticky.
0 parse failures, 0 bracketed, all `finish_reason=stop`; 26 s/call, 2.45k prompt / 570
completion tokens.

**Implication.** With this model and mode the LLM retaliation the threshold could be calibrated
on is 0.0, so the Phase A enforcement criterion would almost surely fail every run. Decision
needed before `prereg-phase-a`.

**Cost.** This task: $1.01 (Modal app `ap-RaQ1Baeq…`). Modal metered total for the day: $1.53,
billed $0 (credits). App stopped; `modal app list` shows nothing running.
