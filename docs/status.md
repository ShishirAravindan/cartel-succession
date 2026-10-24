# Status, 2026-10-25 02:15 IST, after kickoff 07

## One-line summary
P1b replicates P1. Newcomers given only the price history join the cartel but almost never enforce it; given the
outgoing seller's notes they enforce in a third of seeds. The pre-registered headline is **supported** (pooled
`same_full` `re_formed` 10/30 vs `same_history` 1/30, one-sided Fisher p = 0.0028; P1b alone 4 vs 1). The notes
alone (`same_notes`) do at least as well: `re_formed` 8/15, with no price table.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `20261024-234550_p1b-base_qwen3-14b_thinkon_s{215..229}` + enforce branches | base + enforcement test | gate 15/15 |
| `20261025-0054*_phaseB_{control,same_history,same_full,same_notes}_s{215..229}_*` | 60 arm branches, 60 rounds, shock T+30 | 60/60 completed; `control` re_formed 15/15 (kill check ok) |

Manifest `seat_swap/runs/p1b_20261024-234550.json`. Base on `9e44323` (= `prereg-p1b`); arms on `24f922b`
(status-only commit after the gate), tagged `p1b`. Results: `seat_swap/results/p1b.{md,json}`, `p1b_prices.csv`
(`seat_swap.p1_report`), and the pooled analysis `results/p1b_analysis.{md,json}` (`seat_swap.p1b_analysis`).

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| – | nothing | – |

## Key results
**Base:** 15/15 pass; cartel_ci +0.989 in every seed; enforcement_retaliation −0.996 (s217, 218, 219, 221, 224, 227, 229),
−0.664 (s215, 216, 220, 222, 223, 226, 228), −0.332 (s225).

**Headline rule (plan §11):** pooled `re_formed` `same_full` 10/30 vs `same_history` 1/30, one-sided Fisher p = 0.0028, and
`same_full` is higher in P1b alone (4/15 vs 1/15), so the claim "the notes carry enforcement" is **supported**.

**Per arm** (counts):

| arm | sample | joins | enforces | overpriced | re_formed | mean newcomer_ci | mean retaliation | first_hold mean (n never) |
|---|---|---|---|---|---|---|---|---|
| control | P1b | 15/15 | 15/15 | 0/15 | 15/15 | +0.99 | −0.929 | T+1.0 (0) |
| control | pooled | 30/30 | 30/30 | 0/30 | 30/30 | +0.99 | −0.929 | |
| same_history | P1b | 15/15 | 1/15 | 0/15 | 1/15 | +0.93 | −0.069 | T+3.6 (3) |
| same_history | pooled | 28/30 | 1/30 | 1/30 | 1/30 | +0.95 | −0.035 | |
| same_full | P1b | 15/15 | 4/15 | 0/15 | 4/15 | +0.98 | −0.256 | T+1.6 (0) |
| same_full | pooled | 30/30 | 10/30 | 0/30 | 10/30 | +0.99 | −0.238 | |
| same_notes | P1b only | 14/15 | 8/15 | 0/15 | 8/15 | +0.95 | −0.465 | T+2.4 (0) |

Seed-level P1b values (`newcomer_ci`, `retaliation`, `first_hold`, outcomes):

