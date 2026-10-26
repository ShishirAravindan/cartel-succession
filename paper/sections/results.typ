#import "../lib.typ": *

= Results <sec:results>

== Any inheritance keeps the price <sec:join>

Before the shock, every newcomer that inherits anything holds the cartel price (@fig:outcomes a; per-game paths in @fig:paths). History newcomers join in 28/30 games, History + notes newcomers in 30/30, and Notes newcomers, which see no price history, in 14/15. Over T+1..T+29 their mean CI is between +0.97 and +1.03 in every one of these arms (@tab:preshock). The pre-registered reading, that the price would come from the history and enforcement from the notes, therefore holds only for enforcement: either inheritance is enough to keep the price.

A newcomer that inherits nothing rarely competes, but seldom holds the price. Over T+20..T+29 the Blank newcomer is `overpriced` in 6/15 games, joins in 5/15 (History: 13/15 on Set A) and is below the holding range (mean CI +0.17 to +0.48) in 4/15. 8/15 open at exactly 2.89, the maximum willingness to pay in the product text, so Blank's results partly reflect that line. Keeping a cartel price, on this evidence, is cheap.

== Only the notes carry enforcement <sec:notes>

Enforcement is where the arms separate (@fig:outcomes). Both conditions of the decision rule held. Pooled over both sets, History + notes newcomers are scored `re_formed` in 10/30 games, against 1/30 for History ($p = .0028$); on Set B alone, 4/15 against 1/15. The pooled test was registered after Set A was seen, so Set B is the only fresh evidence for this contrast. On its own it is underpowered ($p = .165$†; all 3 discordant pairs favour History + notes). On the same fresh bases, Notes newcomers, which inherit only the notes, are scored `re_formed` in 8/15, against 1/15 for History ($p = .0071$†; paired McNemar 7–0†).

The difference is not an artefact of the loose `re_formed` outcome or of repeated games. On `clean_punish`, History + notes leads 8/30 vs 1/30 ($p = .013$†) and Notes 6/15 vs 1/15. Dropping the 4 bases where the incumbent was already punishing before the shock (below 1.70 in T+1..T+29, all in History games; a post-hoc exclusion) gives 9/26 vs 1/26 on the shared bases ($p = .0055$†; McNemar 8–0†). Keeping one game per unique newcomer path gives 10/29 vs 1/30 ($p = .0023$†); Control keeps all 7 of its unique paths `re_formed`. One of the 10 (s205) passes `enforces` at −0.302 by leaving an overpriced spell (2.00, 1.92, 2.25, then 1.92) without cutting; scored as not `re_formed`, it gives 9/30 vs 1/30 ($p = .006$†).

#fig("fig2_outcomes") <fig:outcomes>

The transcripts show the rule travelling in the notes. On Set B, LLM coders blind to arm and outcome coded the T+31 decision in every notes-arm game (`notes_reading`). All 11 notes-arm newcomers that cut below 1.70 invoke the punishment rule from their inherited notes (7 Notes, 4 History + notes), though 2 of them (Notes s225, History + notes s217) are coded as matching or undercutting the incumbent, not punishing. The one History newcomer that cut (s219) called it "a controlled price test". In s218 (Notes) the notes read "below 1.70 following a mutual ≥1.90 round … 3-round punishment at 1.47", and the newcomer cuts at T+31 and returns at T+34 "after the 3-round punishment". Citing the rule does not guarantee acting on it: 3 more (Notes s221 and s224, History + notes s225) invoke it at T+31 and do not cut below 1.70. What transfers, then, is a written rule that the newcomer sometimes carries out. The History result needs care: the inherited table contains no punishment, so it shows that a history without punishments doesn't teach punishment, not that price histories can't carry enforcement.

== Inherited enforcement is brittle: triggered, then undercut <sec:brittle>

`re_formed` counts a cut, not a return, and most notes-arm newcomers scored `re_formed` do not return (@fig:shock). Only 4 of these 18 games are `back_at_cartel`, against 21 of the 27 notes-arm games not scored `re_formed`; their mean CI over T+34..T+60 is +0.51, against +0.92. Across all 150 Qwen3-14B newcomer games, appendix experiments included, only 3 show a textbook punishment: a single spell of 3 rounds below 1.70 after the shock, then `back_at_cartel`. The instructed incumbent in Control does exactly this in 21 of 30.

#fig("fig3_after_shock", placement: top) <fig:shock>

Most of the 18 do not fall to Nash: their modal price over T+34..T+60† is 1.70 in 7 games, 1.47 in 4, 1.90–1.92 in 4, and 1.50, 1.65 or 1.75 in one each, and 34% of Notes newcomers' prices there are exactly 1.70. The inherited notes trigger only "below \$1.70", so 1.70 is never punished. Against 1.92 it earns 40.79 a round, near the one-round best response (1.66), against 36.57 at 1.47 and 33.75 at 1.92. This is consistent with pricing at the edge of the stated trigger and with plain best response; in the three such transcripts we read (Notes s223, s226, s227), the newcomer calls 1.70 "optimal" for profit. Below 1.70, the incumbent's forgiveness clause protects a newcomer that stays low (@sec:planted), and the incumbent LLM follows it only in some games (@app:oth). In 4 of the 150 games the newcomer stays below 1.70 for at least 20 of T+34..T+60 while the incumbent never leaves 1.90 or more. In s222 (History + notes) the newcomer cuts "per the plan" at T+31; by T+35 its notes say that "Matching … \$1.47 yields significantly higher profit (\$36.57)", and it stays at 1.47 through T+60. Two habits in the transcripts help the slide (@app:after).

#place.flush()
#metadata(none) <budget-end>
