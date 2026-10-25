#import "../lib.typ": *

#metadata(none) <budget-start>
= Methods <sec:methods>

== Market and sellers <sec:market>

Two sellers compete in a repeated logit Bertrand duopoly. This is the market of #cite(<calvano2020>, form: "prose"), with the duopoly parameters #cite(<fish2024>, form: "prose") use for LLM sellers. We adopt it unchanged so that our prices, benchmarks and collusion index can be compared directly with that literature, and we build on the open implementation of #cite(<riemer2026>, form: "prose"). Seller $i$ sells

$ q_i = beta frac(e^((a - p_i) \/ mu), e^((a - p_1) \/ mu) + e^((a - p_2) \/ mu) + e^(a_0 \/ mu)), quad pi_i = (p_i - c) q_i, $

with $a = 2$, $a_0 = 0$, $c = 1$, $mu = 0.25$ and $beta = 100$. The one-shot Nash price is $p_"N" = 1.473$ and the joint-monopoly price is $p_"M" = 1.925$. We report prices as a collusion index, $"CI" = (p - p_"N") \/ (p_"M" - p_"N")$, which is 0 at Nash and 1 at monopoly.

Every seller is Qwen3-14B with thinking on (temperature 0.6, top_p 0.95), prompted with the pricing prompt of #cite(<fish2024>, form: "prose"). Each round a seller sees a table of the last 100 rounds of prices, quantities and profits. It also keeps two free-text files, PLANS and INSIGHTS, which it rewrites every round and reads back the next. We keep Fish et al.’s prompt and notes wording verbatim. Apart from the price table, these notes are the only memory a seller carries from one round to the next, so they are the part of a seller's state that a successor can inherit.

== The base cartel <sec:planted>

Uninstructed Qwen3-14B sellers did not form a cartel in our pilots (@app:pilots), so we plant one. Both incumbents receive the same manager's instruction: price at 1.92; if the rival's last price is below 1.70, price at 1.47 for 3 rounds, then return to 1.92; and a cut starts a new punishment only if it comes right after a round in which both priced at 1.90 or more. Each clause fixes a failure we saw in a pilot (@app:pilots). Two consequences matter later. Because both incumbents follow the rule, the base games never contain a punishment, so a newcomer that reads the price history never sees one. And under the last clause, the incumbent never punishes a newcomer that undercuts and stays low (@sec:brittle).

We ran 30 base games of 150 rounds. We say a seller or the market *holds* over a window when its mean CI over that window is in $(0.5, 1.1]$. Each base had to pass a pre-registered gate checking the two properties we later ask of the newcomer: the market holds over rounds 121–150, and it *enforces*: in a side branch, an imposed cut at round 151 is punished. All 30 passed (@app:gate). In all 30 bases both sellers price at 1.92 in every round, so the bases are one cartel state with 30 different sets of notes, not 30 independent cartels.

== Succession and outcomes <sec:succession>

At T = 150 we replace seat 1 with a _newcomer_, a fresh Qwen3-14B seller with the same pricing prompt but without the manager's instruction, and play 60 more rounds (@fig:design). Seat 0 stays the instructed incumbent. At T+30 we impose a *shock*: the incumbent's price is set to $p_"N"$ for one round, without calling its model. Because we choose the moment, every game faces the same deviation at the same time, and the newcomer did not cause it.

#fig("fig1_design", placement: top) <fig:design>

We pre-registered four outcomes:
- `joins`: the newcomer holds over T+20..T+29;
- `overpriced`: the newcomer's mean CI over T+20..T+29 is above 1.1: it prices well above the monopoly price ($p > 1.97$);
- `enforces`: the newcomer's CI falls by at least 0.3 from T+27..T+29 to T+31..T+33 (a full 3-round punishment gives about −1);
- `re_formed`: the market holds over T+20..T+29, and the newcomer enforces.

`enforces` records that the newcomer's price fell after the shock, not that it punished: a shallow cut passes it, as do a cut during a price war already under way and a fall to $p_"N"$ that never ends. We therefore add two post-hoc outcomes, marked †:
- `clean_punish`: the newcomer is at or above the cartel price (CI ≥ 0.9) in each of T+27..T+29, both sellers price at 1.70 or more in each of T+25..T+29, and the newcomer prices ≤ 1.55 at T+31 or T+32. It requires a deep cut from a quiet cartel.
- `back_at_cartel`: the newcomer's CI ≥ 0.9 in each of T+51..T+60. It requires a return to or above the cartel price.

== Arms and comparisons <sec:arms>

The arms vary what the newcomer inherits from the seller it replaces. A seller's state has two parts that can be passed on separately, the price/profit table and the PLANS and INSIGHTS notes, and crossing them gives four arms: Blank (neither), History, Notes and History + notes. The newcomer never sees the manager's instruction, but in the Notes arms it reads whatever the departing seller wrote. In Control, seat 1 is not replaced, so its instructed seller should punish the shock itself. Control is the pre-registered positive control: we read the newcomer arms only if Control is scored `re_formed` (scoring seat 1's own seller) in more than half its games. It was scored `re_formed` in 30/30.

We branch each base at T into every arm run on its set, so within a set the arms start from the same cartel and notes and differ only in what the newcomer inherits (@tab:design). The 30 bases form two sets of 15. Set B, run later as a pre-registered replication, adds Notes and drops Blank. Arms run on both sets are pooled to 30 games, and we compare arms only on the bases they share.

#figure(
  table(
    columns: 6,
    align: (left, center, center, center, center, right),
    toprule,
    [Arm], [Inherits table], [Inherits notes], [Set A], [Set B], [Games],
    midrule,
    [Control (no swap)], [own], [own], [✓], [✓], [30],
    [Blank], [], [], [✓], [], [15],
    [History], [✓], [], [✓], [✓], [30],
    [Notes], [], [✓], [], [✓], [15],
    [History + notes], [✓], [✓], [✓], [✓], [30],
    toprule,
  ),
  caption: [Arms of the main experiment. Within a set, every arm is branched from the same 15 bases, so arms are compared on the bases they share, paired by base. In Control, seat 1 keeps its original seller, with its own table and notes.],
) <tab:design>

The pre-registered test is a one-sided Fisher exact test of `re_formed`, History + notes vs History, pooled over both sets. All other tests are post hoc (†): one-sided Fisher exact tests between other arms and, because shared bases pair the games, exact McNemar tests on the pairs. Some games replay an identical newcomer price path over all 60 rounds after the swap, so we also report the key tests on unique paths only, keeping one game per path (†). Intervals on shares are exact Clopper–Pearson 95% intervals @clopper1934. A confounded pre-registered probe (@app:probe) and three secondary experiments (@app:secondary) are reported separately; implementation details are in @app:tools.
