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

## 2026-10-24 — newcomer pilot (Kickoff 05, step 3), plan draft, cost

**Base** `20261024-183620_pilot-base_qwen3-14b_thinkon_s{100,101}`: two `forgive` incumbents,
thinking on, warm-up 1.92/1.92, 40 rounds, no shock, snapshot at T = 40. Both sit at 1.92/1.92
throughout; 0 parse failures.

**Branches** `20261024-184355_phaseB_{same_history,same_none,lookalike}_s{100,101}_*`: 30 rounds,
seat 0 forced to p_N at T+20 = 60, uninstructed newcomer (thinking on) in seat 1 (`instructions[1]`
is null in every config). All 6 completed; 1 parse failure (s101 lookalike, retry parsed).
Table, prices and notes: `seat_swap/results/newcomer_pilot.md`; per-round CSV `newcomer_pilot_ci.csv`.

| seed | arm | newcomer prices | newcomer CI T+10–19 | incumbent punishments | retaliation (T+21–23 minus T+17–19) |
|---|---|---|---|---|---|
| 100 | same_history | 2.00, then 1.92 throughout | +0.99 | 0 | +0.000 |
| 101 | same_history | 2.00, 1.92, 1.95, then 1.92 | +0.99 | 0 | +0.000 |
| 100 | same_none | 2.50 → 2.00 from T+6 | +1.17 (overpriced) | 0 | +0.000 |
| 101 | same_none | ≈ 2.50 throughout | +2.27 (overpriced) | 0 | +0.000 |
| 100 | lookalike | 2.89, 2.25, 2.50, 2.10, then 1.92 | +0.99 | n/a | +0.000 |
| 101 | lookalike | ≈ 1.80 throughout | +0.72 | n/a | +0.037 |

- **The newcomer joins at a high price but never enforces.** No branch responded to the
  incumbent's forced cut. The incumbent never punished the newcomer: no newcomer price fell
  below its 1.70 trigger, including the 1.80 undercut in s101 lookalike (seat 0 is scripted there anyway).
- With history the newcomer copies the cartel's 1.92 within 1–2 rounds. Without history it
  reasons from "$1 cost, $2.89 max willingness to pay" and stays above the cartel (the same
  $2.89 anchor as Kickoff 3).
- The newcomer's first-round notes are generic price-testing plans ("test a price increase to
  $2.00 … monitor elasticity"). None mentions the competitor's rule or punishment. No
  "after first punishment" excerpt exists because there was no punishment.
- Newcomer: 922 reasoning tokens/call, 19.0 s/call; incumbents in the branches 706 tokens,
  15.2 s/call; base 427–487 tokens, 9–10 s/call (12–18 streams).

**Sequencing.** The base launched at 13:06 UTC, right after the control passed. The branches
ran 13:14–13:25 UTC.

**Plan.** `docs/plan.md` drafted (DRAFT, not tagged). Budget re-estimated from these timings at
≈ $6–10. Open decisions for the PI: shock T+30 vs T+20, base length, and whether to report "joins"
and "enforces" separately given the pilot.

**Cost.** One app session `ap-57Rhr6zJ…`, 12:46–13:26 UTC, H100: **$2.53** (Modal hourly report:
$0.80 + $1.73). Split by time: forgiveness control ≈ $1.20 (incl. cold start), pilot ≈ $1.33.
Sprint total metered: **$10.05** (billed $0, credits). Redeployed with `scaledown_window` 2 min,
then `modal app stop -y seat-swap-vllm`.
- Note on `first_hold`: it scores the overpriced `same_none` newcomers as holding from T+1, because
  "≥ 1.90" has no upper bound. Left unchanged and raised as a decision; read those T+1s as overpriced, not joined.
- Doc fixes after review: `same_full` added to the working model's exact arm list; plan proposes
  main-run base seeds 200–214; a T+20 shock would move the metric windows (raised in status).


## 2026-10-24 — Kickoff 06 setup: decisions, discipline probe, freeze (before any run)

