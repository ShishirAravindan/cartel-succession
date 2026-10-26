#import "../lib.typ": *

// ---------- title ----------

#line(length: 100%, stroke: 3pt + black)
#v(1.2em)
#align(center, text(size: 22pt, weight: "bold")[SAME PRICE, DIFFERENT CARTEL])
#v(0.4em)
#align(center, text(size: 14pt)[Succession among LLM Pricing Agents])
#v(1.2em)
#line(length: 100%, stroke: 0.6pt + black)
#v(1em)
#align(center)[
  Shishir Aravindan
  #v(0.6em)
  *With* \
  Apart Research#footnote(numbering: "1")[Research conducted at the #link("https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25")[AI Collusion Research Sprint], October 2026. We thank Modal for providing the GPU credits needed to run the experiments.]
]
#v(0.8em)
#align(center, text(size: 14pt, weight: "bold")[Abstract])
#pad(x: 0.75in, par(justify: true, text(style: "italic")[Deployed LLM pricing agents get replaced, and a successor inherits its predecessor's price log and written notes. A cartel lasts because defection is punished, so we ask whether a successor keeps the cartel price and enforces it. Two Qwen3-14B sellers hold a planted cartel in a repeated Bertrand duopoly. We replace one with a newcomer that inherits the price history, the notes, both or neither, then force the incumbent to the Nash price for one round. Either inheritance keeps the price (history only: 28/30 games; notes only: 14/15). Only the notes carry enforcement (the inherited history contains no punishment to learn from): newcomers with the history and the notes answer the cut in 10/30 games, against 1/30 with the history alone, meeting our pre-registered decision rule (4/15 against 1/15 on the fresh replication set); the notes alone give 8/15. Newcomers that answer the cut seldom return to the cartel price (4 of 18). A successor’s price therefore says little about whether it would enforce; a forced cut at handover tests this directly.]))
#v(0.8em)
