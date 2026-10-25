# Status, 2026-10-25 12:50 IST, after kickoff 09 (in progress)

## One-line summary
Branches merged, corrections and provenance in; post-hoc analyses and figures 1–5 pushed. P1c (rewritten notes) is
frozen as `prereg-p1c` and its 45 games are running. Post hoc: newcomers that enforce through the notes mostly don't
return to the cartel price (pooled `same_full` re-formed: 2/10 back at the cartel vs 16/20 for the rest).

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| – | merges into `main`, duration corrections, `docs/provenance.md` | – |
| – | post-hoc analyses, `seat_swap.posthoc` → `results/posthoc.{md,json}` | 195 games (P1, P1b, P2, P3) |
| – | paper figures, `seat_swap.figures` → `results/figures/fig{1..5}_*.{pdf,png}`, `captions.md` | – |

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| `20261025-1240*_phaseB_notes_*_s{215..229}_*` (manifest `runs/p1c_20261025-124057.json`) | P1c, 3 arms × 15 seeds, 60 rounds | ~14:00 |

## Key results
All of this section is **post hoc, not pre-registered** (full tables in `results/posthoc.md`).

**Effective sample size.** History, full and notes arms have no duplicate newcomer paths (P1 `same_full`: one pair,
s201 = s206). Control does: 30 games, 7 distinct paths. All 30 base games (P1 + P1b) have the same price path,
1.92/1.92 throughout, so the bases differ only in their notes. Key tests on unique paths only: pooled `same_full` vs
`same_history` `re_formed` 10/29 vs 1/30, p = 0.0023 (all games 0.0028); P1b `same_notes` vs `same_history` 8/15 vs
1/15, p = 0.0071 (unchanged); P1 `same_history` vs `same_none` `joins` 13/15 vs 5/15, p = 0.0039 (unchanged).

**Recovery after the shock** (newcomer CI T+34..T+60; `back_at_cartel` = CI ≥ 0.9 in each of T+51..T+60):

| sample / arm | re_formed | n | newcomer CI | market CI | back_at_cartel |
|---|---|---|---|---|---|
| P1+P1b control | yes | 30 | +0.98 | +0.97 | 30/30 |
| P1+P1b same_history | no | 29 | +0.94 | +0.96 | 21/29 |
| P1+P1b same_full | yes | 10 | +0.42 | +0.64 | 2/10 |
| P1+P1b same_full | no | 20 | +0.93 | +0.96 | 16/20 |
| P1b same_notes | yes | 8 | +0.61 | +0.78 | 2/8 |
| P1b same_notes | no | 7 | +0.88 | +0.93 | 5/7 |
| P2 sib_full | yes | 3 | +0.69 | +0.84 | 1/3 |
| P3 oth_full | all | 15 | +0.28 | +0.46 | 0/15 |

**Clean punishment** (holding the band at T+27..T+29, no punishment under way at T+25..T+29, ≤ 1.55 at T+31 or T+32):

| arm | enforces | clean_punish | clean_punish_return |
|---|---|---|---|
| control (P1+P1b) | 30/30 | 30/30 | 30/30 |
| same_history (P1+P1b) | 1/30 | 1/30 | 0/30 |
| same_full (P1+P1b) | 10/30 | 8/30 | 4/30 |
| same_notes (P1b) | 8/15 | 6/15 | 3/15 |
| sib_full (P2) | 3/14 | 1/14 | 0/14 |
| oth_history / oth_full (P3) | 3/15 / 6/15 | 0/15 / 2/15 | 0/15 / 2/15 |

**P1b paired by seed** (McNemar exact, two-sided): `same_notes` vs `same_history` on `re_formed` 7 vs 0 discordant,
p = 0.016; on `clean_punish` 5 vs 0, p = 0.063. `same_full` vs `same_history`: 3 vs 0 on both, p = 0.25.

**P3 shock visibility.** 7 of 30 P3 games had the incumbent below 1.70 at T+29 (0 of 29 in P2). Without them P3
`oth_full` `re_formed` is 4/12 (was 6/15) and `oth_history` 1/11 (was 2/15).

**Figures** (`seat_swap/results/figures/`, captions in `captions.md`): 1 design, 2 price paths by arm, 3 outcomes by
arm with exact CIs, 4 replacement across models, 5 mean CI after the shock ("punish but not forgive"). Newcomer dark
blue (solid), incumbent orange (dashed) throughout; bars use a blue ramp with hatching, so they read in greyscale.

**Correction (2026-10-25, see `72d5986`):** P1's status (`cce5bd4`) said the inherited `same_full` notes "none mentions
3 rounds". That came from a regex that missed "3-round": 5 of P1's 15 inherited notes state a duration (3 of the 6
enforcers). The P1b status's "no duration ever" in `log.md` is corrected there too.

## Surprises or worries
None yet.

## Decisions needed
1. Operational choices in the new outcomes (frozen in plan §13 before the P1c run; the kickoff left them open).
   "No punishment under way in T+25..T+29" = both seats ≥ 1.70 in each round. "Back within 6 rounds" counts from the
   first round at ≤ 1.55, and one round at CI ≥ 0.9 suffices. `back_at_cartel` has no upper bound. Options: keep / change
   (change would be post hoc for P1c). My recommendation: keep.

## Spend
This task so far: Modal 14B app since 07:00 UTC (estimate later). Sprint total before today ≈ $55.8.

## Modal state
`seat-swap-vllm` deployed at 10-min scaledown (07:07 UTC), running P1c.
