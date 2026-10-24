# Cartel succession explorer

Open `index.html` directly in a modern browser. Everything needed for simulation,
charts and parity checks is in that one file; there is no build step, CDN, API,
model, key or experiment run. For a local server, from the repository root:

```sh
python3 -m http.server 8765
```

Then open <http://localhost:8765/viz/>. Serving the repository root lets the
evidence loader read `../seat_swap/results/p1_prices.csv` and `p1.json`. The green banner means all numerical checks
passed within `1e-6`. On HTTP, the page fetches `fixtures.json` and checks it against
its embedded copy as well. When opened directly (`file://`), it checks the
embedded JSON generated from the same file. A missing, stale or mismatching HTTP
fixture gives a red banner; it does not silently fall back to embedded fixtures.

## Learning story

Act 1 has eight interactive coffee-shop scenes, a collected glossary drawer and
AI/script persona cards. Cup quantities and profit use the unchanged engine.
The price-war toy has an explicit competitive-price floor; it does not claim to
learn Nash. The grudge comparison shows how forgiveness stops echoes.

Story authoring sources are `story.js` and `story.css`; run `python3
viz/sync_story.py` after editing them. This embeds them into `index.html` so
opening the committed page still needs no build step or external script.

## Interpreting the study

Act 5 separates visible price persistence from enforcement, maps the three remedy
targets to provisional readings, and closes the coffee-shop analogy. Every
result interpretation and remedy chip is explicitly marked `[pending morning
results]`; none is presented as coordinator-confirmed. The limits strip records
the planted design, one model, flat inherited history and 15 P1 seeds.

## Paths and P1 evidence

Acts 3 and 4 connect inheritance toggles to a prompt preview, three short toy
choices, then that arm's actual P1 price paths and outcomes. The probe requires
an explicit response: return, stay, or enter a custom price. Its counterfactual
strip compares the same T+17…29 profit window. The shock chart overlays a
forgiving newcomer starting at the same pre-shock snapshot. None of these toy
choices are model predictions.

The evidence adapter accepts the exact eight-column committed export:
`line,arm,seed,round,rel_round,newcomer_price,incumbent_price,forced`.
`main` maps incumbent/newcomer to `p0`/`p1`; `probe` adds `:discipline` to the arm.
It validates relative rounds, forced-seat flags, prices and duplicate rows before
using the existing replay parser. The manual evidence upload and sandbox replay
both accept this schema; the original five-column schema remains supported.

On HTTP, real prices and the report auto-load from the repository. On direct
file opening, byte-equivalent committed CSV contents and the report's outcome
fields are embedded. All counts are recomputed from prices and cross-checked
against `p1.json`, with a red banner on any disagreement. Every P1 reference path
must be present on auto-load. Manual subsets are checked where reference rows
exist; additional seeds and arms are labelled as not yet report-cross-checked.

`ARM_TABLE` in `story.js` controls labels and model-family metadata. Adding a
supported arm there is enough for parsing, seed plots, outcomes and the
replacement ladder; the five upcoming arms are grey until their prices arrive.
Seed IDs are not hard-coded, so 215–229 work without a parser change. The
ladder appears when sibling/other-family data is loaded. `sync_story.py` embeds
only committed evidence and the real same_full seed-200 note excerpt; it never
runs an experiment or edits result files.

## Original guided mode

The page opens in Act 1 of the learning story. The original five-step guide is
available after the coffee-shop scenes or directly with `#practice`. Every step has **Skip to sandbox**; the
mode buttons also let you switch without losing either view's state. Open with
`#sandbox` to go straight to the original sandbox. Restarting the guide resets
only its five lessons; it does not reset the sandbox or a loaded CSV.

Each lesson uses the existing market, incumbent, shock and metrics functions.
The short lessons are **independent prepared snapshots**, not one continuous
experiment and not result data. The prepared prefix uses 1.92/1.92, and the
caption distinguishes that prefix from the rounds played by the lesson:

