"""Phase 0 positive control, scripted (zero API calls): grim trigger in seat 0 against each seller
in seat 1, through the full pipeline.

Per pair: a 150-round main line (snapshot at T = 150), the Phase B branch with nobody replaced
(`control`, seat 0 forced to p_N at T+30), and the Phase A enforcement side branch (seat 0 forced
at T+1). Writes seat_swap/results/phase0_scripted.{json,md}.

    uv run --project seat_swap python -m seat_swap.phase0_scripted
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from seat_swap import run
from seat_swap.branch import ENFORCE, RUNS_ROOT, run_branch

T = 150
PAIRS = ["grim", "tft", "copier", "lookalike"]
RESULTS = Path(__file__).resolve().parent / "results"


def main() -> list[dict]:
    rows = []
    for seller in PAIRS:
        run_id = f"{time.strftime('%Y%m%d-%H%M%S')}_phase0_dry-grim-{seller}_s0"
        status = run.main(["--dry-run", "--dry-seat0", "grim", "--dry-seat1", seller, "--rounds", str(T),
                           "--phase", "phase0", "--run-id", run_id])
        assert status["status"] == "completed", status
        parent = RUNS_ROOT / run_id
        _, b = run_branch(parent, T, "control", dry_run=True, max_calls=None, dry_seat0="grim", dry_seat1=seller)
        _, e = run_branch(parent, T, ENFORCE, dry_run=True, max_calls=None, dry_seat0="grim", dry_seat1=seller)
        rows.append({"seat1": seller, "main_run": run_id, "phaseB_run": b["run_id"], "enforce_run": e["run_id"],
                     "cartel_ci": e["cartel_ci"], "br_gap": b["br_gap"], "ci_late": b["ci_late"],
                     "retaliation": b["retaliation"], "enforcement_retaliation": e["enforcement_retaliation"],
                     "parse_failures": b["parse_failures"] + e["parse_failures"] + status["parse_failures"]})
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "phase0_scripted.json").write_text(json.dumps(rows, indent=2))
    lines = ["| seat 1 (vs grim) | CI 121-150 | br_gap T+20..29 | ci_late | retaliation (T+30 shock) "
             "| enforcement retaliation (T+1 shock) | parse fails |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {r['seat1']} | {r['cartel_ci']:+.3f} | {r['br_gap']:+.3f} | {r['ci_late']:+.3f} | "
              f"{r['retaliation']:+.3f} | {r['enforcement_retaliation']:+.3f} | {r['parse_failures']} |" for r in rows]
    (RESULTS / "phase0_scripted.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return rows


if __name__ == "__main__":
    main()
