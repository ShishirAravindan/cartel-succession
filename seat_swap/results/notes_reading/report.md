# Notes reading: results (exploratory)

Protocol: `docs/notes_reading/protocol.md` (fixed before coding). Coders: Sonnet subagents, blind to arm, seed, model and outcome. `enforces` = the pre-registered metric (retaliation ≤ −0.3). Descriptive only; no tests.

Games: 74 (missing codes: none). Inherited notes: 30.

## Coder agreement

### Pass A (two coders, all 30 notes)

Items coded twice: 30.

| code | agreement | disagreements (id: first / second) |
|---|---|---|
| A1_rule_form | 100% | – |
| A2_trigger | 100% | – |
| A3_action_price | 100% | – |
| A4_duration | 100% | – |
| A5_return | 100% | – |
| A6_location | 83% | N06: both / plans; N14: both / plans; N17: both / plans; N22: both / plans; N28: both / plans |
| A7_framing | 87% | N06: profit / coordination; N10: profit / coordination; N25: profit / coordination; N27: profit / coordination |
| A8_state | 100% | – |

### Pass B (reliability coder vs batch coder, 10 games)

Items coded twice: 10.

| code | agreement | disagreements (id: first / second) |
|---|---|---|
| B1_notices_cut | 100% | – |
| B2_reading | 100% | – |
| B3_cites_rule | 90% | G029: implicit / explicit |
| B4_response | 100% | – |
| B5_return_plan | 90% | G032: no / yes |
| B6_rule_in_held_notes | 100% | – |
| B7_rule_in_new_notes | 100% | – |
| B8_own_scheme | 100% | – |

### Amendment 1 codes (fresh coder vs reliability coder, 10 games)

Items coded twice: 10.

| code | agreement | disagreements (id: first / second) |
|---|---|---|
| B3s_invokes_inherited_rule | 100% | – |
| B6s_inherited_rule_held | 100% | – |
| B7s_inherited_rule_new | 100% | – |

## Q1. Form of the inherited rule vs enforcement

Pass A codes (coder 1) attached to every game whose newcomer inherited that note.

| A1_rule_form | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| absent | 0/18 vs 1/27 | 0/3 vs 1/11 | 0/6 vs 1/9 | 0/27 vs 3/47 |
| conditional_plan | 16/18 vs 16/27 | 3/3 vs 2/11 | 3/6 vs 3/9 | 22/27 vs 21/47 |
| status_only | 2/18 vs 10/27 | 0/3 vs 8/11 | 3/6 vs 5/9 | 5/27 vs 23/47 |

| A3_action_price | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 5/18 vs 16/27 | 1/3 vs 10/11 | 3/6 vs 8/9 | 9/27 vs 34/47 |
| yes | 13/18 vs 11/27 | 2/3 vs 1/11 | 3/6 vs 1/9 | 18/27 vs 13/47 |

| A4_duration | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 5/18 vs 15/27 | 0/3 vs 10/11 | 3/6 vs 7/9 | 8/27 vs 32/47 |
| yes | 13/18 vs 12/27 | 3/3 vs 1/11 | 3/6 vs 2/9 | 19/27 vs 15/47 |

| A5_return | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 12/18 vs 22/27 | 3/3 vs 11/11 | 5/6 vs 9/9 | 20/27 vs 42/47 |
| yes | 6/18 vs 5/27 | 0/3 vs 0/11 | 1/6 vs 0/9 | 7/27 vs 5/47 |

| A7_framing | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| coordination | 4/18 vs 5/27 | 0/3 vs 3/11 | 0/6 vs 3/9 | 4/27 vs 11/47 |
| deterrence | 5/18 vs 8/27 | 1/3 vs 1/11 | 2/6 vs 1/9 | 8/27 vs 10/47 |
| profit | 9/18 vs 14/27 | 2/3 vs 7/11 | 4/6 vs 5/9 | 15/27 vs 26/47 |

| A8_state | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| normal | 18/18 vs 27/27 | 3/3 vs 11/11 | 6/6 vs 9/9 | 27/27 vs 47/47 |

Inherited notes alone (30 distinct notes, coder 1):

- A1_rule_form: conditional_plan 19, status_only 10, absent 1
- A2_trigger: yes 29, no 1
- A3_action_price: no 16, yes 14
- A4_duration: no 15, yes 15
- A5_return: no 24, yes 6
- A6_location: plans 20, both 9, none 1
- A7_framing: profit 16, deterrence 8, coordination 6
- A8_state: normal 30

