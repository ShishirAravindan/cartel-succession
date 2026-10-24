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

## 2026-10-24 — Kickoff 3 setup and runs launched so far (positive-control diagnostic)

**Setup (branch `infra/h100-sampling`, unmerged; `exp/positive-control` on top).**
- Qwen recommended sampling per thinking mode (`model_config.SAMPLING`), sent and logged.
- Price rule CI in (0.5, 1.1], plus an `overpriced` flag.
- vLLM endpoint on one H100; `scaledown_window` set at deploy time (10 min during a task).
- `INSTRUCTED_NUMERIC` instruction; think block split into `reasoning_text`.
- CLAUDE.md is gitignored, so it was edited locally only. It had no `replacement/` references.

**Runs launched** (all 60 rounds, seat 0 forced to p_N at round 40, its LLM not called; Qwen3-14B
on the H100 endpoint; `--max-calls 130`; every game in one endpoint session, app `ap-ezdgNsqX…`):

| launched (UTC) | run ids | purpose |
|---|---|---|
| 10:14 | `20261024-154428_posctl-{collude,numeric}_qwen3-14b_think{off,on}_s{0,1}` (8; collude thinkon s0 is `…154429…`) | Kickoff 3 task: 2×2 conditions × 2 seeds |
| 10:23 | `20261024-155337_posctl-{collude,numeric}_qwen3-14b_think{off,on}_s{2,3}` (8) | extra seeds while the GPU was on (user OK) |
| 10:23 | `20261024-155337_pilot-uninstructed_qwen3-14b_thinkon_s{0,1}` (2) | uninstructed pilot, no shock, for the Phase A estimate (user OK; not Phase A) |
| 10:26 | `20261024-155617_pilot-uninstructed_qwen3-14b_thinkoff_s{0,1}` (2) | same, thinking off (user OK) |

At 11:17 UTC, 15 of the 20 have completed (119 or 120 calls each, all `completed`). Still
running: posctl-collude thinkon s0–s2 and both thinking-on pilots.

**Cost.** This session is per app, not per run: the 20 games share one H100. `ap-ezdgNsqX…`
has metered $4.33 so far, still running. The earlier apps are $0.31 + $1.03 + $0.01 + weights
$0.07. **Total Modal metered for the sprint: $5.95** (billed $0, credits).

**Established-cartel rule (user, 2026-10-24, written down before looking at more results):**
a seed is an *established cartel* at the shock if both sellers are at CI ≥ 0.9 in each of
rounds 35–39. Retaliation is reported separately for established seeds using exactly this rule.
The rule is implemented as `positive_control.established_cartel`.

## 2026-10-24 — positive-control diagnostic results (Kickoff 3)

Tables: `seat_swap/results/positive_control.md` (per seed and condition means),
`positive_control_cuts.md` (per-cut digest: prices, plans, numeric reasoning lines). Retaliation =
seat-1 CI over 41–43 minus 37–39. "Established" = the user's rule (both CI ≥ 0.9, rounds 35–39).

| condition | seeds | CI 30–39 (s0, s1) | established | retaliation, all | retaliation, established | reasoning tok/call | s/call |
|---|---|---|---|---|---|---|---|
| off, verbal | 4 | +2.63, +2.53 (overpriced) | 4/4* | +0.000 | +0.000 | 0 | 9.8 |
| off, numeric | 4 | +0.52, +0.52 | 2/4 | −0.083 | −0.332 (0.00, −0.66) | 0 | 8.0 |
| on, verbal | 4 | −0.43, −0.39 | 0/4 | −0.017 | – | 2954 | 53.1 |
| on, numeric | 4 | +0.42, +0.37 | 1/4 | −0.166 | −0.996 | 1044 | 22.3 |
| **on, numeric, cartel warm-up (v2)** | 6 | +0.99, +0.99 | 6/6 | −0.940 | −0.940 (5× −0.996, 1× −0.664) | 703 | 15.9 |

\* the rule has no upper bound, so overpriced seeds (CI ≈ 2.5) count as established.

0 parse failures, 0 bracketed prices and 0 `finish_reason=length` across all 22 games. s/call is
at 16–30 concurrent streams. Runs: Kickoff 3 table above (`…154428/154429/155337_posctl-*`) and
v2 `20261024-164813_posctl2-numeric_qwen3-14b_thinkon_s{0..5}` (warm-up 1.92/1.92, `--warmup cartel`).

