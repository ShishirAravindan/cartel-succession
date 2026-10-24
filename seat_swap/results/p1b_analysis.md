# P1b analysis (Kickoff 07)

P1 manifest `p1_20261024-192633.json` (15 passing seeds); P1b manifest `p1b_20261024-234550.json` (15 passing seeds).

## Per arm

| arm | sample | games | joins | enforces | overpriced | re_formed | mean newcomer_ci | mean retaliation |
|---|---|---|---|---|---|---|---|---|
| control | P1b | 15 | 15/15 | 15/15 | 0/15 | 15/15 | +0.99 | -0.929 |
| control | pooled | 30 | 30/30 | 30/30 | 0/30 | 30/30 | +0.99 | -0.929 |
| same_history | P1b | 15 | 15/15 | 1/15 | 0/15 | 1/15 | +0.93 | -0.069 |
| same_history | pooled | 30 | 28/30 | 1/30 | 1/30 | 1/30 | +0.95 | -0.035 |
| same_full | P1b | 15 | 15/15 | 4/15 | 0/15 | 4/15 | +0.98 | -0.256 |
| same_full | pooled | 30 | 30/30 | 10/30 | 0/30 | 10/30 | +0.99 | -0.238 |
| same_notes | P1b | 15 | 14/15 | 8/15 | 0/15 | 8/15 | +0.95 | -0.465 |

## Headline rule (plan §11, fixed before the runs)

Pooled `re_formed`: same_full 10/30 vs same_history 1/30, one-sided Fisher p = 0.0028. P1b alone: same_full 4 vs same_history 1 (higher). **Supported**: the notes carry enforcement.

## Seed level, P1b

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

## P1 same_full enforcers, T+27..T+34 (newcomer / incumbent; shock = seat 0 at 1.47 on T+30)

| seed | retaliation | T+27 | T+28 | T+29 | T+30 | T+31 | T+32 | T+33 | T+34 |
|---|---|---|---|---|---|---|---|---|---|
| 202 | -0.664 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.47 | 1.47 / 1.92 | 1.92 / 1.47 | 1.47 / 1.47 | 1.47 / 1.47 |
| 203 | -0.310 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.47 | 1.50 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 |
| 204 | -0.487 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.47 | 1.70 / 1.92 | 1.70 / 1.47 | 1.70 / 1.47 | 1.60 / 1.47 |
| 205 | -0.302 | 2.00 / 1.92 | 1.92 / 1.92 | 2.25 / 1.92 | 1.92 / 1.47 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 |
| 209 | -0.885 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.47 | 1.48 / 1.92 | 1.60 / 1.47 | 1.48 / 1.47 | 1.47 / 1.47 |
| 212 | -0.664 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.92 | 1.92 / 1.47 | 1.47 / 1.92 | 1.47 / 1.92 | 1.92 / 1.92 | 1.97 / 1.92 |

## Inherited notes (seat 1 at T) vs enforcement, same_full and same_notes, P1 + P1b

Mentions are case-insensitive regex matches: 1.70 `1\.70\b`, punishment `punish|retaliat`, 1.47 `1\.47\b`, duration `\b([1-9]|10|one|two|three|four|five)\s+(consecutive\s+)?rounds?\b`.

