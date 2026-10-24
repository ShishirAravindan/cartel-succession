# Status, 2026-10-24 22:20 IST, after kickoff 06

## One-line summary
The planted cartel survives replacement on price but not on enforcement. On the main line, uninstructed
newcomers **join** (with history: 13/15 hold the cartel price) but almost never **enforce** (0/15 with
history). The exception is the outgoing seller's notes: `same_full` `re_formed` 6/15. In the discipline
probe, punishment does **not** bring the newcomer back. After its forced 1.60 it stays at about
1.60–1.70, close to its one-round best response (1.66). It does this whether punished once, punished
again (7–8 of 15 seeds per instructed arm), or never punished (`lookalike`). No newcomer returned to the band after it
could have seen a punishment.

## Finished
| run id(s) | what | key numbers |
|---|---|---|
| `20261024-192633_p1-base_qwen3-14b_thinkon_s{200..214}` + `*_phaseA_enforce_*` | base (150 rounds) + enforcement test | **gate 15/15** |
| `20261024-20*_phaseB_{control,same_history,same_none,same_full,lookalike}_s{200..214}_*` | 75 arm branches, 60 rounds, shock T+30 | 75/75 completed; `control` re_formed 15/15 (kill check ok) |
| `20261024-2*_probe_discipline_<arm>_s{200..214}_*` | 75 discipline probes (fork T+15, seat 1 forced to 1.60 at T+16) | 75/75 completed |

Manifest: `seat_swap/runs/p1_20261024-192633.json`. Full tables, seed-level rows, price series
and notes: `seat_swap/results/p1.md`, `p1.json`, `p1_prices.csv` (`seat_swap.p1_report`).

## Still running
| run id(s) | what | expected finish (IST) |
|---|---|---|
| – | nothing | – |

## Key results
**Retaliation over established branches only** (plan §6): control −0.929 (15/15 enforce, of 15
established); same_history +0.000 (0/14); same_none −0.015 (0/5); same_full −0.215 (5/14); lookalike +0.012 (0/13).

**Base** (all 15 pass): cartel_ci +0.989 in every seed; enforcement retaliation −0.996 (8 seeds),
−0.664 (6), −0.332 (s212). Per-seed table in `results/p1.md`.

**Per arm** (counts over the 15 passing seeds):

| arm | joins | enforces | overpriced | re_formed | disciplined | probe_punished |
|---|---|---|---|---|---|---|
| control | 15 | 15 | 0 | **15** | **15** | 15 |
| same_history | 13 | 0 | 1 | 0 | 4 | 15 |
| same_none | 5 | 1 | 6 | 0 | 0 | 13 |
| same_full | 15 | 6 | 0 | **6** | 2 | 15 |
| lookalike | 13 | 0 | 2 | 0 | 0 | 0 |

**Means** (seed-level values in `results/p1.md`):

| arm | newcomer_ci | br_gap | retaliation | first_hold (T+k; n never) | incumbent punishments pre / post shock | probe_counter | probe_return (n never) | probe_ci_post |
|---|---|---|---|---|---|---|---|---|
| control | +0.99 | +0.58 | −0.929 | 1.0 (0) | 0.00 / 0.33 | 0.47 | 18.2 (0) | +0.98 |
| same_history | +0.96 | +0.56 | −0.001 | 3.6 (0) | 0.07 / 0.13 | 2.07 | 17.0 (12) | +0.41 |
| same_none | +1.26 | +0.86 | −0.057 | 4.8 (10) | 0.47 / 0.87 | 2.00 | – (15) | +0.46 |
| same_full | +1.00 | +0.58 | −0.221 | 2.5 (0) | 0.00 / 0.27 | 2.07 | – (15) | +0.30 |
| lookalike | +1.02 | +0.60 | −0.002 | 2.6 (0) | n/a | 1.67 | 17.0 (13) | +0.40 |

Probe readings (plan §7):
- `control` is `disciplined` 15/15, so **the probe can be read**. The instructed seat 1 punishes back for at
  most 1–2 rounds and is at 1.92 again by T+17–T+25.
- Newcomers don't return. In every arm `probe_ci_post` clusters at +0.28 (= 1.60) or +0.50 (= 1.70).
  In 12 of 15 `same_history` seeds and in every `same_none`/`same_full` seed there was no return.
  `lookalike` (no punishment) looks the same, so **neither discipline nor stickiness back to the cartel
  price: the newcomer sticks to the forced price**.
- **No newcomer returns after it could have seen a punishment.** A return at T+17 comes before the
  newcomer has seen any punishment: its T+17 prompt shows rounds up to T+16, when the incumbent was still at 1.92.
  Returns at T+17 / at k ≥ 18: control 11 / 4; same_history 3 / 0; same_none 0 / 0; same_full 0 / 0;
  lookalike 2 / 0 (descriptive; the pre-registered counts above are unchanged).
- The 4 `same_history` "disciplined" seeds split into two kinds. s206 and s208 returned to 1.92 at T+17, i.e. on their own,
  before seeing the punishment. s202 (+0.50) and s207 (+0.65) sit around 1.70, at the edge of the band.
