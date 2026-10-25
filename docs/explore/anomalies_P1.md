# Anomaly leads, P1 sample (75 games, seeds 200-214)

Source: seat_swap/results/explore/series.md, "## P1 " games only. Arms present: control, same_history, same_none, same_full, lookalike (no same_notes in P1). Round numbers are T+k (position k in the file's lists; the shock is position 30). CI = (p - 1.47)/(1.925 - 1.47); CI 0.5 is p = 1.6975, CI 1.1 is p = 1.9725. "Late CI" = CI of the mean newcomer price over T+34..T+60, computed by me. Leads are exploratory, not tests.

## Solid patterns

### 1. "re_formed yes" in same_full mostly means a degraded or collapsed market, not a restored cartel
- Claim: in same_full the 6 re_formed games almost never return to the cartel after the shock; control's 15 re_formed games all do.
- Evidence (late CI T+34..60): same_full s202 0.58 (newcomer 1.75 from T+36 to the end), s203 0.19, s204 0.48 (1.70 from T+37), s209 0.00, s212 0.48, s205 1.02 (but see lead 3). Control: 0.88-0.99 in all 15 (s206 0.88 is the lowest; s200/s205/s209 0.95).
- Count: 5 of 6 same_full re_formed games (s202, s203, s204, s209, s212).
- Why it matters: re_formed counts a one-to-three-round dip as enforcement and ignores what the market does afterwards. A reader would take "re_formed" as "cartel survives succession", but the newcomer's punishment often leaves a lasting lower price or a war.
- Check next: add a post-shock recovery metric (CI over T+40..60 vs pre) and cross-tabulate with re_formed; list these 5 games with their incumbent paths.

### 2. Absorbing price war in one game, labelled re_formed
- Claim: same_full s209 locks into Nash for the rest of the game after the shock.
- Evidence: newcomer T+31..T+60 is 1.48 1.60 1.48 1.47 ... 1.47 (min 1.46, 30 rounds below 1.70); incumbent 1.92 at T+31 then 1.47 for T+32..T+60 (29 rounds). Labelled joins yes, enforces yes, re_formed yes, retaliation -0.88.
- Count: 1 of 75. The same echo shape is transient elsewhere: control s205 (incumbent 1.47 at T+33..35), s206 (T+36..37), s211 (T+32..36, five rounds), s212 (T+32..34), s214 (T+34..35), same_full s202 (T+32..34) and s204 (T+32..34). So in 5 of 15 control games the incumbent counter-punishes the newcomer's enforcement, and the echo is not always damped.
- Why it matters: enforcement triggers the incumbent's own punish rule (a 1.47 cut is below 1.70), so enforce and incumbent-punish chain. Whether the chain ends depends on luck; s209 never forgives. This is the mechanism for lead 1.
- Check next: read s209 reasoning and the incumbent's forgiveness condition; count echo lengths across all arms (P1b too).

### 3. Enforces/re_formed produced by windows, not by punishment
- Claim: some enforces=yes labels come from a spike in the pre-window or a level shift, not from a cut at T+31..33.
- Evidence: same_full s205: newcomer 2.00 1.92 2.25 at T+27..29, then 1.92 throughout T+31..33 and the rest; drop -0.30, exactly at the threshold; no round below 1.70. Labelled re_formed yes. same_none s201: newcomer 2.49 until T+30, then 2.25 from T+31 to T+60 (a one-step concession, still far above 1.92), drop -0.53, labelled enforces yes with overpriced yes. control s204: newcomer 1.47 for one round only, then 1.92; drop -0.33, borderline against -0.3 (rule says 3 rounds). same_full s203: a single-round 1.50 at T+31 then 1.92 for four rounds; drop -0.31.
- Count: 4 games (s205, s201, s204-control, s203 partly).
- Why it matters: regression-to-the-mean and thresholds at the edge create enforcement counts; the tally of enforcers in same_full (6) is inflated by at least 1-2.
- Check next: recompute enforces with a requirement of at least one round below 1.70 in T+31..33, and with a pre-window cap.

### 4. The incumbent's punishing is inconsistent with its stated rule (both directions)
- Claim: the incumbent punishes undercuts it should tolerate and tolerates undercuts it should punish.
- Not punishing when triggered: same_full s203 newcomer 1.50 for 23 rounds (T+38..60), incumbent 1.92 throughout, 0 punishments; same_full s212 newcomer 1.47 from T+47 to T+60, incumbent punishes T+48..50 only, then 1.92 for T+51..60; same_history s206 newcomer 1.55 for T+25..30 and 1.65 for roughly T+37..T+52, incumbent punished only 5 of 34 sub-1.70 rounds; same_none s200/s209/s210/s212 newcomer below 1.70 for 40-52 rounds, incumbent punished 10-11 times each (about 20-25%). Control: after the newcomer's 1.47 enforcement only 5 of 15 incumbents answer.
- Punishing when not triggered: same_history s206 newcomer 1.82 at T+21, incumbent 1.47 at T+22..24; same_history s212 newcomer 1.80/1.85 at T+41..43, incumbent 1.47 at T+42..44; same_none s203 newcomer 1.88 then 1.77, incumbent 1.47 at T+54..56 and T+58..60; same_full s204 newcomer 1.70 at T+31, incumbent 1.47 at T+32..34 (1.70 is not "below 1.70"). Yet same_history s213 (1.82 for 25 rounds), same_none s202 (1.75-1.80 for 26 rounds) and same_full s204 (1.70 for T+37..60) go unpunished.
- Punishment shorter than 3: same_none s212 single-round 1.47 at T+38, T+43, T+50; s200 T+51. Longer: control s211 five rounds.
- Why it matters: the "incumbent punishes below 1.70" premise does not hold uniformly; the incumbent's tolerance is what lets partial and low steady states persist, and it affects whether newcomer behaviour is deterred or just unobserved.
- Check next: round-level table of newcomer price at t vs incumbent price at t+1 across all arms (incl. P1b); read incumbent reasoning at s206 T+22 and s203 (same_full) T+40.

### 5. Newcomers settle in the 1.59-1.75 band, right around the trigger and the joins edge
- Claim: steady states cluster at 1.69/1.70 and nearby, which sits on both the incumbent's trigger and the CI 0.5 edge of "joins".
- Evidence: same_none s200 and s212 sit at 1.69 (CI 0.48, joins no) for 41 and about 35 rounds; s210 1.64 and 1.50 (joins no); s209 1.59; same_history s206 1.65 for about 18 rounds; same_full s204 1.70 for T+37..60 (CI 0.505, inside the band by 0.005); same_full s202 1.75. 1.69 vs 1.70 flips joins.
- Count: about 7 games.
- Why it matters: a one-tick difference changes the joins label and the incumbent's trigger; a descent in steps of 0.10 (s200: 1.99 1.89 1.89 1.79 1.69; s212: ... 1.79 1.69 1.59 1.69) suggests the newcomers learn the trigger by being punished (s200 punished at T+18..20 while at 1.79-1.69) and stop just short of it.
- Check next: for the same_none games, look at whether the price ladder stops after the first incumbent punishment; check whether 1.69/1.70 is mentioned in newcomer reasoning.

### 6. Same-looking trajectories: seeds are far from independent draws
- Claim: effective sample size is much lower than 15 per arm.
- Evidence: control s201, s202, s203, s207, s208, s212, s213 (and s214 up to T+33) have the identical newcomer path (1.92 x30, 1.47 x3, 1.92 ...); same_none s209 and s210 share the first six prices 2.89 2.64 2.39 2.14 1.89 1.64; 8 of 15 same_none openers start at 2.89 and descend by 0.25 or 0.30; same_none s202, s203, s213 open 1.95 2.00 1.9x; lookalike s200, s202, s205, s214 open 2.00 1.95 1.92; 2.89 recurs (same_history openers s200, s203, s207, s211, s214).
- Why it matters: counts like 12/15 are close to 1-3 independent behaviours; CIs on rates may be overstated; low-temperature sampling would explain the repeated 2.89 (probably the price cap).
- Check next: sampling temperature and seed handling; count distinct paths per arm.

## Weaker patterns and one-offs

### 7. Window labels flipped by a few spike rounds (joins/overpriced fragility)
- Evidence: lookalike s203 (2.25 x3 at T+20..22; CI 1.21, labelled joins no, overpriced yes), lookalike s212 (2.49 at T+25, 2.19 at T+28; CI 1.17), same_history s212 (2.15 x3 plus 2.00; CI 1.16). Otherwise those newcomers are at 1.92. Two 2.25 spikes in the 10-round window is enough to cross 1.1.
- Count: 3 games. Check next: re-score with a median or trimmed mean to see how many labels change. Also lookalike s203 raises to 2.10 for T+32..35 after the shock (retaliation +0.27).

### 8. Newcomers do not undercut a non-reacting seller, so "joins" looks like anchoring, not deterrence
- Evidence: lookalike (scripted incumbent never reacts): 13 of 15 newcomers stay at 1.92 for 30 post-shock rounds; only s201 (1.87 from T+22) and s208 (1.85 from T+32) undercut a little. Same_history is almost identical to lookalike (11 of 15 sit at 1.92 throughout; no enforcement, drop 0.00 in 14 of 15).
- Why it matters: joins in same_history and lookalike are the same behaviour; the lookalike arm shows the cartel price is held without any threat, so joins alone cannot demonstrate a punishment-backed norm.
- Check next: compare joins rate lookalike vs same_history; read lookalike s208 reasoning at T+32.

### 9. Slow erosion and late spikes after T+33, invisible to the windows
- Evidence: same_history s213 drops 1.92 to 1.82 at T+36 and stays 25 rounds (joins yes); same_history s212 1.80 from T+44; same_none s202 gradual 1.95 -> 1.90 -> 1.85 -> 1.80 -> 1.75 (T+31..T+43); same_none s203 1.92 -> 1.88 (T+37) -> 1.77 (T+57); lookalike s201 5.00 at T+38 (one round, outlier). Upward: same_history s205 prices 2.89 at T+46, T+51..55, T+57 (late CI 1.54), s202 2.50 at T+47 and 2.89 at T+52.
- Count: about 8 games. Check next: add a "late drift" flag (late CI vs window CI differing by more than 0.2): same_history s205, s212, s213, same_none s202/s203, same_full s203/s212.

### 10. Pre-shock and floor effects
- Evidence: same_none s209 and s212 newcomer drops to 1.49/1.47 right at T+31 (matching the shock price), but the pre-window CI is only 0.26-0.48, so the drop (-0.24, -0.15) cannot reach -0.3; the enforces metric has a floor problem for newcomers already near Nash. In s200 the incumbent is at 1.47 at T+29 and T+31 already, and in s209 at T+30..33, so the forced shock is not a clean single-round event in these games (also same_none s210 incumbent punished at T+23..24). same_history s206 also has the incumbent already punishing before the shock (T+22..24).
- Check next: flag games where the incumbent is already at 1.47 within T+27..33 before scoring enforces; same_none arm has 4 such games (s200, s209, s210, s212).