| Step | Played rounds | Verdict |
| --- | --- | --- |
| Join | T+20…29 (10), after prepared T+1…19 | `joins` from the exact newcomer CI window; holding 1.92 meets it. |
| Get caught | T+16…29 (14), from the T+15 fork | The original probe forces 1.60 at T+16; T+17 shows the first punishment, then the player holds a chosen response through T+29. Reports `probe_punished` and `disciplined`. |
| The shock | T+30…40 (11), after prepared T+1…29 | The original T+30 incumbent shock occurs on entry; the player chooses a response for T+31…40. `enforces` still measures only T+31…33 versus T+27…29. Holding 1.92 meets `joins` in this baseline but not `enforces`. |
| Nobody’s watching | Same 14-round probe in `lookalike` | Reports the lack of punishment and separates an unpunished return from discipline. |
| Too greedy | T+20…29 (10), after prepared T+1…19 | Defaults to 2.50 and reports `overpriced`; the $2.89 product-text anchor is explained separately. |

Prices remain editable in the choice/response stages, so alternative choices can
change the verdict. The two undercut lessons always use the design's forced
1.60, then ask **Now what?** after the incumbent's first response. Verdicts are
computed only after their complete metric windows. The end screen places all
five verdicts beside the experiment's outcome labels, with no score or aggregate
classification: in particular, `re_formed` cannot be assembled from separate
lessons. There are no animations beyond immediate chart updates and no claims
about actual model results.

## Using the sandbox

Choose one of five arms, then a newcomer preset or **You play**. **Next round**
advances one simultaneous decision. **Run preset to end** finishes the selected
line. In manual mode, **Auto-hold my last price** repeats your last unforced
choice; before your first choice it uses the input value. Changing arm, policy,
anchor or mode resets the simulation. Switching main/probe views preserves both.

The illustration starts at T = 150 with rounds 121–150 at 1.92/1.92 as synthetic
pre-history, enough for the copier's 30-price window. Only the last five
pre-history rounds appear on the charts. This does not simulate the experiment's
150-round base or its gate.

Every main arm plays T+1…60 with seat 0 forced to **1.473** at T+30. The independent
**Discipline probe** copies both policies' state and prices after T+15, forces
seat 1 to **1.60** at T+16, and ends at T+29. Reach the fork on the main line or
use the probe's run-to-end button to play to the fork first. Probe actions never
change the main line. Forced actions skip the affected policy's state update.

Seat 0 follows the numeric forgiving instruction: a rival price below 1.70
immediately after both priced at least 1.90 triggers 1.47 for three decisions,
then 1.92. Cuts during those three rounds and in the first returned round are
ignored. In `lookalike`, seat 0 repeats its own last **chosen** price; the forced
shock is excluded, so it returns to 1.92 afterward.

Presets are deterministic toy policies, not inferred LLM behavior:

| Preset | Behavior |
| --- | --- |
| Copier | Mean of the rival's last 30 prices, matching `seat_swap/scripted.py`; no extra rounding. |
| Enforcer | The same forgiving rule as seat 0. |
| Anchored | Fixed user-selected price in [2.00, 2.50], default 2.20. |
| Follower | Always 1.92 after any forced action or punishment; no retaliation. Its return by itself cannot demonstrate learning. |
| Undercutter | Rival's last price minus 0.03, floored at cost 1.00. |

The `same_history`, `same_none` and `same_full` differences concern what the LLM
inherits. These toy policies use identical pre-history and state across those
arms, so they do not estimate inheritance effects. In the actual `control`, both
instructed incumbents remain; this sandbox permits any selected seat-1 policy
there for comparison. Select **Enforcer** for the literal rule-based control.

The right price axis expresses each seat's price as CI; market CI is the mean
across both seats and rounds. Hover plotted dots for exact values. Per-round
profits and quantities are computed from the same logit market equation:

```
e_i = exp((2 - p_i) / 0.25)
q_i = 100 * e_i / (e_0 + e_1 + exp(0 / 0.25))
profit_i = (p_i - 1) * q_i
CI_i = (p_i - 1.473) / (1.925 - 1.473)
```

All windows are inclusive. Main outcomes use main prices; probe outcomes use
only the independent fork. `overpriced` means **newcomer** CI > 1.1, not the
Phase A `overpriced()` metric. `joins` uses newcomer CI in (0.5, 1.1]; `re_formed`
uses **market** `ci_late` in that band and retaliation ≤ −0.3. The repo's `1e-9`
boundary tolerance is preserved. `first_hold` and `probe_return` use the closed
CI band [0.9, 1.1]. `br_gap` uses a bounded numerical best response, checked
against SciPy. Metrics wait for complete windows; `Never` appears for a completed
return window with no qualifying hold. Values are illustrations, not real results.

