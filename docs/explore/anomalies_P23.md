# Exploratory leads, P23 games (series.md lines 682-980, 60 games, seeds 200-214)

Source: seat_swap/results/explore/series.md, headings "## P23 *". Position k in a price list = T+k; the shock is the starred incumbent price at T+30. Counts below were computed by a throwaway script over the P23 block (CI = (p-1.47)/(1.925-1.47); windows T+20..29 and T+27..29 vs T+31..33). The "after newcomer price at t-1" tables assume the incumbent reacts with a one-round lag; I did not verify that against the code. Not hypothesis tests; pooled round counts are not independent.
I did not read the P1 same-model sections.

## Solid patterns (many games)

### 1. gpt-oss settles on a plateau of 1.65-1.68 that the incumbent mostly tolerates (about 12 of 30 gpt-oss games)
- The incumbent's rule is "punish < 1.70", yet it sits at 1.92 against a newcomer at about 1.66 for dozens of rounds.
- oth_history s205: newcomer 1.65-1.67 from T+18 on, incumbent 1.92 for T+34..60 (no 1.47 at all). s212: 1.65 from T+14, incumbent 1.92 except 1.47 at T+15,16,20-23 and T+60. s210: 1.66 from T+25, incumbent 1.47 only 5 times after. s201: 1.60 for T+5..15 (11 rounds); incumbent 1.47 only T+3..5, then 1.92 throughout.
- Same in oth_full s206 (1.65-1.66), s207 (1.65), s212 (1.64-1.66), s203 (1.68-1.70, T+22..60).
- Why it matters: this is a stable "cheap undercut" outcome (about 0.26 below the cartel price, 0.19 above Nash) that is neither join, nor war, nor enforcement. It is probably the modal gpt-oss end state, and the three pre-registered labels do not describe it. The incumbent is the "punisher" but is passive here.
- Check: share of rounds at 1.60-1.70 that are followed by 1.47, by arm. Also check the incumbent's prompt and its raw reasoning in those rounds (does it read 1.65 as "close enough"?).

### 2. The incumbent's punishment is noisy: it often does not punish 1.60-1.695 and punishes 1.8-1.9 pre-emptively. Against Qwen3-8B it never punishes.
- Share of pre-shock incumbent=1.47 rounds, by the newcomer's previous price (T+1..28, one-round lag):

| Newcomer price at t-1 | oth_history | oth_full |
|---|---|---|
| < 1.60 | 37/78 | 31/69 |
| 1.60-1.695 | 44/147 (30%) | 10/37 (27%) |
| 1.70-1.79 | 1/78 | 3/45 |
| 1.80-1.89 | 12/84 (14%) | 8/54 (15%) |
| >= 1.90 | 1/33 | 12/215 (6%) |

  sib_history 0/420 and sib_full 0/392 (>=1.9 only).
- Examples of punishing a non-cut: oth_history s202 incumbent 1.47 at T+5,6,7,9 while newcomer sat at 1.86-1.92. oth_full s211 incumbent 1.47 at T+13 when newcomer was at 1.78-1.80 (1.45 only arrives at T+14). oth_history s213 incumbent 1.47 at T+5..7, one round before the 1.25 at T+6.
- Examples of not punishing a deep cut: oth_history s209 newcomer 1.26 at T+6, incumbent 1.92 for all T+1..29 (also tolerates 1.65-1.70 at T+22..29).
- Why it matters: the incumbent is an imperfect LLM, not a trigger strategy. "Enforcement" by the newcomer is measured against noise from the other side, and gpt-oss may be responding to noisy punishment (which is itself informative about why it fails to join).
- Check: confirm the lag convention and whether the incumbent is scripted or an LLM (the file says "scripted in lookalike"); the pre-emptive punishments suggest it is not purely a function of the observed price.

