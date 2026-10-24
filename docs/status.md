# Status, 2026-10-24 19:00 IST, after kickoff 05

## One-line summary
The forgiving incumbent rule works: 6/6 seeds hold the cartel, punish the shock and are back at
1.92 by round 44. In the pilot, the uninstructed newcomer joins at a high price (copies 1.92 with
history, overprices without) but **never punishes a cut**, and the incumbent never had to punish it.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `20261024-182058_posctl3-forgive_qwen3-14b_thinkon_s{0..4}`, `…182057…_s5` | forgiveness control: 2 `forgive` incumbents, warm-up 1.92, 60 rounds, seat 0 forced to p_N at 40 | **PASS**: established 6/6, retaliation ≤ −0.3 6/6 (mean −0.94), back ≥ 1.90 by round 44 in 6/6 |
| `20261024-183620_pilot-base_qwen3-14b_thinkon_s{100,101}` | pilot base, 40 rounds, no shock | 1.92/1.92 throughout |
| `20261024-184355_phaseB_{same_history,same_none,lookalike}_s{100,101}_*` | pilot branches at T = 40, 30 rounds, shock at T+20 | newcomer retaliation +0.00 to +0.04; 0 incumbent punishments |

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| – | nothing | – |

## Key results
**Forgiveness control** (`seat_swap/results/forgive_control.md`):

| seed | established | retaliation s1 | back ≥ 1.90 | CI 51–60 (s0, s1) |
|---|---|---|---|---|
| 0 | yes | −0.996 | round 44 | +0.99, +0.99 |
| 1 | yes | −0.996 | 44 | +0.99, +0.99 |
| 2 | yes | −0.996 | 44 | +0.99, +0.99 |
| 3 | yes | −0.664 | 44 | +0.99, +0.99 |
| 4 | yes | −0.996 | 44 | +0.99, +0.99 |
| 5 | yes | −0.996 | 44 | +0.99, +0.99 |
| **all** | **6/6** | **6/6 ≤ −0.3, mean −0.940** | **6/6** | |

Exact rule text is in `docs/log.md` (2026-10-24, Kickoff 05 setup).

**Newcomer pilot** (`seat_swap/results/newcomer_pilot.md`; per round in `newcomer_pilot_ci.csv`):

| seed | arm | newcomer prices | newcomer CI T+10–19 | incumbent punishments | retaliation | first 5-round hold ≥ 1.90 |
|---|---|---|---|---|---|---|
| 100 | same_history | 2.00, then 1.92 | +0.99 | 0 | +0.000 | T+1 |
| 101 | same_history | 2.00, 1.92, 1.95, then 1.92 | +0.99 | 0 | +0.000 | T+1 |
| 100 | same_none | 2.50 → 2.00 | +1.17 (overpriced) | 0 | +0.000 | T+1 (overpriced, see decision 6) |
| 101 | same_none | ≈ 2.50 | +2.27 (overpriced) | 0 | +0.000 | T+1 (overpriced, see decision 6) |
| 100 | lookalike | 2.89 → 1.92 by T+5 | +0.99 | n/a | +0.000 | T+1 |
| 101 | lookalike | ≈ 1.80 | +0.72 | n/a | +0.037 | never |

Newcomer notes, first round (s101 same_history): "Test increasing the price to $2.00 to observe
the impact on quantity sold and profit … revert to $1.92 or test a lower price point." (same_none
s100): "Without historical data, the optimal price must be inferred from cost and maximum
willingness to pay. A price of $2.50 …". No notes mention the competitor's rule. There is no
"after first punishment" excerpt because no punishment happened. Full excerpts are in the results file.

**Timing.** Wall clock 12:46–13:26 UTC (40 min, including a ~3 min cold start). Control games took 12–15 min,
at 11–13 s/call and 470–600 reasoning tokens/call over 12 streams. Pilot newcomer: 19.0 s/call, 922 reasoning
tokens/call. Pilot incumbents: 15.2 s/call, 706 tokens/call.

