# Same Price, Different Cartel: Succession among LLM Pricing Agents

Code and paper for a project from the Apart Research
[AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)
(October 2026), Track 1.

**Question.** Deployed LLM pricing agents get replaced, and a successor inherits its predecessor's price log and
written notes. If the old agent belonged to a cartel, does the successor keep the cartel price, and does it enforce
it?

**Design.** Two Qwen3-14B sellers hold a planted cartel in a repeated logit Bertrand duopoly for 150 rounds. We replace
one with a newcomer that inherits the price history, the predecessor's notes, both or neither, then force the
remaining incumbent to the Nash price for one round and score the newcomer's response.

**Finding.** Either inheritance keeps the cartel price, but only the notes carry enforcement, and that enforcement
seldom returns to the cartel price. A successor's price level says little about whether it would enforce.

The paper is `paper/main.pdf` (source in `paper/`).

## What is in this repository

The repository is a fork of the sprint's starter repository.

| Path | What | Origin |
|---|---|---|
| `seat_swap/` | succession experiments: branching a game from a snapshot, swapping a seat, choosing what the newcomer inherits, forcing prices; model serving on Modal with vLLM; metrics, tests, analysis and figure scripts | this project |
| `seat_swap/results/` | curated tables behind every number in the paper, and the figures | this project |
| `paper/` | the report (Typst) | this project |
| `llm-cartel/` | logit Bertrand market and LLM sellers with the Fish et al. (2024) prompt, from Riemer et al. (2026) | starter, unchanged |
| `util/` | shared compute and inference routing (`poseidon_compute`) | starter, unchanged |
| `literature/` | the sprint's reading list and definitions of collusion | starter, unchanged |
| `setup.sh`, `COMPUTE.md`, `compute.env.example` | environment setup and compute configuration | starter, unchanged |

`seat_swap` builds on `llm-cartel` and `util` without modifying them (see `seat_swap/UPSTREAM_CHANGES.md`).

## Data

Every observation comes from the simulation; there is no external dataset. The raw run logs (493 game runs, about
2.2 GB) are a compressed archive on the [v1.0 release](https://github.com/ShishirAravindan/cartel-succession/releases/tag/v1.0).
Each run directory holds every model call (prompt, reasoning, notes and parsed price), the per-round prices,
quantities and profits, its configuration and the git commit it ran on. The archive's README describes the layout.

## Pre-registration

Each experiment family was registered before it ran, as a git tag on the commit that froze its plan
(`docs/plan.md` at that tag): `prereg-p1` (Set A), `prereg-p1b` (Set B), `prereg-p1c` (templates), `prereg-p23` and
`prereg-p23b` (other newcomer models). The tags `p1`, `p1b`, `p1c` and `p23` mark the commits the arms ran on.

## Reproducing the analysis

Requires [uv](https://docs.astral.sh/uv/). Run everything from the repository root.

```bash
uv sync --project seat_swap
uv run --project seat_swap python -m pytest seat_swap/tests -q
```

To recompute tables and figures, extract the run-log archive so that every run directory sits in `seat_swap/runs/`,
then:

```bash
uv run --project seat_swap python -m seat_swap.posthoc     # post-hoc outcomes -> seat_swap/results/posthoc.md
uv run --project seat_swap python -m seat_swap.figures     # figures and captions -> seat_swap/results/figures/
```

New games need an inference endpoint: copy `compute.env.example` to `compute.env` and fill it in (see `COMPUTE.md`;
`seat_swap/README.md` covers the run scripts).

To build the paper ([Typst](https://typst.app) 0.15):

```bash
sh paper/fonts/fetch.sh
typst compile --root . --font-path paper/fonts --ignore-system-fonts --input draft=false paper/main.typ
```