- Merged `exp/planted-design` into `main` (`--no-ff`), pushed. Work continues on `exp/p1`.
- PI decisions on plan §10, recorded in the working model and applied to `docs/plan.md`: shock
  at T+30 in 60 rounds (windows unchanged); T = 150; outcomes split into `joins`
  (newcomer CI T+20..29 in (0.5, 1.1]), `enforces` (retaliation ≤ −0.3) and newcomer `overpriced`
  (> 1.1), `re_formed` unchanged; one-round shock kept; `first_hold` bounded at CI [0.9, 1.1];
  base seeds 200–214. §9 now discloses the $2.89 anchor and the probe's forced newcomer price.
- **`first_hold` changed**: 5 consecutive rounds with CI in [0.9, 1.1] (about 1.880–1.970), was
  price ≥ 1.90 with no upper bound. The committed Kickoff 05 pilot table used the old definition
  and is not regenerated; `newcomer_pilot.py`'s docstring says so.
- **Discipline probe** (`branch.run_probe`): every P1 arm writes `snapshot_T<T+15>`, and an
  `on_probe_fork` callback launches the probe at once. Fork after T+15, seat 1 forced to 1.60 at
  T+16 (LLM not called, notes unchanged), T+17..T+29 played, 14 rounds; the lookalike arm keeps its
  scripted seat 0. The probe's `arm` string is `discipline_<parent arm>` so the per-call sampling
  seeds differ between the five probes of one seed. Metrics `probe_punished`, `probe_counter`,
  `probe_return`, `probe_ci_post`, `disciplined` in `metrics.py`, metrics evaluated on the arm's T.
- **Orchestrator** `seat_swap.p1`, two stages so `status.md` can be committed after the gate
  (coordinator's addition to the kickoff): `base` (15 base games + enforcement branches, gate
  ≥ 8/15) and `arms` (5 arms per passing seed, probes launched from the T+15 callback, control kill
  check = `re_formed` in more than half). Per-game `--max-calls`: base 340, enforce 30, arm 135,
  probe 32.
- **Self-test** (`p1 selftest`, dry, and `test_discipline_probe`): grim seat 0 vs copier seat 1 →
  `probe_punished` true in every incumbent arm; lookalike / non-reacting seat 0 → false. 85 tests pass.
- Prompt length at round 150 (dry, with notes): 6,156 tokens; with max_tokens 8192 that fits the
  16,384 context. LLM notes are longer than dry-run notes, so the margin is ~2k tokens.
- One-seed-per-arm price listing: the lowest-numbered passing seed (fixed in plan §5.3 before results).
- Frozen and tagged `prereg-p1`.

## 2026-10-24 — P1 base and gate; arms launched (Kickoff 06, step 4, in progress)

- **Base** `20261024-192633_p1-base_qwen3-14b_thinkon_s{200..214}` (code `650e722` = `prereg-p1`):
  15/15 completed, 0 parse / transport failures, 1.92/1.92 throughout; cartel_ci +0.989 in all 15.
  Enforcement retaliation ≤ −0.3 in 15/15 (8× −0.996, 6× −0.664, s212 −0.332). **Gate 15/15 → arms.**
  Base 13:59–14:59 UTC, one H100, 30 streams, 18.3 s/call (11 s early, ~20 s by round 90).
