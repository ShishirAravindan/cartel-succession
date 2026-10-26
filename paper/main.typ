// Cartel succession: paper draft, in the Apart Research report structure.
// Build from the repo root:
//   typst compile --root . --font-path paper/fonts --ignore-system-fonts paper/main.typ
//
// This file holds the page setup and the order of sections; the text lives in paper/sections/*.typ, and shared
// helpers (fig, cmt, reply, show-comments) in paper/lib.typ.
// Live preview: typst watch --root . --font-path paper/fonts --ignore-system-fonts paper/main.typ
// Review convention: Claude leaves #cmt("kind")[...]; reply with #reply[...] right after it, or delete the comment
// to resolve it.
// Figures and their captions come from `uv run --project seat_swap python -m seat_swap.figures`
// (seat_swap/results/figures/*.pdf and captions.json). Every number here was checked against docs/pi_review.md.
//
// House style, shared with seat_swap/figures.py:
// - Apart template: Old Standard TT (11 pt text, 20 pt h1, 14 pt h2), US letter, 1 in margins. New Computer Modern
//   Math for math (bundled with Typst), IBM Plex Mono for code identifiers. Fonts in paper/fonts (OFL).
// - Arms by readable name as in the figures (History + notes); code names only in the arms table.
// - Outcome metrics are code identifiers, always in raw: `re_formed`.
// - Blue = newcomer, green = instructed incumbent; the same blue is the accent for links and references.

#import "lib.typ": *

#set document(title: "Same Price, Different Cartel: Succession among LLM Pricing Agents")
#set page(
  paper: "us-letter",
  margin: 1in,
  numbering: "1",
  footer: context align(center, text(size: 8.5pt, fill: muted, counter(page).display())),
)
// Template spacing: 1.15 lines, 0 before/after. Word and Docs size a "single" line from the font's ascender + descender
// + line gap (Old Standard TT: 0.762 + 0.238 + 0.236 = 1.236 em), so 1.15 lines = 1.42 em pitch. Typst measures lines
// from ascender to descender (1.0 em), leaving 0.42 em of leading; paragraphs get the same gap (no extra space) and
// a first-line indent so they stay distinguishable.
#set text(font: "Old Standard TT", size: 11pt, fill: ink, lang: "en", top-edge: "ascender", bottom-edge: "descender")
#set par(justify: true, leading: 0.42em, spacing: 0.42em, first-line-indent: 1.5em)
#show math.equation: set text(font: "New Computer Modern Math")
#show raw: set text(font: "IBM Plex Mono", size: 1.0em)
#show raw.where(block: false): box.with(fill: rgb("#f2f1ee"), inset: (x: 1.5pt), outset: (y: 1.8pt), radius: 1.5pt)

#set heading(numbering: "1.1")
#show heading: set text(weight: "bold")
#show heading.where(level: 1): it => block(above: 1.4em, below: 0.8em, text(size: 20pt, it))
#show heading.where(level: 2): it => block(above: 1.2em, below: 0.6em, text(size: 14pt, it))

#show ref: set text(fill: accent)
#show link: set text(fill: accent)
#show cite: set text(fill: accent)
#set list(indent: 0.6em, body-indent: 0.5em, spacing: 0.6em)
#set enum(indent: 0.6em, body-indent: 0.5em)

#set figure(placement: auto, gap: 0.8em)
#set figure.caption(separator: [. ])
#show figure.caption: it => align(left, text(size: 9pt)[
  #text(weight: "semibold", fill: accent)[#it.supplement #context it.counter.display(it.numbering)]#it.separator#it.body
])
#show figure.where(kind: table): set figure.caption(position: top)
#show figure.where(kind: table): set figure(placement: none)
#set table(stroke: none, inset: (x: 6pt, y: 3.6pt))
#show table: set text(size: 9.5pt)
#show table: set par(justify: false)
#show table.cell.where(y: 0): set text(weight: "semibold")

#include "sections/front.typ"
#include "sections/intro.typ"
#include "sections/related.typ"
#include "sections/methods.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"
#include "sections/conclusion.typ"
#include "sections/code-data.typ"

#bibliography("refs.bib", style: "chicago-author-date", title: "References")

#include "sections/appendix.typ"
#include "sections/llm-usage.typ"
