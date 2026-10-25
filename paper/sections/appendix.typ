#import "../lib.typ": *

// ---------- appendix ----------

#pagebreak()
#counter(heading).update(0)
#set heading(numbering: "A.1", supplement: [Appendix])
#counter(figure.where(kind: image)).update(0)
#counter(figure.where(kind: table)).update(0)
#set figure(numbering: n => "A" + str(n))
// Appendix figures stay where they are written, so none floats past the end of the appendix.
#set figure(placement: none)

= Design details <app:design>

== Arms and base sets <app:arms>

@tab:arms lists every arm in the study. The 30 bases form two sets of 15: Set A is seeds 200–214, and Set B, seeds 215–229, was run later as a pre-registered replication of Set A that also adds Notes. Each secondary experiment changes one thing the main experiment holds fixed: the incumbent (Look-alike), what the notes say (templates) or the newcomer's model.

#figure(
  text(size: 9pt, table(
    columns: 7,
    align: (left, left, left, left, left, left, right),
    toprule,
    [Arm], [Code], [Newcomer], [Inherits], [Incumbent], [Sets], [Games],
    midrule,
    table.cell(colspan: 7, text(style: "italic")[Main experiment]),
    [Control], [`control`], [–], [no swap], [instructed], [A + B], [30],
    [Blank], [`same_none`], [Qwen3-14B], [nothing], [instructed], [A], [15],
    [History], [`same_history`], [Qwen3-14B], [history], [instructed], [A + B], [30],
    [Notes], [`same_notes`], [Qwen3-14B], [notes], [instructed], [B], [15],
    [History + notes], [`same_full`], [Qwen3-14B], [history + notes], [instructed], [A + B], [30],
    midrule,
    table.cell(colspan: 7, text(style: "italic")[Secondary experiments (@app:secondary)]),
    [Look-alike], [`lookalike`], [Qwen3-14B], [history], [*scripted*], [A], [15],
    [Rule + return], [`notes_rule_return`], [Qwen3-14B], [*template:* rule + return], [instructed], [B], [15],
    [Rule, no return], [`notes_rule_noreturn`], [Qwen3-14B], [*template:* rule, no return], [instructed], [B], [15],
    [Status], [`notes_status`], [Qwen3-14B], [*template:* status], [instructed], [B], [15],
    [Qwen3-8B], [`sib_history`], [*Qwen3-8B*], [history], [instructed], [A], [15],
    [], [`sib_full`], [*Qwen3-8B*], [history + notes], [instructed], [A], [14],
    [gpt-oss-20b], [`oth_history`], [*gpt-oss-20b*], [history], [instructed], [A], [15],
    [], [`oth_full`], [*gpt-oss-20b*], [history + notes], [instructed], [A], [15],
    toprule,
  )),
  caption: [All arms. Bold marks what a secondary experiment changes relative to the main experiment. The scripted incumbent repeats its last price and never reacts. A newcomer that does not inherit the history sees only the rounds it plays itself; a template replaces the inherited notes. Qwen3-8B with history and notes has 14 games (@app:oth). Code names match the repository.],
) <tab:arms>

== Pilots behind the base cartel <app:pilots>

*No cartel forms on its own.* In short pilots (60 rounds, two seeds per mode), two uninstructed Qwen3-14B sellers did not collude. With thinking on they stayed near Nash (CI −0.19 to +0.12). With thinking off they froze at high prices (CI 1.55–1.86), above the monopoly price, and their prices stopped moving.

*How the rule was built.* Each part of the incumbents' rule comes from a pilot in which a simpler version failed (positive controls, 4–6 seeds each, with a forced cut at round 40):
- *Numbers, not words.* A verbal instruction ("keep prices high … if the competitor undercuts you, punish them") did not work. With thinking off the sellers froze near \$2.5–2.9, anchored on the prompt's \$2.89 maximum willingness to pay, and wrote about punishing without ever cutting their price. With thinking on they read "punish" as about \$1.05 and spiralled below Nash. Explicit prices with thinking on worked once combined with the next two changes, so every seller in the study runs with thinking on.
- *Start at the cartel.* Starting from a Nash warm-up put every game in punishment from round 1, because 1.47 is below the trigger. We start at 1.92/1.92 instead.
- *A forgiveness clause.* Without the last sentence of the rule, each seller read the other's punishment as a new trigger. Punishments chained, and only 1 of 6 games was back at the cartel by round 50. With the clause, the unshocked seller punished the forced cut for exactly 3 rounds in all 6 games, and both sellers were back at 1.92 by round 44.

== Base gate <app:gate>

Before any newcomer arrives, each base had to pass a pre-registered gate:
+ *Holds:* the market's mean CI over rounds 121–150 is in $(0.5, 1.1]$.
+ *Enforces:* in a side branch from round 150, seat 0 is shocked at round 151, and seat 1 punishes: its mean CI over rounds 152–154 is at least 0.3 below its mean over rounds 148–150. The main line, from which the arms branch, is never shocked.

All 30 bases passed both checks. The positive control described in @sec:arms passed on both sets of bases: Control is scored `re_formed` in 15/15 games on Set A and in 15/15 on Set B.

== Implementation and tools <app:tools>

We use no external dataset: every observation is generated by the simulation. The market and prompts come from the open implementation of #cite(<riemer2026>, form: "prose"). The succession code is ours: branching a game from a saved snapshot, swapping a seat, choosing what the newcomer inherits, and forcing prices.

All three models (Qwen3-14B, Qwen3-8B and gpt-oss-20b) are open-weights models at pinned revisions, which we serve with vLLM on Modal H100 GPUs. We render each chat template locally and send the exact prompt string. This choice serves three ends:
- every game can be re-run on the same weights and prompts;
- the reasoning trace of every call is visible, which the transcript analysis in @sec:results depends on;
- the whole sprint, pilots included, cost about \$62 of GPU time.