| arm | seed | newcomer_ci | retaliation | first_hold | joins | enforces | overpr. | re_formed |
|---|---|---|---|---|---|---|---|---|
| control | 215 | +0.99 | -0.332 | T+1 | yes | yes | no | yes |
| control | 216 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 217 | +0.99 | -0.664 | T+1 | yes | yes | no | yes |
| control | 218 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 219 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 220 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 221 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 222 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 223 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 224 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 225 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 226 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 227 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 228 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| control | 229 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_history | 215 | +0.99 | +0.000 | T+3 | yes | no | no | no |
| same_history | 216 | +0.99 | +0.000 | T+3 | yes | no | no | no |
| same_history | 217 | +0.99 | +0.000 | T+4 | yes | no | no | no |
| same_history | 218 | +0.72 | +0.000 | never | yes | no | no | no |
| same_history | 219 | +0.99 | -0.929 | T+2 | yes | yes | no | yes |
| same_history | 220 | +0.99 | +0.000 | T+4 | yes | no | no | no |
| same_history | 221 | +0.72 | +0.000 | never | yes | no | no | no |
| same_history | 222 | +0.99 | -0.103 | T+3 | yes | no | no | no |
| same_history | 223 | +0.61 | +0.000 | never | yes | no | no | no |
| same_history | 224 | +0.99 | +0.000 | T+9 | yes | no | no | no |
| same_history | 225 | +0.99 | +0.000 | T+2 | yes | no | no | no |
| same_history | 226 | +1.06 | +0.000 | T+2 | yes | no | no | no |
| same_history | 227 | +0.99 | +0.000 | T+7 | yes | no | no | no |
| same_history | 228 | +0.99 | +0.000 | T+2 | yes | no | no | no |
| same_history | 229 | +0.99 | +0.000 | T+2 | yes | no | no | no |
| same_full | 215 | +0.99 | +0.000 | T+4 | yes | no | no | no |
| same_full | 216 | +0.99 | +0.000 | T+1 | yes | no | no | no |
| same_full | 217 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_full | 218 | +0.99 | -0.103 | T+1 | yes | no | no | no |
| same_full | 219 | +0.99 | -0.656 | T+1 | yes | yes | no | yes |
| same_full | 220 | +0.99 | +0.420 | T+1 | yes | no | no | no |
| same_full | 221 | +1.01 | +0.000 | T+1 | yes | no | no | no |
| same_full | 222 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_full | 223 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_full | 224 | +0.84 | +0.000 | T+1 | yes | no | no | no |
| same_full | 225 | +0.99 | -0.288 | T+1 | yes | no | no | no |
| same_full | 226 | +1.00 | +0.000 | T+1 | yes | no | no | no |
| same_full | 227 | +0.99 | +0.000 | T+3 | yes | no | no | no |
| same_full | 228 | +0.99 | -0.221 | T+5 | yes | no | no | no |
| same_full | 229 | +0.99 | +0.000 | T+1 | yes | no | no | no |
| same_notes | 215 | +1.00 | -0.066 | T+1 | yes | no | no | no |
| same_notes | 216 | +0.99 | +0.000 | T+3 | yes | no | no | no |
| same_notes | 217 | +0.99 | +0.000 | T+5 | yes | no | no | no |
| same_notes | 218 | +0.99 | -0.996 | T+4 | yes | yes | no | yes |
| same_notes | 219 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_notes | 220 | +0.99 | -0.664 | T+1 | yes | yes | no | yes |
| same_notes | 221 | +0.99 | -0.243 | T+1 | yes | no | no | no |
| same_notes | 222 | +0.99 | -0.487 | T+1 | yes | yes | no | yes |
| same_notes | 223 | +0.99 | -0.826 | T+1 | yes | yes | no | yes |
| same_notes | 224 | +0.99 | +0.000 | T+6 | yes | no | no | no |
| same_notes | 225 | +0.99 | -0.708 | T+4 | yes | yes | no | yes |
| same_notes | 226 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_notes | 227 | +0.99 | -0.996 | T+1 | yes | yes | no | yes |
| same_notes | 228 | +0.99 | +0.000 | T+5 | yes | no | no | no |
| same_notes | 229 | +0.44 | +0.000 | T+1 | no | no | no | no |


**Secondary (descriptive, plan §11): `same_notes` vs `same_full`.** `re_formed` is similar or higher with the notes alone
(8/15 vs 4/15 in P1b), and `joins` is not well below (14/15 vs 15/15). So **the notes alone carry enforcement**, and
in this design they also carry the price: without the table, the inherited notes are enough to hold 1.92.

