# Notes: Methods and Results (talking points behind paper/main.typ)

These are points to write from, not prose. Every number is tagged with its source in `docs/pi_review.md`: [a], [b1]–[b6], [c1]–[c5], [d], or [Add] for the addendum. Numbers were checked mechanically against that file (see the end of this file).

## Methods

### Market [Add]
- Logit Bertrand duopoly with a = 2, c = 1, mu = 0.25, beta = 100.
- Nash price p_N = 1.473, monopoly price p_M = 1.925.
- Collusion index CI = (p − p_N)/(p_M − p_N): 0 at Nash, 1 at monopoly. The cartel band is CI 0.9–1.1.

### Sellers [Add]
- All sellers are Qwen3-14B with thinking on (temperature 0.6, top_p 0.95), using the Fish et al. pricing prompt.
- Each seller keeps PLANS/INSIGHTS notes and sees a history table of the last 100 rounds.

### Planted base cartel [Add], [b1]
- Both incumbents get a manager's instruction:
  - price at 1.92;
  - if the rival's last price is below 1.70, price at 1.47 for 3 rounds, then return to 1.92;
  - a new punishment starts only after a round in which both priced ≥ 1.90.
- Why the cartel is planted: uninstructed Qwen3-14B does not form a cartel on its own (state it, cite the earlier kickoff).
- 150 base rounds; seeds 200–214 (P1) and 215–229 (P1b).
- Be upfront: all 30 bases are at 1.92/1.92 in every round, so there is one cartel state with 30 note variants, not 30 independent cartels [b1].

### Succession [Add]
- At T = 150, seat 1 is replaced by an uninstructed newcomer for 60 rounds. Seat 0 stays the instructed incumbent.
- At T+30, seat 0 is forced to p_N for one round. This is the shock that tests whether the newcomer enforces.

### Arms (what the newcomer inherits) [Add]
- control: no swap; seat 1 stays the instructed incumbent.
- same_none: nothing.
- same_history: the price/profit table.
- same_notes: the predecessor's notes.
- same_full: history plus notes.
- lookalike: seat 0 replaced by a scripted seller that never reacts.
- Model ladder, history or full: sib_* = Qwen3-8B (P2); oth_* = gpt-oss-20b (P3).
- P1c: the notes replaced by fixed templates (rule_return, rule_noreturn, status).

### Pre-registered outcomes [Add]
- `joins`: newcomer CI over T+20..29 in (0.5, 1.1].
- `enforces`: newcomer CI drop of at least 0.3 from T+27..29 to T+31..33.
- `re_formed`: market CI in band and `enforces`.

### Post-hoc outcomes [a], [b3]
- `clean_punish`: newcomer in band at T+27..29, no punishment under way, then ≤ 1.55 at T+31 or T+32.
- `back_at_cartel`: newcomer CI ≥ 0.9 in each of T+51..60.
- Low-spell length after the shock.
- Say why they were added: `re_formed` can't distinguish a punishment from a collapse [b3].

### Tests and sample [a]
- One-sided Fisher exact tests, plus McNemar for paired seeds.
- Every arm has 15 games, except sib_full with 14 (s212 aborted twice; not at random).

### Reproducibility [a]
- An independent recompute from raw logs matched every reported number.

## Results

### R1. Without the shock, every Qwen newcomer looks like a cartel member [Add], [a]
- Pre-shock (T+1..29), every Qwen newcomer arm except same_none averages about +1.0: same_history +1.03 / +0.97 (P1 / P1b), same_full +1.01 / +0.99, same_notes +0.98.
- Nothing inherited means overpricing, not competition:
  - same_none averages +1.42 over T+1..29;
  - it is overpriced in 6/15 games;
  - it joins in 5/15, vs 13/15 for same_history in P1 [a].
- Point to make: the history anchors the price level. Joining is cheap; `joins` is 28/30 for same_history pooled [d].

### R2. Only the notes transfer enforcement (headline) [a], [b4], [d]
- `re_formed`, pooled same_full vs same_history: 10/30 vs 1/30, p = .0028. P1b alone 4 vs 1, which meets the pre-registered rule.
- `re_formed`, same_notes vs same_history in P1b: 8/15 vs 1/15, p = .0071 (McNemar 7–0).
- Robustness:
  - on the cleaner `clean_punish` metric: 8/30 vs 1/30, p = .013; same_notes 6/15 vs 1/15 [d];
  - excluding pre-shock price wars: 10/30 vs 1/26, p = .006 [b4].