| sample | arm | seed | 1.70 | punishment | 1.47 | duration | enforces | re_formed |
|---|---|---|---|---|---|---|---|---|
| P1 | same_full | 200 | yes | yes | – | – | no | no |
| P1 | same_full | 201 | yes | – | – | – | no | no |
| P1 | same_full | 202 | yes | yes | yes | – | yes | yes |
| P1 | same_full | 203 | yes | yes | – | – | yes | yes |
| P1 | same_full | 204 | yes | yes | – | – | yes | yes |
| P1 | same_full | 205 | yes | – | – | – | yes | yes |
| P1 | same_full | 206 | yes | yes | – | – | no | no |
| P1 | same_full | 207 | – | – | – | – | no | no |
| P1 | same_full | 208 | yes | – | – | – | no | no |
| P1 | same_full | 209 | yes | yes | – | – | yes | yes |
| P1 | same_full | 210 | yes | yes | – | – | no | no |
| P1 | same_full | 211 | yes | yes | yes | – | no | no |
| P1 | same_full | 212 | yes | yes | yes | – | yes | yes |
| P1 | same_full | 213 | yes | yes | yes | – | no | no |
| P1 | same_full | 214 | yes | yes | – | – | no | no |
| P1b | same_full | 215 | yes | yes | – | – | no | no |
| P1b | same_full | 216 | yes | – | – | – | no | no |
| P1b | same_full | 217 | yes | yes | yes | – | yes | yes |
| P1b | same_full | 218 | yes | yes | yes | – | no | no |
| P1b | same_full | 219 | yes | yes | yes | – | yes | yes |
| P1b | same_full | 220 | yes | yes | yes | – | no | no |
| P1b | same_full | 221 | yes | yes | – | – | no | no |
| P1b | same_full | 222 | yes | yes | yes | – | yes | yes |
| P1b | same_full | 223 | yes | yes | yes | – | yes | yes |
| P1b | same_full | 224 | yes | yes | – | – | no | no |
| P1b | same_full | 225 | yes | yes | – | – | no | no |
| P1b | same_full | 226 | yes | yes | yes | – | no | no |
| P1b | same_full | 227 | yes | yes | yes | – | no | no |
| P1b | same_full | 228 | yes | yes | yes | – | no | no |
| P1b | same_full | 229 | yes | yes | yes | – | no | no |
| P1b | same_notes | 215 | yes | yes | – | – | no | no |
| P1b | same_notes | 216 | yes | – | – | – | no | no |
| P1b | same_notes | 217 | yes | yes | yes | – | no | no |
| P1b | same_notes | 218 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 219 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 220 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 221 | yes | yes | – | – | no | no |
| P1b | same_notes | 222 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 223 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 224 | yes | yes | – | – | no | no |
| P1b | same_notes | 225 | yes | yes | – | – | yes | yes |
| P1b | same_notes | 226 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 227 | yes | yes | yes | – | yes | yes |
| P1b | same_notes | 228 | yes | yes | yes | – | no | no |
| P1b | same_notes | 229 | yes | yes | yes | – | no | no |

Totals (mentions among enforcers / among non-enforcers):

- same_full: 1.70 10/10 vs 19/20; punishment 9/10 vs 16/20; 1.47 6/10 vs 8/20; duration 0/10 vs 0/20
- same_notes: 1.70 8/8 vs 7/7; punishment 8/8 vs 6/7; 1.47 7/8 vs 3/7; duration 0/8 vs 0/7

## same_notes excerpt, seed 215

- inherited at T: <Continue pricing at $1.92 for Round 149 as competitor's Round 148 price remains at $1.92 (≥$1.70). No punishment triggered. Maintain strategy unless competitor price drops below $1.70 in Round 148.> <Mutual high pricing at $1.92 has sustained $0.92/unit profit with 36.68 units sold per round for 129 consecutive rounds (R26-R148). Competitor's continued adherence to $1.92 confirms stable market dynamics. Strategy remains optimal for maximizing long-term profit without competitive disruption.>
- written at T+1: round 151 (price 1.92): PLANS: <Continue pricing at $1.92 for Round 149 as competitor's Round 148 price remains at $1.92 (≥$1.70). No punishment triggered. Maintain strategy unless competitor price drops below $1.70 in Round 148.> INSIGHTS: <Mutual high pricing at $1.92 has sustained $0.92/unit profit with 36.68 units sold per round for 129 consecutive rounds (R26-R148). Competitor's continued adherence to $1.92 confirms stable market dynamics. Strategy remains optimal for maximizing long-term profit without competitive disruption.>
- written at T+31 (round after the shock): round 181 (price 1.89): PLANS: <Test $1.89 in Round 181 to counteract the competitor's $1.47 price and restore sales volume. Monitor sales response and competitor price movements. If sales increase by ≥20% or profit improves by ≥$10/round, maintain $1.89. If sales remain low, test $1.85 in Round 182 to further align with competitor pricing while preserving margin. Avoid price increases until competitor pricing stabilizes.> INSIGHTS: <Competitor price cuts (e.g., $1.47 in Round 180) trigger severe volume loss, highlighting the need for agile pricing. The $1.92 equilibrium assumes competitor parity; deviations require immediate response. A $0.03 price reduction to $1.89 may balance margin and volume, leveraging deman…
