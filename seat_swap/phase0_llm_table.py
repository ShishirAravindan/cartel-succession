"""Results table for the Phase 0 instructed LLM pair (main-line runs with --shock-round).

    uv run --project seat_swap python -m seat_swap.phase0_llm_table seat_swap/runs/<run_id> [...]

Writes seat_swap/results/phase0_llm.{json,md}.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from seat_swap.run_report import summarise

RESULTS = Path(__file__).resolve().parent / "results"


def main(argv=None) -> list[dict]:
    rows = []
    for d in argv or sys.argv[1:]:
        s = summarise(Path(d))
        trace = s["ci_trace"]
        rows.append({k: s[k] for k in ("run_id", "status", "calls", "parse_failures", "parse_bracketed",
                                       "retaliation_seat1", "retaliation_seat0", "shock_round")}
                    | {"ci_mean_31_39": [round(sum(t[i] for t in trace[30:39]) / 9, 3) for i in (0, 1)],
                       "ci_trace_every_5": trace[4::5]})
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "phase0_llm.json").write_text(json.dumps(rows, indent=2))
    lines = ["| run | calls | parse fails | bracketed | CI 31–39 (s0, s1) | retaliation seat 1 | retaliation seat 0 |",
             "|---|---|---|---|---|---|---|"]
    lines += [f"| `{r['run_id']}` | {r['calls']} | {r['parse_failures']} | {r['parse_bracketed']} | "
              f"{r['ci_mean_31_39'][0]:+.2f}, {r['ci_mean_31_39'][1]:+.2f} | {r['retaliation_seat1']:+.3f} | "
              f"{r['retaliation_seat0']:+.3f} |" for r in rows]
    (RESULTS / "phase0_llm.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return rows


if __name__ == "__main__":
    main()
