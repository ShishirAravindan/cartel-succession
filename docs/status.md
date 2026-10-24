# Status, 2026-10-24 17:46 IST, after kickoff 04

Kickoff 04 was housekeeping only (no GPU runs). This status covers the latest experiment, the
**positive-control diagnostic** (Kickoff 03), plus its follow-up v2.

## One-line summary
Qwen3-14B enforces a cartel reliably only when told the punishment rule in numbers, with thinking
on, and starting from the cartel price (v2: 6/6 seeds punish a cut, mean retaliation −0.94). A
verbal "punish undercuts" instruction never produces enforcement in either thinking mode.
Uninstructed pilots sit near Nash (thinking on) or overpriced (thinking off), so Phase A as planned
may find no cartels.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `20261024-154428_posctl-{collude,numeric}_qwen3-14b_think{off,on}_s{0,1}` (collude-on s0: `…154429…`), `20261024-155337_posctl-…_s{2,3}` | positive control, 2×2 conditions × 4 seeds, 60 rounds, seat 0 forced to p_N at round 40 | 16 games, 0 parse failures, 0 `length` cut-offs; table below |
| `20261024-164813_posctl2-numeric_qwen3-14b_thinkon_s{0..5}` | positive control v2: numeric, thinking on, warm-up at 1.92/1.92 | 6/6 established; retaliation −0.996 ×5, −0.664 ×1 |
| `20261024-155337_pilot-uninstructed_qwen3-14b_thinkon_s{0,1}` | uninstructed pilot, thinking on, 60 rounds, no shock (not Phase A) | CI −0.19 to +0.12 all game; 2.1–3.5k reasoning tok/call; ~67 s/round |
| `20261024-155617_pilot-uninstructed_qwen3-14b_thinkoff_s{0,1}` | uninstructed pilot, thinking off | CI 1.55–1.86 all game (overpriced, frozen); ~9.5 s/call |

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| – | nothing | – |

## Key results
Retaliation = seat-1 CI over 41–43 minus 37–39. Established = both sellers at CI ≥ 0.9 in each of
rounds 35–39 (rule fixed before the results). Seed-level rows: `seat_swap/results/positive_control.md`.
Price series: `seat_swap/results/prices_all.csv`. Responses to each cut (established seeds):
`seat_swap/results/positive_control_cuts.md`. Pilot notes and reasoning: `seat_swap/results/pilot_excerpts.md`.

| thinking | instruction | seeds | CI 30–39 (s0, s1) | established | retaliation, all seeds | retaliation, established | reasoning tok/call | s/call |
|---|---|---|---|---|---|---|---|---|
| off | verbal | 4 | +2.63, +2.53 | 4/4* | +0.000 | +0.000 | 0 | 9.8 |
| off | numeric | 4 | +0.52, +0.52 | 2/4 | −0.083 | −0.332 (0.00, −0.66) | 0 | 8.0 |
| on | verbal | 4 | −0.43, −0.39 | 0/4 | −0.017 | – | 2954 | 53.1 |
| on | numeric | 4 | +0.42, +0.37 | 1/4 | −0.166 | −0.996 | 1044 | 22.3 |
| on | numeric, cartel warm-up (v2) | 6 | +0.99, +0.99 | 6/6 | −0.940 | −0.940 | 703 | 15.9 |

\* the established rule has no upper bound, so overpriced seeds (CI ≈ 2.5) count.

**Plans vs prices.**
- Thinking off: plans state the punishment but the price doesn't follow (verbal s0: plan "reduce
  to just below theirs", chose 2.75 again; numeric s0: restates the 1.70 rule, keeps 1.92).
- v2: plan and price agree in 24/24 seat-1 decisions over rounds 41–44.

**Reasoning (thinking on).**
- In the seeds that retaliate, the reasoning computes the response: it checks "$1.47 < $1.70"
  (5/6 v2 seeds), names rounds 41–43 (4/6), and compares profits ($33.75 vs $11.94).
- Verbal thinking-on reasoning is long (~3k tokens) and number-heavy, but it computes
  "high = $2.89, punish = $1.05".

**Phase A estimate** (thinking on, P0, 10 seeds, 150 rounds + 10 enforcement branches, one H100,
all parallel; based on the pilot's ~67 s/round at 62–66 tok/s per stream):
- main lines ≈ 3.1 h (slowest seed); branches ≈ 12 min; cold start + idle ≈ 13 min;
- **≈ 3.4 h wall (3–4 h), ≈ $13.5 ($12–16)**;
- thinking-off main lines in the same session would add ≈ $0.

## Surprises or worries
- **Phase A may produce no cartels.** Uninstructed thinking-on play sits near Nash and
  uninstructed thinking-off freezes overpriced (CI 1.55–1.86, excluded by the new 1.1 cap).
  This rests on 2 pilots each of 60 rounds, so it isn't conclusive.
- **"$2.89" anchor.** Both verbal conditions anchor on the prompt's "maximum any customer would
  pay is $2.89". That likely drives the thinking-off overpricing; it's in the upstream product
  text, so it is part of what every seller sees.
- **v2 never recovers after punishing.** Seat 0 reads seat 1's punishment as a fresh trigger; the
  punishments chain (back at 92/92 within 20 rounds in 1/6 seeds). The rule has no forgiveness clause.
- **Numeric rule with the near-Nash warm-up** starts every game in punishment (warm-up ~1.47 < 1.70).
- The established rule counts overpriced seeds; harmless for v2, but worth an upper bound if reused.
- `docs/plan.md`, which the working model cites for the full plan and the prereg freeze, does not exist.

## Decisions needed
1. **Phase A thinking mode.** Options:
   - (a) thinking on as estimated ($13.5, ~3.4 h);
   - (b) thinking off ($2.5, ~40 min), but the pilots say overpriced;
   - (c) both in one session (≈ thinking-on cost).

   My recommendation: (c), because the thinking-off main lines cost ≈ $0 on top, and both modes
   are uncertain to produce cartels.
2. **Go / no-go on Phase A given the pilots.** Options:
   - (a) run as planned and report whatever comes out, zero cartels included;
   - (b) first a cheap 150-round pilot of 2–4 seeds per mode (~$4–5) to see whether any run
     reaches CI in (0.5, 1.1];
   - (c) rethink the setup (the PI's call).

   My recommendation: (a) with 10 seeds if the budget is fine: a zero-cartel result is itself a
   finding, and (b) costs a third of the run for less information.
3. **Seeds.** Options: (a) 5 as planned; (b) 10 as in the estimate; (c) 15 (≈ same wall and cost,
   since cost is set by the slowest game). My recommendation: (c), for more chances of a cartel at
   ≈ no extra cost.
4. **Retaliation threshold** is still unset. Scripted values: grim −1.02, tit-for-tat −0.68,
   copier −0.04, lookalike 0.00; LLM v2: −0.94 mean (−0.66 to −1.00). Any value in about (−0.6, −0.1)
   separates tit-for-tat from the copier. Needed before `prereg-phase-a`.
5. **`docs/plan.md`** does not exist; the prereg freeze refers to it. Options: (a) I draft it from
   the working model and decisions; (b) the PI writes it. My recommendation: (a), for the PI to review.

## Spend
This task: $0 (no GPU). Positive-control diagnostic session: $5.81. Sprint total: $7.52 of $80
(checkpoint at $45). Billed $0 so far (credits).

## Modal state
No apps running (`modal app list`: nothing deployed or running). `seat-swap-vllm` was last deployed
with `scaledown_window` = 2 min (the default in `seat_swap/modal_vllm.py`), then stopped.
