# P1C results (manifest `p1c_20261025-124057.json`)

## Base

| seed | base run | status | cartel_ci 121–150 | enforcement_retaliation | pass |
|---|---|---|---|---|---|
| 215 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s215` | completed | +0.989 | -0.664 | yes |
| 216 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s216` | completed | +0.989 | -0.664 | yes |
| 217 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s217` | completed | +0.989 | -0.996 | yes |
| 218 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s218` | completed | +0.989 | -0.996 | yes |
| 219 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s219` | completed | +0.989 | -0.996 | yes |
| 220 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s220` | completed | +0.989 | -0.664 | yes |
| 221 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s221` | completed | +0.989 | -0.996 | yes |
| 222 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s222` | completed | +0.989 | -0.664 | yes |
| 223 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s223` | completed | +0.989 | -0.664 | yes |
| 224 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s224` | completed | +0.989 | -0.996 | yes |
| 225 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s225` | completed | +0.989 | -0.332 | yes |
| 226 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s226` | completed | +0.989 | -0.664 | yes |
| 227 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s227` | completed | +0.989 | -0.996 | yes |
| 228 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s228` | completed | +0.989 | -0.664 | yes |
| 229 | `20261024-234550_p1b-base_qwen3-14b_thinkon_s229` | completed | +0.989 | -0.996 | yes |

Gate: **15/15** pass (need 8): PASS. Passing seeds: [215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229].

## Per arm (counts over passing seeds with a finished branch)

| arm | games | joins | enforces | overpriced | re_formed | disciplined | probe_punished | established at shock |
|---|---|---|---|---|---|---|---|---|
| notes_rule_return | 15 | 15/15 | 3/15 | 0/15 | 3/15 | 0/0 | 0/0 | 15/15 |
| notes_rule_noreturn | 15 | 15/15 | 4/15 | 0/15 | 4/15 | 0/0 | 0/0 | 14/15 |
| notes_status | 15 | 15/15 | 0/15 | 0/15 | 0/15 | 0/0 | 0/0 | 14/15 |

Means (main line; probe):

| arm | newcomer_ci | br_gap | retaliation | first_hold (T+k, never excluded; n never) | punishments pre / post | probe_counter | probe_return (n never) | probe_ci_post |
|---|---|---|---|---|---|---|---|---|
| notes_rule_return | +0.99 | +0.57 | -0.193 | 3.5 (0) | 0.00 / 0.20 | – | – (0) | – |
| notes_rule_noreturn | +0.97 | +0.56 | -0.247 | 3.3 (0) | 0.00 / 0.33 | – | – (0) | – |
| notes_status | +0.97 | +0.56 | -0.020 | 3.9 (0) | 0.07 / 0.13 | – | – (0) | – |

Established branches only (plan §6), and descriptive probe counts: a return at T+17 comes before the newcomer can see any punishment (its T+17 prompt shows rounds up to T+16); incumbent re-punishments = seat-0 spells below 1.70 starting in T+21..T+29 of the probe.

| arm | established | retaliation (established) | enforces (established) | return at T+17 | return at k ≥ 18 | seeds with probe re-punishment (spells) |
|---|---|---|---|---|---|---|
| notes_rule_return | 15/15 | -0.193 | 3/15 | 0 | 0 | 0/0 (0) |
| notes_rule_noreturn | 14/15 | -0.265 | 4/14 | 0 | 0 | 0/0 (0) |
| notes_status | 14/15 | -0.021 | 0/14 | 0 | 0 | 0/0 (0) |

## Seed level

