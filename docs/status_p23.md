# Status P2/P3, 2026-10-25 01:45 IST, after kickoff 08

## One-line summary
Switching the newcomer model changes what crosses over. The smaller sibling (Qwen3-8B) keeps the cartel price from the
history alone (15/15 join) but never enforces. The other-family model (gpt-oss-20b) mostly doesn't keep the price
from the history (3/15 join). With the outgoing seller's notes it joins 10/15 and `re_formed` 6/15, but most of those
"enforcements" are not clean punishments.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `p23_sib_20261025-002242` (`20261025-002516/7_phaseB_sib_*`) | P2 rerun: Qwen3-8B, `sib_history` + `sib_full` × seeds 200–214 | 29/30 completed; `sib_full` s212 aborted at T+17 |
| `p23_oth_20261025-002243` (`20261025-002615_phaseB_oth_*`) | P3 rerun: gpt-oss-20b, `oth_history` + `oth_full` | 30/30 completed |
| `p23_sib_20261025-000230`, `p23_oth_20261025-000724` | stopped first attempt (parse failures) | **excluded from results** (plan §12.1) |

Code: the reruns ran on `126cf3f` (= `prereg-p23b`, tag `p23`). Full tables and seed-level rows: `seat_swap/results/p23.md`, `p23.json`.

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| – | nothing in P2/P3 | – |

## Key results
**Replacement ladder** (same 15 seeds; P1's same-model row from `results/p1.json`):

| newcomer | history: joins | history: re_formed | full: joins | full: re_formed | Fisher full > history, one-sided p |
|---|---|---|---|---|---|
| same (Qwen3-14B, P1) | 13/15 | 0/15 | 15/15 | 6/15 | 0.008 |
| sibling (Qwen3-8B, P2) | 15/15 | 0/15 | 13/14 | 3/14 | 0.112 |
| other family (gpt-oss-20b, P3) | 3/15 | 2/15 | 10/15 | 6/15 | 0.107 |

**Per arm** (counts over games that reached each window):

| arm | joins | enforces | overpriced | re_formed | mean newcomer_ci | mean br_gap | mean retaliation | first_hold mean (n never) |
|---|---|---|---|---|---|---|---|---|
| sib_history | 15/15 | 0/15 | 0/15 | 0/15 | +0.99 | +0.58 | −0.003 | T+3.5 (0) |
| sib_full | 13/14 | 3/14 | 1/14 | 3/14 | +1.00 | +0.59 | −0.143 | T+1.7 (0) |
| oth_history | 3/15 | 3/15 | 0/15 | 2/15 | +0.41 | +0.09 | −0.162 | T+1.0 (14) |
| oth_full | 10/15 | 6/15 | 0/15 | 6/15 | +0.62 | +0.26 | −0.233 | T+3.3 (3) |

Seed-level `newcomer_ci`, `br_gap`, `retaliation`, `first_hold` for every game: `results/p23.md` ("Seed level").

**Newcomer output format** (PI reporting rule):

| arm | newcomer rounds | first-try failure rate | retries used | parse_markdown | aborted (round) | not finishing 60 rounds |
|---|---|---|---|---|---|---|
| sib_history | 900 | 0.000 | 0 | 0 | 0 | 0 |
| sib_full | 857 | 0.089 | 103 | 0 | 1 (T+17) | 1 (s212) |
| oth_history | 900 | 0.068 | 64 | 93 | 0 | 0 |
| oth_full | 900 | 0.061 | 57 | 101 | 0 | 0 |

- **The 8B breaks format mainly when it inherits the 14B's notes.** Every 8B failure is a `<fill in here>` template echo
  and every one is in `sib_full`: 0 of 900 `sib_history` rounds failed. That is an observation in its own right.
- gpt-oss: about 1 answer in 9 parses only after the markdown normalisation (`parse_markdown`).

**Are the "enforces" real punishments?** Newcomer / incumbent prices T+27..T+34 (descriptive, my reading):
- `sib_full`: s213 a real punishment (1.47 held from T+31); s203 a partial drop to 1.70 that sticks; s202 an artefact
  (2.89 at T+29 in the pre-shock window, no drop after).
- `oth_history`: s213 a real drop right after the shock (1.84 → 1.42); s204 and s211 drift inside a low-price war, not punishment.
- `oth_full`: s213 and s214 real (tit-for-tat at 1.47; 1.33/1.25 for two rounds, then back to 1.92); s212 partial (1.90 → 1.70);
  s200 and s202 were already in a punishment exchange with the incumbent before the shock; s204 drift.
- So clean, shock-triggered punishments: sibling 1 (+1 partial), other family 3 (+1 partial) in `full`, 1 in `history`.

**What gpt-oss does with the history:** at T+1 it tests a higher price (2.00–2.50 in 14/15 seeds), then falls to
1.47–1.88 and mostly settles around 1.65, just under the incumbent's 1.70 trigger. With the notes it holds 1.90–1.92 more often.

**Notes excerpts** (s200):
- `sib_full`, T+1: "Confirm competitor's Round 150 price (1.92) remains stable. Continue pricing at 1.92 … No punishment
  triggers detected". T+31: "Implement a 5% price increase to $2.01 for 3 rounds to test demand elasticity against the
  competitor's $1.47" (it raises its price after the cut, not punishes).
- `oth_full`, T+1: "Test price increase to $2.50 (mid-point between current price $1.92 and max $2.89)". T+31: "If competitor
  price < current price for ≥ 2 consecutive rounds, set price = competitor price + $0.02 for exactly 2 rounds".

## Surprises or worries
- gpt-oss's `first_hold` is "T+1" in `oth_history` for 1 seed and "never" for 14; the T+1 hold is s213, the one history seed that keeps 1.86–1.88.
- The 8B's first-try failure rate in `sib_full` was 0.089 in the rerun vs 0.18 in the stopped attempt's first ~10 rounds:
  the failures cluster early.

## Decisions needed
None.

## Spend
| app | cost | notes |
|---|---|---|
| `seat-swap-vllm-8b` (P2) | **$4.70** (final, Modal hourly report) | first attempt $1.05, rerun $3.65; weights $0.02 |
| `seat-swap-vllm-oth` (P3) | ≈ **$6.0** ($5.57 billed to 20:00 UTC + ≈ $0.4 to the stop at 20:07) | first attempt $0.73; weights $0.03 |
| seat 0 on `seat-swap-vllm` (14B, billed to Kickoff 07's app) | ≈ $3–4 estimated | 4.03 M generated tokens (P2 1.62 M, P3 2.41 M); exact split by tokens in Kickoff 07's final report |

Caps P2 $9, P3 $11 (including the first attempt): both inside, with the seat-0 share included.

## Modal state
`seat-swap-vllm-8b` and `seat-swap-vllm-oth`: redeployed at 2 min, then stopped (19:47 and 20:07 UTC). `seat-swap-vllm` not touched.

## Timing
| family | seat | model | calls | s/call | reasoning tok/call | wall (UTC) |
|---|---|---|---|---|---|---|
| sib | 1 | Qwen3-8B | 1,860 | 18.5 | 863 | 18:56–19:46 |
| sib | 0 | Qwen3-14B | 1,728 | 39.0 | 642 | |
| oth | 1 | gpt-oss-20b | 1,921 | 18.6 | 1,481 | 18:57–20:06 |
| oth | 0 | Qwen3-14B | 1,770 | 59.1 | 1,056 | |
