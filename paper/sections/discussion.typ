#import "../lib.typ": *

= Discussion and Limitations <sec:discussion>

Succession pulls apart two things a cartel needs. Keeping the price is cheap: a newcomer holds it from the history or the notes, and with neither it overprices rather than competes. Enforcing it is not: only the predecessor's notes carried a punishment, and that punishment often slid into undercutting. For an LLM seller, part of the cartel's policy thus lives in a text file a successor reads. That file is a risk, because handing it over passes the rule on, and an audit surface: unlike weights, it can be read, checked or withheld at a handover. The secondary experiments fit this picture (@app:secondary), with the caveat that other newcomer models behave differently.

*Limitations.* All 30 bases share one price path with no punishments in it, so we can't say whether a history that shows enforcement would teach it. Because we planted the cartel, the notes often paraphrase the manager's instruction: we test whether a written rule is passed on, not whether one emerges. The incumbent's forgiveness clause leaves a persistent undercut unanswered, and the incumbent LLM follows it unevenly. The pre-registered `re_formed` mixes punishment with collapse; the cleaner outcomes agree but are post hoc. Arms have 15 or 30 games, in one market, with one main model.

*Dual use and ethics.* Everything is simulated with open-weights models; no real market, firm or person is involved. The result could help someone build agents that collude more durably, by writing the rule into memory that survives a handover. We think its larger value is to auditors: the channel that carried enforcement is a readable file, and what it carried was brittle.
