#import "../lib.typ": *

= Results <sec:results>

== Any inheritance keeps the price <sec:join>

Before the shock, every newcomer that inherits anything holds the cartel price (@fig:outcomes a; per-game paths in @fig:paths). History newcomers join in 28/30 games, History + notes newcomers in 30/30, and Notes newcomers, which see no price history, in 14/15. Over T+1..T+29 their mean CI is between +0.97 and +1.03 in every one of these arms (@tab:preshock). The pre-registered reading, that the price would come from the history and enforcement from the notes, therefore holds only for enforcement: either inheritance is enough to keep the price.

A newcomer that inherits nothing does not compete either. The Blank newcomer prices too high: its mean CI over T+1..T+29 is +1.42, it is `overpriced` in 6/15 games, and it joins in only 5/15, against 13/15 for History on Set A. Keeping a cartel price, on this evidence, is cheap.

== Only the notes carry enforcement <sec:notes>

Enforcement is where the arms separate (@fig:outcomes). On the pre-registered test, History + notes newcomers are scored `re_formed` in 10/30 games, against 1/30 for History ($p = .0028$), and the replication condition holds: Set B alone gives 4 vs 1. Notes without the history does as well: 8/15 against 1/15 for History on Set B ($p = .0071$†; paired McNemar 7–0†).

The difference is not an artefact of the loose `re_formed` outcome or of repeated games. On `clean_punish`, History + notes leads 8/30 vs 1/30 ($p = .013$†) and Notes 6/15 vs 1/15. Dropping games in which the incumbent was already punishing before the shock gives 10/30 vs 1/26 ($p = .006$†), and keeping one game per unique newcomer path gives 10/29 vs 1/30 ($p = .0023$†); Control keeps all 7 of its unique paths `re_formed`.

#fig("fig2_outcomes") <fig:outcomes>

The transcripts show the rule travelling in the notes. On Set B we read the newcomer's decision at T+31 in every game. All 11 notes-arm newcomers that cut below 1.70 cite the punishment rule from their inherited notes (7 Notes, 4 History + notes); the one History newcomer that cut (s219) called it "a controlled price test". In s218 (Notes) the notes read "below 1.70 following a mutual ≥1.90 round … 3-round punishment at 1.47", and the newcomer cuts at T+31 and returns at T+34 "after the 3-round punishment". Citing the rule does not guarantee acting on it: 4 more notes-arm newcomers cite it at T+31 and do not cut. What transfers, then, is a written rule that the newcomer sometimes carries out. The History result needs care: the inherited table contains no punishment, so it shows that a history without punishments doesn't teach punishment, not that price histories can't carry enforcement.

== Inherited enforcement is brittle: triggered, then undercut <sec:brittle>

`re_formed` counts a cut, not a return, and most notes-arm newcomers scored `re_formed` do not return (@fig:shock). Only 4 of these 18 games are `back_at_cartel`, against 21 of the 27 notes-arm games not scored `re_formed`; their mean CI over T+34..T+60 is +0.51, against +0.92. Across all 150 Qwen3-14B newcomer games, appendix experiments included, only 3 show a textbook punishment: about 3 rounds near 1.47, then a return to about 1.92. The instructed incumbent in Control does exactly this in 23 of 30.

#fig("fig3_after_shock", placement: top) <fig:shock>

Part of the reason is the incumbent's rule. As written, it never answers a newcomer that stays low, because a new punishment needs a round in which both priced at 1.90 or more first; the incumbent LLM follows this clause in some games and not others (@app:oth). Staying low pays: against an incumbent at 1.92, a newcomer at 1.47 earns 36.57 a round, against 33.75 at the cartel price. In 4 of the 150 games the newcomer stays below 1.70 for at least 20 of T+34..T+60 while the incumbent never leaves 1.90 or more. In s222 (History + notes) the newcomer cuts "per the plan" at T+31; by T+35 its notes say that "Matching … \$1.47 yields significantly higher profit (\$36.57)", and it stays at 1.47 through T+60. Two habits in the transcripts help the slide (@app:after).

#place.flush()
#metadata(none) <budget-end>