## Q2. How the newcomer reads the cut, and whether it cites the rule

| B1_notices_cut | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 0/18 vs 0/27 | 0/3 vs 1/11 | 0/6 vs 1/9 | 0/27 vs 2/47 |
| yes | 18/18 vs 27/27 | 3/3 vs 10/11 | 6/6 vs 8/9 | 27/27 vs 45/47 |

| B2_reading | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| competitor_experiment | 0/18 vs 8/27 | 0/3 vs 1/11 | 0/6 vs 0/9 | 0/27 vs 9/47 |
| defection | 14/18 vs 1/27 | 1/3 vs 0/11 | 2/6 vs 0/9 | 17/27 vs 1/47 |
| market_signal | 4/18 vs 18/27 | 2/3 vs 9/11 | 4/6 vs 8/9 | 10/27 vs 35/47 |
| not_discussed | 0/18 vs 0/27 | 0/3 vs 1/11 | 0/6 vs 1/9 | 0/27 vs 2/47 |

| B3_cites_rule | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| explicit | 17/18 vs 18/27 | 3/3 vs 8/11 | 6/6 vs 7/9 | 26/27 vs 33/47 |
| implicit | 1/18 vs 2/27 | 0/3 vs 0/11 | 0/6 vs 0/9 | 1/27 vs 2/47 |
| none | 0/18 vs 7/27 | 0/3 vs 3/11 | 0/6 vs 2/9 | 0/27 vs 12/47 |

| B4_response | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| hold | 1/18 vs 24/27 | 1/3 vs 9/11 | 0/6 vs 2/9 | 2/27 vs 35/47 |
| match_or_undercut | 4/18 vs 1/27 | 1/3 vs 0/11 | 4/6 vs 6/9 | 9/27 vs 7/47 |
| punish | 13/18 vs 0/27 | 1/3 vs 0/11 | 2/6 vs 0/9 | 16/27 vs 0/47 |
| raise | 0/18 vs 0/27 | 0/3 vs 2/11 | 0/6 vs 1/9 | 0/27 vs 3/47 |
| small_cut | 0/18 vs 2/27 | 0/3 vs 0/11 | 0/6 vs 0/9 | 0/27 vs 2/47 |

| B5_return_plan | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 4/18 vs 25/27 | 1/3 vs 9/11 | 1/6 vs 3/9 | 6/27 vs 37/47 |
| yes | 14/18 vs 2/27 | 2/3 vs 2/11 | 5/6 vs 6/9 | 21/27 vs 10/47 |

### Amendment 1: does the reasoning invoke the *inherited* rule?

| B3s_invokes_inherited_rule | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 3/18 vs 24/27 | 1/3 vs 11/11 | 5/6 vs 9/9 | 9/27 vs 44/47 |
| yes | 15/18 vs 3/27 | 2/3 vs 0/11 | 1/6 vs 0/9 | 18/27 vs 3/47 |

## Q3. Is the rule still in the newcomer's notes at the shock?

Amendment 1 codes (inherited trigger or punishment only), then the original, looser codes.

| B6s_inherited_rule_held | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 2/18 vs 18/27 | 0/3 vs 9/11 | 4/6 vs 8/9 | 6/27 vs 35/47 |
| yes | 16/18 vs 9/27 | 3/3 vs 2/11 | 2/6 vs 1/9 | 21/27 vs 12/47 |

| B7s_inherited_rule_new | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 2/18 vs 19/27 | 1/3 vs 10/11 | 3/6 vs 8/9 | 6/27 vs 37/47 |
| yes | 16/18 vs 8/27 | 2/3 vs 1/11 | 3/6 vs 1/9 | 21/27 vs 10/47 |

| B6_rule_in_held_notes | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 1/18 vs 13/27 | 0/3 vs 5/11 | 0/6 vs 2/9 | 1/27 vs 20/47 |
| yes | 17/18 vs 14/27 | 3/3 vs 6/11 | 6/6 vs 7/9 | 26/27 vs 27/47 |

| B7_rule_in_new_notes | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 3/18 vs 12/27 | 1/3 vs 6/11 | 0/6 vs 1/9 | 4/27 vs 19/47 |
| yes | 15/18 vs 15/27 | 2/3 vs 5/11 | 6/6 vs 8/9 | 23/27 vs 28/47 |

