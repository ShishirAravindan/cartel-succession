"""Paper figures (Kickoff 09 §3) from the run logs, via posthoc.load_games.

    uv run --project seat_swap python -m seat_swap.figures

Writes fig1_design .. fig3_after_shock and figA1_price_paths .. figA5_oth_history, numbered as in the paper
(figA3_templates once a P1c manifest has finished games; PDF + PNG), plus captions.md, to seat_swap/results/figures/.

Style (shared with the paper, paper/main.typ): sized for a 6.5 in text width; Old Standard TT at 9 pt (the caption size; 7 pt minimum) for all text,
IBM Plex Mono for code identifiers (outcome names such as re_formed, via code()), both loaded from paper/fonts; panel
letters; readable arm names; no in-figure titles beyond panel labels (the caption carries the message).
- Price paths are seed x round heatmaps of the collusion index: every game is one row, sorted by its post-shock CI, so
  identical paths don't hide each other. One-hue pastel blue ramp (pale = Nash, deep = monopoly): monotone lightness
  and one hue pass the dataviz ordinal checks; its pale end is deliberately below the 2:1 surface-contrast floor (meant
  for lone marks) so that collapse to Nash reads at a glance, and every heatmap gets a hairline frame instead. CI above
  the band (> 1.1) gets a separate sand colour so overpricing never reads as "very collusive".
- Outcomes are dot plots with exact (Clopper-Pearson) 95% intervals, not bars.
- Identity: newcomer blue, incumbent green, each a mid-tone stroke with a pastel tint for fills and bands (dataviz
  validator on the strokes: CVD dE 15.7, normal-vision dE 16.9); context in warm grey.
Outcomes beyond P1's pre-registered ones are post hoc and labelled so (dagger).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from seat_swap import metrics as M  # noqa: E402
from seat_swap.positive_control import RESULTS  # noqa: E402
from seat_swap.posthoc import count, load_games, rate, select  # noqa: E402

OUT = RESULTS / "figures"
FONTS = Path(__file__).resolve().parents[1] / "paper" / "fonts"
TEXTW = 6.5  # inches, full text width (Apart template: US letter, 1 in margins)
NEWCOMER, INCUMBENT = "#3567a0", "#2f8a5f"
NEWCOMER_TINT, INCUMBENT_TINT = "#dde8f4", "#dcefe4"
INK, MUTED, GRID, CONTEXT, CONTEXT2 = "#22252a", "#62605b", "#ebe9e4", "#8f8c86", "#c2bfb8"
OVER = "#e8c27a"  # sand: CI above the cartel band
CI_CMAP = LinearSegmentedColormap.from_list("ci", ["#f5f8fc", "#dae6f3", "#b5cde8", "#8daedb", "#6990c6", "#4d78b2"])
CI_CMAP.set_over(OVER)
CI_CMAP.set_under("#f5f8fc")
CI_CMAP.set_bad("#f2f1ee")
CI_MIN, CI_MAX = 0.0, 1.1
BAND = (M.P_NASH + 0.9 * (M.P_MONOPOLY - M.P_NASH), M.P_NASH + 1.1 * (M.P_MONOPOLY - M.P_NASH))
POOLED = ("P1", "P1b")
# Typst labels of the figures (@fig:<key> in captions and in paper/main.typ)
FIG_FILE = {"design": "fig1_design", "paths": "figA1_price_paths", "outcomes": "fig2_outcomes", "models": "figA4_models",
            "shock": "fig3_after_shock", "p1c": "figA3_templates", "oth": "figA5_oth_history",
            "lookalike": "figA2_lookalike"}
CAPTIONS: dict[str, str] = {}

SHORT = {"control": "Control", "lookalike": "Look-alike", "same_none": "Blank", "same_history": "History",
         "same_notes": "Notes", "same_full": "History + notes"}
LABEL = {
    "control": "Control (no swap)",
    "lookalike": "Look-alike incumbent",
    "same_none": "Blank",
    "same_history": "History",
    "same_notes": "Notes",
    "same_full": "History + notes",
    "notes_rule_return": "Template: rule + return",
    "notes_rule_noreturn": "Template: rule, no return",
    "notes_status": "Template: status only",
}

for _f in sorted(FONTS.glob("*.ttf")):
    font_manager.fontManager.addfont(str(_f))
SERIF, MONO = "Old Standard TT", "IBM Plex Mono"

plt.rcParams.update({
    "font.family": "serif", "font.serif": [SERIF, "DejaVu Serif"],
    "mathtext.fontset": "custom", "mathtext.rm": SERIF, "mathtext.it": f"{SERIF}:italic", "mathtext.tt": MONO,
    "mathtext.bf": SERIF, "mathtext.sf": SERIF, "mathtext.cal": SERIF,
    "axes.unicode_minus": True,
    "font.size": 9, "axes.titlesize": 9, "axes.labelsize": 9, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "legend.fontsize": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.6, "xtick.major.width": 0.6,
    "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False, "legend.frameon": False,
    "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42, "axes.titlelocation": "left",
})


def code(name: str) -> str:
    """An identifier in the code font (mathtext tt = IBM Plex Mono), as the paper sets it."""
    return r"$\mathtt{" + name.replace("_", r"\_") + "}$"


def save(fig, name: str, caption: str) -> None:
    """The paper places figures at their natural size, so the cropped figure must fit the text width."""
    OUT.mkdir(parents=True, exist_ok=True)
    w = fig.get_tightbbox(fig.canvas.get_renderer()).width
    if w > TEXTW:
        print(f"warning: {name} is {w:.2f} in wide, over the {TEXTW} in text width")
    for ext in ("pdf", "png"):
        meta = {"CreationDate": None} if ext == "pdf" else {}
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", pad_inches=0.02, metadata=meta)  # no timestamp
    plt.close(fig)
    CAPTIONS[name] = caption


def arm_games(games, arm):
    """Pool P1 + P1b where the arm exists in both; otherwise the sample it ran in."""
    return select(games, arm, POOLED)


def sample_label(gs) -> str:
    fams = sorted({g["family"] for g in gs})
    return "P1+P1b" if len(fams) > 1 else fams[0]


def panel_title(ax, letter: str, text: str, right: str = "", pad: float = 4, size: float = 9) -> None:
    ax.set_title(f"({letter})  {text}", fontsize=size, color=INK, pad=pad)
    if right:
        ax.text(1.0, 1.0, right, transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=MUTED)
        ax.title.set_position((0, 1))


# ---------- Fig 1: design ----------

def fig1() -> None:
    fig, ax = plt.subplots(figsize=(TEXTW - 0.25, 1.75))
    ax.set_axis_off()
    ax.set_xlim(-14, 101)
    ax.set_ylim(-1.55, 2.05)
    # compressed time axis: base rounds 1..150 -> 0..36, branch T+1..T+60 -> 40..100
    xb = lambda r: 36 * r / 150  # noqa: E731
    xt = lambda k: 40 + 60 * k / 60  # noqa: E731
    h = 0.5

    def bar(x0, x1, y, fc, ec, text):
        ax.add_patch(FancyBboxPatch((x0, y - h / 2), x1 - x0, h, boxstyle="round,pad=0,rounding_size=0.12",
                                    fc=fc, ec=ec, lw=0.7))
        ax.text((x0 + x1) / 2, y, text, ha="center", va="center", fontsize=8, color=INK)

    for y, name in ((1.25, "Seat 0"), (0.45, "Seat 1")):
        ax.text(-1.5, y, name, ha="right", va="center", fontsize=8.5, color=INK)
    bar(xb(0), xb(150), 1.25, INCUMBENT_TINT, INCUMBENT, "instructed incumbent")
    bar(xt(0), xt(60), 1.25, INCUMBENT_TINT, INCUMBENT, "instructed incumbent")
    bar(xb(0), xb(150), 0.45, INCUMBENT_TINT, INCUMBENT, "instructed incumbent")
    bar(xt(0), xt(60), 0.45, NEWCOMER_TINT, NEWCOMER, "newcomer without the instruction")
    # swap
    ax.plot([38, 38], [0.05, 1.65], color=INK, lw=0.8)
    ax.text(38, 1.95, "swap at T = 150: newcomer inherits nothing, history, notes or both", ha="center",
            va="center", fontsize=8, color=INK)
    # shock
    xs = xt(30)
    ax.plot([xs], [1.25 + h / 2 + 0.12], marker="v", ms=4.5, color=INK, clip_on=False)
    ax.text(xs + 1.8, 1.25 + h / 2 + 0.14, "shock at T+30: incumbent forced to Nash for one round",
            ha="left", va="center", fontsize=7.5, color=INK)
    # time axis
    ax.plot([xb(0), xb(150)], [-0.12, -0.12], color=MUTED, lw=0.6)
    ax.plot([xt(0), xt(60)], [-0.12, -0.12], color=MUTED, lw=0.6)
    for x, lab, ha in ((xb(0), "1", "center"), (xb(150), "150", "right"), (xt(1), "T+1", "left"),
                       (xt(30), "T+30", "center"), (xt(60), "T+60", "center")):
        ax.plot([x, x], [-0.12, -0.2], color=MUTED, lw=0.6)
        ax.text(x, -0.36, lab, ha=ha, va="center", fontsize=7.5, color=MUTED)
    ax.text(xb(75), -0.62, "base rounds, both at 1.92 throughout", ha="center", va="center", fontsize=7.5,
            color=MUTED)
    # outcome windows
    for (k0, k1), lab, y in (((20, 29), code("joins"), -0.8), ((27, 33), code("enforces"), -1.25), ((51, 60), code("back_at_cartel") + " †", -0.8)):
        ax.plot([xt(k0 - 0.5), xt(k1 + 0.5)], [y, y], color=NEWCOMER, lw=1.6, solid_capstyle="butt")
        ax.text(xt(k1 + 0.5) + 0.8, y, lab, ha="left", va="center", fontsize=7, color=INK)
    save(fig, "fig1_design",
         "Design. Two instructed Qwen3-14B incumbents hold the cartel price of 1.92 for 150 rounds. At T = 150 "
         "seat 1 is replaced by a newcomer that inherits nothing, the history, the notes or both, but never the "
         "manager's instruction; at T+30 the incumbent is forced to the Nash price for one round. Green: instructed "
         "incumbent; blue: newcomer. Blue bars mark the outcome windows († post hoc). The base phase is "
         "compressed.")


# ---------- heatmaps (Figs A1, A3, A5) ----------

def ci_matrix(gs, key="path", order=None):
    """Rows = games, columns = T+1..T+60, CI of `key`'s price; short games padded with NaN."""
    m = np.full((len(gs), 60), np.nan)
    for i, g in enumerate(gs):
        p = np.asarray(g[key], dtype=float)
        m[i, :len(p)] = M.ci(p)
    if order is None:  # most collusive after the shock on top
        post = np.nanmean(m[:, 33:60], axis=1)
        order = np.argsort(-np.nan_to_num(post, nan=-9), kind="stable")
    return m[order], order


