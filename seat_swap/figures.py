"""Paper figures (Kickoff 09 §3) from the run logs, via posthoc.load_games.

    uv run --project seat_swap python -m seat_swap.figures

Writes fig1_design .. fig5_after_shock (and fig6_p1c once a P1c manifest has finished games) (PDF + PNG) and captions.md to seat_swap/results/figures/. One style throughout:
the newcomer is dark blue (solid), the incumbent orange (dashed); the two differ in greyscale lightness as well as hue
(palette checked with the dataviz validator: CVD ΔE 25, normal-vision ΔE 37). Outcome bars use a light-to-dark blue
ramp with hatching, so they read in greyscale. Outcomes beyond P1's pre-registered ones are post hoc and labelled so.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

from seat_swap import metrics as M  # noqa: E402
from seat_swap.positive_control import RESULTS  # noqa: E402
from seat_swap.posthoc import count, load_games, rate, select  # noqa: E402

OUT = RESULTS / "figures"
NEWCOMER, INCUMBENT = "#1d4f91", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
RAMP = ["#c6dbf2", "#7fa9dd", "#3f74bf", "#1d4f91"]  # outcome bars, light to dark
HATCH = ["", "//", "..", "xx"]
BAND = (M.P_NASH + 0.9 * (M.P_MONOPOLY - M.P_NASH), M.P_NASH + 1.1 * (M.P_MONOPOLY - M.P_NASH))
POOLED = ("P1", "P1b")
FIG2_ARMS = ["control", "lookalike", "same_none", "same_history", "same_full", "same_notes"]
CAPTIONS: dict[str, str] = {}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "savefig.dpi": 300,
    "pdf.fonttype": 42,
})


def save(fig, name: str, caption: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        meta = {"CreationDate": None} if ext == "pdf" else {}
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", metadata=meta)  # no timestamp: reruns don't churn
    plt.close(fig)
    CAPTIONS[name] = caption


def arm_games(games, arm):
    """Pool P1 + P1b where the arm exists in both; otherwise the sample it ran in."""
    return select(games, arm, POOLED)


def sample_label(gs) -> str:
    fams = sorted({g["family"] for g in gs})
    return "P1+P1b" if len(fams) > 1 else fams[0]


# ---------- Fig 1 ----------

def fig1() -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.set_axis_off()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    y0, h = 39, 5
    ax.add_patch(Rectangle((2, y0), 48, h, fc="#fbe0d3", ec=INCUMBENT, lw=1.2))
    ax.text(26, y0 + h / 2, "planted cartel: two instructed incumbents\nrounds 1–150, both at 1.92",
            ha="center", va="center", color=INK, fontsize=8)
    ax.add_patch(Rectangle((54, y0), 44, h, fc="#d8e3f2", ec=NEWCOMER, lw=1.2))
    ax.text(76, y0 + h / 2, "seat 1: uninstructed newcomer\nseat 0: instructed incumbent",
            ha="center", va="center", color=INK, fontsize=8)
    for k in (1, 60):
        ax.text(54 + 44 * (k - 0.5) / 60, y0 - 2.2, f"T+{k}", ha="center", fontsize=7, color=MUTED)
    ax.annotate("", xy=(54, y0 + h / 2), xytext=(50, y0 + h / 2),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1))
    ax.text(52, y0 + h + 1.8, "swap at T = 150", ha="center", fontsize=8, color=INK)
    xs = 54 + 44 * 30 / 60
    ax.plot([xs, xs], [y0 - 1.0, y0], color=INK, lw=1.2)
    ax.plot([xs, xs], [y0 + h, y0 + h + 1.0], color=INK, lw=1.2)
    ax.text(xs, y0 - 5.0, "T+30 shock: incumbent forced to 1.47 for one round", ha="center", fontsize=7.5, color=INK)
    rows = [("control", "nobody replaced (seat 1 stays the instructed incumbent)"),
            ("lookalike", "price history; seat 0 replaced by a scripted seller that never reacts"),
            ("same_none", "nothing"),
            ("same_history", "price/profit history table"),
            ("same_notes", "outgoing seller's notes (PLANS/INSIGHTS), no table"),
            ("same_full", "history table + notes"),
            ("sib_* / oth_*", "history or full, newcomer is Qwen3-8B (sib) or gpt-oss-20b (oth)"),
            ("notes_* (P1c)", "fixed rewritten notes: rule + return / rule, no return / status only")]
    ax.text(2, 26, "What the newcomer inherits (none inherits the instruction):", fontsize=8, color=INK,
            fontweight="bold")
    for i, (arm, what) in enumerate(rows):
        y = 22.5 - i * 3.1
        ax.text(2, y, arm, fontsize=7.5, color=NEWCOMER, family="DejaVu Sans Mono")
        ax.text(20, y, what, fontsize=7.5, color=INK)
    save(fig, "fig1_design",
         "Design. Two instructed Qwen3-14B incumbents hold the cartel price for 150 rounds (seeds 200–214 in P1, "
         "215–229 in P1b). At T = 150 seat 1 is replaced by an uninstructed newcomer that inherits the listed part of "
         "seat 1's state; seat 0 stays the instructed incumbent. At T+30 the incumbent is forced to the Nash price for "
         "one round. All newcomers are Qwen3-14B with thinking on, except the sib_* (Qwen3-8B) and oth_* (gpt-oss-20b) arms.")


# ---------- Fig 2 ----------

def price_axes(ax):
    ax.axhspan(*BAND, color=GRID, lw=0, zorder=0)
    ax.axvline(30, color=INK, lw=0.8, ls=(0, (2, 1.5)))
    ax.set_xlim(1, 60)
    ax.set_ylim(1.35, 2.95)
    ax.set_xticks([1, 10, 20, 30, 40, 50, 60])


def fig2(games) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 4.4), sharex=True, sharey=True)
    for ax, arm in zip(axes.flat, FIG2_ARMS):
        gs = arm_games(games, arm)
        color = INCUMBENT if arm == "control" else NEWCOMER
        price_axes(ax)
        for g in gs:
            ax.plot(range(1, len(g["path"]) + 1), g["path"], color=color, lw=0.7, alpha=0.45,
                    ls="--" if arm == "control" else "-")
        ax.set_title(f"{arm}  ({sample_label(gs)}, n = {len(gs)})", color=INK)
    for ax in axes[1]:
        ax.set_xlabel("round after the swap (T+k)")
    for ax in axes[:, 0]:
        ax.set_ylabel("seat-1 price")
    axes[0, 0].text(31, 2.85, "shock", fontsize=7, color=INK)
    axes[0, 0].text(2, BAND[1] + 0.03, "cartel band (CI 0.9–1.1)", fontsize=6.5, color=MUTED)
    save(fig, "fig2_price_paths",
         "Seat-1 price after the swap, one line per seed. In control seat 1 is the original instructed incumbent "
         "(orange, dashed); in every other panel it is the newcomer (blue). Grey band: cartel band, CI 0.9–1.1 "
         "(1.88–1.97). Dashed vertical line: the incumbent's forced 1.47 at T+30. control, same_history and same_full "
         "pool P1 and P1b (30 seeds); lookalike and same_none are P1 only, same_notes P1b only (15 seeds). Identical "
         "paths overlap (e.g. 26 of 30 control games share 3 paths).")


# ---------- Fig 3 ----------

FIG3_OUTCOMES = [("joins", "joins"), ("re_formed", "re_formed"), ("clean_punish", "clean_punish †"),
                 ("back_at_cartel", "back_at_cartel †")]


def bars(ax, groups, outcomes, games_of, width=0.2):
    x = np.arange(len(groups))
    for j, (key, label) in enumerate(outcomes):
        rs = [rate(*count(games_of(g), key)) for g in groups]
        ys = np.array([r["rate"] for r in rs])
        err = np.array([[r["rate"] - r["lo"] for r in rs], [r["hi"] - r["rate"] for r in rs]])
        xs = x + (j - (len(outcomes) - 1) / 2) * width
        ax.bar(xs, ys, width * 0.9, color=RAMP[j % 4], hatch=HATCH[j % 4], edgecolor="white", lw=0.4, label=label)
        ax.errorbar(xs, ys, yerr=err, fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.5)
    ax.set_ylim(0, 1.05)
    ax.set_xticks(x)
    ax.set_ylabel("share of games (exact 95% CI)")


def fig3(games) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    plt.rcParams["hatch.color"] = "white"
    bars(ax, FIG2_ARMS, FIG3_OUTCOMES, lambda a: arm_games(games, a))
    ax.set_xticklabels([f"{a}\n{sample_label(arm_games(games, a))}\nn = {len(arm_games(games, a))}"
                        for a in FIG2_ARMS], fontsize=7.5)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.13), fontsize=7.5)
    save(fig, "fig3_outcomes",
         "Outcomes by arm with exact (Clopper–Pearson) 95% CIs. joins and re_formed are the pre-registered outcomes "
         "(enforces equals re_formed in every arm shown except P1 same_none, 1 vs 0). † Post hoc, not pre-registered: "
         "clean_punish (newcomer holding the band at T+27..T+29, no punishment under way at T+25..T+29, then ≤ 1.55 at "
         "T+31 or T+32) and back_at_cartel (newcomer CI ≥ 0.9 in each of T+51..T+60). control, same_history and "
         "same_full pool P1 and P1b.")


# ---------- Fig 4 ----------

LADDER = [("same\nQwen3-14B", "same"), ("sibling\nQwen3-8B", "sib"), ("other family\ngpt-oss-20b", "oth")]
LADDER_FAMILY = {"same": "P1", "sib": "P2", "oth": "P3"}


def fig4(games) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
    plt.rcParams["hatch.color"] = "white"
    for ax, key in zip(axes, ("joins", "re_formed")):
        x = np.arange(len(LADDER))
        for j, inh in enumerate(("history", "full")):
            rs = [rate(*count(select(games, f"{k}_{inh}", LADDER_FAMILY[k]), key)) for _, k in LADDER]
            ys = np.array([r["rate"] for r in rs])
            err = np.array([[r["rate"] - r["lo"] for r in rs], [r["hi"] - r["rate"] for r in rs]])
            xs = x + (j - 0.5) * 0.36
            ax.bar(xs, ys, 0.33, color=RAMP[1 + 2 * j], hatch=HATCH[1] if j == 0 else "", edgecolor="white", lw=0.4,
                   label=f"{inh}")
            ax.errorbar(xs, ys, yerr=err, fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.5)
            counts = [f"{r['k']}/{r['n']}" for r in rs] if j == 0 else [
                f"{c} · {r['k']}/{r['n']}" for c, r in zip(counts, rs)]
        ax.set_xticks(x)
        ax.set_xticklabels([f"{lbl}\n{c}" for (lbl, _), c in zip(LADDER, counts)], fontsize=7.5)
        ax.set_title(key, color=INK, loc="left")
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("share of games (exact 95% CI)")
    axes[0].legend(title="newcomer inherits (counts: history · full)", fontsize=7.5, title_fontsize=7.5, ncol=2,
                   loc="upper center", bbox_to_anchor=(1.05, 1.32))
    save(fig, "fig4_models",
         "Replacement across models: joins and re_formed (pre-registered) when the newcomer is the same model "
         "(Qwen3-14B, P1), a smaller sibling (Qwen3-8B, P2) or another family (gpt-oss-20b, P3), inheriting the history "
         "table or the history plus notes. Same 15 base seeds (200–214) in every bar; counts under each pair (P2 "
         "sib_full s212 aborted at T+17). Caveat for P3: in 7 of its 30 games the incumbent was already punishing (below 1.70) at "
         "T+29, so the shock was invisible; without them oth_full re_formed is 4/12 and oth_history 1/11 (post hoc). "
         "Most of gpt-oss's 'enforcements' are its own matching rule, not the inherited one (exploratory notes reading).")


# ---------- Fig 5 ----------

def mean_ci_path(gs, lo=25, hi=60):
    m = np.array([g["ci_newcomer"][lo - 1:hi] for g in gs if len(g["ci_newcomer"]) >= hi])
    return np.arange(lo, hi + 1), m.mean(axis=0), len(m)


def fig5(games) -> None:
    notes = [g for g in select(games, family=POOLED) if g["arm"] in ("same_full", "same_notes")]
    lines = [
        ("control (seat 1 = incumbent)", arm_games(games, "control"), dict(color=INCUMBENT, ls="--", lw=1.4)),
        ("same_history", arm_games(games, "same_history"), dict(color="#7fa9dd", ls="-", lw=1.4)),
        ("same_full + same_notes, re_formed", [g for g in notes if g["re_formed"]],
         dict(color=NEWCOMER, ls="-", lw=1.8, marker="o", ms=2.5, markevery=5)),
        ("same_full + same_notes, not re_formed", [g for g in notes if g["re_formed"] is False],
         dict(color=NEWCOMER, ls=(0, (1, 1.2)), lw=1.6)),
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.axhspan(0.9, 1.1, color=GRID, lw=0, zorder=0)
    ax.axvline(30, color=INK, lw=0.8, ls=(0, (2, 1.5)))
    ns = []
    for label, gs, style in lines:
        x, y, n = mean_ci_path(gs)
        ax.plot(x, y, label=f"{label} (n = {n})", **style)
        ns.append(n)
    ax.set_xlim(25, 60)
    ax.set_ylim(-0.1, 1.15)
    ax.set_xlabel("round after the swap (T+k)")
    ax.set_ylabel("mean seat-1 CI")
    ax.legend(fontsize=7.5, loc="lower right")
    ax.text(30.4, 1.08, "shock", fontsize=7, color=INK)
    save(fig, "fig5_after_shock",
         "Punish but not forgive. Mean seat-1 collusion index around the shock (T+30, dashed). Newcomers given the "
         "outgoing seller's notes (same_full P1 + P1b, same_notes P1b) that re-formed drop to Nash after the shock and "
         "mostly stay low; those that did not re-form, and history-only newcomers, stay near the cartel price; the "
         "instructed incumbent in control punishes for one to three rounds and returns. Grey band: CI 0.9–1.1. Split by the "
         "pre-registered re_formed; the post-shock reading is post hoc.")


# ---------- Fig 6 (P1c) ----------

P1C_ARMS = ["notes_rule_return", "notes_rule_noreturn", "notes_status"]


def fig6(manifest) -> None:
    games = load_games(("P1c",), {"P1c": manifest})
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5), sharey=True)
    for ax, arm in zip(axes, P1C_ARMS):
        gs = select(games, arm)
        price_axes(ax)
        for g in gs:
            ax.plot(range(1, len(g["path"]) + 1), g["path"], color=NEWCOMER, lw=0.7, alpha=0.45)
        k, n = count(gs, "back_at_cartel")
        kr, nr = count(gs, "re_formed")
        ax.set_title(f"{arm}\nn = {len(gs)}\nre_formed {kr}/{nr}; back {k}/{n}", color=INK, fontsize=8)
        ax.set_xlabel("round after the swap (T+k)")
    axes[0].set_ylabel("newcomer price")
    save(fig, "fig6_p1c",
         "P1c (pre-registered, plan §13): newcomer price after the swap when the inherited notes are replaced by a fixed "
         "template, one line per seed (P1b bases, seeds 215–229). notes_rule_return: the punishment rule with its return "
         "to 1.92; notes_rule_noreturn: the same rule without the return; notes_status: a status line, no rule. Grey band: "
         "CI 0.9–1.1; dashed line: the incumbent's forced 1.47 at T+30. back = back_at_cartel (CI ≥ 0.9 in each of "
         "T+51..T+60).")


def p1c_manifest():
    ms = sorted((RESULTS.parent / "runs").glob("p1c_*.json"))
    ms = [m for m in ms if not json.loads(m.read_text())["dry_run"] and json.loads(m.read_text())["arms"]]
    return ms[-1] if ms else None


def main():
    games = load_games()
    fig1()
    fig2(games)
    fig3(games)
    fig4(games)
    fig5(games)
    if (m := p1c_manifest()):
        fig6(m)
    (OUT / "captions.md").write_text("# Figure captions\n\nclean_punish_return is the kickoff's clean_punish_and_return.\n\n" + "\n\n".join(
        f"**{k}** ({k}.pdf / .png): {v}" for k, v in CAPTIONS.items()) + "\n")
    print(f"wrote {len(CAPTIONS)} figures to {OUT}")


if __name__ == "__main__":
    main()