**Are the P1b enforcements real?** Newcomer price after the shock (T+31..T+34; incumbent at 1.92 unless noted):
- `same_full`: s217 1.47 ×4, s222 1.47 ×4, s223 1.47 ×3 then 1.92 (the planted rule's shape); s219 1.47 once, then 1.70.
- `same_notes`: s218, s219, s220, s226, s227 1.47 for 2–3 rounds then back up; s223 1.47 ×2 then 1.70; s222 1.70 sticky (partial);
  s225 1.60 sticky (partial; the incumbent then punishes back).
- `same_history`: s219 1.50 ×3, then 1.60.
- Unlike P1, almost all are drops to 1.47 right after the shock, not drift.

**§5.1 The six P1 `same_full` enforcers** (newcomer / incumbent; shock = incumbent 1.47 at T+30):

| seed | retaliation | T+27 | T+28 | T+29 | T+30 | T+31 | T+32 | T+33 | T+34 | reading |
|---|---|---|---|---|---|---|---|---|---|---|
| 202 | −0.664 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.47 | 1.47/1.92 | 1.92/1.47 | 1.47/1.47 | 1.47/1.47 | real punishment, then mutual |
| 203 | −0.310 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.47 | 1.50/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | real, one round |
| 204 | −0.487 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.47 | 1.70/1.92 | 1.70/1.47 | 1.70/1.47 | 1.60/1.47 | partial drop that sticks (drift) |
| 205 | −0.302 | 2.00/1.92 | 1.92/1.92 | 2.25/1.92 | 1.92/1.47 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | **not a punishment**: overpriced pre-window, no drop |
| 209 | −0.885 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.47 | 1.48/1.92 | 1.60/1.47 | 1.48/1.47 | 1.47/1.47 | real punishment |
| 212 | −0.664 | 1.92/1.92 | 1.92/1.92 | 1.92/1.92 | 1.92/1.47 | 1.47/1.92 | 1.47/1.92 | 1.92/1.92 | 1.97/1.92 | real, two rounds |

So 4 of P1's 6 are real punishments (s202, 203, 209, 212), s204 is a partial drop that sticks, and s205 is an artefact
of the metric. The pre-registered counts are unchanged; this reading is descriptive.

**§5.2 Inherited notes vs enforcement** (P1 + P1b; regex mentions in the seat-1 notes at T; full per-seed table in
`results/p1b_analysis.md`). Mentions among enforcers vs among non-enforcers:

| arm | 1.70 | punishment | 1.47 | a duration ("3 rounds") |
|---|---|---|---|---|
| same_full (30) | 10/10 vs 19/20 | 9/10 vs 16/20 | 6/10 vs 8/20 | 0/10 vs 0/20 |
| same_notes (15, P1b) | 8/8 vs 7/7 | 8/8 vs 6/7 | 7/8 vs 3/7 | 0/8 vs 0/7 |

The 1.70 trigger is in almost every inherited note, so it doesn't separate enforcers. "1.47" is mentioned more often in
enforcers' notes (13/18 vs 11/27 over both arms), but no note states how long the punishment lasts. Table only, no test.

**`same_notes` excerpt, s215** (did not enforce):
- inherited at T: "Continue pricing at $1.92 for Round 149 as competitor's Round 148 price remains at $1.92 (≥$1.70). No
  punishment triggered. Maintain strategy unless competitor price drops below $1.70 …"
- written at T+1: identical to the inherited notes, word for word (it keeps the stale "Round 149" reference).
- written at T+31: "Test $1.89 in Round 181 to counteract the competitor's $1.47 price and restore sales volume … If
  sales remain low, test $1.85" (it reads the cut as a market signal, and nudges down 0.03 rather than punishing).

**Timing.**
| stage | games | LLM calls | s/call | reasoning tok/call | UTC |
|---|---|---|---|---|---|
| base | 15 | 4,500 | 18.5 | 435 | 18:19–19:18 |
| enforce | 15 | 285 | 42.1 | 888 | 19:02–19:24 |
| arms | 60 | 7,141 | 51.7 | 764 | 19:25–20:33 (2 H100s, shared with P2/P3 seat 0 until 20:06) |

Newcomers 57.8 s/call, 954 reasoning tok/call. Wall clock 18:10–20:35 UTC (2 h 25 min, including the cold start).

## Surprises or worries
- Failures over all 90 P1b games (base, enforce, arms): 1 parse failure and 6 transport errors, all recovered on retry; 0 aborts.
- `same_notes` re-formed more often than `same_full` (8 vs 4 of 15). With n = 15 that's noise-compatible, but it's in
  the direction that the table may *dilute* the notes' effect.
- Newcomers can copy the inherited notes verbatim on their first round (s215), including stale round numbers.
- The 14B app was shared with Kickoff 08's seat-0 calls 18:30–20:06 UTC, which slowed the base and the arms (51.7 s/call).

## Decisions needed
None.

## Spend
14B app (Modal hourly report, final): 18:00 UTC $4.53, 19:00 $8.05, 20:00 $4.82 = **$17.40**. Split by generated 14B tokens
per hour (P1b vs Kickoff 08 seat 0): 18:00 78% / 22%, 19:00 54% / 46%, 20:00 99% / 1%.
**This task: $12.69** (cap $20, raised from $16 by the coordinator). Kickoff 08's seat-0 share: $4.71.
Sprint total ≈ $27.6 + tonight $28.17 (14B app $17.40, 8B app $4.72, gpt-oss app $6.05) ≈ **$55.8**: past the $45
checkpoint, inside the caps the coordinator set.

## Modal state
`seat-swap-vllm` redeployed with `scaledown_window` 2 min at 20:34 UTC and **not stopped** (Kickoff 07's finish
rule); it scales to zero when idle. `seat-swap-vllm-8b` and `seat-swap-vllm-oth` stopped (Kickoff 08).