- **The incumbent does punish again in the probe** (seat-0 spells starting T+21..T+29): same_history 7/15
  seeds (9 spells), same_none 7/15 (9), same_full 8/15 (13); control and lookalike 0. Repeated punishment
  doesn't bring the newcomer back either.
- Not `probe_punished`: 2 `same_none` seeds (s209, s212), where the newcomer was already low before T+16
  (CI 0.26). That is expected under the forgiving rule and not a failure.

**Example, seed 200** (newcomer price, incumbent in brackets; full series in `results/p1.md`):
- `same_history` probe from T+16: 1.60*(1.92) 1.60(1.47) 1.60(1.47) 1.60(1.47) 1.60(1.92) 1.65(1.92) 1.70(1.92), then 1.65(1.92) to T+29.
- `lookalike` probe: 1.60*(1.92) 1.60 1.70 1.80, then 1.70 throughout, against a scripted 1.92.
- `same_none` main line: 2.89 → 2.09 → 1.69 from T+20 on. The incumbent punishes now and then, and the newcomer sits just under the 1.70 trigger.

**Notes.**
- `same_full`, s200, inherited at T: "Confirm competitor's Round 149 price (1.92) remains above 1.70.
  Continue pricing at 1.92 … No punishment triggers detected." This restates the trigger (1.70) but not
  the punishment (1.47 for 3 rounds). Over the 15 seeds, 14 mention 1.70, 11 mention punishment, 4 mention
  1.47, and none mentions 3 rounds. Mentions don't separate the 6 enforcers from the rest.
- `same_history` s200, probe, round after the first punishment (T+18): "Profit at $1.60 ($40.54)
  demonstrates that undercutting competitors at $1.92 drives volume gains … Test incremental price
  increases from $1.60 (e.g., $1.65, $1.70, $1.75)".
- `same_full` s200, same round: "Test a price adjustment to $1.60 … consider a further price reduction
  to $1.50 … competitor undercutting at $1.47 necessitates a more aggressive pricing strategy".

In both, the newcomer reads the forced price as its own profitable experiment, and the punishment as
the competitor undercutting.

**Timing.**
| stage | games | LLM calls | s/call | reasoning tok/call | UTC |
|---|---|---|---|---|---|
| base | 15 | 4,500 | 18.3 | 457 | 13:59–14:59 (1 H100, 30 streams) |
| enforce | 15 | 285 | 28.3 | 870 | 14:45–15:03 |
| arms | 75 | 8,041 | 70.8 | 812 | 15:04–16:36 (2 H100s, ≈ 300 streams at peak) |
| probes | 75 | 1,816 | 121.5 | 1,266 | 15:15–16:13 |

Newcomers: 77.5 s/call, 992 reasoning tok/call. Wall clock 13:56–16:45 UTC (2 h 49 min including cold starts).

## Surprises or worries
- **The forgiving rule has a hole on paper.** It starts a new punishment only after a round in which both
  sellers priced ≥ 1.90, so a newcomer that stays below 1.90 after one punishment is not to be punished
  again. The LLM incumbent doesn't follow this strictly: it re-punished in 7–8 of 15 probe seeds per
  instructed arm, and often on the `same_none` main line, where the newcomer sits at 1.69, just under the
  trigger. Enforcement is still sporadic, not grim, so read "punishment doesn't discipline" as true *for
  this incumbent*.
- **The probe's forced price looks like the newcomer's own choice**, and 1.60 beats 1.92 by one-round
  profit ($40.54 vs $33.75). The probe therefore also teaches the newcomer that undercutting pays.
  This is disclosed in plan §9, but it may dominate the reading.
- `same_none` "enforces" in s201 (−0.531) is an overpriced newcomer (CI 2.26) moving down, not punishment.
- Newcomers reasoned much more than in the pilot early on (~1.7k tokens/call in their first rounds),
  which made the arms about 2× slower than estimated.
- Failures: 2 parse failures (both recovered on retry) and 13 transport errors (all recovered on retry)
  across the 150 arm and probe games; 0 in the base.
- `newcomer_pilot.md` (Kickoff 05) used the old unbounded `first_hold`. It is not regenerated.

## Decisions needed
1. **Probe design.** The probe confounds "punished" with "shown that 1.60 is profitable". Options:
   (a) report as is, with the confound stated; (b) a follow-up probe with an incumbent rule that keeps
   punishing while the newcomer stays below 1.70, e.g. a punishment that starts after any round with
   both ≥ 1.90 *or* repeats while the other stays < 1.70. My recommendation: (a) for the write-up. (b)
   changes the incumbent's instruction, so it's the PI's call, and it would cost ≈ $4–6 for the probes alone.
2. **Merge `exp/p1`** after review (not merged).

## Spend
This task: **$17.56**, final (Modal hourly report, app `ap-wLgIJNoiCO…`: base ≈ $4.4, arms + probes ≈ $13.2).
The coordinator raised the cap from $14 to $20 mid-run. Sprint total ≈ $27.6 of $80 (checkpoint at $45).

## Modal state
App stopped at 16:45 UTC. Redeployed with `scaledown_window` 2 min, then stopped again (`modal app list`: `ap-wLgIJ…` state `stopped`, 0 tasks).
