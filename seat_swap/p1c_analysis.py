"""P1c analysis (Kickoff 09 §4, plan §13, frozen as `prereg-p1c`).

    uv run --project seat_swap python -m seat_swap.p1c_analysis seat_swap/runs/p1c_<id>.json

Writes seat_swap/results/p1c_analysis.md and .json: per-arm counts of joins, enforces, re_formed, clean_punish,
clean_punish_return and back_at_cartel; mean post-shock CI; the two primary one-sided Fisher tests; duplicate
newcomer paths; games that did not reach T+33; one excerpt per arm of the newcomer's notes at T+31. P1b's
`same_history` and `same_notes` (same base seeds) are shown beside them for reference, with no test.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

from seat_swap.p1 import P1C_ARMS
from seat_swap.p1_report import notes_at
from seat_swap.positive_control import RESULTS
from seat_swap.posthoc import count, duplicates, fisher_greater, load_games, rate, select

T = 150
REFERENCE = ["same_history", "same_notes"]
OUTCOMES = ["joins", "enforces", "re_formed", "clean_punish", "clean_punish_return", "back_at_cartel"]
PRIMARY = [("notes_rule_return", "notes_status", "re_formed"),
           ("notes_rule_return", "notes_rule_noreturn", "back_at_cartel")]
EXCERPT_SEED = 215  # lowest seed; the first later seed with a parsed T+31 call if it has none
# descriptive, not pre-registered: is the rule still in the newcomer's own notes? (both prices mentioned)
RULE_RE = (re.compile(r"1\.47"), re.compile(r"1\.70"))
RULE_ROUNDS = (1, 10, 29)
RULE_ARMS = P1C_ARMS + ["same_notes", "same_full"]


def rule_kept(games, arm):
    out = {}
    for k in RULE_ROUNDS:
        hits = 0
        for g in select(games, arm):
            n = notes_at(Path(g["dir"]), T + k) or {}
            text = n.get("plans", "") + n.get("insights", "")
            hits += all(r.search(text) for r in RULE_RE)
        out[k] = [hits, len(select(games, arm))]
    return out


def per_arm(games, arm):
    gs = select(games, arm)
    post = [g for g in gs if g["post_ci_newcomer"] is not None]
    return {"n": len(gs), **{k: rate(*count(gs, k)) for k in OUTCOMES},
            "post_ci_newcomer": float(np.mean([g["post_ci_newcomer"] for g in post])) if post else None,
            "post_ci_market": float(np.mean([g["post_ci_market"] for g in post])) if post else None,
            "short": [g["seed"] for g in gs if g["enforces"] is None],
            "duplicates": duplicates(gs)}


def excerpt(games, arm):
    for g in sorted(select(games, arm), key=lambda g: (g["seed"] != EXCERPT_SEED, g["seed"])):
        n = notes_at(Path(g["dir"]), T + 31)
        if n:
            return {"seed": g["seed"], **n}
    return None


def main(argv=None):
    args = argv or sys.argv[1:]
    manifest = Path(args[0])
    m = json.loads(manifest.read_text())
    games = load_games(("P1c",), {"P1c": manifest}) + load_games(("P1b",))
    rule = {a: rule_kept(games, a) for a in RULE_ARMS}
    enforcers = {a: [(g["seed"], g["back_at_cartel"]) for g in select(games, a) if g["enforces"]] for a in RULE_ARMS}
    games = [g for g in games if g["family"] == "P1c" or g["arm"] in REFERENCE]
    arms = {a: per_arm(games, a) for a in P1C_ARMS + REFERENCE}
    tests = []
    for a, b, key in PRIMARY:
        ka, na = count(select(games, a), key)
        kb, nb = count(select(games, b), key)
        tests.append({"test": f"{a} > {b}, {key}", a: [ka, na], b: [kb, nb],
                      "p_one_sided": fisher_greater(ka, na, kb, nb)})
    ex = {a: excerpt(games, a) for a in P1C_ARMS}
    flag = [a for a in P1C_ARMS if len(arms[a]["short"]) > 2]
    out = {"manifest": str(manifest), "status": {k: v.get("status") for k, v in m["arms"].items()},
           "arms": arms, "tests": tests, "excerpts_T31": ex, "short_flag": flag,
           "descriptive_rule_kept": rule, "descriptive_enforcers_back": enforcers}
    (RESULTS / "p1c_analysis.json").write_text(json.dumps(out, indent=1))

    def fr(r):
        return f"{r['k']}/{r['n']}" if r["n"] else "–"

    L = ["# P1c: rewritten notes (Kickoff 09, plan §13, `prereg-p1c`)", "",
         f"Manifest `{manifest.name}`. Seeds 215–229 from P1b's base snapshots; 60 rounds; shock at T+30. Outcomes and tests "
         "pre-registered in plan §13. P1b's `same_history` and `same_notes` (same bases, real inherited notes) are shown "
         "for reference only (not part of any test).", "",
         "## Per arm", "",
         "| arm | games | joins | enforces | re_formed | clean_punish | clean_punish_return | back_at_cartel | "
         "newcomer CI T+34..T+60 | market CI T+34..T+60 | unique paths | did not reach T+33 |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a, r in arms.items():
        ref = " (P1b, reference)" if a in REFERENCE else ""
        pc = (lambda v: f"{v:+.2f}" if v is not None else "–")
        L.append(f"| {a}{ref} | {r['n']} | " + " | ".join(fr(r[k]) for k in OUTCOMES) +
                 f" | {pc(r['post_ci_newcomer'])} | {pc(r['post_ci_market'])} | {r['duplicates']['unique']} | "
                 f"{', '.join(map(str, r['short'])) or '0'} |")
    L += ["", "Exact 95% CIs (Clopper–Pearson):", "", "| arm | " + " | ".join(OUTCOMES) + " |",
          "|---|" + "---|" * len(OUTCOMES)]
    for a in P1C_ARMS:
        L.append(f"| {a} | " + " | ".join(f"[{arms[a][k]['lo']:.2f}, {arms[a][k]['hi']:.2f}]" if arms[a][k]["n"] else "–"
                                          for k in OUTCOMES) + " |")
    L += ["", "## Primary tests (one-sided Fisher exact, α = 0.05 each)", "", "| test | first | second | p |", "|---|---|---|---|"]
    for t in tests:
        a, b = [k for k in t if k not in ("test", "p_one_sided")]
        L.append(f"| {t['test']} | {a} {t[a][0]}/{t[a][1]} | {b} {t[b][0]}/{t[b][1]} | {t['p_one_sided']:.4f} |")
    L += ["", f"Kill flag (more than 2 games in an arm not reaching T+33): {', '.join(flag) or 'none'}.", "",
          "## Does the rule stay in the newcomer's notes? (descriptive, not pre-registered)", "",
          "Games whose newcomer PLANS + INSIGHTS, written at round T+k, mention both 1.47 and 1.70 (regexes `1\\.47`, "
          "`1\\.70`). P1b arms on the same bases for reference.", "",
          "| arm | " + " | ".join(f"T+{k}" for k in RULE_ROUNDS) + " | enforcers (seed, back_at_cartel) |",
          "|---|" + "---|" * len(RULE_ROUNDS) + "---|"]
    for a in RULE_ARMS:
        L.append(f"| {a}{' (P1b)' if a not in P1C_ARMS else ''} | " +
                 " | ".join(f"{rule[a][k][0]}/{rule[a][k][1]}" for k in RULE_ROUNDS) + " | " +
                 (", ".join(f"s{s} {'yes' if b else 'no'}" for s, b in enforcers[a]) or "–") + " |")
    L += ["",
          "## Newcomer notes at T+31 (one per arm)", ""]
    for a, n in ex.items():
        if not n:
            L.append(f"- `{a}`: no parsed call at T+31.")
            continue
        L.append(f"- `{a}`, s{n['seed']}, price {n['price']:.2f} at T+31.")
        L.append(f"  - PLANS: {n.get('plans', '')}")
        L.append(f"  - INSIGHTS: {n.get('insights', '')}")
    (RESULTS / "p1c_analysis.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
