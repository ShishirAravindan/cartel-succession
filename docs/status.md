# Status, 2026-10-25 12:45 IST, after kickoff 09 (in progress)

## One-line summary
Branches merged, corrections and provenance in. P1c (rewritten notes) is frozen as `prereg-p1c` and its 45 games are
running. Post-hoc analyses and figures next.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| – | merges into `main`, duration corrections, `docs/provenance.md` | – |

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| `20261025-1240*_phaseB_notes_*_s{215..229}_*` (manifest `runs/p1c_20261025-124057.json`) | P1c, 3 arms × 15 seeds, 60 rounds | ~14:00 |

## Key results
None yet.

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
