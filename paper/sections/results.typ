#import "../lib.typ": *

= Results <sec:results>

== Before the shock, every newcomer looks like a cartel member <sec:join>

Up to the shock the arms are almost indistinguishable (@fig:paths): over T+1..T+29 the mean newcomer CI is between +0.97 and +1.03 for History, Notes and History + notes (@tab:preshock). The exception is the newcomer that inherits nothing. It does not compete; it overprices, at a mean CI of +1.42, lands above the band in 6/15 games, and joins in only 5/15, against 13/15 for history-only newcomers on the same 15 bases. Across all 30 bases, history-only newcomers join in 28/30 games. The price history is enough to anchor a newcomer at the cartel price: joining, on this evidence, is cheap.

#fig("fig2_price_paths") <fig:paths>

== Only the notes transfer enforcement <sec:notes>

Enforcement is where the arms separate (@fig:outcomes). On the pre-registered outcome, History + notes newcomers re-form the cartel in 10/30 games, against 1/30 for History ($p = .0028$). The pre-registered replication holds: the last 15 bases alone give 4 vs 1. Notes alone give 8/15 against 1/15 for History on the same 15 bases ($p = .0071$; paired McNemar 7–0). The result survives the cleaner post-hoc metric: on `clean_punish`, History + notes leads 8/30 vs 1/30 ($p = .013$), and Notes leads 6/15 vs 1/15. It also survives dropping games in which the incumbent was already punishing before the shock: 10/30 vs 1/26 ($p = .006$).

#fig("fig3_outcomes") <fig:outcomes>

The transcripts show where the enforcement comes from. All 13 newcomers with notes who cut at T+31 cite the punishment rule in their inherited notes; the single history-only newcomer who cut (s219) called it "a controlled price test". In s218 (Notes) the notes read "below 1.70 following a mutual ≥1.90 round … 3-round punishment at 1.47", and the newcomer cuts at T+31 and returns at T+34 "after the 3-round punishment". Citing the rule does not guarantee acting on it: 7 newcomers cite it at T+31 and still hold the price. What transfers, then, is a written rule that the newcomer sometimes carries out. The history-only result needs care: the inherited table contains no punishment events, so it shows that a history without punishments doesn't teach punishment, not that price histories can't carry enforcement.

== Inherited enforcement is brittle: triggered, then undercut <sec:brittle>

Newcomers that punish mostly do not come back (@fig:shock). Of the 18 notes-arm games scored `re_formed`, only 4 are at the cartel price in T+51..T+60. Their mean newcomer CI over T+34..T+60 is +0.51, against +0.92 for the 27 notes-arm games not scored `re_formed`. Across all 150 Qwen3-14B newcomer games, appendix experiments included, only 3 show the textbook pattern of about 3 rounds near 1.47 and then a return to about 1.92; the control incumbent makes that return in 23 of 30.

#fig("fig5_after_shock") <fig:shock>

Part of the reason lies in the incumbent's rule. As written, it never answers a newcomer that stays low, because a new punishment needs a round in which both priced at 1.90 or more first. Against an incumbent at 1.92, a newcomer at 1.47 earns 36.57 a round, against 33.75 at the cartel price. In 8 games the newcomer stays below 1.70 for at least 20 of T+34..T+60 while the incumbent stays high. In s222 (History + notes) the newcomer cuts "per the plan" at T+31; by T+35 it writes that "\$1.47 yields significantly higher profit (\$36.57)", and it stays there through T+60. Two habits in the transcripts help the slide (@app:after).

#place.flush()
#metadata(none) <budget-end>
