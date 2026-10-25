#import "../lib.typ": *

= Discussion and Limitations <sec:discussion>

_Discussion to be written._

Three secondary experiments (@app:secondary) fit this picture without adding to it. With a scripted incumbent that never reacts, newcomers join just as readily and never enforce. Replacing the real notes with a fixed template of the same rule transferred less enforcement, not more. And other newcomer models behave differently enough (a smaller Qwen joins but rarely enforces; gpt-oss-20b drifts into price wars) that the result should be read as Qwen3-14B's.

Limitations:
- *One planted cartel state.* We planted it because uninstructed sellers did not collude in pilots (@sec:planted). Its history contains no punishments, so we can't say whether a history that shows enforcement would teach it.
- *The incumbent's rule is exploitable.* The forgiveness clause we added to stop punishments chaining also leaves a persistent undercut unanswered, and the incumbent LLM follows its clauses unevenly.
- *`re_formed` is noisy.* It mixes punishment with collapse, so we lead with the post-hoc `clean_punish` and recovery measures.
- *Small samples.* Arms have 15 games.
- *Discipline probe omitted.* It is confounded and was not recomputed (@app:probe).
