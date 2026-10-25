# Paper: Cartel Succession (Apart AI Collusion Sprint report)

Handoff for anyone, human or agent, picking up the paper. Read this, then `docs/pi_review.md` (the independent check
of every number), then the section you are editing.

## Build and preview

Typst 0.15 (`brew install typst`). On a fresh clone, first fetch the fonts (gitignored): `sh paper/fonts/fetch.sh`.
Then, from the repo root:

```bash
typst watch   --root . --font-path paper/fonts --ignore-system-fonts paper/main.typ                     # live, draft
typst compile --root . --font-path paper/fonts --ignore-system-fonts --input draft=false paper/main.typ  # submission
uv run --project seat_swap python -m seat_swap.figures   # figures + captions.json, after any figure/caption change
```

`paper/main.pdf` is gitignored while drafting; unignore it for the submission. `--root .` is needed because the paper reads figures from `seat_swap/results/figures/`. `--ignore-system-fonts` keeps
the build identical on every machine. To inspect pages as images, render into a fresh temporary directory
(`typst compile ... --ppi 100 paper/main.typ "$(mktemp -d)/p{0p}.png"`); never `rm` with a variable in the path.

## Layout

| File | Holds |
|---|---|
| `main.typ` | page setup (template fonts, sizes, spacing) and the order of sections; no content |
| `lib.typ` | shared helpers: `fig(name)`, `cmt`, `reply`, `note`, table rules, `show-comments` (draft switch) |
| `sections/*.typ` | the text, one file per section: front (title, abstract, draft note), intro, related, methods, results, discussion, conclusion, code-data, appendix, llm-usage |
| `refs.bib` | bibliography |
| `notes.md` | earlier bullet talking points behind Methods and Results, with sources |
| `tools/numcheck.py` | lists numbers in a file that are not in `docs/pi_review.md` |
| `fonts/` | template fonts (OFL; gitignored, fetched by `fonts/fetch.sh`), so the build doesn't depend on installed fonts |

Figure captions are not in the paper: they live in `seat_swap/figures.py`, are written to
`seat_swap/results/figures/captions.json`, and `fig()` evaluates them as Typst markup (so `code` and `@fig:` work).
Change a caption there and regenerate.

## Apart template and limits

- Old Standard TT, 11 pt text, 20 pt h1, 14 pt h2; US letter, 1 in margins; 1.15 line spacing, no space before/after
  (implemented in `main.typ`; paragraphs get a first-line indent).
- Order: title (footnote: sprint + Modal credits), author, abstract; 1 Introduction, 2 Related Work, 3 Methods,
  4 Results, 5 Discussion and Limitations, 6 Conclusion, Code and Data, References, Appendix, LLM Usage Statement.
- **Methods + Results: 2.5 pages recommended, 4.5 maximum. Introduction + Related Work: 2 pages maximum.** Appendix
  unlimited. The draft note at the top of the PDF shows the live Methods + Results length; measure the submission
  layout with `--input draft=false` (comments hidden).

## Conventions

- **Arms** use readable names everywhere: Control, Blank, History, Notes, History + notes. Code names
  (`same_full` …) appear only in the appendix arms table.
- **Outcome metrics** are code identifiers in raw: `joins`, `overpriced`, `enforces`, `re_formed`, `clean_punish` †,
  `back_at_cartel` † († = post hoc; also marks post-hoc p-values). Only the pooled History + notes vs History Fisher
  test is pre-registered in the main experiment.
- **No "band".** *Holds* = mean CI over a window in (0.5, 1.1]; *at the cartel price* = CI ≥ 0.9; `overpriced` =
  mean CI > 1.1 (above the monopoly price).
- **Round windows** as plain text: T+20..T+29. "Punishment", not "retaliation".
- **Base sets** are neutral labels, Set A and Set B (batches are provenance, not design). Seeds appear only in
  appendix A.1. Never "first/last 15" or internal phase codes. Internal → paper: P1 = Set A (seeds 200–214);
  P1b = Set B (seeds 215–229, pre-registered replication, adds Notes); P1c = the template experiment (Set B);
  P2 / P3 = the model experiment, Qwen3-8B / gpt-oss-20b (Set A). P2/P3 raw runs live in the sibling worktree
  `../cartel-succession-p23/seat_swap/runs`.
- **Colours** (shared with the figures): blue = newcomer, green = instructed incumbent, pale→deep blue = CI.
- **Voice:** "we".
- **Main paper = the main experiment.** Look-alike, templates and other models are appendix C, mentioned once in
  Discussion.

## Review loop

Claude leaves `#cmt("fix")[…]` (numbered amber highlights). The author answers with `#reply[…]` right after it
(green), or deletes the comment to resolve it. Each round, when the author says so: grep `paper/sections` for
`#reply`, act on each, remove resolved pairs. Re-read files from disk before editing; the author edits in parallel
with a live preview. No commits unless the author asks (then: conventional, one line, no trailers; see CLAUDE.md).

## Verification

- Every result number must trace to `docs/pi_review.md`; run `python3 paper/tools/numcheck.py <file>` after content
  edits. Expected misses: styling values, citation years, seeds, and numbers sourced from `docs/log.md` / `docs/status.md`
  (pilots and the base gate, A.2–A.3; costs, A.4; the discipline probe, A.5), which were not independently recomputed.
- Citations: check claims against `literature/papers.csv` (summaries and links for nearly every cited paper) and the
  PDFs (`python3 literature/fetch_papers.py`). Bib entries with a braced `{X et al.}` author are placeholders for full
  author lists.
- Pre-registration: `docs/plan.md` (§7 kill tests define the Control positive control and the Look-alike reading).

## Open items (25 Oct 2026)

- Related Work rewritten (25 Oct): comments resolved, citations checked against the PDFs, Arslan et al. 2026 added
  (it already separates price level from punishment, for Q-learners; our gap is what an LLM successor inherits).
  Introduction drafted (motivation, RealPage hook). Intro + Related Work: 1.97 pages in the submission layout (limit 2),
  so any addition needs a matching cut. Garra moved to the templates appendix.
- `results.typ` §4.2 pools two transcript counts with the appendix template arm (rule_return): "all 13 … who cut"
  (11 in the main arms) and "7 … still hold the price" (4 in the main arms).
- Methods + Results: 4.04 pages (limit 4.5); further options: Fig. 1 to the appendix, drop the demand equation.
- To write: abstract, Discussion, Conclusion, LLM Usage Statement (mandatory; frame the author's and Claude's
  contributions fairly). Fill in: affiliation; make the GitHub repo public; first names for Garra (still cited).