- Status with the base table committed and pushed before the arms (`47138da`, coordinator's addition).
  **Arms and probes run on `47138da`**, which differs from `prereg-p1` only in `docs/status.md`.
- **Arms** launched 15:03 UTC: 15 seeds × 5 arms, probes launched from each arm's T+15 snapshot
  (75/75 launched by 15:33). Two containers came up.
- **Cost projection rose** once the arms ran: newcomers reason ~1.7k tokens/call in their first
  rounds (pilot average 922), so the projected task total reached the $14 cap (~$13–14.5).
  Planned a hard money stop at 16:10 UTC; the **coordinator then raised the cap to $20** (in session).
  At 15:28 UTC: ~122 calls/min, ~2.4k generated tok/s over two containers, ~100 s/call.

## 2026-10-24 — P1 arms and discipline probes (Kickoff 06, steps 4–5): results

- Arms `20261024-20*_phaseB_*_s{200..214}_*` (75/75 completed, 15:04–16:36 UTC) and probes
  `20261024-2*_probe_discipline_*` (75/75, 15:15–16:13 UTC), code `47138da` (tag `p1`).
  Report: `seat_swap.p1_report` → `results/p1.{md,json}`, `p1_prices.csv`. The report recomputes every
  metric from `snapshot_T*` + `rounds.jsonl` (same `metrics.py` functions), not from the manifest.
- **Kill check: `control` re_formed 15/15** → newcomer arms readable. Probe control: `control`
  disciplined 15/15 → probe readable.
- Per arm (joins / enforces / overpriced / re_formed / disciplined, of 15): control 15/15/0/15/15;
  same_history 13/0/1/0/4; same_none 5/1/6/0/0; same_full 15/6/0/6/2; lookalike 13/0/2/0/0.
- **Newcomers join but don't enforce**, except through the notes: `same_full` re_formed 6/15. The inherited
  notes restate the 1.70 trigger (14/15) but not the 3-round 1.47 punishment, and mentions don't separate enforcers.
- **Probe**: newcomers stay at 1.60–1.70 after the forced 1.60 (`probe_ci_post` ≈ +0.28 / +0.50), punished
  or not (`lookalike` the same). Their notes read the forced price as their own profitable test
  ($40.54 at 1.60 vs $33.75 at 1.92). No newcomer returns to the band at k ≥ 18 (after it could see a
  punishment); the only non-control returns are at T+17, before any punishment was visible (same_history 3,
  lookalike 2). The incumbent re-punished in the probe (spells starting T+21..T+29) in same_history 7/15,
  same_none 7/15 and same_full 8/15 seeds, and the newcomer still didn't return.
- Established-only retaliation (plan §6): control −0.929 (15/15), same_history +0.000 (0/14), same_none
  −0.015 (0/5), same_full −0.215 (5/14), lookalike +0.012 (0/13).
- `same_full` notes: 14/15 mention 1.70, 11/15 punishment, 4/15 1.47, 0/15 three rounds.
  - **Correction (2026-10-25, see `72d5986`):** "0/15 three rounds" is wrong: the regex missed the hyphenated "3-round".
    With the fixed regex, 5/15 P1 `same_full` inherited notes state a duration (3 of the 6 enforcers). The same error is in
    P1's status (`cce5bd4`, "none mentions 3 rounds").
- Failures across the 150 arm and probe games: 2 parse (retry ok), 13 transport (retry ok).
- `same_none`: 6/15 overpriced ($2.89 anchor), several settle at 1.69, just under the 1.70 trigger.
- Timing: arms 70.8 s/call, probes 121.5 s/call (≈ 300 streams on 2 H100s at peak); newcomers 992
  reasoning tok/call, ~1.7k in their first rounds. The arms took about 2× the estimate.
- **Cost: $17.56** for the task (cap raised $14 → $20 by the coordinator mid-run); sprint ≈ $27.6.
  App stopped 16:45 UTC, redeployed at 2 min scaledown, stopped.
- Commits: the base ran on `650e722` (= `prereg-p1`); the arms and probes ran on `47138da` (status-only commit
  after the gate, per the coordinator). Tag `p1` → `47138da`.

## 2026-10-25 — P1b setup, base and gate (Kickoff 07, steps 1–4.1)

- `exp/p1` merged into `main` (`--no-ff`, `d821918`) and pushed; work on `exp/p1b`.
- New arm `same_notes` (`branch.py`: inherit `notes`, the newcomer sees only its own rounds, no instruction) with a
  test of its first prompt (notes in, no round before T+1, no instruction text). `p1.py --phase p1b` (seeds 215–229,
  four arms, no probes); `p1_report` writes `<phase>.*` and reads arms from the manifest (P1 output reproduced
  byte-identical). Decisions recorded in the working model; plan §11 pre-registers P1b with the headline rule.
  Tagged `prereg-p1b` (`9e44323`).
- **Base** `20261024-234550_p1b-base_qwen3-14b_thinkon_s{215..229}` (code `9e44323`): 15/15 completed, cartel_ci +0.989 in
  all, enforcement retaliation −0.996 (7), −0.664 (7), −0.332 (s225). **Gate 15/15 → arms.** 18:13–19:22 UTC,
  slower from 18:30 UTC while P2/P3 also called the 14B app.
- Status with the base table committed and pushed before the arms (as the kickoff says). The arms run on that commit.

## 2026-10-25 — P1b budget cap raised to $20 (coordinator)

- Coordinator's decision during the run (about 19:35 UTC): **P1b cap $20** (was $16). P1b has priority: if total spend would
  pass the caps, the P2/P3 games are stopped first, never P1b. P2 ($9) and P3 ($11) caps are unchanged.
- Projection at that time: P1b ≈ $14–15 (base ≈ $5 on the shared 14B app, arms ≈ 1.6 h at two containers, split by calls with
  the P2/P3 seat-0 load).

## 2026-10-25 — P1b arms: results (Kickoff 07, steps 4–6)

- Arms `20261025-0054*_phaseB_{control,same_history,same_full,same_notes}_s{215..229}_*`, 60/60 completed, 19:25–20:33 UTC,
  code `24f922b` (status-only commit after the gate), tag `p1b`. 0 aborts. Kill check `control` re_formed 15/15.
- P1b (joins / enforces / overpriced / re_formed): control 15/15/0/15; same_history 15/1/0/1; same_full 15/4/0/4; same_notes 14/8/0/8.
  Pooled with P1: same_history 28/1/1/1 of 30; same_full 30/10/0/10 of 30.
- **Headline rule: supported.** Pooled one-sided Fisher p = 0.0028 (same_full 10/30 vs same_history 1/30); P1b alone 4 vs 1.
- Secondary: same_notes re_formed 8/15 ≥ same_full 4/15, joins 14/15, so the notes alone carry enforcement (and the price).
- P1b enforcements are nearly all drops to 1.47 right after the shock (unlike P1). P1's six same_full enforcers: 4 real
  (s202, 203, 209, 212), s204 partial/sticky, s205 a metric artefact (overpriced pre-window).
- Notes features: 1.70 in nearly all inherited notes; "1.47" more often in enforcers' notes (13/18 vs 11/27); no duration ever.
  - **Correction (2026-10-25, see `72d5986`):** "no duration ever" is wrong (same regex bug). A duration is stated in
    same_full 6/10 enforcers vs 9/20 non-enforcers (P1 + P1b), same_notes 7/8 vs 3/7.
- `seat_swap/p1b_analysis.py` (pooled tables, headline rule, §5 tables) → `results/p1b_analysis.{md,json}`.
- Cost split by generated tokens: P1b ≈ $12 of the 14B app's ≈ $16.6 (20:00 UTC hour estimated); Kickoff 08 seat 0 ≈ $4.7.
- `seat-swap-vllm` back to 2 min scaledown, not stopped (Kickoff 07 finish).
- Failures over the 90 P1b games: 1 parse (retry ok), 6 transport (retry ok), 0 aborts.
- Final cost (20:00 UTC hour billed): 14B app $17.40 tonight; **P1b $12.69**, Kickoff 08 seat 0 $4.71. Sprint ≈ $55.8.

## 2026-10-25 — Correction: duration regex in the notes-features table

- `p1b_analysis` matched "3 rounds" but not the hyphenated "3-round" that the notes actually use, so its duration column read
  0 everywhere. Fixed (`[\s-]+`) and regenerated: duration is stated in same_full 6/10 enforcers vs 9/20 non-enforcers,
  same_notes 7/8 vs 3/7. Found by the blinded notes reading (branch `analysis/notes-reading`), whose coders marked a
  duration in 15 of the 30 inherited notes. P1's status claim "none mentions 3 rounds" (Kickoff 06) is likely the same bug.
- `seat-swap-vllm` stopped 2026-10-25 04:30 UTC (`modal app stop`); no Modal app running. Kickoff 08 had finished at 20:06 UTC.

## 2026-10-25 — Kickoff 09: merges, corrections, provenance, P1c freeze and launch

- Merged `exp/p1b`, `exp/p23`, `analysis/notes-reading` into `main` (`--no-ff`, in that order; `1ccc0ab`, `2719592`,
  `4ed4479`). One conflict, `docs/plan.md`: P1b's §11 and P2/P3's §12 both kept, in that order. 109 tests passed after
  the merge. Pushed `main`; work on `exp/p1c`. Branches not deleted: P2/P3's raw runs live only in the
  `cartel-succession-p23` worktree (gitignored), and the post-hoc analyses read them there.
- Duration-regex corrections added under the original lines (above; P1 `same_full`: 5/15 inherited notes state a
  duration, 3 of the 6 enforcers). P1's status line survives only at `cce5bd4`; its correction is in this kickoff's status.
- `docs/provenance.md`: base / arms commits and freeze tags per family.
- **P1c freeze** (`prereg-p1c` = `9c54acb`): three arms `notes_rule_return`, `notes_rule_noreturn`, `notes_status`
  (`same_notes` with fixed template notes; text in plan §13). New metrics in `metrics.py` with tests:
  `back_at_cartel`, `post_shock_ci`, `clean_punish`, `clean_punish_return`. Operational choices made by me and frozen
  in §13 (listed for the PI in status): "no punishment under way" = both seats ≥ 1.70 in each of T+25..T+29; the
  6-round return window starts after the first round at ≤ 1.55; one round at CI ≥ 0.9 counts as back;
  `back_at_cartel` has no upper bound. `p1.py rebranch` writes a new manifest from P1b's (P1b's is only read).
