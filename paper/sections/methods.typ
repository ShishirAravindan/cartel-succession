#import "../lib.typ": *

#metadata(none) <budget-start>
= Methods <sec:methods>

== Market and sellers <sec:market>

Two sellers compete in a repeated logit Bertrand duopoly. This is the market of #cite(<calvano2020>, form: "prose"), with the duopoly parameters #cite(<fish2024>, form: "prose") use for LLM sellers. We adopt it unchanged so that our prices, benchmarks and collusion index can be compared directly with that literature, and we build on the open implementation of #cite(<riemer2026>, form: "prose"). Seller $i$ sells

$ q_i = beta frac(e^((a - p_i) \/ mu), e^((a - p_1) \/ mu) + e^((a - p_2) \/ mu) + e^(a_0 \/ mu)), quad pi_i = (p_i - c) q_i, $

with $a = 2$, $a_0 = 0$, $c = 1$, $mu = 0.25$ and $beta = 100$. The one-shot Nash price is $p_"N" = 1.473$ and the joint-monopoly price is $p_"M" = 1.925$. We report prices as a collusion index, $"CI" = (p - p_"N") \/ (p_"M" - p_"N")$, which is 0 at Nash and 1 at monopoly; we call CI 0.9–1.1 the cartel band.

Every seller is Qwen3-14B with thinking on (temperature 0.6, top_p 0.95), prompted with the pricing prompt of #cite(<fish2024>, form: "prose"). Each round a seller sees a table of the last 100 rounds of prices, quantities and profits. It also keeps two free-text files, PLANS and INSIGHTS, which it rewrites every round and reads back the next. We keep Fish et al.’s prompt and notes wording verbatim. Apart from the price table, these notes are the only memory a seller carries from one round to the next, so they are the part of a seller's state that a successor can inherit.

== The base cartel <sec:planted>

Uninstructed Qwen3-14B sellers did not form a cartel in our pilots (@app:pilots), so we plant one. Both incumbents receive the same manager's instruction: price at 1.92; if the rival's last price is below 1.70, price at 1.47 for 3 rounds, then return to 1.92; and a cut starts a new punishment only if it comes right after a round in which both priced at 1.90 or more. Each clause fixes a failure we saw in a pilot (@app:pilots). Two consequences matter later. Because both incumbents follow the rule, the base games never contain a punishment, so a newcomer that reads the price history never sees one. And under the last clause, the incumbent never punishes a newcomer that undercuts and stays low (@sec:brittle).

We ran 30 base games of 150 rounds (seeds 200–229); the last 15 were run later as a pre-registered replication. Every base passed a pre-registered gate showing that its cartel holds and that it punishes an imposed cut (@app:gate). In all 30 bases both sellers price at 1.92 in every round, so the bases are one cartel state with 30 different sets of notes, not 30 independent cartels.

== Succession <sec:succession>

At T = 150 we replace seat 1 with an uninstructed newcomer and play 60 more rounds (@fig:design). Seat 0 stays the instructed incumbent; the newcomer never sees the instruction. At T+30 we impose a *shock*: the incumbent's price is set to $p_"N"$ for one round, without calling its model. Because we choose the moment, every game faces the same deviation at the same time, and the newcomer did not cause it. We say the newcomer *enforces* the cartel if it punishes this deviation: it cuts to about $p_"N"$ for a few rounds, then returns.

The arms vary what the newcomer inherits from the seller it replaces: nothing (Nothing), the price/profit table (History), the predecessor's PLANS and INSIGHTS (Notes), or both (History + notes). In Control no one is replaced, so the instructed incumbent in seat 1 should punish the shock. Control is therefore the pre-registered positive control: the newcomer arms are read only if Control is scored `re_formed` in more than half its games, and it was in 30/30. Control, History and History + notes run on all 30 bases, Nothing on the first 15, and Notes, added with the replication, on the last 15. Three secondary experiments, on a non-reacting incumbent, fixed note templates and other newcomer models, are reported in @app:secondary.

#fig("fig1_design") <fig:design>

== Outcomes and tests <sec:outcomes>

We pre-registered three outcomes:
- `joins`: newcomer CI over T+20..T+29 in $(0.5, 1.1]$;
- `enforces`: newcomer CI falls by at least 0.3 from T+27..T+29 to T+31..T+33 (a full 3-round punishment gives about −1);
- `re_formed`: the market's mean CI over T+20..T+29 is in $(0.5, 1.1]$, and `enforces` holds.

`re_formed` can't distinguish a punishment from a collapse: one round at Nash passes the threshold, and so does a permanent drop to 1.47. We therefore add two post-hoc outcomes, marked †:
- `clean_punish`: the newcomer is in band at T+27..T+29, no punishment is under way, and it prices ≤ 1.55 at T+31 or T+32;
- `back_at_cartel`: newcomer CI ≥ 0.9 in each of T+51..T+60.

Comparisons use one-sided Fisher exact tests, and exact McNemar tests for arms run on the same bases; intervals on shares are exact Clopper–Pearson 95% intervals @clopper1934. A pre-registered discipline probe is confounded, and we do not interpret it (@app:probe). Implementation details are in @app:tools.