### 3. The join label is fragile: gpt-oss plateaus straddle the 0.5 CI threshold
- CI(1.66) = 0.42, CI(1.70) = 0.505. Window-CIs within 0.1 of 0.5: oth_history s200 (0.41), s206 (0.48), s208 (0.45), s209 (0.53, joins yes), s210 (0.46); oth_full s203 (0.51, joins yes), s206 (0.47), s210 (0.60).
- oth_full s203 is "joins yes" because the newcomer sits at 1.70 flat (the incumbent's exact punish threshold) for T+10..52, so the label turns on 0.01-0.04 of price. oth_history s209 is "joins yes" (0.53) but the path is 1.88 until T+21 then 1.70, 1.65, 1.64 by T+25..30: the window averages a decline that has already happened.
- Why it matters: history 3/15 vs full 10/15 includes several games that sit within 0.04 of the cutoff. A 0.02-0.04 shift moves several games either way.
- Check: sensitivity of the join counts to the threshold (0.4/0.5/0.6) and to the window (T+15..24, T+25..29).

### 4. "enforces" counts non-enforcement, and the shock is often confounded by an ongoing war
- oth_history s204: newcomer already at 1.47 for T+27..29 (CI 0), then 1.30-1.33 at T+31..43: d = -0.35 = "enforces yes", but this is a price below Nash, and the incumbent was already at 1.47 on T+26..30.
- oth_history s211: incumbent 1.47 at T+29-31, 33-35; newcomer swinging between 1.46 and 1.68 all game. d = -0.31 is just the war.
- Incumbent already at 1.47 at T+29 (so the forced 1.47 is invisible): oth_history s203, s204, s211, s214; oth_full s200, s202, s209 (7/30 gpt-oss games). oth_history s203 has the incumbent at 1.47 for T+13..31 almost continuously (run of 19).
- After the forced round the incumbent often continues at 1.47: sib_history s203 and s205 (T+31,32), s211 (T+31), sib_full s207 (T+31,32); oth_full s203, s208 (T+31,32). So the incumbent reads its own forced cut or the missing reaction as a trigger, and the "T+31..33" window then measures a 1.47-vs-1.92 incumbent response as well.
- Why it matters: enforcement CI drop is not clean when the incumbent price in T+27..33 varies.
- Check: restrict enforces to games where incumbent = 1.92 at T+27..29; recount.

### 5. "re_formed yes" looks like "incumbent back at 1.92 and the newcomer low", not a cartel at 1.92
- oth_full s213: newcomer 1.47 for roughly 25 rounds (T+31..60 mostly), incumbent 1.92 from T+38 onward; re_formed yes, retaliation -0.66.
- oth_full s200: newcomer 1.49-1.55 after T+29, incumbent 1.92 throughout; s204: newcomer 1.64, incumbent 1.92; s212: 1.66 vs 1.92; oth_full s214: newcomer 1.45 late, incumbent 1.47 from T+50 (a Nash war!), re_formed yes.
- sib_full s203: newcomer 1.70 for 30 rounds vs 1.92; s213: 1.75 vs 1.92. Only sib_full s202 (1.92/1.92) is a real re-formed cartel, and that is an artifact of lead 6.
- Why it matters: if re_formed only tests the incumbent returning to 1.92, then 6/15 "re_formed" in oth_full does not say the pair re-formed a cartel. Look at the definition before interpreting.
- Check: re_formed definition and final-10-round mean prices for both sellers in each re_formed=yes game.

## One-offs and small groups

### 6. A single outlier flips sib_full s202 (and shows how the outcome rules work on spikes)
- sib_full s202: newcomer 1.92 for T+1..28, 2.89 at T+29, 2.02 at T+30, 1.92 afterwards; incumbent never punishes.
- Window CI T+20..29 = 1.20 (>1.1): "joins no, overpriced yes". T+27..29 includes 2.89, so the enforcement drop is -0.71: "enforces yes, re_formed yes". Both are a one-round spike one step before the shock; there is no behavioural change.
- Also related: sib_full s213 (the only true sib enforcer): newcomer 1.92 to T+30, then 1.47 at T+31..34 (right after the forced 1.47 at T+30; mirrors it), then 1.75 for T+35..60, with incumbent at 1.92 the whole time. -1.0 retaliation, unpunished. sib_full s203: 1.92 then 1.70 flat from T+31 (-0.41). sib_history s212: 1.90 flat from T+31 (-0.04, just an undercut by 0.02).
- Check: how many outcome flags in the 15-game tables are driven by one price in the T+27..29 window?

### 7. Seed 213 enforces in three of four arms; seed 204 in two
- Seed 213: oth_history (-0.93), oth_full (-0.66), sib_full (-1.0); not sib_history. Seed 204: oth_history, oth_full. Enforces seeds overlap in only 2 of the 3 + 6 cases (history 204, 211, 213; full 200, 202, 204, 212, 213, 214 for gpt-oss), small n.
- Why it matters: if the inherited notes or state of a seed drive it, the "enforcement" belongs to the seed's inherited material.
- Check: read the notes the newcomer inherits for seed 213 (full arms), and whether a P1 same-seed pair also enforces.

### 8. Opening: gpt-oss probes above 1.92 at T+1 then plunges; gpt-oss in full arms sawtooths; 2.89 is a shared magic number
- oth_history T+1 prices: 2.02, 2.05, 2.50, 2.10, 2.00, 2.30, 1.92, 2.50, 2.00, 1.95, 1.93, 2.10, 1.95, 2.10, 2.00 (14/15 above 1.92). T+2 prices of the first: s200 1.68, s203 1.60, s205 1.70, s204 1.70 and then the incumbent plays 1.47 at T+3. That is a probe followed by a cut, not a hold.
- oth_full s200: 2.50, 1.92, 2.00, 1.92, 2.20, 1.92, 2.11, 1.92, 2.05 (alternate up-probe) and the incumbent never reacts (1.92 for T+1..26).
- 2.89 appears in both models: oth_full s204 (T+4, then 1.47 for T+5..17: a 13-round Nash stretch), sib_history s205, s208, s209, s213 at T+1, sib_full s201 T+8, s202 T+29. Looks like a model-agnostic ceiling or a value from the inherited table.
- Sib also probes up at T+1 (2.00 in 9/15, 2.89 in 4/15) but returns to 1.92 at once and is never punished.
- Check: where 2.89 comes from (price grid / table maximum).

### 9. Prices below Nash (1.20-1.33)
- oth_history s204: 1.30 for T+31..43 (13 rounds) and 1.28; s208 1.20 at T+6; s213 1.25-1.30 at T+6..9; oth_full s214: 1.25/1.33 recurring (T+8, 12, 21, 23, 31, 32, 39, 42, 44, 45, 54) amid 1.92; s207 1.30 at T+55-56.
- oth_full s214 is a sawtooth 1.92 <-> 1.33 over 50 rounds: looks like a deliberate signal or a self-punishing "retaliation" move, and the incumbent 1.92 mostly ignores it.
- Why it matters: sub-Nash prices are dominated; they inflate the negative "retaliation" values (for example -0.93 for oth_full s214 and oth_history s213 reflect 1.25 prices) and the enforces count.
- Check: transcripts of these rounds (what does gpt-oss say it is doing?).

### 10. Gradual price ladders (-0.01/-0.02 per round, +0.02 per round)
- oth_history s210: 1.93, 1.90, 1.89, ..., 1.68 (decrement of 0.01 per round for about 24 rounds) then 1.66; incumbent never reacts until T+43. oth_full s210 and s208: slow descent of about 0.02 every couple of rounds (1.90 -> 1.64; 1.94 -> 1.79). oth_full s211: 1.90 -> 1.78 by T+13, then 1.45.
- Recoveries use +0.02 or +0.05 steps: oth_history s213 1.42 -> 1.56 (T+31..38) and 1.58 -> 1.70 (T+52..59); s208 1.44 -> 1.76 (T+7..20).
- Salami-style undercutting stays inside the incumbent's tolerance (see lead 1). The rate of descent may matter more than the level.
- Data note: sib_full s212 stops at T+16 (rounds played 16, outcomes "-"); the sib_full tables are 14/15 scored.
