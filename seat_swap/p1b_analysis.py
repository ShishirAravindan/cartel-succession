"""P1b analysis (Kickoff 07 §5–6, docs/plan.md §11): P1b alone and pooled with P1, the headline rule,
the P1 same_full enforcers' prices around the shock, and inherited-notes features vs enforcement.

    uv run --project seat_swap python -m seat_swap.p1b_analysis

Reads seat_swap/results/p1.json and p1b.json (seat_swap.p1_report) and the arm directories they
name; writes seat_swap/results/p1b_analysis.md and p1b_analysis.json.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from scipy.stats import fisher_exact

from seat_swap.p1_report import excerpt, mean, notes_at, prices_of
from seat_swap.positive_control import RESULTS, fmt

ROOT = Path(__file__).resolve().parent.parent
POOLED_ARMS = ["control", "same_history", "same_full"]
COUNTS = ["joins", "enforces", "overpriced", "re_formed"]
P1_ENFORCERS = [202, 203, 204, 205, 209, 212]  # P1 same_full enforces (Kickoff 07 §5.1)
FEATURES = {  # inherited seat-1 notes at T (PLANS + INSIGHTS), case-insensitive
    "1.70": r"1\.70\b",
    "punishment": r"punish|retaliat",
    "1.47": r"1\.47\b",
    "duration": r"\b([1-9]|10|one|two|three|four|five)\s+(consecutive\s+)?rounds?\b",
}


def count(rows, k):
    return f"{sum(bool(r.get(k)) for r in rows)}/{sum(r.get(k) is not None for r in rows)}"


def inherited(row, T):
    snap = json.loads((ROOT / row["arm_dir"] / f"snapshot_T{T}.json").read_text())
    n = snap["notes"][1]
    return f"{n['plans']}\n{n['insights']}"


def main(argv=None) -> dict:
    argv = sys.argv[1:] if argv is None else argv
    results = Path(argv[0]) if argv else RESULTS  # optional: another results directory (checks on partial runs)
    p1, p1b = (json.loads((results / f"{x}.json").read_text()) for x in ("p1", "p1b"))
    T = p1b["T"]
    rows = {"P1": p1["rows"], "P1b": p1b["rows"]}
    L = ["# P1b analysis (Kickoff 07)", "",
         f"P1 manifest `{p1['manifest']}` ({len(p1['passing'])} passing seeds); "
         f"P1b manifest `{p1b['manifest']}` ({len(p1b['passing'])} passing seeds).", ""]

    # per arm, P1b alone and pooled
    L += ["## Per arm", "", "| arm | sample | games | " + " | ".join(COUNTS) + " | mean newcomer_ci | mean retaliation |",
          "|---|---|---|" + "---|" * len(COUNTS) + "---|---|"]
    out = {"counts": {}}
    for arm in POOLED_ARMS + ["same_notes"]:
        for sample, rs in (("P1b", [r for r in rows["P1b"] if r["arm"] == arm]),
                           ("pooled", [r for s in rows.values() for r in s if r["arm"] == arm])):
            if sample == "pooled" and arm == "same_notes":
                continue
            out["counts"][f"{arm}/{sample}"] = {k: [sum(bool(r.get(k)) for r in rs), sum(r.get(k) is not None for r in rs)]
                                                for k in COUNTS}
            L.append(f"| {arm} | {sample} | {len(rs)} | " + " | ".join(count(rs, k) for k in COUNTS) +
                     f" | {fmt(mean([r.get('newcomer_ci') for r in rs]))} | {fmt(mean([r.get('retaliation') for r in rs]), '+.3f')} |")

    # headline rule (plan §11)
    c = out["counts"]
    full, hist = c["same_full/pooled"]["re_formed"], c["same_history/pooled"]["re_formed"]
    _, p = fisher_exact([[full[0], full[1] - full[0]], [hist[0], hist[1] - hist[0]]], alternative="greater")
    bf, bh = c["same_full/P1b"]["re_formed"][0], c["same_history/P1b"]["re_formed"][0]
    supported = p < 0.05 and bf > bh
    out["headline"] = {"pooled_full": full, "pooled_history": hist, "fisher_p_one_sided": p,
                       "p1b_full": bf, "p1b_history": bh, "supported": supported}
    L += ["", "## Headline rule (plan §11, fixed before the runs)", "",
          f"Pooled `re_formed`: same_full {full[0]}/{full[1]} vs same_history {hist[0]}/{hist[1]}, one-sided Fisher "
          f"p = {p:.4f}. P1b alone: same_full {bf} vs same_history {bh} ({'higher' if bf > bh else 'not higher'}). "
          f"**{'Supported' if supported else 'Not supported'}**: "
          + ("the notes carry enforcement." if supported else
             "reported as an observation in P1 that did not replicate.")]

    # seed level P1b
    L += ["", "## Seed level, P1b", "", "| arm | seed | newcomer_ci | retaliation | first_hold | joins | enforces | overpr. | re_formed |",
          "|---|---|---|---|---|---|---|---|---|"]
    yn = lambda v: "–" if v is None else ("yes" if v else "no")
    for r in rows["P1b"]:
        L.append(f"| {r['arm']} | {r['seed']} | {fmt(r.get('newcomer_ci'))} | {fmt(r.get('retaliation'), '+.3f')} | "
                 f"{'never' if r.get('first_hold') is None else 'T+' + str(r['first_hold'] - T)} | {yn(r.get('joins'))} | "
                 f"{yn(r.get('enforces'))} | {yn(r.get('overpriced'))} | {yn(r.get('re_formed'))} |")

    # §5.1 the P1 same_full enforcers around the shock
    L += ["", "## P1 same_full enforcers, T+27..T+34 (newcomer / incumbent; shock = seat 0 at 1.47 on T+30)", "",
          "| seed | retaliation | " + " | ".join(f"T+{k}" for k in range(27, 35)) + " |", "|---|---|" + "---|" * 8]
    for r in rows["P1"]:
        if r["arm"] == "same_full" and r["seed"] in P1_ENFORCERS:
            pr = prices_of(ROOT / r["arm_dir"], T, T)
            L.append(f"| {r['seed']} | {fmt(r['retaliation'], '+.3f')} | " +
                     " | ".join(f"{pr[T + k][1]:.2f} / {pr[T + k][0]:.2f}" for k in range(27, 35)) + " |")

    # §5.2 inherited notes features vs enforcement
    L += ["", "## Inherited notes (seat 1 at T) vs enforcement, same_full and same_notes, P1 + P1b", "",
          "Mentions are case-insensitive regex matches: " + ", ".join(f"{k} `{v}`" for k, v in FEATURES.items()) + ".", "",
          "| sample | arm | seed | " + " | ".join(FEATURES) + " | enforces | re_formed |", "|---|---|---|" + "---|" * (len(FEATURES) + 2)]
    out["notes_features"] = []
    for sample, rs in rows.items():
        for r in rs:
            if r["arm"] not in ("same_full", "same_notes") or not r.get("arm_dir"):
                continue
            text = inherited(r, T)
            f = {k: bool(re.search(v, text, re.I)) for k, v in FEATURES.items()}
            out["notes_features"].append({"sample": sample, "arm": r["arm"], "seed": r["seed"], **f,
                                          "enforces": r.get("enforces"), "re_formed": r.get("re_formed")})
            L.append(f"| {sample} | {r['arm']} | {r['seed']} | " + " | ".join("yes" if f[k] else "–" for k in FEATURES) +
                     f" | {yn(r.get('enforces'))} | {yn(r.get('re_formed'))} |")
    L += ["", "Totals (mentions among enforcers / among non-enforcers):", ""]
    for arm in ("same_full", "same_notes"):
        nf = [x for x in out["notes_features"] if x["arm"] == arm]
        e, ne = [x for x in nf if x["enforces"]], [x for x in nf if x["enforces"] is False]
        L.append(f"- {arm}: " + "; ".join(f"{k} {sum(x[k] for x in e)}/{len(e)} vs {sum(x[k] for x in ne)}/{len(ne)}"
                                          for k in FEATURES))

    # one same_notes excerpt
    sn = [r for r in rows["P1b"] if r["arm"] == "same_notes" and r.get("arm_dir")]
    if sn:
        r = sn[0]
        d = ROOT / r["arm_dir"]
        L += ["", f"## same_notes excerpt, seed {r['seed']}", "",
              f"- inherited at T: {inherited(r, T)[:700]}".replace("\n", " "),
              f"- written at T+1: {excerpt(notes_at(d, T + 1))}",
              f"- written at T+31 (round after the shock): {excerpt(notes_at(d, T + 31))}"]

    (results / "p1b_analysis.md").write_text("\n".join(L) + "\n")
    (results / "p1b_analysis.json").write_text(json.dumps(out, indent=2))
    print("\n".join(L))
    return out


if __name__ == "__main__":
    main()
