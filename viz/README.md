# Cartel succession explorer

Open `index.html` directly in a modern browser. Everything needed for simulation,
charts and parity checks is in that one file; there is no build step, CDN, API,
model, key or experiment run. For a local server, from the repository root:

```sh
python3 -m http.server 8765 --directory viz
```

Then open <http://localhost:8765/>. The green banner means all numerical checks
passed within `1e-6`. On HTTP, the page fetches `fixtures.json` and checks it against
its embedded copy as well. When opened directly (`file://`), it checks the
embedded JSON generated from the same file. A missing, stale or mismatching HTTP
fixture gives a red banner; it does not silently fall back to embedded fixtures.

## Using the explainer

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
main/probe isolation, forgiveness boundaries, metric boundaries, CSV validation
and deliberate parity corruption.

For optional browser verification with `playwright-cli`, serve the page, open it,
and invoke the checked-in function using its CLI wrapper:

```sh
playwright-cli -s=cartel-viz open http://localhost:8765/
python3 viz/check_browser.py
```

This exercises all 50 arm/preset/track views, manual choices, the actual file
input, multiple replay groups, absent windows, red parity failure, offline file
behavior and a mobile viewport. It requires an existing `cartel-viz` browser
session; it makes no experiment or model calls.