Every call is logged with its prompt, reasoning, notes and parsed price. The analysis uses Python, SciPy for the exact tests and matplotlib for the figures.

== Discipline probe (not interpreted) <app:probe>

The main experiment also pre-registered a discipline probe on Set A: a side branch at T+15 forced the newcomer to 1.60, below the incumbent's trigger, to test whether being punished brings a newcomer back into line. Its positive control passed: in Control, the forced instructed incumbent was punished and returned to the cartel price in 15/15 games. But newcomers read the forced price as their own profitable experiment, earning 40.54 a round at 1.60 against 33.75 at 1.92. Staying low after the probe therefore can't be separated from preferring the higher profit, and the probe was not independently recomputed. We do not interpret it.

= Additional results <app:results>

== Before the shock <app:preshock>

@fig:paths shows seat 1's price in every main-experiment game after the swap, and @tab:preshock gives the mean newcomer CI before the shock, by set. Before T+30 the arms with any inheritance look alike; Blank stands out by pricing above 1.1.

#fig("fig2_price_paths") <fig:paths>

#figure(
  table(
    columns: 3,
    align: (left, right, right),
    toprule,
    [Arm], [Set A], [Set B],
    midrule,
    [History], [+1.03], [+0.97],
    [History + notes], [+1.01], [+0.99],
    [Notes], [–], [+0.98],
    toprule,
  ),
  caption: [Mean newcomer CI over T+1..T+29. Notes ran only on Set B.],
) <tab:preshock>

== After the shock <app:after>

Post-shock newcomer CI is +0.78 (Set A) and +0.75 (Set B) for History + notes, and +0.74 for Notes, against +0.97 and +0.98 for the instructed incumbent in Control. About 6 of the 150 Qwen3-14B newcomer games come back after a cut of any length.

Two habits help the slide from punishment to undercutting:
- Newcomers recast the inherited punishment as a price experiment. In s223 (Rule + return template, @app:templates) the template's punishment becomes "a 3-round \$1.47 test to reset market dynamics". "Test" framing is Qwen's default, though: it appears in 13/15 history-only notes too.
- Note-holders read the forced shock as a trigger they missed. At T+31, 8/15 Notes newcomers say they "failed to" or "should have" responded to round 180, against 0/15 history-only newcomers.

= Secondary experiments <app:secondary>

== A non-reacting incumbent (Look-alike) <app:lookalike>

Does the newcomer's behaviour depend on an incumbent that reacts? In Look-alike, seat 0 is replaced by a scripted seller that repeats its last price, and the newcomer inherits the history. The newcomer prices like a History newcomer: it joins in 13/15 games, as History does on Set A, and never enforces (@fig:lookalike). By the pre-registered reading of this arm, a newcomer that prices as high against a non-reacting seller as against the real incumbent is anchoring on the price table, not responding to enforcement.

#fig("fig8_lookalike") <fig:lookalike>

== Fixed note templates <app:templates>

This experiment (pre-registered, on Set B) asks whether the wording of the rule matters, by replacing the inherited notes with fixed templates. Both pre-registered predictions failed (@fig:p1c). The rule with its return clause was scored `re_formed` in 3/15 games, against 0/15 for a status line ($p = .112$). The return clause did not raise `back_at_cartel`: 8/15 with it, 10/15 without ($p = .868$). The status template behaved like history alone, as predicted. Descriptively, the template transferred less enforcement than the real notes on the same bases: 3/15 vs 8/15 for Notes ($p = .064$†). None of the 7 template games scored `re_formed` is at the cartel price at the end (0/7 `back_at_cartel`). We do not claim to know why a cleaner statement of the same rule did not help. Changing the text an LLM pricing agent reads often has only partial effects. Elsewhere, a prompt-only antitrust warning reduced supracompetitive pricing without eliminating it @garra2026.

#fig("fig6_p1c") <fig:p1c>

== Other newcomer models <app:oth>

On Set A we also replaced seat 1 with a smaller model from the same family (Qwen3-8B) and a model from another family (gpt-oss-20b), each inheriting the history, or the history and notes (@fig:models). We report these descriptively: the history + notes vs history tests give $p approx .10$ at this sample size. Qwen3-8B with history and notes has 14 games, because one base (seed 212) aborted on unparseable output in both attempts, so it is not missing at random. These runs also used a more permissive parser (3 retries vs 1), and gpt-oss ran with Qwen's sampling settings.

The Qwen3-8B sibling joins from history alone (`joins` 15/15) and never enforces from it (0/15). With history and notes it is scored `re_formed` in 3/14 games.

#fig("fig4_models") <fig:models>

gpt-oss-20b does not hold the cartel price from history (`joins` 3/15). @fig:oth shows where it goes:
- It opens high, at 2.00 or more at T+1 in 11/15 games.
- Within a few rounds it drifts below the incumbent's 1.70 trigger, and it settles at 1.65–1.70, neither the cartel price nor Nash. Its median price is 1.66 (CI about 0.41); 5% of its prices are at the cartel price (CI 0.9–1.1) and 9% below Nash.
- The instructed incumbent starts punishing before the shock in 13/15 games, with the first cut at a median of T+5. It then keeps restarting, with a median of 3 punishments per game and 17% of its rounds below 1.70.
- 52 of the incumbent's 61 punishments break its own "ignore" clause. The incumbent LLM obeys that clause in some games and not others.

Because these games are already price wars before T+30, we do not interpret the shock outcomes for gpt-oss-20b.

#fig("fig7_oth_history") <fig:oth>