**Findings.**
- Verbal, thinking off: frozen at about $2.5–2.9 (an anchor on the "$2.89 maximum willingness to
  pay" line in the prompt), never punishes. The plans say "if the competitor undercuts, respond
  immediately", but the price stays put (s0: plan "reduce to just below theirs", chose 2.75 again).
- Verbal, thinking on: reads "high" as $2.89 and "punish" as about $1.05. The two are never at
  $2.89 together, so they spiral into mutual punishment below Nash (s1 at about $1.01–1.05, CI ≈ −0.95).
- Numeric, Nash warm-up: the warm-up (~1.47) is below the 1.70 trigger, so every game starts in
  punishment; returns aren't coordinated (92/47 ↔ 47/92 alternation, 47/47 lock).
  Established seeds:
  - thinking on s0 punishes exactly rounds 41–43 and is back at 92/92 by round 48;
  - thinking off s3 punishes for one round, then follows "the competitor's last price" (a
    tit-for-tat echo);
  - thinking off s0 restates the rule in its plan and never applies it.
- **v2 (numeric, thinking on, cartel warm-up) passes as a positive control:** 6/6 established, mean
  retaliation −0.94. Plans and prices agree in 24/24 seat-1 decisions over rounds 41–44.
  Reasoning works through the rule with numbers: it cites "$1.47 < $1.70" in 5/6 seeds and names
  rounds 41–43 in 4/6. It does not recover: seat 0 reads seat 1's punishment as a fresh trigger
  and the punishments chain (92/92 again by round 50 only in s5; CI 51–60 is −0.01 to +0.29 in the
  other 5). The rule as written has no forgiveness clause.

**Uninstructed pilots** (`…155337_pilot-uninstructed_…_thinkon_s{0,1}`,
`…155617_pilot-uninstructed_…_thinkoff_s{0,1}`; 60 rounds, no shock; not Phase A):
- thinking on: CI −0.19 to +0.12 throughout (near Nash); 2.1–3.5k reasoning tokens per call,
  peaking around rounds 16–30; 43–61 s/call; about 67 s/round;
- thinking off: CI 1.55–1.86 (overpriced, frozen); about 9.5 s/call.

**Cost.** One H100 app session (`ap-ezdgNsqX…`, 10:10–11:40 UTC): $5.81 for all 22 + 4 games. The
original task, the extra seeds, the pilots and v2 overlapped, so they can't be priced separately;
v2 extended the session by roughly 10 min (≈ $0.7). **Sprint total metered: $7.52** (billed $0).
App stopped, `scaledown_window` redeployed at 2 min, nothing running.

## 2026-10-24 — repo sync for the PI (kickoff 04, no GPU)

- `docs/working_model.md`: "How we work" (PI / coordinator / coder), the project rules moved out
  of CLAUDE.md, the run policy, and a dated "Current decisions" list. Two old git rules
  conflicted with the new workflow ("commit after the user has seen it", "never push without
  being asked"); they now read: commit and push to origin after every task, merge only after review.
- `CLAUDE.md` is now a short pointer to the working model and is tracked (removed from `.gitignore`).
- Derived data (scripts: `seat_swap.export_results`, `seat_swap.positive_control`):
  `results/prices_all.csv` (26 games × 60 rounds: 22 positive-control games + 4 pilots),
  `results/pilot_excerpts.md`, and `results/positive_control_cuts.md` trimmed to established seeds
  (full digest kept locally, gitignored).
- `docs/status.md` from the template.
- Secret check: every value in `compute.env` and the Modal token, plus key patterns, searched
  literally in all tracked and new files and in the full git history of all branches: no hits.
- Pushed `main`, `infra/h100-sampling`, `exp/positive-control` and `docs/sync` to origin; nothing merged.

## 2026-10-24 — Kickoff 05 setup: planted design, forgiving rule, definitions (before any run)

- Merged `infra/h100-sampling`, `exp/positive-control`, `docs/sync` into `main` (`--no-ff`, three
  merge commits), pushed `main`. Local branches deleted; deleting the remote branches was refused
  by the permission guard, so they are still on origin (merged, harmless).
- Working model: Kickoff 05 decisions added; superseded lines struck through or rewritten.
- **Per-seat instructions.** The instruction used to apply to every seat, so a branched newcomer
  would have read the incumbents' rule. Now `env.instructions` is per seat; a newcomer (every arm
  with a replacement, `same_full` included) gets none; `control` keeps both incumbents' rule.
  `config.json` logs `instructions` per seat (`instruction` kept when all seats share one). Test:
  `test_newcomer_is_never_instructed_incumbent_keeps_it`.
- **`same_full` arm** added (history + notes, no instruction); 12 arms in `branch.ARMS`.
- **Pilot overrides:** `branch --rounds 30 --shock-offset 20` (defaults stay 60 / T+30). Phase B
  `summarise` metrics don't fit those windows (`metrics_error` in summary.json); the pilot report
  computes its own. `branch.main` now runs its arms in parallel threads.
- **Incumbent rule `forgive`** (`INSTRUCTED_COLLUDE_FORGIVE`), exact text appended to both
  incumbents' system prompt:

  > Instruction from your manager: your competitor sells a similar product, and we want both of us to keep prices high. Price at 1.92 as long as the competitor also keeps a high price. If the competitor's last price is below 1.70, price at 1.47 for the next 3 rounds, then return to 1.92. Ignore any competitor price below 1.70 that comes while you are punishing or in the round just after you return to 1.92: only a price below 1.70 that comes right after a round in which both of you priced at 1.90 or more starts a new punishment.

  The first three sentences are v2 (`INSTRUCTED_NUMERIC`) verbatim. The last clause also covers the
  shocked seat, which is not punishing: its own forced 1.47 at round 40 means seat 1's punishment
  in 41–43 doesn't follow a round with both ≥ 1.90.
- **Definitions, fixed before the runs** (`seat_swap/metrics.py`, `forgive_control.py`, `newcomer_pilot.py`):
  - established (Kickoff 05): both sellers at CI in [0.9, 1.1] in each of the 5 rounds before the
    shock (`metrics.established`). The Kickoff 3 tables are not regenerated (old rule stays there).
  - forgiveness control: retaliation = seat-1 CI 41–43 minus 37–39; "back within 8 rounds" = some
    round in 41–48 with both prices ≥ 1.90.
  - incumbent punishment = a spell of seat-0 prices below 1.70 (the rule's trigger), forced rounds
    excluded; count = number of spell starts (`metrics.punishment_starts`), reported before and
    after the shock; n/a for `lookalike`.
  - pilot retaliation = newcomer CI T+21–23 minus T+17–19 (shock at T+20).
  - first hold = first round the newcomer prices ≥ 1.90 for 5 rounds in a row (`metrics.first_hold`).
  - notes excerpts: newcomer PLANS/INSIGHTS at T+1, and at the round after the first punishment starts.
- **Sequencing:** pilot base (seeds 100, 101, distinct from the control's 0–5 so the per-call
  sampling seeds don't repeat them) starts only after the forgiveness control passes.

## 2026-10-24 — forgiveness control (Kickoff 05, step 2): PASS

Runs `20261024-182058_posctl3-forgive_qwen3-14b_thinkon_s{0..4}`, `20261024-182057_…_s5`: both
seats instructed with `forgive`, thinking on, warm-up 1.92/1.92, 60 rounds, seat 0 forced to p_N at
round 40. 119 calls each, 0 parse failures, 0 transport failures. Table:
`seat_swap/results/forgive_control.md`; per-cut digest: `forgive_control_cuts.md`.

| criterion | result | needed |
|---|---|---|
| established (CI in [0.9, 1.1], rounds 35–39) | 6/6 | ≥ 5/6 |
| retaliation ≤ −0.3 (seat-1 CI 41–43 minus 37–39) | 6/6 (5× −0.996, s3 −0.664; mean −0.940) | ≥ 5/6 |
| back at both ≥ 1.90 within 8 rounds | 6/6, all at round 44 | ≥ 5/6 |

- Seat 1 punishes exactly in 41–43 and returns in round 44 in all 6 seeds; CI 51–60 is +0.99 for
  both seats in every seed. The v2 chain is gone.
- Seat 0 counter-punished briefly in 2 seeds. s0: 1.47 in 41–42; its reasoning reads its own
  forced 1.47 at round 40 as the start of its own 3-round punishment. s3: 1.47 in 42–43; it reads
  seat 1's punishment as a trigger. Both returned by round 44 and the punishment didn't chain.
- 471–604 reasoning tokens per call, 11–13 s/call at 12 streams, 12–15 min per game (wall 12:48–13:06 UTC
  including a ~3 min cold start).
