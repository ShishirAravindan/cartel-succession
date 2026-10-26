"""One line per main-line game (P1, P1b, P2/P3 reruns): price paths T+1..T+60 and the pre-registered outcomes.

    uv run --project seat_swap python -m seat_swap.explore_series

Writes seat_swap/results/explore/series.md, the input of the exploratory anomaly hunt (not used in the paper).
"""

from __future__ import annotations

import json
from pathlib import Path

from seat_swap.notes_packets import P23_RESULTS, RESULTS, ROOT, T
from seat_swap.p1_report import prices_of

MODEL = {"sib": "Qwen3-8B", "oth": "gpt-oss-20b"}


def main() -> None:
    L = ["# Price paths, every main-line game", "",
         "Each game: newcomer prices T+1..T+60 (seat 1), then incumbent prices (seat 0; scripted in `lookalike`).",
         "Shock: incumbent forced to 1.47 at T+30 (marked *). p_N = 1.47, cartel price 1.92, the incumbent's rule punishes < 1.70.",
         "Outcomes are the pre-registered metrics. Sample P1 = seeds 200–214, P1b = 215–229, P23 = P1's seeds with another newcomer model.", ""]
    for sample, path in (("P1", RESULTS / "p1.json"), ("P1b", RESULTS / "p1b.json"), ("P23", P23_RESULTS)):
        for r in json.loads(path.read_text())["rows"]:
            if not r.get("arm_dir"):
                continue
            d = Path(r["arm_dir"])
            p = prices_of(d if d.is_absolute() else ROOT / d, T, T)
            rng = [k for k in range(T + 1, T + 61) if k in p]
            yn = lambda k: {True: "yes", False: "no", None: "–"}[r.get(k)]
            model = MODEL.get(r["arm"].split("_")[0], "Qwen3-14B")
            L += [f"## {sample} {r['arm']} s{r['seed']} (newcomer {model if r['arm'] != 'control' else 'none: instructed incumbent'})",
                  f"joins {yn('joins')}, enforces {yn('enforces')}, overpriced {yn('overpriced')}, re_formed {yn('re_formed')}, "
                  f"retaliation {r['retaliation'] if r.get('retaliation') is None else round(r['retaliation'], 2)}, "
                  f"rounds played {len(rng)}",
                  "newcomer:  " + " ".join(f"{p[k][1]:.2f}" for k in rng),
                  "incumbent: " + " ".join(f"{p[k][0]:.2f}{'*' if k == T + 30 else ''}" for k in rng), ""]
    out = RESULTS / "explore" / "series.md"
    out.write_text("\n".join(L))
    print(f"{sum(1 for x in L if x.startswith('## '))} games -> {out}")


if __name__ == "__main__":
    main()