def heat(ax, m, xlabel=True, ylabel=True):
    im = ax.imshow(m, aspect="auto", cmap=CI_CMAP, vmin=CI_MIN, vmax=CI_MAX, interpolation="nearest",
                   extent=(0.5, 60.5, len(m) + 0.5, 0.5))
    ax.set_xticks([1, 10, 20, 30, 40, 50, 60])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_linewidth(0.4)
        s.set_color(CONTEXT)
    ax.tick_params(axis="x", length=2)
    ax.plot([30], [1.0], marker="v", ms=3.2, color=INK, clip_on=False, markeredgewidth=0,
            transform=ax.get_xaxis_transform())
    ax.set_ylim(len(m) + 0.5, 0.5)
    if xlabel:
        ax.set_xlabel("round after the swap (T+k)")
    if ylabel:
        ax.set_ylabel("games", color=MUTED)
    return im


def ci_colorbar(fig, im, cax, horizontal=False):
    cb = fig.colorbar(im, cax=cax, extend="max", extendfrac=0.06, ticks=[0, 0.5, 1.0],
                      orientation="horizontal" if horizontal else "vertical")
    labels = ["0\nNash", "0.5", "1\nmonopoly"] if horizontal else ["0  Nash", "0.5", "1  monopoly"]
    (cb.ax.set_xticklabels if horizontal else cb.ax.set_yticklabels)(labels)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2, labelsize=7.5)
    cb.ax.set_title("collusion index (CI)" if horizontal else "CI", fontsize=8, color=INK, loc="left", pad=4 if horizontal else 6)
    return cb