- Smoke (2 rounds, s215 `notes_rule_return`, scratch dir): first attempt hit the cold start (503 "no upstreams"),
  second completed: model revision `40c06982`, template in the rendered prompt, no table, no instruction.
- **Launch** 07:10 UTC: `seat_swap.p1 rebranch --phase p1c --manifest seat_swap/runs/p1b_20261024-234550.json` →
  manifest `seat_swap/runs/p1c_20261025-124057.json`, 45/45 games started on `9c54acb`. `seat-swap-vllm` at 10-min scaledown.

## 2026-10-25 — Kickoff 09: post-hoc analyses, figures, P1c results

- `seat_swap/posthoc.py` → `results/posthoc.{md,json}` (post hoc, not pre-registered; 195 games P1/P1b/P2/P3; pre-registered
  outcomes recomputed and matched every run summary). Key numbers: all 30 bases share one price path; pooled `same_full`
  vs `same_history` on unique paths p = 0.0023; pooled `same_full` re-formed 2/10 back at the cartel vs 16/20 for the rest;
  clean_punish pooled `same_full` 8/30, `same_notes` 6/15; P1b McNemar `same_notes` vs `same_history` `re_formed` 7–0,
  p = 0.016; P3 without the 7 invisible-shock games: `oth_full` re_formed 4/12.
- `seat_swap/figures.py` → figs 1–6 (PDF/PNG, deterministic PDFs) + `captions.md`. matplotlib added to the project.
- **P1c** (manifest `runs/p1c_20261025-124057.json`, code `9c54acb`, tag `p1c`): 45/45 completed 07:11–07:56 UTC,
  0 parse / 0 transport failures, 5,355 calls, 29.9 s/call, newcomers 865 reasoning tok/call.
  re_formed: rule_return 3/15, rule_noreturn 4/15, status 0/15; back_at_cartel 8/15, 10/15, 10/15.
  Primary tests: rule_return > status on re_formed p = 0.112; rule_return > noreturn on back_at_cartel p = 0.868.
  Neither prediction for the rule arms met; status arm as predicted. Descriptive: the template rule survives in the newcomer's
  notes to T+10 in 3/15 (return) and 7/15 (no return) vs 8/15 for real notes; 0/7 template enforcers back at the cartel.
- Cost: 14B app $6.39 (07:00 UTC hour). Sprint ≈ $62.2. App redeployed at 2 min and stopped 07:58 UTC.
