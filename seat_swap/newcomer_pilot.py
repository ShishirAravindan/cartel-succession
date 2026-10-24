"""Newcomer pilot (Kickoff 05): planted forgiving base at T = 40, branched into same_history,
same_none and lookalike; 30 rounds, incumbent forced to p_N at T+20; uninstructed newcomer in seat 1.

    uv run --project seat_swap python -m seat_swap.newcomer_pilot seat_swap/runs/<branch_run_id> [...]

Per branch (rounds relative to the branch point T):
    newcomer CI per round, T+1..T+30
    incumbent punishments of the newcomer (metrics.punishment_starts on seat 0): before the shock
        (T+1..T+19) and after it (T+21..T+30); n/a for lookalike, whose seat 0 never reacts
    retaliation: newcomer CI over T+21..T+23 minus T+17..T+19 (the Phase B window, moved to the pilot's shock)
    first_hold: first round the newcomer prices >= 1.90 for 5 rounds in a row (as T+k). The committed
        results used that Kickoff 05 definition; metrics.first_hold is bounded at CI [0.9, 1.1] since Kickoff 06
    notes excerpts: the newcomer's PLANS / INSIGHTS after its first round (T+1) and in the round
        after the incumbent's first punishment of it starts

Writes seat_swap/results/newcomer_pilot.{json,md} and newcomer_pilot_ci.csv.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

from seat_swap import metrics as M
from seat_swap.positive_control import RESULTS, fmt
from seat_swap.run_report import read_jsonl

EXCERPT_CHARS = 600


def notes_at(calls: list[dict], rnd: int) -> dict | None:
    c = next((c for c in calls if c["round"] == rnd and c["seat"] == 1 and c["parse_ok"]), None)
    if not c:
        return None
    return {"round": rnd, "price": c["parsed_price"], **(c["notes_text"] or {})}


def analyse(run_dir: Path) -> dict:
    cfg = json.loads((run_dir / "config.json").read_text())
    status = json.loads((run_dir / "status.json").read_text())
    snap = json.loads((run_dir / f"snapshot_T{cfg['branch_T']}.json").read_text())
    rounds = read_jsonl(run_dir / "rounds.jsonl")
    calls = read_jsonl(run_dir / "calls.jsonl")
    T, n = cfg["branch_T"], cfg["rounds"]
    shock = int(next(iter(cfg["shocks"])))
    prices = {row["round"]: list(row["prices"]) for row in snap["history"]}
    prices.update(M.prices_by_round(rounds))
    forced = {r["round"] for r in rounds if r["shock"]}
    last = max(prices)
    lookalike = cfg["arm_spec"]["seat0"] == "lookalike"

    def safe(f, *a):
        try:
            return f(*a)
        except KeyError:
            return None

    pre = None if lookalike else safe(M.punishment_starts, prices, T + 1, min(shock - 1, last), forced)
    post = None if lookalike else safe(M.punishment_starts, prices, shock + 1, last, forced)
    first_p = (pre or post or [None])[0]
    done = [c for c in calls if c["raw_completion"] is not None and c["seat"] == 1]
    return {
        "run_id": cfg["run_id"], "parent_run_id": cfg["parent_run_id"], "arm": cfg["arm"], "seed": cfg["seed"],
        "T": T, "shock_round": shock, "status": status["status"], "rounds_completed": status["rounds_completed"],
        "newcomer_instruction": cfg["instructions"][1], "inheritance": cfg["inheritance"],
        "newcomer_ci": {r: float(M.ci(prices[r][1])) for r in range(T + 1, last + 1)},
        "newcomer_prices": {r: prices[r][1] for r in range(T + 1, last + 1)},
        "incumbent_prices": {r: prices[r][0] for r in range(T + 1, last + 1)},
        "punishments_pre_shock": pre, "punishments_post_shock": post,
        "retaliation": safe(lambda: M.mean_ci(prices, shock + 1, shock + 3, 1) - M.mean_ci(prices, shock - 3, shock - 1, 1)),
        "first_hold": safe(M.first_hold, prices, T + 1, last),
        "newcomer_ci_pre_shock": safe(M.mean_ci, prices, shock - 10, shock - 1, 1),
        "notes_first": notes_at(calls, T + 1),
        "notes_after_first_punishment": notes_at(calls, first_p + 1) if first_p else None,
        "parse_failures": status["parse_failures"],
        "s_per_call_newcomer": sum(c["latency_s"] for c in done) / len(done) if done else None,
        "completion_tokens_newcomer": sum((c["usage"] or {}).get("completion_tokens") or 0 for c in done) / len(done)
        if done else None,
        "planned_rounds": n,
    }


def rel(r, T):
    return "–" if r is None else f"T+{r - T}"


def excerpt(n: dict | None) -> str:
    if not n:
        return "(none)"
    text = f"PLANS: {n.get('plans', '')} INSIGHTS: {n.get('insights', '')}".replace("\n", " ")
    return f"round {n['round']} (price {n['price']:.2f}): " + text[:EXCERPT_CHARS] + ("…" if len(text) > EXCERPT_CHARS else "")


def main(argv=None) -> list[dict]:
    rows = sorted((analyse(Path(d)) for d in argv or sys.argv[1:]), key=lambda r: (r["seed"], r["arm"]))
    lines = ["| seed | arm | status | newcomer CI T+10–T+19 | incumbent punishments pre / post shock "
             "| retaliation (T+21–23 minus T+17–19) | first 5-round hold ≥ 1.90 | parse fails | s/call (newcomer) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        T = r["T"]
        pun = "n/a" if r["punishments_pre_shock"] is None and r["arm"] == "lookalike" else (
            f"{len(r['punishments_pre_shock'] or [])} {[rel(x, T) for x in r['punishments_pre_shock'] or []]} / "
            f"{len(r['punishments_post_shock'] or [])} {[rel(x, T) for x in r['punishments_post_shock'] or []]}")
        lines.append(f"| {r['seed']} | {r['arm']} | {r['status']} | {fmt(r['newcomer_ci_pre_shock'])} | {pun} | "
                     f"{fmt(r['retaliation'], '+.3f')} | {rel(r['first_hold'], T)} | {r['parse_failures']} | "
                     f"{fmt(r['s_per_call_newcomer'], '.1f')} |")
    lines += ["", "Newcomer price per round (seat 1; incumbent in brackets; * = incumbent forced to p_N):", ""]
    for r in rows:
        T = r["T"]
        series = " ".join(f"{p:.2f}({r['incumbent_prices'][k]:.2f}{'*' if k == r['shock_round'] else ''})"
                          for k, p in r["newcomer_prices"].items())
        lines.append(f"- s{r['seed']} {r['arm']}: {series}")
    lines += ["", "Newcomer notes:", ""]
    for r in rows:
        lines.append(f"- **s{r['seed']} {r['arm']}**, first round: {excerpt(r['notes_first'])}")
        lines.append(f"  - after first punishment: {excerpt(r['notes_after_first_punishment'])}")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "newcomer_pilot.json").write_text(json.dumps(rows, indent=2))
    (RESULTS / "newcomer_pilot.md").write_text("\n".join(lines) + "\n")
    with open(RESULTS / "newcomer_pilot_ci.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run_id", "seed", "arm", "round", "rel_round", "newcomer_price", "incumbent_price", "newcomer_ci", "shock"])
        for r in rows:
            for k, p in r["newcomer_prices"].items():
                w.writerow([r["run_id"], r["seed"], r["arm"], k, k - r["T"], p, r["incumbent_prices"][k],
                            round(r["newcomer_ci"][k], 4), int(k == r["shock_round"])])
    print("\n".join(lines))
    return rows


if __name__ == "__main__":
    main()