# ---------- Fig A1 ----------

FIGA1_LAYOUT = [["control", "same_history", "same_full"], ["same_none", "same_notes", None]]


def figA1(games) -> None:
    fig = plt.figure(figsize=(TEXTW, 2.75))
    gs_ = fig.add_gridspec(2, 3, height_ratios=[30, 15], hspace=0.55, wspace=0.2)
    letters = iter("abcde")
    im = None
    for r, row in enumerate(FIGA1_LAYOUT):
        for c, arm in enumerate(row):
            if arm is None:
                continue
            ax = fig.add_subplot(gs_[r, c])
            gs = arm_games(games, arm)
            m, _ = ci_matrix(gs)
            im = heat(ax, m, xlabel=(r == 1 and c == 1), ylabel=(c == 0))
            panel_title(ax, next(letters), SHORT[arm], f"n = {len(gs)}", pad=7)
            if r == 0:
                ax.set_xticklabels([])
    # the free bottom-right cell holds the colour key, horizontal
    cell = gs_[1, 2].subgridspec(3, 1, height_ratios=[1, 0.32, 1.6])
    ci_colorbar(fig, im, fig.add_subplot(cell[1]), horizontal=True)
    save(fig, "figA1_price_paths",
         "Seat-1 collusion index after the swap, one row per game, sorted by mean CI over T+34..T+60. (a) Control: "
         "the instructed incumbent; (b)–(e): the newcomer without the instruction, by what it inherits. Triangle: the shock at "
         "T+30. Pale blue is near Nash, deep blue near monopoly; sand marks rounds with CI above 1.1. (a)–(c): all "
         "30 bases; (d) Set A; (e) Set B.")


