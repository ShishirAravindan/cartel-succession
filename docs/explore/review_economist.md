# Skeptical IO review: "Cartel Re-forms" (P1, P1b, P2/P3)

Reviewer stance: IO economist, algorithmic collusion (Calvano et al. 2020; Fish et al. 2024). Based on plan.md,
status.md, p1b_analysis.md, p1.md and status_p23.md only. I have not run anything. Probabilities I quote
(Fisher/McNemar) are my own hand calculations from the posted counts, so recompute them before citing.

## 1. What the project claims

A planted, instructed two-seller LLM cartel (Qwen3-14B, logit Bertrand, flat 1.92 for 150 rounds) is entered by an
uninstructed newcomer. Newcomers that inherit the outgoing seller's price table keep the cartel price (about 28/30
join) but almost never punish a one-round forced cut by the incumbent (1/30 `re_formed`). Newcomers that inherit the
outgoing seller's PLANS/INSIGHTS notes punish in about a third of seeds (10/30 pooled, Fisher p = 0.0028), and notes
alone do at least as well (8/15). The headline is "the notes carry enforcement", and a secondary claim is that this
partly transfers across model families.

## 2. The five strongest objections, ranked

### O1. The price history contains no information about enforcement, so the key contrast is "written rule vs nothing", not "history vs notes"
- **Objection.** The main line is never shocked (plan §2). The base is 150 rounds at 1.92/1.92 in every seed
  (`cartel_ci` = +0.989 in all 30 base seeds, p1.md and status.md). `same_history` newcomers are handed a table with
  zero deviations and zero punishments. They cannot learn that cuts get punished, because no cut ever happened in the
  data they see. The same goes for the notes at T. They were written by an instructed seller who never observed a
  deviation, so they are a restatement of the system-prompt rule ("punish below 1.70", sometimes "1.47 for 3 rounds").
  `same_full` therefore tests whether a *copy of the planted instruction text* survives in a memory channel. It does
  not test whether a norm or an enforcement capacity is inherited.
- **Why it matters.** The plan §1 question ("does it need the cartel's price history, or the outgoing seller's notes")
  suggests two parallel information sources. In fact one is informationless about punishment by construction. The
  right headline is "instruction leakage through self-written memory". That is interesting, but it is not "cartel
  succession".
