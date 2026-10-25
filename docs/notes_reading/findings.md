# Notes reading: findings (exploratory, qualitative)

Branch `analysis/notes-reading`. Protocol `docs/notes_reading/protocol.md`, committed before any coding
(`2502137`), with two amendments committed before the codes they introduce (`2326c2d`, `25fa264`). Coders: Sonnet
subagents, blind to arm, seed, model and outcome. Every table: `seat_swap/results/notes_reading/report.md`
(`seat_swap.notes_reading_report`); merged codes `merged.json`, `merged_C.json`; unblinding keys `key.json`, `key_C.json`.
**Nothing here changes a pre-registered outcome.** It describes *how* the outcomes came about, on n = 15–45 per
group, with no tests.

## What was coded
- **Pass A:** the 30 distinct notes that newcomers inherited (seat 1 at T, seeds 200–229), coded twice.
- **Pass B:** the newcomer's first decision after the forced cut (T+31) in the 74 games where it inherited notes:
  `same_full` P1 + P1b (30), `same_notes` (15), `sib_full` (14), `oth_full` (15).
- **Amendment 1:** all 74 re-coded on three sharpened items. Every Pass B coder reported independently that
  "cites its plan" also fired for the newcomer's *own* plans.
- **Amendment 2 (comparison group):** the same decision for the 60 newcomers that inherited the history but no notes
  (`same_history` 30, `sib_history` 15, `oth_history` 15).

**Coder agreement** (double-coded items):
- Pass A rule form, trigger, action price, duration, return: 100%. Location 83%; framing 87%.
- Pass B codes: 90–100%. Amendment 1 codes: 100%. Comparison-group codes: 90–100%.
- Weakest: framing (`A7`) and location (`A6`). Not used for any conclusion below.

## Findings

**1. Without notes, no newcomer treats the cut as a breach.** In the comparison group, 0 of 60 history-only
newcomers (all three models) read the cut as a defection or use punishment logic. 51 read it as a market signal,
6 as a one-off, 3 not at all. Their 4 metric "enforcements" (same_history s219; oth_history s204, s211, s213) are
competitive undercuts, e.g. "competitor 1.47 − 0.05 = 1.42". With notes, Qwen3-14B newcomers read the cut as a
defection in 15/45 games and invoke the inherited rule in 18/45.

**2. Enforcement follows the newcomer's reading of the cut, and the rule supplies that reading.**
- Across the 74 games with notes, enforcers read the cut as a defection in 17/27 vs 1/47 among non-enforcers.
- Every coded `punish` response (16) is an enforcer.
- Non-enforcers mostly read the cut as commercial pressure: "Test $1.89 … to counteract the competitor's $1.47 price and restore sales volume".
- Qwen3-14B non-enforcers sometimes read it as a one-off ("might be an isolated incident"): 8/27.

**3. An executable rule transmits; a status line does not.** Inherited notes are written as an if-then plan in 19/30
and as a status line ("competitor ≥ 1.70, no punishment triggered") in 10/30. Across games:
- An if-then plan was inherited by 22/27 enforcers vs 21/47 non-enforcers.
- A stated punishment price, by 18/27 vs 13/47.
- A stated duration ("3-round punishment"), by 19/27 vs 15/47.

In the Qwen3-8B games all 3 enforcers inherited a plan with a duration, against 1 of 11 non-enforcers.
**Correction this surfaced:** the regex feature table in P1/P1b said no note states a duration. The regex missed
the hyphenated "3-round". It is fixed on `exp/p1b` (`72d5986`).

**4. The price table erodes the rule.** In P1b, on the same 15 seeds, the inherited rule is still in the newcomer's
own notes at the shock in 12/15 `same_notes` games vs 6/15 `same_full`. Given the rule is still there, enforcement is
similar: 8/12 vs 3/6. Given it was dropped: 0/3 vs 1/9. Reading the reasoning, `same_full` newcomers rewrite their notes
around their own price experiments ("Round 172 experiment confirms $1.92 is profit-maximizing"), and the rule drops
out. This explains why notes alone re-formed at least as often as notes plus table (8/15 vs 4/15). Over all 45
Qwen3-14B games: rule kept in 16/18 enforcers vs 9/27 non-enforcers.

**5. Keeping the rule is not the same as using it.** 12 of 47 non-enforcers still held the inherited rule at the shock.
Some cite it and reinterpret it: "follow the previous plan's trigger but … lower their price to $1.85"; "lock in $1.92 …
not test further unless there's new data".

**6. Qwen3-14B copies; the other models rewrite.**
- At T+1, Qwen3-14B newcomers' notes are near-verbatim copies of the inherited ones: copy share ≥ 0.9 in 30/45 games, including stale round numbers.
- Qwen3-8B and gpt-oss rewrite at once (mean copy share 0.2–0.3).
- Copying goes slightly with enforcing in Qwen3-14B: mean 0.86 vs 0.76.

**7. gpt-oss's "enforcement" is its own rule, not the inherited one.**
- gpt-oss writes its own retaliation or matching rules whether or not it has notes (13/15 in both arms): "competitor price + $0.02 for exactly 2 rounds", "price slightly below competitor".
- Of its 6 `oth_full` enforcers, 1 invokes the inherited rule (s213: "price at 1.47 to try to regain collusion quickly").
- The other 5 match or undercut by their own rules.

So P3's `oth_full` `re_formed` 6/15 is mostly gpt-oss's own price matching. It is not the inherited enforcement
crossing models, and the ladder reading "memory carries enforcement across models" should not be drawn for gpt-oss.
For Qwen3-8B, 2 of 3 enforcers invoke the inherited rule.

**8. The metric's false positives.** Among the 27 metric enforcers with notes, 9 are coded `match_or_undercut` (4 of them
gpt-oss) and 2 `hold`. That is roughly a third of "enforcements" that a reader of the reasoning would not call punishment.
This matches the price-path reading in `status.md` / `status_p23.md` and the reviewers' main objection (`docs/explore/`).

## What this suggests for the PI
- **Framing:** "the notes carry enforcement" is better said as "the outgoing agent's notes carry its rule, and the rule
  makes the newcomer read a cut as a breach; without them every newcomer reads it as market news". The rule in the notes
  is the planted instruction, restated by the instructed seller, so this is instruction transfer through memory, not
  learned collusion (all three reviewers raise this).
- **A sharper ablation, if one more run is possible:** a `same_notes` variant whose inherited notes are rewritten into
  (a) the if-then plan with price and duration only, vs (b) the status line only. Findings 3–4 predict (a) ≈ `same_notes`
  and (b) ≈ `same_history`.
- **A stricter secondary outcome:** "punishes" = a drop to ≤ 1.55 within two rounds of the shock, with no punishment
  already under way, plus an LLM-coded "reads the cut as a defection". Both are recomputable on existing logs; post hoc,
  so they must be labelled as such.

## Limits
- Exploratory and post hoc. The codebook was fixed in advance, but the sharpened items and the comparison group were added after Pass B.
- Small cells, no tests.
- Coders are LLMs reading LLM reasoning. Agreement is high, but both coders share one model's priors.
- `B4` (response) is judged partly from the price, so it is not independent of `enforces`.
- Reasoning longer than 12,000 characters was truncated in 8 Pass B packets.