# ---------- dot plots (Figs 2, A4) ----------

def dot(ax, y, r, color, filled=True, label_counts=True):
    ax.plot([r["lo"], r["hi"]], [y, y], color=color, lw=1.0, solid_capstyle="butt", zorder=2)
    ax.plot([r["rate"]], [y], marker="o", ms=4.2, color=color, mfc=color if filled else "white", mew=1.0, zorder=3)
    if label_counts:
        ax.text(1.04, y, f"{r['k']}/{r['n']}", transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=7.5, color=MUTED)


def share_axis(ax, ylim):
    ax.set_xlim(-0.03, 1.03)
    ax.set_xticks([0, 0.5, 1])
    ax.set_xticklabels(["0", ".5", "1"])
    ax.set_ylim(*ylim)
    ax.invert_yaxis()
    for x in (0, 0.5, 1):
        ax.axvline(x, color=GRID, lw=0.6, zorder=0)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)


FIG2_ARMS = ["control", "same_none", "same_history", "same_notes", "same_full"]
FIG2_OUTCOMES = [("joins", code("joins")), ("re_formed", code("re_formed")), ("clean_punish", code("clean_punish") + " †"),
                 ("back_at_cartel", code("back_at_cartel") + " †")]


def fig2(games) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(TEXTW - 0.36, 1.8), sharey=True, gridspec_kw=dict(wspace=0.62))
    for j, (ax, (key, title)) in enumerate(zip(axes, FIG2_OUTCOMES)):
        for i, arm in enumerate(FIG2_ARMS):
            gs = arm_games(games, arm)
            dot(ax, i, rate(*count(gs, key)), INCUMBENT if arm == "control" else NEWCOMER)
        share_axis(ax, (-0.6, len(FIG2_ARMS) - 0.4))
        panel_title(ax, "abcd"[j], title, size=8)  # code-font titles run wide
        ax.set_xlabel("share of games")
    axes[0].set_yticks(range(len(FIG2_ARMS)))
    axes[0].set_yticklabels([SHORT[a] for a in FIG2_ARMS], color=INK)
    save(fig, "fig2_outcomes",
         "Outcomes by what the newcomer inherits: share of games with exact 95% intervals, and counts. † Post hoc."
         " Green: Control (the instructed incumbent). `enforces` equals `re_formed` in every arm except Blank (1"
         " vs 0). Control, History and History + notes: all 30 bases; Blank: Set A; Notes: Set B.")


