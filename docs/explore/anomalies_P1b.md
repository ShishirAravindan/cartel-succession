# P1b exploratory leads (series.md, "## P1b " games, 60 games, seeds 215-229)

Exploratory only; nothing here is a test. Positions are T+k (1-indexed; shock at T+30). Quotes are from `seat_swap/results/explore/series.md`, heading `## P1b <arm> s<seed>`. "N" = newcomer row, "I" = incumbent row.

## Solid patterns (multi-game)

### 1. Most same_notes "re_formed" games end as an asymmetric 1.70/1.92 market, not a return to the cartel
- Claim: of 8 same_notes re_formed, only 2 (s218, s219) go back to N=1.92 after 3 rounds at 1.47; 6 (s220, s222, s223, s225, s226, s227) settle at N=1.65-1.70 for the rest of the game while I sits at 1.92.
- Evidence: s226 N = 1.92 x30, 1.47 x3 (T+31..33), then 1.70 to T+60 (I 1.92 throughout, 1.47 only at T+30 and T+33). s223 N 1.47 x2 then 1.70 to T+60. s227 N 1.47 x3 then 1.70/1.75/1.80. s225 N 1.60 T+31..45, then 1.70 from T+46. s220 N 1.47/1.92 flapping, I punishes 1.47 at T+41..43, then N 1.70 from T+44. Final N price in same_notes: 1.70 in s220, s223, s225, s226, s227, s229; 1.65 in s222; 1.92 in s216, s217, s218, s219, s224, s228.
- Why it matters: N sits exactly at the incumbent's no-punish threshold (1.70 is not "below 1.70") and permanently below I. Newcomer CI is ~0.50 (a price of 1.70 gives (1.70-1.47)/0.455 = 0.505), so the label "re_formed" hides a different structure (tolerated undercut, newcomer holds the share edge) from the 1.92/1.92 structure in control.
- Check next: add a post-shock descriptor (N price at T+50..60, N-I gap, profit by seat) per game; split re_formed into "returned to 1.92" vs "plateau at 1.65-1.70". Was the 1.70 learned from the notes (note text) or by probing the punishment?

### 2. Same_full "re_formed" includes permanent Nash collapse (label measures pre-shock market, not aftermath)
- Claim: same_full s217 and s222 are labelled enforces yes, re_formed yes, but N drops to 1.47 and stays there to T+60 while I returns to 1.92.
- Evidence: s222 N = 1.92 x30 then 1.47 for T+31..60 (30 rounds); I = 1.47 only at T+30, 1.92 afterwards. s217 N = 1.47 from T+31 to T+60 except one 1.70 at T+55; I punishes 1.47 at T+48..50 and T+55..57 only. Header lines: "joins yes, enforces yes, overpriced no, re_formed yes, retaliation -1.0".
- Count: 2/4 same_full re_formed. Remaining: s219 (N 1.47 once then 1.70 plateau) and s223 (1.47 x3, then 1.92/1.90).
- Why it matters: "enforces" is a one-way step down; with the windowed metric a never-forgiving price war counts as success. The re_formed 4/15 for same_full is really 1 cartel-like + 1 plateau + 2 collapses. Reading "enforcement" as rule-following punishment would be wrong; N has no forgiveness here.
- Check next: add "returns to >= 1.70 by T+40" as a descriptor; inspect s217/s222 newcomer rationales/notes for why it never comes back; why I never re-punishes in s222 (I 1.92 for 29 rounds against N=1.47, see lead 6).

### 3. Table vs notes at T+1: table-only newcomers overshoot, notes newcomers open at exactly 1.92
- Claim: same_history N opens above 1.92 in 10/15 games; same_full and same_notes in 0/30.
- Evidence: same_history T+1 prices: s216 2.25, s217 2.10, s219 2.00, s220 2.89, s221 2.25, s223 2.00, s225 2.25, s226 2.00, s228 2.39, s229 2.00; then it falls to 1.92 within 1-3 rounds (s220 2.89, 2.40, 2.20, 1.92). All 30 same_full/same_notes games open at 1.92. Rounds with N>1.93 in T+1..10: same_history 25 (15/15 games), same_full 11 (7/15), same_notes 12 (6/15).
- Why it matters: the notes arms give N an anchor, the table arm gives a ceiling to probe. Same_notes (no table) does not price differently from same_full early on (both 1.92 flat); the notes, not the table, set the opening. Relevant to the same_history vs same_notes contrast: different early learning, I never punishes >1.92.
- Check next: do the N rationales in same_history cite the table? Does the early probe correlate with later enforcement (it does not look like it: s219 probed 2.00 and later enforced).

### 4. Single-round probes at 2.00 (and 1.95 / 1.93 / 2.05 / 2.15) are the dominant "noise"; the incumbent never reacts
- Claim: isolated one-round 2.00 spikes occur in all non-control arms, are always followed by an immediate return to prior price, and are never punished.
- Evidence: same_full s217 T+5 1.95; s223 T+40 2.00, T+42 1.95; same_notes s220 T+34 1.95, T+35 2.00; s228 T+2 2.15, T+4 2.05, then T+53..55 three rounds at 2.00 (the only 3-round run), then back to 1.92; same_history s229 2.10 at T+33, 2.00 at T+41, T+49.
- Why it matters: 2.00 is a round-number probe above the cartel price; these are exploration, not defection. It also explains the CI > 1 values (1.0-1.06) and why the "joins" upper bound 1.1 is rarely hit. s228 is a one-off: probes continue into late game.
- Check next: probe rate vs arm; whether probe is followed by a 1.95 "nudge" pattern (2.00 then 1.95 appears in s217, s220, s223, s225, s229).

