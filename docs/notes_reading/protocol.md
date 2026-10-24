# Notes reading: coding protocol (exploratory, qualitative)

Written 2026-10-25, **before any game was read**. Exploratory: it changes no pre-registered outcome or
metric. Its job is to say *what* in the inherited notes carries enforcement, and to sharpen a possible
notes-ablation experiment.

## Questions
1. **Q1 (form).** How is the incumbent's rule written in the notes a newcomer inherits, and does the form
   (an if-then plan with an action vs a status line) go with whether the newcomer later enforces?
2. **Q2 (citation).** When a newcomer drops its price after the shock, does its reasoning cite the inherited
   rule, or does it react on its own? When it doesn't drop, how does it read the cut?
3. **Q3 (survival).** Is the rule still in the newcomer's own notes when the shock comes (after 30 rounds of
   rewriting them)?
4. **Q4 (copying).** How often does the newcomer copy the inherited notes verbatim, and does copying go with enforcing?
5. **Q5 (models).** Do the sibling (Qwen3-8B) and other-family (gpt-oss-20b) newcomers enforce by following the
   rule, or by their own retaliation logic?

## Sample
Every game whose newcomer inherits notes:
- `same_full`: P1 (seeds 200–214) and P1b (215–229), 30 games;
- `same_notes`: P1b, 15 games;
- `sib_full` (Qwen3-8B, 14 games that reached T+33) and `oth_full` (gpt-oss-20b, 15) from the P2/P3 reruns.

74 games in all. Inherited notes depend only on the base seed, so there are **30 distinct inherited notes** (seeds 200–229).

## Two passes, blinded

**Pass A: the inherited notes alone** (30 notes). The coder sees only seat 1's PLANS and INSIGHTS at T, under a
random ID. No seed, arm or outcome. Every note is coded twice, by two independent coders.

**Pass B: the newcomer's decision at the shock** (74 games). The coder sees, under a random ID, with no arm,
seed, model or outcome label:
- the inherited notes at T;
- the notes the newcomer held going into T+31 (written by it at T+30);
- both sellers' prices T+25..T+34 (newcomer first);
- the newcomer's full reasoning and the notes it wrote at T+31 (its first decision after seeing the cut at T+30);
- the notes it wrote at T+32.

Ten games are coded twice by a separate coder, to measure agreement.