LADDER = [("Qwen3-14B (same)", "same"), ("Qwen3-8B (sibling)", "sib"), ("gpt-oss-20b (other family)", "oth")]
LADDER_FAMILY = {"same": "P1", "sib": "P2", "oth": "P3"}


def figA4(games) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(TEXTW - 0.45, 1.6), sharey=True, gridspec_kw=dict(wspace=0.3))
    for j, (ax, (key, title)) in enumerate(zip(axes, (("joins", code("joins")), ("re_formed", code("re_formed"))))):
        for i, (_, k) in enumerate(LADDER):
            for dy, inh, filled in ((-0.17, "history", False), (0.17, "full", True)):
                r = rate(*count(select(games, f"{k}_{inh}", LADDER_FAMILY[k]), key))
                grey = key == "re_formed" and k == "oth"  # P3 shock outcomes are not interpretable (review b5)
                dot(ax, i + dy, r, CONTEXT2 if grey else NEWCOMER, filled)
        share_axis(ax, (-0.55, len(LADDER) - 0.45))
        panel_title(ax, "ab"[j], title)
        ax.set_xlabel("share of games")
    axes[1].text(0.45, 1.5, "grey: price war before the\nshock, not interpretable", fontsize=7, color=MUTED,
                 va="center", ha="left")
    axes[0].set_yticks(range(len(LADDER)))
    axes[0].set_yticklabels([lbl for lbl, _ in LADDER], color=INK)
    h1 = axes[0].plot([], [], marker="o", ms=4.2, color=NEWCOMER, mfc="white", mew=1.0, ls="none")[0]
    h2 = axes[0].plot([], [], marker="o", ms=4.2, color=NEWCOMER, ls="none")[0]
    fig.legend([h1, h2], ["inherits history", "inherits history + notes"], ncol=2, loc="lower center",
               bbox_to_anchor=(0.55, 0.98), handletextpad=0.3, columnspacing=1.2)
    save(fig, "figA4_models",
         "Replacement across newcomer models on the same 15 base games (Set A): open circles inherit the "
         "history, filled circles the history and notes; exact 95% intervals and counts. `re_formed` for gpt-oss-20b "
         "(grey) is shown but not interpreted: in most of its games the incumbent is already punishing before the "
         "shock (in 7 of 30 at T+29; without those games `re_formed` is 4/12 with notes and 1/11 with history, post "
         "hoc). Qwen3-8B with history and notes has 14 games (seed 212 aborted at T+17).")


# ---------- Fig 3 ----------

def ci_band_path(gs, lo=25, hi=60):
    m = np.array([g["ci_newcomer"][lo - 1:hi] for g in gs if len(g["ci_newcomer"]) >= hi])
    mean, se = m.mean(axis=0), m.std(axis=0, ddof=1) / np.sqrt(len(m))
    return np.arange(lo, hi + 1), mean, 1.96 * se, len(m)