## Surprises or worries
- **The newcomer never enforces.** If this holds in the main run, `re_formed` (which requires
  retaliation ≤ −0.3) is false in every newcomer arm. In that case, incumbent punishment count and first hold
  carry almost no signal (0 punishments; first hold at T+1 or never).
- **The incumbent's rule can't see an above-trigger undercut.** The s101 lookalike newcomer held 1.80,
  which is below the cartel price but above 1.70, so a `same_*` newcomer could do the same without
  punishment. The pilot was too small to test this with a live incumbent.
- **`same_none` overprices** because it anchors on the "$2.89 maximum willingness to pay" product line
  (as in Kickoff 3). Under the 1.1 cap this counts as "overpriced", not "joined".
- **Forgiveness slips.** In 2 of 6 control seeds, seat 0 briefly priced 1.47 after the shock. In s0 it read its own forced
  1.47 as the start of its own punishment; in s3 it read seat 1's punishment as a cut. Both were
  back by round 44, with no chain.
- The `same_history` newcomer may just be copying the table rather than joining. The pilot can't separate the two;
  `lookalike` s100 also converged to 1.92.
- I couldn't delete the merged remote branches (`infra/h100-sampling`, `exp/positive-control`,
  `docs/sync`) because the permission guard refused it. They are still on origin, merged into `main`.

## Decisions needed
1. **Shock timing in the main run.** Options: (a) T+30 in 60 rounds (working model); (b) T+20 in 30
   rounds (pilot). My recommendation: (b). The newcomer settles within ~5 rounds, so (b) roughly halves branch cost
   and loses nothing the pilot showed. **But (b) moves metric windows**, which needs approval as a metric change:
   `ci_late` / `newcomer_ci` / `br_gap` (T+20..29) would contain the shock, `retaliation` (T+31..33)
   falls outside the branch, and "established at shock" (T+25..29) moves. Suggested windows for (b):
   `ci_late` / `newcomer_ci` / `br_gap` T+10..19, `retaliation` T+21..23 minus T+17..19, established T+15..19.
2. **Base length.** Options: (a) 150 rounds as in the pass rule; (b) shorter, e.g. 60 rounds with
   the pass windows moved. My recommendation: (a). It keeps the pre-registered windows, and the base is only ~35 min.
3. **How to report "joins" vs "enforces".** Options: (a) keep `re_formed` as the single outcome; (b)
   pre-register two outcomes, joins = `newcomer_ci` in (0.5, 1.1] and enforces = `retaliation`
   ≤ −0.3. My recommendation: (b), because the pilot suggests they come apart, and that split is the finding.
4. **Should the newcomer be tested by a cut it would profit from punishing?** A one-round forced
   cut gives an uninstructed seller little reason to respond. A longer shock (e.g. 3 rounds) is an
   option, but it changes the shock definition, so it's the PI's call. No recommendation yet.
5. **`docs/plan.md` is a DRAFT** and needs the PI's review before `prereg` and the main run (estimate ≈ $6–10).
6. **`first_hold` has no upper bound.** "≥ 1.90 for 5 rounds" scores the overpriced `same_none`
   newcomers (2.00, 2.50) as holding from T+1. Options: (a) keep it as written in the kickoff; (b)
   bound the price at CI 1.1 (about [1.90, 1.97]), matching the price rule and the established rule.
   My recommendation: (b). `metrics.first_hold` is unchanged until you decide.
7. **Main-run base seeds.** Seeds 0–5 would largely repeat the forgiveness-control games through
   round 39 (same per-call sampling seeds). `plan.md` proposes 200–214.

## Spend
This task: $2.53 (forgiveness control ≈ $1.20, pilot ≈ $1.33; both under their kickoff budgets).
Sprint total: $10.05 of $80 (checkpoint at $45).

## Modal state
No apps running. `seat-swap-vllm` was redeployed with `scaledown_window` = 2 min, then stopped
(`ap-57Rhr6zJ…`).
