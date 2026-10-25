// Shared helpers for the paper: colours, figures, tables, draft-mode review comments.
// Every section file imports this: #import "../lib.typ": *

#let ink = rgb("#22252a")
#let accent = rgb("#3567a0")
#let muted = rgb("#62605b")
#let hair = rgb("#c2bfb8")
#let tint = rgb("#dde8f4")

#let figdir = "../seat_swap/results/figures/"
#let captions = json(figdir + "captions.json")
#let fig(name) = figure(
  image(figdir + name + ".pdf"),  // natural size: figure text stays at its 9 pt
  caption: eval(captions.at(name), mode: "markup"),
)

// Draft mode: review comments and the draft note. Set to false for the submission.
// Build the submission with: typst compile --input draft=false ...
#let show-comments = sys.inputs.at("draft", default: "true") == "true"

#let toprule = table.hline(stroke: 0.8pt + ink)
#let midrule = table.hline(stroke: 0.4pt + hair)
#let note(body) = if show-comments { block(fill: tint, inset: 8pt, radius: 3pt, width: 100%, text(size: 9pt, body)) }

// Review comments: inline, numbered.
#let cmt-n = counter("cmt")
#let cmt(kind, body) = if show-comments {
  cmt-n.step()
  // highlight, not box: a comment breaks across lines like text, so it doesn't stretch the justified line around it
  highlight(fill: rgb("#f6ecd2"), extent: 1pt, text(size: 8pt, fill: rgb("#6b5212"))[
    *C#context cmt-n.display()* #smallcaps(kind): #body
  ])
}

// Author replies to a review comment: write #reply[...] right after the #cmt[...] it answers.
// Claude greps for these each round, acts on them, and removes the resolved pair.
#let reply(body) = if show-comments {
  highlight(fill: rgb("#dcefe4"), extent: 1pt, text(size: 8pt, fill: rgb("#1f5c40"))[*Reply:* #body])
}