def fig3(games) -> None:
    notes = [g for g in select(games, family=POOLED) if g["arm"] in ("same_full", "same_notes")]
    lines = [  # context first, emphasis last
        ("History (dashed), n = {n}", arm_games(games, "same_history"), CONTEXT2, 1.1, False),
        (f"Notes arms, not {code('re_formed')}, n = {{n}}", [g for g in notes if g["re_formed"] is False], CONTEXT, 1.1, False),
        ("Control incumbent, n = {n}", arm_games(games, "control"), INCUMBENT, 1.4, True),
        (f"Notes arms, {code('re_formed')}, n = {{n}}", [g for g in notes if g["re_formed"]], NEWCOMER, 1.8, True),
    ]
    fig, ax = plt.subplots(figsize=(TEXTW - 1.15, 1.95))
    ax.axhspan(0.9, 1.1, color=GRID, lw=0, zorder=0)
    ax.axvline(30, color=MUTED, lw=0.6, zorder=1)
    ax.text(30.4, 1.13, "shock", fontsize=7.5, color=MUTED, va="bottom")
    ends = {}
    for label, gs, color, lw, band in lines:
        x, y, e, n = ci_band_path(gs)
        if band:
            ax.fill_between(x, y - e, y + e, color=color, alpha=0.15, lw=0, zorder=2)
        ax.plot(x, y, color=color, lw=lw, zorder=3, ls=(0, (3, 1.5)) if label.startswith("History") else "-")
        ends[label.replace("{n}", str(n))] = (y[-1], color)
    # direct labels at the right end, nudged apart
    ys = sorted(ends.items(), key=lambda kv: kv[1][0])
    placed = []
    for lab, (yv, color) in ys:
        yl = max(yv, placed[-1] + 0.085) if placed else yv
        placed.append(yl)
        ax.text(60.8, yl, lab, fontsize=7.5, color=INK if color in (CONTEXT, CONTEXT2) else color, va="center")
    ax.set_xlim(25, 60)
    ax.set_ylim(-0.08, 1.2)
    ax.set_xticks([25, 30, 35, 40, 45, 50, 55, 60])
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlabel("round after the swap (T+k)")
    ax.set_ylabel("mean seat-1 CI")
    save(fig, "fig3_after_shock",
         "Triggered, then undercut. Mean seat-1 CI around the shock (T+30), with 95% intervals for the two "
         "highlighted groups. Notes-arm newcomers scored `re_formed` (History + notes and Notes) cut "
         "to about Nash and mostly stay low (4 of 18 `back_at_cartel`). The instructed "
         "incumbent in Control punishes for one to four rounds (three in 23 of 30) and returns. Grey: notes-arm "
         "newcomers not scored `re_formed`, and History (dashed). The split is pre-registered; this reading of it "
         "is post hoc.")


# ---------- Fig A3 (P1c) ----------

P1C_ARMS = ["notes_rule_return", "notes_rule_noreturn", "notes_status"]


def figA3(manifest) -> None:
    games = load_games(("P1c",), {"P1c": manifest})
    fig = plt.figure(figsize=(TEXTW, 1.55))
    gs_ = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 0.045], wspace=0.2)
    im = None
    for c, arm in enumerate(P1C_ARMS):
        ax = fig.add_subplot(gs_[0, c])
        gs = select(games, arm)
        m, _ = ci_matrix(gs)
        im = heat(ax, m, xlabel=(c == 1), ylabel=(c == 0))
        panel_title(ax, "abc"[c], LABEL[arm].replace("Template: ", ""), pad=7)
    ci_colorbar(fig, im, fig.add_subplot(gs_[0, 3]))
    save(fig, "figA3_templates",
         "Template experiment (pre-registered): newcomer collusion index when the inherited notes are replaced by a "
         "fixed template; one row per game (Set B), sorted by mean CI over T+34..T+60. (a) the punishment "
         "rule with its return to 1.92; (b) the same rule without the return; (c) a status line, no rule. Triangle: "
         "the incumbent's forced Nash price at T+30. 15 games per panel. `re_formed`: 3/15, 4/15, 0/15; `back_at_cartel` "
         "(CI ≥ 0.9 in each of T+51..T+60): 8/15, 10/15, 10/15. Colour scale as in @fig:paths.")


# ---------- Fig A5 (P3 history arm) ----------