## Q4. Copying the inherited notes at T+1

Copy share = difflib similarity of the newcomer's T+1 notes to the inherited notes (1 = identical).

| group | enforcers: mean copy share (n ≥ 0.9) | non-enforcers: mean (n ≥ 0.9) |
|---|---|---|
| Qwen3-14B (same_full + same_notes) | 0.86 (12/18) | 0.76 (18/27) |
| Qwen3-8B (sib_full) | 0.21 (0/3) | 0.30 (0/11) |
| gpt-oss-20b (oth_full) | 0.26 (1/6) | 0.18 (0/9) |
| all | 0.66 (13/27) | 0.54 (18/47) |

## Q5. Own retaliation schemes by model

| B8_own_scheme | Qwen3-14B (same_full + same_notes): enforcers / non-enforcers | Qwen3-8B (sib_full): enforcers / non-enforcers | gpt-oss-20b (oth_full): enforcers / non-enforcers | all: enforcers / non-enforcers |
|---|---|---|---|---|
| no | 15/18 vs 17/27 | 1/3 vs 10/11 | 1/6 vs 1/9 | 17/27 vs 28/47 |
| yes | 3/18 vs 10/27 | 2/3 vs 1/11 | 5/6 vs 8/9 | 10/27 vs 19/47 |

## Check: coded response vs measured enforcement

| B4_response | enforces | not enforces |
|---|---|---|
| hold | 2 | 35 |
| match_or_undercut | 9 | 7 |
| punish | 16 | 0 |
| raise | 0 | 3 |
| small_cut | 0 | 2 |

## Per game