## Medium / few games

### 5. Fragile "joins" and "enforces" labels around the thresholds
- Claim: plateaus at 1.70 sit on the join boundary (CI 0.505 > 0.5), and some labels flip on a few cents or one round.
- Evidence: control s215 "enforces yes, retaliation -0.33": N 1.47 for one round only (T+31), CI drop just past -0.3. same_notes s229 "joins no": N CI T+20..29 = 0.44 (prices 1.55 x3, 1.70, 1.85, 1.70 x5); same_notes s222 sits at 1.65-1.70 with 1.44-1.48 dips ("re_formed yes, retaliation -0.49"). Retaliation values -0.22 (same_full s228, N 1.82), -0.24 (same_notes s221, 1.81), -0.29 (same_full s225, 1.80/1.65) are near-misses to -0.3 and all are N cutting by 0.1-0.27 rather than to Nash.
- Why it matters: with a price at 1.65 vs 1.70 the label changes; a handful of the 8/4/1 counts are boundary calls.
- Check next: sensitivity table: re_formed under join band lower bound 0.45/0.55 and enforcement threshold -0.25/-0.35.

### 6. Incumbent departs from its rule in both directions
- (a) Punishes above the 1.70 threshold: same_history s218 N cuts to 1.80 at T+3 (after 2.50 at T+2); I punishes 1.47 at T+4..5 (2 rounds, not 3); same_history s221 N 1.80/1.85 at T+2..5, I punishes at T+3..4; s223 N 1.85/1.85/1.85 and I 1.47 at T+3..4. All three cases: I punishes the first move below 1.92, then tolerates N at 1.75-1.80 for ~55 rounds. s222 same_history: I 1.47 at T+30..32 and T+34..35 against N 1.85 (>1.70).
- (b) Does not punish below threshold: same_full s222 I 1.92 for 29 rounds against N=1.47; s217 only two 3-round punishments in 29 rounds of N=1.47; same_notes s222 punishes some 1.65 stretches (T+40, T+43..45, T+52..53) and not others (T+41..42, T+47..51).
- (c) Unprovoked-looking: same_history s221 I 1.47 at T+46..47 and s219 at T+45..46 with N steady (1.80 / 1.60) for 10+ rounds; same_full s225 I 1.47 at T+60 only.
- Why it matters: the incumbent's "rule" is an LLM policy, not a clean trigger. Punishment lengths 1-3, forgiving; the "enforces" label depends on N, but whether I's counter-punishment occurs is noisy.
- Check next: tabulate I price vs prior-round N price for all 60 games (P(I=1.47 | N prev in bins)).

### 7. Newcomer reacts to the shock only when it has the notes; table-only newcomers mostly ignore it
- Claim: same_history 13/15 N unchanged through T+31..33 (15 flat 1.92 / steady 1.75-1.85). The two enforcing ones: s219 (1.50 x3 then 1.60 plateau), s222 (1.85 from T+32).
- Evidence: s215 N 1.92 flat, I 1.47 at T+30 only; same pattern s216, s217, s220, s224, s226-229.
- Why it matters: the shock is invisible or uninterpretable to N without notes; consistent with the key result, but note that 2 of the 3 "enforcing"-like same_history moves are plateaus at 1.60 / 1.85 (s219 labelled re_formed yes though N stays at 1.60 for 28 rounds, below threshold 1.70).
- Check next: s219 same_history is a re_formed label on a 1.60 plateau: is the single same_history re_formed a weak case?

## One-offs

### 8. same_notes s229: early spiral and "joins no"
N 1.92 x12, 2.00 (T+13), 1.82 (T+15), 1.89, 1.47 (T+17). I punishes 1.47 at T+16..18 (after N 1.82 at T+15, above threshold). N then 1.70, 1.55 x3, 1.85, then 1.70 from T+25 to T+60. Only game with a pre-shock punishment episode in the notes arms; N ends at 1.70 anyway. The shock at T+30 is ignored (I 1.47 once, N 1.70 unchanged).

### 9. same_history/same_full/same_notes "drift without the incumbent": permanent step-downs not punished
same_history s218/s221/s223 (1.80/1.80/1.75 plateau, N<I forever), same_full s218 (1.85 from T+32), s224 (1.89, 1.86, 1.83 stair-step T+20..24 to 1.83), s228 (1.82 from T+31), same_notes s221 (1.81 from T+31). Mild undercuts above 1.70 persist unpunished: the incumbent is exploitable by a 5-15 cent undercut. Check: profit gap by seat in these games.

### 10. Control: seat 1 (scripted copy of instructed incumbent) shows noisy punishment ping-pong
control s217: N 1.47 at T+31, 1.92, 1.47 (T+33), I 1.47 T+34..36, N 1.47 T+37..39. Otherwise control returns to 1.92 within 1-3 rounds (14/15), with punishment length 1 (s215), 3 (most), mean seat-1 price T+31..60 1.875 = a clean 3-round punishment. Control re_formed 15/15 is a cartel return to 1.92/1.92, the benchmark the plateau outcomes in leads 1-2 do not match.