- **Where.** `seat_swap/results/p1.md` "Prices per round" (all 1.92 for the incumbent in the main line); plan §2 (main
  line never shocked); the P1b notes excerpt (s215: "No punishment triggered… Maintain strategy unless competitor
  price drops below $1.70") in p1b_analysis.md; control re_formed 30/30 (instruction in the system prompt) as the
  upper bound.
- **Cheapest fix.** One sentence in the abstract, plus a line in the plan §9 disclosures: "the table the
  `same_history` newcomer sees contains no deviation or punishment episode." Optional but the single most valuable
  extra arm: `same_history_shocked`, with the table taken from an enforcement side branch that already exists (the
  150+10 rounds contain a forced cut and the incumbents' reaction). I would run that only if you have budget.

### O2. "P1b replicates P1" is overstated. P1b alone is not significant, and the pooled test includes the hypothesis-generating sample
- **Objection.** P1b alone: `same_full` 4/15 vs `same_history` 1/15. One-sided Fisher is about 0.17 by my
  calculation. The pooled p = 0.0028 is driven by P1's 6 vs 0, and P1 is the sample that generated the hypothesis.
  The pre-registered rule is satisfied (pooled p < 0.05 and `same_full` > `same_history` in P1b), but a skeptic reads
  the replication as directionally consistent and underpowered. The effect also shrank: 6/15 (40%) in P1, 4/15 (27%)
  in P1b. On top of that, the 10 includes artefacts. P1 s205 is a metric artefact (pre-window price of 2.25 inflates
  the baseline; status.md §5.1). P1 s204 and P1b s222/s225 are partial drops that stick, which is drift or price
  shaving rather than punishment. P1b s219 `same_full` is 1.47 once and then 1.70. Clean punish-and-restore in
  `same_full` is roughly 7/30 (P1: 202, 203, 209, 212; P1b: 217, 222, 223), not 10/30.
- **Why it matters.** The paper's one test statistic carries the main claim. Reporting it alone invites a "forking
  paths / hypothesis-generating sample" objection, and the cleaned count is lower.
- **Where.** p1b_analysis.md "Per arm" and "Headline rule"; status.md §5.1 table of the six P1 enforcers; the P1b
  `same_full` seed table (s219, s222, s225, s228).
- **Cheapest fix (analysis only).**
  1. Report P1b-alone Fisher beside the pooled one.
  2. Use the paired structure: all arms share the base seed, so use exact McNemar (discordant pairs). Pooled it looks
     like about 9 vs 0 discordant, p about 0.004. That is a better, honest test.
  3. Re-run the contrast with a stricter pre-declared-as-robustness definition: "newcomer at or below 1.60 for at
     least 2 of T+31..T+34 and back at or above 1.90 by T+40". If it holds at about 7/30 vs 1/30, p is still about
     0.03, and you can say so.
  4. Note that the cleanest replicated contrast is `same_notes` vs `same_history` in P1b alone: 8/15 vs 1/15, about
     p = 0.007. It was secondary/descriptive, and it is confounded with removing the table (see §3, A4).

### O3. Construct validity of "enforces": a one-round dip passes, and "retaliation" is indistinguishable from lagged best response or trigger-shaving
- **Objection.** `retaliation` is the mean of three rounds, so it takes values in multiples of 0.332. The threshold
  −0.3 is passed by a single round at p_N (e.g. P1 s203, 1.50 for one round, then straight back). A myopic agent that
  best-responds to the *last observed* rival price (1.47 → BR close to 1.47) produces exactly this. The `br_gap` of
  +0.58 shows that 1.92 is far above the one-shot best reply, so any agent that attends to the rival's last price will
  undercut. The P1b note excerpt (s215 `same_notes`) is the telling case: "Test $1.89 … to counteract the competitor's
  $1.47 price and restore sales volume". That is volume-driven reaction, not rule enforcement. Second, the incumbent's
  rule is exploitable: any price at or above 1.70 is not punished. The "partial, sticky" drops at 1.70 (P1 s204,
  P1b same_notes s222) and gpt-oss settling "just under 1.70" (status_p23.md) are what a profit-maximiser who has found
  the trigger would do. That is deviation to the threshold, not enforcement of the cartel. Third, no arm demonstrates
  *deterrence*: the incumbent never has a chance to deviate in the arms except by force, so nothing shows the threat
  sustains the price.
- **Why it matters.** Calvano-style collusion evidence is reward-punishment: a cut, a drop, then return to the high
  price. "Dip then restore" is the signature to count. "Dip and stay" is a price war.
- **Where.** Newcomer price paths T+27..T+60 in `seat_swap/results/p1b_prices.csv` (and P1's prices). Note that
  `same_history` newcomers also suffer the sales loss at T+30 and mostly do not react (retaliation 0.000 in 13/15), so
  the *notes* raise reactivity. That part is a genuine finding (see §3, A2).
- **Cheapest fix.** Classify every arm-seed's T+31..T+45 path into four bins: no response; punish-and-restore (at or
  below 1.60 for at least 2 rounds, then at or above 1.90 within 5 rounds); sticky undercut (settles 1.60 to 1.89);
  war (incumbent also stays low). Report counts per arm. Also report post-shock `ci` over T+40..T+60 per arm: if
  "enforcers" end with a *lower* late CI than non-enforcers, then "enforcement" is destabilising.

### O4. The cartel price survives without enforcement and without discipline, so "sustain" is not shown; the P1 probe says the opposite of discipline
- **Objection.** Market CI is about 0.99 in every arm regardless of enforcement (`ci_late`, `joins` 28/30 for
  `same_history`, 0 enforcers). So replacement does not break the price; it removes the enforcement capacity silently.
  The P1 `lookalike` arm (scripted seller that never reacts) joins 13/15 versus 13/15 in `same_history` and has mean
  `newcomer_ci` +1.02 vs +0.96. By the plan's own kill table (§7) this reads "the high price is anchoring on the table,
  not a response to enforcement." Next, the discipline probe: the incumbent punished the forced cut in 15/15 and the
  newcomer returned to the cartel price in only 3 of 15 `same_history` (12 never) and 0 of 15 `same_full`, versus 13
  never in `lookalike` (no punishment at all). By the §7 table, "the newcomer returns equally in `lookalike`" =
  stickiness, not discipline. The incumbent's punishment does not discipline the uninstructed newcomer; only the
  instructed `control` returns (15/15). The probe was dropped from P1b, and the P1 probe result is not in status.md's
  headline.
- **Why it matters.** Question 1 asks whether the newcomer "helps sustain it". On the data, newcomers hold a price
  that nobody is threatening, and are not brought back by threats. "Re-forms" is an accurate word for the price,
  not for the enforcement.
- **Where.** p1.md "Per arm" (disciplined 4/15, 2/15, 0/15 vs 15/15) and the "Established branches" table
  (`probe_return`); the seed-200 probe price lines (same_history 1.60 → 1.65 stuck, `lookalike` 1.70 stuck, which look
  the same).
- **Cheapest fix.** Separate the two outcomes in the write-up: "price persistence" (robust, 28 to 30/30) and
  "enforcement transfer" (partial, 25 to 50% depending on arm). Put the probe result back in the headline as a
  negative.

### O5. Effective sample, planting and external validity
- **Objection.** All 15 base games are identical in trajectory (flat 1.92, `cartel_ci` +0.989 in every seed), so
  seeds vary only the note wording and the newcomer's sampling. That is 15 draws of noise from one prompt, one model,
  one environment and one rule text. The result does not generalise to "LLM agents" or "algorithmic collusion" without
  qualification. The cartel is instructed, the shock is forced, and `lookalike` is scripted (all disclosed in §9).
  The P2/P3 ladder is not significant (one-sided p 0.10 and 0.11), the 8B echoes the template (format failures all
  in `sib_full`), and half of the gpt-oss "enforcements" are in a price war (status_p23.md). It should not be a
  headline. Also, the notes-features regex table (1.47 and duration, 13/18 vs 11/27) is exploratory, was corrected
  after a first look (hyphenated "3-round"), and measures the notes *at T*, not at the shock.
- **Why it matters.** A judge will discount any statement that reads as "LLM cartels transmit norms", and will notice
  that the base gate of 15/15 with an identical trajectory is trivially passed.
- **Where.** p1.md Base table; plan §9; status_p23.md ladder; p1b_analysis.md notes table.
- **Cheapest fix.** Put "one model, one planted rule, one environment" in the first paragraph. Move P2/P3 to "exploratory,
  not significant". Re-compute the notes regex on notes at T+29 (the text the newcomer actually has when the shock
  lands), not T.

## 3. Alternative explanations for "the notes carry enforcement" that the data does not yet rule out

| # | Alternative | Why it fits | The check that would separate it |
|---|---|---|---|
| A1 | **Instruction leakage / rule-text copying** (not a norm). The notes are a verbatim restatement of the planted rule, which the newcomer then executes. | Main line never shocked, so notes cannot contain learned enforcement. Newcomers copy notes verbatim, even stale round numbers (s215). Enforcers' notes more often contain "1.47" and a duration. | Sort by notes at T+29: among notes that state the full script (1.47, duration), what share enforce? From the table it is only about 14 notes in `same_full` with 1.47, 6 enforcing, so compliance with an explicit script is ~half. Say that it is lossy transmission. |
| A2 | **Vigilance priming.** The notes include a "watch the rival below 1.70" clause. That makes any newcomer react to the rival's price, in either direction. `same_history` newcomers write fresh notes with no such clause and ignore the cut (13/15 retaliation 0). | Direction of reaction varies (sticky drops, undercut, "restore volume"). | Bin paths as in O3. If reaction is punish-and-restore, it is a rule. If it is undercut-and-stay, it is vigilance plus myopic profit seeking. Read the T+31 reasoning traces for "punish / retaliate / rule" vs "regain share / volume". |
| A3 | **Pain-driven myopic response** to the sales loss at T+30. | The cut costs the newcomer volume; a 1.47 match is the lagged BR. | Same traces; also compare to `same_history`, which has the same pain but does not respond. That partly rules A3 out as the whole story. |
| A4 | **Table dilution / attention.** 150 rows of "1.92 forever" in the prompt push out the notes and tell the model nothing ever happens. `same_notes` (8/15) > `same_full` (4/15) in P1b fits this. | Context length and recency differ across arms. | Compare `same_full` vs `same_notes` pooled; look at prompt token counts; a `same_full` with a truncated table (last 20 rows) would settle it. Do not claim "the notes alone do at least as well" as support for "notes carry enforcement" if the table is hurting; say it is a different mechanism. |
| A5 | **Identity continuity.** The newcomer in `same_notes` is the same model with the same notes, minus only the system-prompt instruction. It is the incumbent's state with a different system prompt. | Verbatim note copying at T+1. | Then control (30/30) minus `same_notes` (about 50%) measures the system prompt's marginal value over memory, which is a more interesting number. |
| A6 | **Trigger shaving.** "Partial / sticky" 1.60 to 1.70 drops are exploitation of the 1.70 threshold (see O3). | Incumbent rule only punishes below 1.70; s222, s204, s225. | Count them as deviations, not enforcement; report headline with and without. |
| A7 | **Anchoring on the product-text maximum.** `same_history` s200 starts at 2.89, then falls to 1.92 as it sees the rival at 1.92. The join is price-matching of a visible rival. | `lookalike` joins equally (13/15). | Already evidenced by the kill table; state it. |

## 4. What is genuinely interesting and may be underplayed

1. **Price and enforcement dissociate at turnover.** Prices stay at 0.99 of the collusive level while enforcement
   capacity vanishes (`same_history`: 28/30 join, 1/30 enforce). Price-monitoring (the usual antitrust screen) cannot
   see this; only a perturbation reveals it. That is a real, clean message: a replaced seller keeps the price and
   loses the threat.
2. **Notes as institutional memory that transmits a rule at partial fidelity.** Rule text written by the agent into
   its own notes survives a change of "seller" about a third to a half of the time, and it is verbatim-copied. It is
   lossy and idiosyncratic (some notes drop the 1.47 and duration). This is a concrete mechanism for "collusion
   outlives its authors" in LLM-agent markets.
3. **More information can hurt.** `same_notes` (no table) enforces at least as often as `same_full` (table + notes).
   Worth a sentence and the A4 check.
4. **Punishment does not discipline an uninformed follower.** In P1 the incumbent punishes a forced cut in 15/15 and
   the newcomer does not come back (12/15 never), exactly as for the non-reactive `lookalike`. Punishment works as a
   *convention* shared by agents who know the rule (control: 15/15 return), not as an incentive on a naive agent. That
   is a nice, Calvano-flavoured point (threats need to be understood to bind), and it is currently buried.
5. **The planted rule has a seam.** The "unpunished at or above 1.70" threshold is an attractor for uninstructed
   agents (gpt-oss settles just under it; sticky 1.70s). It suggests focal-threshold exploitation as a failure mode of
   rule-based cartels.
6. **Honest reporting.** The team already audits its own enforcers (real vs artefact vs drift) and corrects its
   regex; that is a strength and should be foregrounded.

## 5. Verdict

**Survives as written.**
- Replacement by an LLM newcomer that sees the price table and the rival at 1.92 keeps the price at about the
  collusive level (28/30 `joins`, mean CI about 0.95), and it does so about as well as a scripted non-reactive seller.
- With only the table, the newcomer essentially never punishes a one-round forced cut (1/30).
- `control` works (30/30) so the shock design is readable.
- By the pre-registered rule the headline passes (pooled one-sided p = 0.0028, higher in P1b).

**Change the wording.**
- "The notes carry enforcement" -> "inherited notes that restate the planted punishment rule raise the share of
  newcomers that respond to a rival cut with a drop to the punishment price from about 0 to about 25 to 40%
  (`same_full` 10/30, `same_notes` 8/15 vs `same_history` 1/30); about two thirds of notes that contain the full rule
  are not followed."
- "Replicates" -> "replicates in direction; P1b alone is 4/15 vs 1/15, not significant by itself; pooled test includes
  the hypothesis-generating sample; the cleanest P1b contrast is notes-only vs history, 8/15 vs 1/15."
- "Re-forms" / "sustain the cartel" -> "keeps the cartel price" for `joins`, and "executes the written punishment
  rule" for `enforces`. Do not say "helps sustain" without O4's deterrence caveat.
- Say prominently: the table contains no deviation or punishment episode; the cartel and the rule are planted;
  one model, one environment; the P2/P3 ladder is exploratory (p about 0.10).
- Report the clean-punishment count (about 7/30 `same_full`) and the post-shock CI by arm beside the pre-registered
  count, and put the P1 discipline probe (negative) in the headline.

**Priority order given limited time.** All of these are analysis on existing CSVs: (1) path-classification and
clean-enforcement count (O3); (2) P1b-alone, McNemar, strict-definition tests (O2); (3) notes regex at T+29 (O5/A1);
(4) post-shock CI by arm (O3/O4); (5) rewrite headline sentences (O1, §5). Only if budget allows, `same_history_shocked`
and a truncated-table `same_full` are the two arms that would actually move a skeptic.