| arm | seed | status (last round) | newcomer_ci | br_gap | retaliation | joins | enforces | overpr. | re_formed | first_hold | pun. pre / post | probe: status | newc. CI T+11–15 | punished | counter | return | ci_post | disciplined |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| notes_rule_return | 215 | completed (T+60) | +0.99 | +0.58 | -0.302 | yes | yes | no | yes | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 216 | completed (T+60) | +0.99 | +0.58 | -0.125 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 217 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 218 | completed (T+60) | +0.99 | +0.58 | -0.155 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 219 | completed (T+60) | +0.95 | +0.54 | -0.044 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 220 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+4 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 221 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 222 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 223 | completed (T+60) | +0.99 | +0.58 | -0.973 | yes | yes | no | yes | T+1 | 0 / 3 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 224 | completed (T+60) | +0.99 | +0.58 | -0.922 | yes | yes | no | yes | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 225 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 226 | completed (T+60) | +0.99 | +0.58 | -0.066 | yes | no | no | no | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 227 | completed (T+60) | +0.99 | +0.58 | -0.044 | yes | no | no | no | T+9 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 228 | completed (T+60) | +0.99 | +0.58 | -0.103 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_return | 229 | completed (T+60) | +0.99 | +0.58 | -0.155 | yes | no | no | no | T+7 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 215 | completed (T+60) | +0.99 | +0.58 | -0.996 | yes | yes | no | yes | T+1 | 0 / 2 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 216 | completed (T+60) | +0.99 | +0.58 | -0.066 | yes | no | no | no | T+9 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 217 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+4 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 218 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 219 | completed (T+60) | +0.63 | +0.22 | +0.000 | yes | no | no | no | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 220 | completed (T+60) | +0.99 | +0.58 | -0.996 | yes | yes | no | yes | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 221 | completed (T+60) | +0.99 | +0.58 | -0.996 | yes | yes | no | yes | T+1 | 0 / 2 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 222 | completed (T+60) | +1.07 | +0.66 | -0.656 | yes | yes | no | yes | T+1 | 0 / 1 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 223 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+4 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 224 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 225 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+4 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 226 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+4 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 227 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 228 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_rule_noreturn | 229 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+6 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 215 | completed (T+60) | +0.99 | +0.58 | -0.052 | yes | no | no | no | T+1 | 0 / 1 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 216 | completed (T+60) | +1.06 | +0.64 | +0.000 | yes | no | no | no | T+6 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 217 | completed (T+60) | +0.99 | +0.58 | -0.155 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 218 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+6 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 219 | completed (T+60) | +0.72 | +0.31 | +0.000 | yes | no | no | no | T+1 | 1 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 220 | completed (T+60) | +0.92 | +0.51 | +0.000 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 221 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+7 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 222 | completed (T+60) | +0.99 | +0.58 | -0.088 | yes | no | no | no | T+1 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 223 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 224 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+6 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 225 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 226 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+5 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 227 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 228 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+3 | 0 / 0 | not started (T+None) | – | – | – | never | – | – |
| notes_status | 229 | completed (T+60) | +0.99 | +0.58 | +0.000 | yes | no | no | no | T+5 | 0 / 1 | not started (T+None) | – | – | – | never | – | – |

## Prices per round, seed 215 (newcomer price, incumbent in brackets; * = forced)

- **notes_rule_return** main T+1..T+60: 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 2.00(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.97(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.47*) 1.75(1.92) 1.75(1.92) 1.85(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92) 1.75(1.92)
- **notes_rule_noreturn** main T+1..T+60: 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.47*) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.47(1.92) 1.65(1.92) 1.65(1.92) 1.65(1.92) 1.75(1.92) 1.65(1.92) 1.65(1.92) 1.80(1.92) 1.65(1.92) 1.65(1.92) 1.65(1.92) 1.65(1.92) 1.65(1.92) 1.65(1.92) 1.65(1.47) 1.65(1.47) 1.65(1.92) 1.65(1.47)
- **notes_status** main T+1..T+60: 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 2.00(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.96(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.47*) 1.92(1.47) 1.85(1.47) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.92(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.47) 1.85(1.47) 1.85(1.92) 1.85(1.92) 1.85(1.92) 1.85(1.92)

## Notes


## Timing

| stage | games | LLM calls | s/call | reasoning tok/call | first call – last call (UTC) |
|---|---|---|---|---|---|
| base | 15 | 4500 | 18.5 | 435 | 18:19:01 – 19:17:38 |
| enforce | 15 | 285 | 42.1 | 888 | 19:01:52 – 19:23:51 |
| arms | 45 | 5355 | 29.9 | 780 | 07:11:22 – 07:55:58 |

Newcomer (seat 1, non-control arms): 32.6 s/call, 865 reasoning tok/call.