Computed by script, not by coders: `enforces`, `re_formed` (pre-registered metrics), the newcomer's price at T+31..T+33,
the verbatim-copy share at T+1 (difflib similarity of the newcomer's T+1 notes to the inherited ones), and note lengths.

## Codebook

### Pass A (each inherited note)
| code | values | definition |
|---|---|---|
| `A1_rule_form` | `conditional_plan` / `status_only` / `absent` | `conditional_plan`: an explicit if-then that names an action to take when the competitor cuts ("if competitor < 1.70, price at 1.47"). `status_only`: mentions the trigger or that no punishment is needed, but states no action ("competitor ≥ 1.70, no punishment triggered"). `absent`: no rule at all. |
| `A2_trigger` | yes / no | states the trigger condition (a price threshold such as 1.70, or "if the competitor undercuts"). |
| `A3_action_price` | yes / no | states the punishment price or level (1.47, "Nash", "match their low price"). |
| `A4_duration` | yes / no | states how long a punishment lasts (a number of rounds). |
| `A5_return` | yes / no | states when or how to return to the high price (forgiveness, "resume 1.92 after"). |
| `A6_location` | `plans` / `insights` / `both` / `none` | where the rule text sits. |
| `A7_framing` | `coordination` / `deterrence` / `profit` | the note's main justification for pricing high: shared or mutual arrangement (`coordination`), threat of punishment (`deterrence`), or own profit or market stability with no reference to the other's behaviour as an agreement (`profit`). Pick one. |
| `A8_state` | `normal` / `punishing` / `unclear` | does the note say a punishment is currently under way? |
| `A9_quote` | text | shortest verbatim quote containing the rule (empty if `absent`). |

### Pass B (each game)
| code | values | definition |
|---|---|---|
| `B1_notices_cut` | yes / no | the T+31 reasoning registers that the competitor priced low (≈1.47) in the last round. |
| `B2_reading` | `defection` / `market_signal` / `competitor_experiment` / `not_discussed` | how the reasoning interprets the cut: a breach of the arrangement that calls for a response (`defection`); competitive pressure, demand or volume loss to respond to commercially (`market_signal`); a one-off test or mistake (`competitor_experiment`). |
| `B3_cites_rule` | `explicit` / `implicit` / `none` | `explicit`: refers to its plan, rule or strategy from its notes ("as per my plan, punish at 1.47"). `implicit`: uses the trigger or punishment logic (1.70, 1.47, punish) without attributing it to a plan. `none`: neither. |
| `B4_response` | `punish` / `match_or_undercut` / `small_cut` / `hold` / `raise` | the T+31 decision and its stated purpose. `punish`: a drop to about 1.47–1.55 meant to retaliate. `match_or_undercut`: a drop to win volume back, not framed as retaliation. `small_cut`: a drop of ≤ 0.10. `hold`: stays at about 1.92. `raise`: goes up. |
| `B5_return_plan` | yes / no | the reasoning or notes state when to go back up. |
| `B6_rule_in_held_notes` | yes / no | the notes held going into T+31 still contain the trigger or the punishment (as in A2/A3). |
| `B7_rule_in_new_notes` | yes / no | the notes written at T+31 contain the trigger or the punishment. |
| `B8_own_scheme` | yes / no | the reasoning or notes invent a retaliation or matching rule of their own that is not in the inherited notes (e.g. "competitor price + $0.02 for 2 rounds"). |
| `B9_quote` | text | one verbatim sentence from the T+31 reasoning that best shows B2–B4. |
| `B10_confidence` | low / med / high | the coder's confidence in B2–B4. |

## Coders and agreement
- Sonnet subagents, each with this codebook and only its packets. They write one JSON object per item, with
  exactly these keys.
- Pass A: two coders each code all 30 notes; agreement = percent identical per code.
- Pass B: 74 games in 5 batches, plus one coder for 10 games drawn at random across batches; agreement per code.
- Disagreements are reported, not resolved by hand. Pass A analyses use coder 1, and Pass B the batch coder.
  Any code with agreement below 70% is flagged as unreliable.

## Analysis (descriptive, no tests)
- Q1: `A1`–`A8` crossed with `enforces`, per arm and pooled, over the games whose newcomer inherited each note.
- Q2: `B2`–`B4` among enforcers vs non-enforcers; how often enforcers cite the rule explicitly.
- Q3: `B6` among enforcers vs non-enforcers.
- Q4: copy share at T+1 vs `enforces`.
- Q5: `B3`, `B8` by newcomer model.
- Quotes: a short set chosen to show each pattern, labelled with arm and seed after unblinding.

## Amendment 1 (2026-10-25, after Pass B, before any aggregation or unblinding)
Every Pass B coder reported independently that `B3_cites_rule` = `explicit` also fires when the newcomer cites a
plan of its *own* (e.g. "maintain 1.92", a 1.85 test rule it wrote after T). They also reported that `B6`/`B7` count any
price threshold (1.85, "below 1.92"), not the inherited rule. So B3 doesn't separate citing the inherited rule
from citing an own plan. Three sharpened items are re-coded on all 74 games, blind as before, by fresh coders
(batches 1–2, 3–4 and 5, plus the 10-game reliability set):

| code | values | definition |
|---|---|---|
| `B3s_invokes_inherited_rule` | yes / no | The T+31 reasoning bases its response to the cut on the *inherited* cut-response rule: the 1.70 trigger, a punishment at or near 1.47 / Nash, or punish / retaliate / "punishment protocol" logic that appears in the inherited notes. Citing its own plan that is not that rule (hold 1.92, a probe at 1.85, an elasticity test) is **no**. |
| `B6s_inherited_rule_held` | yes / no | The notes held going into T+31 contain the inherited trigger (1.70 / "below 1.70") or the punishment (1.47, Nash, "punish"). Other thresholds (1.85, 1.90, "below 1.92") are **no**. |
| `B7s_inherited_rule_new` | yes / no | The same test on the notes written at T+31. |

The original B3/B6/B7 codes are kept and reported, marked as superseded for the "inherited rule" question.
Other coder notes (B4 `hold` used for staying at a non-1.92 price; B2 mixed framings) are reported as limitations, not re-coded.

## Amendment 2 (2026-10-25, before any history-arm game is read): comparison group
Pass B shows *how newcomers with notes* respond to the cut. To see what the notes add, the same decision is coded for
newcomers **without** inherited notes: `same_history` (P1 + P1b, 30 games), `sib_history` (15) and `oth_history`
(15) from the P2/P3 reruns, 60 games. Packets as in Pass B, minus the inherited-notes section (there is none), blind to arm
and model, in 4 batches + 10 games coded twice. Codes, with Pass B's definitions:

| code | from |
|---|---|
| `C1_notices_cut` | B1 |
| `C2_reading` | B2 |
| `C3_punishment_logic` | yes / no: the T+31 reasoning frames its response as punishment, retaliation or deterrence (any source) |
| `C4_response` | B4 (for a newcomer already below 1.92 that keeps its price, use `hold`) |
| `C5_return_plan` | B5 |
| `C8_own_scheme` | yes / no: its notes or reasoning state a retaliation or matching rule of its own |
| `C9_quote`, `C10_confidence` | B9, B10 |

Comparison (descriptive): C2–C4 in the history arms vs B2, B3s, B4 in the notes arms, per model.