def figA5(games) -> None:
    gs = select(games, "oth_history", "P3")
    fig = plt.figure(figsize=(TEXTW, 1.6))
    gs_ = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.03], wspace=0.16)
    m_new, order = ci_matrix(gs, "path")
    m_inc, _ = ci_matrix(gs, "path_incumbent", order=order)  # same row order: row i is the same game in both panels
    ax = fig.add_subplot(gs_[0, 0])
    im = heat(ax, m_new)
    panel_title(ax, "a", "Newcomer (gpt-oss-20b)", f"n = {len(gs)}", pad=7)
    ax = fig.add_subplot(gs_[0, 1])
    heat(ax, m_inc, ylabel=False)
    panel_title(ax, "b", "Incumbent (instructed Qwen3-14B)", pad=7)
    ci_colorbar(fig, im, fig.add_subplot(gs_[0, 2]))
    save(fig, "figA5_oth_history",
         "Where the gpt-oss-20b history-only newcomer goes (Set A; post hoc, descriptive). Row i is the "
         "same game in both panels, sorted by the newcomer's mean CI over T+34..T+60. (a) The newcomer opens high (2.00 "
         "or more at T+1 in 11 of 15 games), drifts below the incumbent's 1.70 trigger within a few rounds and settles "
         "at 1.65–1.70 (median 1.66, CI about 0.41): neither the cartel price nor Nash. (b) The incumbent starts "
         "punishing before the shock in 13 of 15 games and keeps restarting (a median of 3 punishments per game, 17% of "
         "its rounds below 1.70); 52 of its 61 punishments break its own rule, which restarts only after a round in "
         "which both priced at 1.90 or more. Triangle: the forced Nash price at T+30. Colour scale as in @fig:paths.")


# ---------- Fig A2 (Look-alike) ----------

def figA2(games) -> None:
    gs = arm_games(games, "lookalike")
    fig = plt.figure(figsize=(TEXTW * 0.6, 1.5))
    gs_ = fig.add_gridspec(1, 2, width_ratios=[1, 0.045], wspace=0.08)
    m, _ = ci_matrix(gs)
    ax = fig.add_subplot(gs_[0, 0])
    im = heat(ax, m)
    ax.set_title("Look-alike", fontsize=9, color=INK, pad=7)  # one panel: no letter
    ax.text(1.0, 1.0, f"n = {len(gs)}", transform=ax.transAxes, ha="right", va="bottom", fontsize=7.5, color=MUTED)
    ci_colorbar(fig, im, fig.add_subplot(gs_[0, 1]))
    j, r = count(gs, "joins"), count(gs, "re_formed")
    save(fig, "figA2_lookalike",
         f"Look-alike control (Set A): seat 0 is a scripted seller that repeats its last price and never "
         f"reacts; the newcomer inherits the history. Newcomer collusion index, one row per game, sorted as in "
         f"@fig:paths. The newcomer joins in {j[0]}/{j[1]} games and is never scored `re_formed` ({r[0]}/{r[1]}). "
         f"Colour scale as in @fig:paths.")


def p1c_manifest():
    ms = sorted((RESULTS.parent / "runs").glob("p1c_*.json"))
    ms = [m for m in ms if not json.loads(m.read_text())["dry_run"] and json.loads(m.read_text())["arms"]]
    return ms[-1] if ms else None


def main():
    games = load_games()
    fig1()
    figA1(games)
    fig2(games)
    figA4(games)
    fig3(games)
    if (m := p1c_manifest()):
        figA3(m)
    figA5(games)
    figA2(games)
    # captions are Typst markup (`code`, @fig: references): paper/main.typ reads captions.json; captions.md is for reading
    (OUT / "captions.json").write_text(json.dumps(CAPTIONS, ensure_ascii=False, indent=1) + "\n")
    md = {k: re.sub(r"@fig:(\w+)", lambda m_: FIG_FILE[m_.group(1)], v) for k, v in CAPTIONS.items()}
    (OUT / "captions.md").write_text("# Figure captions\n\nclean_punish_return is the kickoff's clean_punish_and_return.\n\n" + "\n\n".join(
        f"**{k}** ({k}.pdf / .png): {v}" for k, v in md.items()) + "\n")
    print(f"wrote {len(CAPTIONS)} figures to {OUT}")


if __name__ == "__main__":
    main()