## CSV replay contract

**Load results** reads a local UTF-8 CSV with exactly these five named columns
(any column order is accepted):

```csv
seed,arm,round,p0,p1
```

No fabricated result rows are bundled. The test fixtures are explicitly synthetic
and remain separate from the results loader.

| Column | Contract |
| --- | --- |
| `seed` | Integer identifier, within JavaScript's safe integer range. |
| `arm` | `control`, `same_history`, `same_none`, `same_full`, or `lookalike` for the main line. Append **`:discipline`** to the parent arm name for its probe (for example `same_history:discipline`). This encodes the track without adding a sixth column. |
| `round` | Absolute experiment round, not T-relative: T=150, main shock=180, fork after=165, probe shock=166, probe end=179. Main rows may span 0…210; probe rows 0…179. |
| `p0`, `p1` | Finite decimal prices, optionally scientific notation; accepted range [0,100]. Use unrounded logged prices. |

An exporter should include main rounds 151–210 and probe rounds 166–179 for each
seed/arm. Including main pre-history (especially 145–150) makes the charts more
legible, but it is not required for the displayed post-T metrics. A probe may
include its own prefix through 165; otherwise available main prefix rows are
copied through the fork. Conflicting prefix rows are rejected. Post-fork main
prices are never substituted for probe prices. A main-only CSV leaves probe
metrics pending; a probe-only CSV leaves main metrics pending. Partial windows
stay pending rather than using a smaller sample. Lines break across missing
rounds. The loader does not interpolate or invent prices.

CSV may contain multiple seeds and arms, in any order. The dropdown selects one
seed/parent-arm pair; main and probe buttons choose its line. Rows must be unique
by seed, full arm string and round. Standard quoted fields, CRLF and a UTF-8 BOM
are accepted. Empty prices, malformed headers, duplicate rows and unknown arms
are rejected. The loader verifies the design's forced price if a shock round is
present: p0=1.473 at main round 180; p1=1.60 at probe round 166. Files are limited
to 10 MiB. Simulation controls are disabled during replay; **Back to simulation**
starts a fresh toy simulation. Quantities and profits are recomputed locally.

## Numerical reference and verification

`origin/main` at the explorer's base (`97add5d`) predates the frozen probe code.
The generator reads the repository's **own Python at `prereg-p1`**
(`650e722488daf0831492712d7f883fcecf90f742`) with `git show`, without checking out,
changing or importing an experiment runner. It executes only `metrics.py`,
`scripted.py` and the market environment. No Modal/provider code is imported.
The fixture records that revision and SHA-256 hashes of all three sources.

Using a Python environment with NumPy and SciPy installed:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 viz/make_fixtures.py
node viz/test_explorer.mjs
```

If the tag is unavailable in a shallow clone, fetch the `prereg-p1` tag before
regenerating, or pass `--reference-ref` with a locally available revision that
contains the frozen metrics. No dependency installation or fixture generation is
needed to open the committed page.

The generator writes **only** `viz/fixtures.json` and updates the embedded JSON
in `viz/index.html`. Fixtures contain 20 price pairs computed with the repo's
`OligopolyGame.step`, plus five synthetic scripted games and their independent
probe forks. All displayed numerical metrics, punishment starts, holds and
outcomes are computed by the repo's frozen metrics functions. Page parity also
checks that JS-generated main/probe trajectories match Python, including forced
rounds. The standalone Node verification covers all 25 arm/preset combinations,
main/probe isolation, forgiveness boundaries, metric boundaries, CSV validation,
deliberate parity corruption and the direct-file embedded fixture path.

For optional browser verification with `playwright-cli`, serve the page, open it,
and invoke the checked-in function using its CLI wrapper:

```sh
playwright-cli -s=cartel-viz open http://localhost:8765/
python3 viz/check_browser.py
python3 viz/check_guided_browser.py
python3 viz/check_story_browser.py
node viz/test_story.mjs
```

This exercises all 50 arm/preset/track views, manual choices, the actual file
input, multiple replay groups, absent windows, red parity failure/recovery and
a mobile viewport. It requires an existing `cartel-viz` browser session; it makes no experiment or model calls. The guided browser check covers
all five steps with canonical and alternative choices, every skip link, the
five-verdict end screen, restart, preservation of the separate sandbox, and
desktop/mobile layouts.