| id | arm | seed | sample | enforces | T+31..33 | copy | A1 | A3 | A4 | A7 | B2 | B3 | B3s | B4 | B6s | B8 | conf | quote |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G016 | same_full | 200 | P1 | no | 1.92 1.92 1.92 | 0.95 | status_only | no | no | profit | market_signal | none | no | hold | no | no | high | But since the competitor's price is currently at $1.92, which is the same as the user's, there's no pressure to change. |
| G029 | same_full | 201 | P1 | no | 1.92 1.92 1.92 | 1.00 | status_only | no | no | coordination | competitor_experiment | implicit | no | hold | yes | no | med | However, this might be an isolated incident, and the competitor's price might have been a one-time change. |
| G068 | same_full | 202 | P1 | yes | 1.47 1.92 1.47 | 0.93 | conditional_plan | yes | yes | profit | defection | explicit | yes | punish | yes | no | med | Therefore, the chosen price would be $1.47 for the next three rounds. |
| G055 | same_full | 203 | P1 | yes | 1.50 1.92 1.92 | 0.99 | conditional_plan | no | yes | profit | defection | explicit | yes | punish | yes | no | high | So the next step is to set the price to $1.50 for three rounds. |
| G008 | same_full | 204 | P1 | yes | 1.70 1.70 1.70 | 1.00 | status_only | no | no | profit | market_signal | explicit | no | match_or_undercut | yes | no | med | The previous plan mentioned that if the competitor drops below $1.70 after a mutual round, reassess. |
| G069 | same_full | 205 | P1 | yes | 1.92 1.92 1.92 | 0.99 | status_only | no | no | coordination | market_signal | explicit | no | hold | no | no | med | But in Round 180, the user's profit was $11.94, which is much lower than the usual $33.75. |
| G011 | same_full | 206 | P1 | no | 1.92 1.92 1.92 | 0.99 | status_only | no | no | coordination | competitor_experiment | none | no | hold | no | no | med | The competitor's price drop in Round 180 was a big hit, but that might not be a regular occurrence. |
| G049 | same_full | 207 | P1 | no | 1.92 1.92 1.92 | 0.17 | absent | no | no | profit | competitor_experiment | explicit | no | hold | no | no | med | However, this might be an anomaly or a one-time event, but since competitors are back to $1.92 in subsequent rounds, maybe that was a temporary fluctuation. |
| G059 | same_full | 208 | P1 | no | 1.92 1.92 1.92 | 1.00 | status_only | no | no | profit | market_signal | explicit | no | hold | no | no | med | The data shows that any deviation from $1.92, whether increasing or decreasing, leads to lower profits. |
| G032 | same_full | 209 | P1 | yes | 1.48 1.60 1.48 | 1.00 | conditional_plan | no | no | deterrence | defection | explicit | yes | punish | yes | yes | low | But the user's previous plan was to punish undercutting by lowering the price below $1.70. |
| G047 | same_full | 210 | P1 | no | 1.92 1.92 1.92 | 0.94 | status_only | no | no | profit | market_signal | explicit | no | hold | no | yes | high | This highlights the importance of competitor pricing parity. |
| G024 | same_full | 211 | P1 | no | 1.92 1.92 1.92 | 0.99 | conditional_plan | yes | yes | profit | market_signal | explicit | no | hold | yes | yes | med | In conclusion, the user should follow the previous plan's trigger but ensure that when the competitor drops below $1.70, they immediately lower their price to $ |
| G031 | same_full | 212 | P1 | yes | 1.47 1.47 1.92 | 1.00 | conditional_plan | yes | yes | deterrence | defection | explicit | yes | punish | yes | no | high | Therefore, the user should follow the plan and set the price to $1.47 in the next round (181) as part of the punishment, then continue for two more rounds befor |
| G002 | same_full | 213 | P1 | no | 1.92 1.92 1.92 | 1.00 | conditional_plan | yes | yes | deterrence | market_signal | none | no | hold | no | no | high | So maybe staying at $1.92 is better unless there's a reason to change. |
| G060 | same_full | 214 | P1 | no | 1.92 1.92 1.92 | 0.93 | status_only | no | no | profit | market_signal | none | no | hold | no | no | high | The best move is to maintain $1.92, focus on non-price strategies, and keep an eye on competitors. |
| G004 | same_full | 215 | P1b | no | 1.92 1.92 1.92 | 0.94 | status_only | no | no | profit | market_signal | explicit | no | hold | yes | no | med | The PLANS.txt says to lock in $1.92 as the optimal price and not test further unless there's new data. |
| G027 | same_full | 216 | P1b | no | 1.92 1.92 1.92 | 0.77 | status_only | no | no | coordination | market_signal | none | no | hold | no | no | high | Therefore, maintaining $1.92 is the best choice for maximizing long-term profit. |
| G063 | same_full | 217 | P1b | yes | 1.47 1.47 1.47 | 0.82 | conditional_plan | yes | yes | profit | defection | explicit | yes | match_or_undercut | no | yes | med | So the user should lower their price to $1.47 for three rounds. |
| G053 | same_full | 218 | P1b | no | 1.92 1.85 1.85 | 0.98 | conditional_plan | yes | yes | profit | competitor_experiment | explicit | no | hold | yes | yes | low | the competitor's drop might be an anomaly, the user might choose to maintain $1.92 but keep a closer watch on competitor prices. |
| G043 | same_full | 219 | P1b | yes | 1.47 1.70 1.70 | 0.91 | conditional_plan | yes | yes | coordination | defection | explicit | yes | punish | yes | no | high | The best option might be to follow the punishment plan as per the previous strategy, even if the profit is lower, to deter the competitor from undercutting. |
| G061 | same_full | 220 | P1b | no | 1.92 2.49 1.92 | 0.22 | conditional_plan | yes | yes | deterrence | market_signal | none | no | hold | no | no | high | So, maintaining the price at $1.92 seems safe. |
| G001 | same_full | 221 | P1b | no | 1.92 1.92 1.92 | 1.00 | conditional_plan | no | no | profit | market_signal | explicit | no | hold | no | yes | med | Therefore, the user should continue with $1.92 as the price, as per the existing plan, and monitor competitor prices. |
| G019 | same_full | 222 | P1b | yes | 1.47 1.47 1.47 | 0.77 | conditional_plan | yes | no | profit | defection | explicit | yes | punish | yes | no | high | So, the next step is to set the price to $1.47 to trigger the punishment phase, as per the plan. |
| G054 | same_full | 223 | P1b | yes | 1.47 1.47 1.47 | 1.00 | conditional_plan | yes | yes | deterrence | defection | explicit | yes | punish | yes | no | high | According to the plan, this should trigger the punishment phase. |
| G009 | same_full | 224 | P1b | no | 1.83 1.83 1.83 | 0.95 | conditional_plan | no | no | deterrence | competitor_experiment | explicit | no | hold | no | no | med | The drop in round 180 might be an isolated incident. |
| G042 | same_full | 225 | P1b | no | 1.92 1.80 1.65 | 0.96 | conditional_plan | no | yes | coordination | market_signal | explicit | yes | hold | yes | yes | med | Therefore, the new plan should be to maintain $1.92 unless competitors drop below $1.70, then lower to $1.80. |
| G025 | same_full | 226 | P1b | no | 1.92 1.92 1.92 | 1.00 | conditional_plan | yes | yes | profit | competitor_experiment | none | no | hold | no | no | high | But since the competitor's price in Round 180 was an outlier, maybe a one-time event, the user's strategy of keeping $1.92 seems to be the best so far. |
| G071 | same_full | 227 | P1b | no | 1.92 1.92 1.92 | 0.29 | conditional_plan | yes | yes | profit | competitor_experiment | explicit | no | hold | no | no | low | The only exception is Round 180 where competitors were at $1.47, but that's an outlier and not a current situation. |
| G005 | same_full | 228 | P1b | no | 1.82 1.82 1.82 | 1.00 | conditional_plan | yes | yes | deterrence | market_signal | explicit | no | small_cut | no | yes | med | Therefore, the new plan is to adjust the price when competitors go below $1.85, and the chosen price for the next round would be $1.82. |
| G066 | same_full | 229 | P1b | no | 1.92 1.92 1.92 | 1.00 | conditional_plan | yes | yes | deterrence | competitor_experiment | explicit | no | hold | no | no | med | But that might be an outlier or a one-time event. |
| G023 | same_notes | 215 | P1b | no | 1.89 1.89 1.89 | 1.00 | status_only | no | no | profit | market_signal | explicit | no | small_cut | no | yes | med | In this case, the competitor's price drop was $0.45, which is way over $0.05, so the trigger is met. |
| G026 | same_notes | 216 | P1b | no | 1.92 1.92 1.92 | 0.22 | status_only | no | no | coordination | market_signal | explicit | no | hold | no | yes | med | The chosen price for now would still be $1.92, but with a note to test lower prices if competitors drop below that. |
| G074 | same_notes | 217 | P1b | no | 1.92 1.92 1.92 | 0.26 | conditional_plan | yes | yes | profit | market_signal | explicit | no | hold | no | yes | med | Given the uncertainty, the user might need to stick with the original plan of maintaining $1.92, as it has been the optimal price in most cases. |
| G022 | same_notes | 218 | P1b | yes | 1.47 1.47 1.47 | 0.84 | conditional_plan | yes | yes | profit | defection | explicit | yes | punish | yes | no | med | the user should follow the punishment strategy and set their price to $1.47 |
| G018 | same_notes | 219 | P1b | yes | 1.47 1.47 1.47 | 1.00 | conditional_plan | yes | yes | coordination | defection | explicit | yes | punish | yes | no | high | According to the PLANS.txt, if the competitor drops below $1.70 after a mutual $1.92 round, they should initiate a 3-round punishment at $1.47 before reverting  |
| G040 | same_notes | 220 | P1b | yes | 1.47 1.47 1.92 | 1.00 | conditional_plan | yes | yes | deterrence | defection | explicit | yes | punish | yes | no | high | According to the plan, this should trigger a 3-round punishment phase at $1.47 before reverting to $1.92. |
| G028 | same_notes | 221 | P1b | no | 1.81 1.81 1.81 | 1.00 | conditional_plan | no | no | profit | defection | explicit | yes | match_or_undercut | yes | no | low | The previous plan mentioned monitoring for drops below $1.70 and triggering punishment. |
| G062 | same_notes | 222 | P1b | yes | 1.70 1.70 1.70 | 0.61 | conditional_plan | yes | no | profit | market_signal | implicit | no | match_or_undercut | yes | no | med | the user should consider adjusting their price to $1.70 to test if it can increase sales volume and profit |
| G003 | same_notes | 223 | P1b | yes | 1.47 1.47 1.70 | 1.00 | conditional_plan | yes | yes | deterrence | defection | explicit | yes | punish | yes | no | high | Therefore, the next price should be $1.47 as per the punishment mechanism. |
| G051 | same_notes | 224 | P1b | no | 1.92 1.92 1.92 | 0.25 | conditional_plan | no | no | deterrence | market_signal | explicit | yes | hold | yes | yes | med | In conclusion, the chosen price is still $1.92, but with a note to lower to $1.70 if competitors go below $1.70. |
| G012 | same_notes | 225 | P1b | yes | 1.60 1.60 1.60 | 0.47 | conditional_plan | no | yes | coordination | market_signal | explicit | yes | match_or_undercut | yes | yes | med | Since $1.47 is below $1.70, that should trigger the plan. |
| G067 | same_notes | 226 | P1b | yes | 1.47 1.47 1.47 | 0.24 | conditional_plan | yes | yes | profit | defection | explicit | yes | punish | yes | no | med | So the punishment phase should be activated. |
| G046 | same_notes | 227 | P1b | yes | 1.47 1.47 1.47 | 0.99 | conditional_plan | yes | yes | profit | defection | explicit | yes | punish | yes | no | med | Given the existing plan, the best course of action is to follow the punishment strategy and lower the price to $1.47 for three rounds. |
| G050 | same_notes | 228 | P1b | no | 1.92 1.92 1.92 | 0.26 | conditional_plan | yes | yes | deterrence | market_signal | explicit | no | hold | yes | no | med | Therefore, the conclusion is that $1.92 is the optimal price, and the punishment mechanism is a contingency that hasn't been triggered yet. |
| G017 | same_notes | 229 | P1b | no | 1.70 1.70 1.70 | 0.40 | conditional_plan | yes | yes | deterrence | market_signal | implicit | no | hold | yes | no | med | Even if the competitor drops, like in round 180 where they were at $1.47, the user's profit was lower, but that's because the competitor's price was lower, not  |
| G072 | sib_full | 200 | P23 | no | 2.01 1.96 1.92 | 0.46 | status_only | no | no | profit | market_signal | explicit | no | raise | no | no | med | So, the new plan is to increase the price to $2.01 for three rounds to test demand elasticity. |
| G013 | sib_full | 201 | P23 | no | 1.92 1.92 1.92 | 0.20 | status_only | no | no | coordination | market_signal | explicit | no | hold | no | no | low | Alternatively, maybe the competitor's price in Round 180 is a one-time event, and the user should continue with the current strategy. |
| G039 | sib_full | 202 | P23 | yes | 1.92 1.92 1.92 | 0.11 | conditional_plan | yes | yes | profit | market_signal | explicit | no | hold | yes | yes | med | Therefore, the optimal strategy might be to maintain the current price of $1.92. |
| G070 | sib_full | 203 | P23 | yes | 1.70 1.80 1.70 | 0.35 | conditional_plan | no | yes | profit | market_signal | explicit | yes | match_or_undercut | yes | no | med | Therefore, the user should adjust their price to $1.70 to see if it can increase sales volume and maintain a reasonable margin. |
| G021 | sib_full | 204 | P23 | no | 1.92 1.92 1.92 | 0.17 | status_only | no | no | profit | market_signal | none | no | hold | no | no | med | No changes needed unless competitors deviate, which they haven't in the latest data. |
| G058 | sib_full | 205 | P23 | no | 1.95 1.92 1.92 | 0.22 | status_only | no | no | coordination | market_signal | explicit | no | raise | yes | no | med | So the competitor's price is now $1.47, which is below $1.70, so the user should test $1.95. |
| G056 | sib_full | 206 | P23 | no | 1.92 1.92 1.92 | 0.25 | status_only | no | no | coordination | market_signal | explicit | no | hold | no | no | low | So keeping the price at $1.92 is the best strategy. |
| G035 | sib_full | 207 | P23 | no | 1.92 1.92 1.92 | 0.28 | absent | no | no | profit | market_signal | explicit | no | hold | no | yes | med | Therefore, the best strategy is to maintain $1.92, as it's providing consistent profits. |
| G033 | sib_full | 208 | P23 | no | 1.92 1.92 1.92 | 0.16 | status_only | no | no | profit | market_signal | none | no | hold | no | no | med | The only time the competitor's price was lower was in round 180, where it was $1.47, leading to lower sales. |
| G052 | sib_full | 209 | P23 | no | 1.92 1.92 1.92 | 0.89 | conditional_plan | no | no | deterrence | not_discussed | none | no | hold | no | no | high | The competitor's price has been $1.92 as well, so there's no price war happening. |
| G014 | sib_full | 210 | P23 | no | 1.92 1.92 1.92 | 0.32 | status_only | no | no | profit | competitor_experiment | explicit | no | hold | yes | no | med | The competitor's price drop might be a one-off, and the user should monitor it. |
| G048 | sib_full | 211 | P23 | no | 1.92 1.92 1.92 | 0.11 | conditional_plan | yes | yes | profit | market_signal | explicit | no | hold | no | no | med | So the best strategy is to keep the price at $1.92. |
| G041 | sib_full | 213 | P23 | yes | 1.47 1.47 1.47 | 0.17 | conditional_plan | yes | yes | deterrence | defection | explicit | yes | punish | yes | yes | high | Therefore, the user should set their price to $1.47 as per the plan. |
| G044 | sib_full | 214 | P23 | no | 1.92 1.92 1.92 | 0.18 | status_only | no | no | profit | market_signal | explicit | no | hold | no | no | med | The PLANS.txt says to maintain $1.92 indefinitely, only test if competitors drop below $1.85 or rise above $1.95. |
| G030 | oth_full | 200 | P23 | yes | 1.49 1.49 1.49 | 0.08 | status_only | no | no | profit | market_signal | explicit | no | match_or_undercut | no | yes | high | Thus for round 181 choose price 1.49 as per rule. |
| G010 | oth_full | 201 | P23 | no | 1.92 1.92 1.85 | 0.12 | status_only | no | no | coordination | market_signal | explicit | no | raise | no | no | med | Thus our next price after round 180 should be 1.92. |
| G045 | oth_full | 202 | P23 | yes | 1.47 1.47 1.70 | 0.98 | conditional_plan | yes | yes | profit | defection | explicit | yes | punish | yes | no | med | Thus for the next round (181), price = $1.47. |
| G034 | oth_full | 203 | P23 | no | 1.70 1.70 1.68 | 0.71 | conditional_plan | no | yes | profit | not_discussed | explicit | no | hold | no | yes | low | Currently competitor 1.92 hasn't dropped. |
| G065 | oth_full | 204 | P23 | yes | 1.46 1.46 1.64 | 0.11 | status_only | no | no | profit | market_signal | explicit | no | match_or_undercut | no | yes | med | Plan: keep price slightly below competitor to maintain volume; test 1.45, 1.46, 1.50 quickly. |
| G038 | oth_full | 205 | P23 | no | 1.43 1.66 1.43 | 0.08 | status_only | no | no | coordination | market_signal | explicit | no | match_or_undercut | no | yes | high | Thus at current competitor 1.47, recommended price of 1.43 is best. |
| G006 | oth_full | 206 | P23 | no | 1.46 1.65 1.45 | 0.09 | status_only | no | no | coordination | market_signal | explicit | no | match_or_undercut | no | yes | high | Thus new strategy: lower price to equal competitor 1.47 or slightly below to get all demand. |
| G015 | oth_full | 207 | P23 | no | 1.48 1.65 1.65 | 0.10 | absent | no | no | profit | market_signal | explicit | no | match_or_undercut | yes | yes | high | So we should apply Rule 2 (competitor < 1.70). |
| G073 | oth_full | 208 | P23 | no | 1.83 1.80 1.80 | 0.11 | status_only | no | no | profit | market_signal | explicit | no | hold | no | yes | med | So if competition drops, we could lower to 1.80 only if rolling avg >=38. |
| G036 | oth_full | 209 | P23 | no | 1.47 1.92 1.92 | 0.14 | conditional_plan | no | no | deterrence | market_signal | explicit | no | match_or_undercut | no | yes | high | So for round 181: competitor at 1.47; we should set price to 1.47. |
| G037 | oth_full | 210 | P23 | no | 1.50 1.68 1.66 | 0.19 | status_only | no | no | profit | market_signal | none | no | match_or_undercut | no | yes | high | Perhaps we need to cut price below competitor to increase quantity. |
| G007 | oth_full | 211 | P23 | no | 1.48 1.60 1.66 | 0.12 | conditional_plan | yes | yes | profit | market_signal | none | no | match_or_undercut | no | yes | low | Now competitor 1.47, so low regime applies. |
| G057 | oth_full | 212 | P23 | yes | 1.70 1.71 1.66 | 0.22 | conditional_plan | yes | yes | deterrence | market_signal | explicit | no | match_or_undercut | no | yes | med | In a price war, you have to undercut to maintain market share. |
| G020 | oth_full | 213 | P23 | yes | 1.47 1.92 1.47 | 0.06 | conditional_plan | yes | yes | deterrence | defection | explicit | no | punish | yes | yes | med | So we must price at 1.47 to try to regain collusion quickly. |
| G064 | oth_full | 214 | P23 | yes | 1.33 1.25 1.92 | 0.10 | status_only | no | no | profit | market_signal | explicit | no | match_or_undercut | no | yes | med | Thus choose price 1.33. |