- Mechanism from transcripts:
  - all 13 note-arm cutters at T+31 cite the inherited rule; the single history-only cutter (s219) calls its cut a "test" [c1];
  - 7 newcomers cite the rule but don't punish [c2].
- Concede: the notes are a near-verbatim paraphrase of the manager's instruction. What transfers is a written rule the newcomer sometimes acts on [c1], [d].
- Caveat: the history contains no punishment events, so "history doesn't teach punishment" is true by design [b1].

### R3. Inherited enforcement is brittle: triggered, then undercut [b2], [b3], [Add]
- After the shock, note-arm newcomer CI falls: same_full +0.78 / +0.75 (P1 / P1b), same_notes +0.74, vs control +0.97 / +0.98 [Add].
- Note-arm games scored `re_formed` (n = 18): 4/18 `back_at_cartel`, mean newcomer CI +0.51 over T+34..60. Not `re_formed` (n = 27): 21/27 back, +0.92 [Add].
- Textbook punish-and-return (about 3 rounds at about 1.47, then back to about 1.92): 3 of 150 non-control games. About 6 return after a cut of any length. Control does the 3-round return in 23/30 [b3].
- Why they stay low: the incumbent's rule never answers a persistent undercut.
  - At 1.47 against 1.92 the newcomer earns 36.57 a round, vs 33.75 at the cartel price [b2].
  - In 8 games the newcomer stays below 1.70 for ≥ 20 of T+34..60 while the incumbent stays high [b2].
- Transcript to quote: in same_full s222 the newcomer cuts "per the plan" at T+31. By T+35 it writes "$1.47 yields significantly higher profit ($36.57)" and stays there to T+60 [c3].
- Supporting observations:
  - newcomers recast the punishment as a "test", e.g. rule_return s223, and "test" framing appears in 13/15 history-only notes too [c4];
  - note-holders blame themselves for the shock round: same_notes 8/15 vs same_history 0/15 [c5].
- Fig. 5 (new caption): "Triggered, then undercut."

### R4. A fixed rule template transfers less than real notes (P1c, pre-registered null) [a], [d]
- Primary tests:
  - `re_formed`, rule_return vs status: 3/15 vs 0/15, p = .112;
  - `back_at_cartel`, rule_return vs rule_noreturn: 8/15 vs 10/15, p = .868.
- The status arm behaves like history, as predicted.
- Descriptive, not pre-registered: rule_return vs same_notes on the same bases, 3/15 vs 8/15, p = .064 [d].
- The 7 P1c `re_formed` games: 0/7 `back_at_cartel` [b3].
- Point to make: a cleaner statement of the same rule did not help. Don't claim why (note persistence is speculative) [e].

### R5. Across models (descriptive only) [a], [Add], [b5]
- Qwen3-8B, the sibling:
  - joins from history alone: `joins` 15/15;
  - never enforces from history (0/15);
  - with full inheritance, `re_formed` 3/14.
- gpt-oss-20b, the other family, does not hold the price from history: `joins` 3/15.
  - It opens high (T+1 ≥ 2.00 in 11/15), then drifts just below the incumbent's 1.70 trigger and settles at 1.65–1.70 (median 1.66, CI ≈ 0.41). Only 5% of its prices are in band and 9% are below Nash [Add].
  - In 13/15 games the incumbent punishes before the shock (first cut at a median of T+5). It keeps restarting: a median of 3 punishments per game, 17% of its rounds below 1.70. 52 of its 61 punishments break its own rule, so this is not the b2 loophole. The incumbent LLM obeys the clause only sometimes [Add].
- Don't report P3 enforcement or `re_formed`; the shock metrics can't be read there [b5].
- Don't report the ladder p-values (≈ .10) [e].

### Limitations to state
- One planted cartel state; the history contains no punishments [b1].
- The incumbent's rule is exploitable after a cut [b2].
- `re_formed` mixes punishment with collapse [b3].
- 15 games per arm.
- The P2/P3 parser differs from P1's (3 retries vs 1), and gpt-oss ran with Qwen's sampling [b6].
- The discipline probe is left out (not recomputed; known confound) [e].

---
**Number check:** every numeric token in this file was matched against `docs/pi_review.md` by a script; tokens that appear only in this draft are listed in the session log.
