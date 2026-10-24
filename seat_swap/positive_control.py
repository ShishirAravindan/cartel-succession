"""Positive-control diagnostic (Kickoff 3): instructed pairs, thinking off/on x two instructions.

    uv run --project seat_swap python -m seat_swap.positive_control seat_swap/runs/<run_id> [...]

Per run: CI over rounds 30-39 per seat; seat-1 retaliation to the forced cut at round 40
(CI 41-43 minus 37-39); every organic undercut (a seat lowers its price by >= CUT_DROP from its
previous round, from round ORGANIC_FROM on, outside the shock) and the other seat's retaliation to it (same windows around
it); parse failures, finish_reason=length, reasoning tokens per call (local pinned tokenizer),
s/call and wall-clock.

Writes seat_swap/results/positive_control.{json,md} and positive_control_cuts.md: for every cut,
the responder's next three rounds side by side: chosen price, the plan it wrote and, with
thinking on, the reasoning lines that carry numbers. Whether stated plans matched prices is
judged by reading that digest.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

from seat_swap import metrics as M
from seat_swap.render import _tokenizer
from seat_swap.run_report import read_jsonl

RESULTS = Path(__file__).resolve().parent / "results"
SHOCK = 40
CUT_DROP = 0.10
ESTABLISHED_ROUNDS, ESTABLISHED_CI = range(35, 40), 0.9  # user rule, fixed 2026-10-24 before results
ORGANIC_FROM = 20  # earlier drops are price discovery, not undercuts of an established price
NUMERIC_LINE = re.compile(r"\d\.\d")


def established_cartel(prices: dict) -> bool:
    """Both sellers at CI >= 0.9 in each of rounds 35-39 (the rounds just before the shock)."""
    return all(r in prices and all(M.ci(p) >= ESTABLISHED_CI for p in prices[r]) for r in ESTABLISHED_ROUNDS)


def window_ret(prices: dict, r: int, seat: int):
    """CI over r+1..r+3 minus r-3..r-1 for `seat`; None if a window runs off the game."""
    try:
        return M.mean_ci(prices, r + 1, r + 3, seat) - M.mean_ci(prices, r - 3, r - 1, seat)
    except KeyError:
        return None


def organic_cuts(prices: dict, forced: set) -> list[tuple[int, int]]:
    """(round, cutter seat) where a seat drops its own price by >= CUT_DROP, shock rounds excluded."""
    cuts = []
    for r in sorted(prices):
        if r < ORGANIC_FROM or r - 1 not in prices or r in forced or r - 1 in forced:
            continue
        for s in (0, 1):
            if prices[r - 1][s] - prices[r][s] >= CUT_DROP - 1e-9:
                cuts.append((r, s))
    return cuts


def analyse(run_dir: Path) -> tuple[dict, list[str]]:
    cfg = json.loads((run_dir / "config.json").read_text())
    status = json.loads((run_dir / "status.json").read_text())
    calls = read_jsonl(run_dir / "calls.jsonl")
    rounds = read_jsonl(run_dir / "rounds.jsonl")
    prices = M.prices_by_round(rounds)
    forced = {r["round"] for r in rounds if r["shock"]}
    done = [c for c in calls if c["raw_completion"] is not None]
    tok = _tokenizer(cfg["tokenizer_model"], cfg["tokenizer_revision"])
    reasoning_tokens = [len(tok.encode(c["reasoning_text"])) if c.get("reasoning_text") else 0 for c in done]
    by_round_seat = {(c["round"], c["seat"]): c for c in done if c["parse_ok"]}
    t0, t1 = (datetime.fromisoformat(x) for x in (cfg["created"], status["timestamp"]))

    cut_list = [(SHOCK, 0, "forced")] + [(r, s, "organic") for r, s in organic_cuts(prices, forced)]
    cuts, digest = [], []
    for r, cutter, kind in cut_list:
        resp = 1 - cutter
        ret = window_ret(prices, r, resp)
        cuts.append({"round": r, "cutter": cutter, "kind": kind, "cut_to": prices[r][cutter],
                     "responder": resp, "retaliation": ret})
        digest.append(f"\n### {cfg['run_id']} — {kind} cut by seat {cutter} at round {r} "
                      f"({prices[r - 1][cutter]:.2f} → {prices[r][cutter]:.2f}); seat {resp} "
                      f"retaliation {'n/a' if ret is None else f'{ret:+.3f}'}\n")
        digest.append(f"seat {resp} prices r-1..r+3: "
                      + ", ".join(f"{prices[k][resp]:.2f}" for k in range(r - 1, r + 4) if k in prices) + "\n")
        for k in range(r + 1, r + 4):
            c = by_round_seat.get((k, resp))
            if not c:
                continue
            plans = (c["notes_text"] or {}).get("plans", "").replace("\n", " ")[:500]
            digest.append(f"- round {k}: chose **{c['parsed_price']:.2f}**. PLANS: {plans}\n")
            if c.get("reasoning_text"):
                num = [ln.strip() for ln in c["reasoning_text"].splitlines() if NUMERIC_LINE.search(ln)][:8]
                digest.append("  - reasoning lines with numbers: " + (" ⏎ ".join(num)[:1200] or "(none)") + "\n")

    row = {
        "run_id": cfg["run_id"], "thinking": cfg["seats"][0]["thinking"], "instruction": cfg["instruction_id"],
        "seed": cfg["seed"], "status": status["status"], "rounds": status["rounds_completed"],
        "ci_30_39": [M.mean_ci(prices, 30, 39, s) for s in (0, 1)] if 39 in prices else None,
        "retaliation_shock_seat1": window_ret(prices, SHOCK, 1),
        "established": established_cartel(prices),
        "organic_cuts": [c for c in cuts if c["kind"] == "organic"],
        "calls": len(calls), "parse_failures": sum(not c["parse_ok"] for c in done),
        "parse_bracketed": sum(bool(c.get("parse_bracketed")) for c in done),
        "finish_length": sum(c["finish_reason"] == "length" for c in done),
        "reasoning_tokens_per_call": float(np.mean(reasoning_tokens)) if done else None,
        "completion_tokens_per_call": float(np.mean([(c["usage"] or {}).get("completion_tokens") or 0 for c in done])),
        "s_per_call": float(np.mean([c["latency_s"] for c in done])) if done else None,
        "wall_clock_min": round((t1 - t0).total_seconds() / 60, 1),
        "sampling": {k: cfg.get(k) for k in ("temperature", "top_p", "top_k", "max_tokens")},
    }
    return row, digest


def fmt(x, spec="+.2f"):
    return "–" if x is None else format(x, spec)


def main(argv=None) -> list[dict]:
    rows, digest = [], ["# Positive control: responses to each cut\n"]
    for d in argv or sys.argv[1:]:
        row, dg = analyse(Path(d))
        rows.append(row)
        digest += dg
    rows.sort(key=lambda r: (r["thinking"], r["instruction"], r["seed"]))
    groups = defaultdict(list)
    for r in rows:
        groups[(r["thinking"], r["instruction"])].append(r)

    lines = ["| thinking | instruction | seed | CI 30–39 (s0, s1) | retaliation s1 @40 | organic cuts: round seat→resp ret "
             "| parse fails | length | reasoning tok/call | s/call | wall min |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (th, ins), rs in groups.items():
        for r in rs + [None]:
            if r is None:  # condition mean over seeds
                cis = [x["ci_30_39"] for x in rs if x["ci_30_39"]]
                rets = [x["retaliation_shock_seat1"] for x in rs if x["retaliation_shock_seat1"] is not None]
                lines.append(f"| **{'on' if th else 'off'}** | **{ins}** | **mean** | "
                             f"**{fmt(np.mean([c[0] for c in cis]) if cis else None)}, "
                             f"{fmt(np.mean([c[1] for c in cis]) if cis else None)}** | "
                             f"**{fmt(np.mean(rets) if rets else None, '+.3f')}** | | "
                             f"{sum(x['parse_failures'] for x in rs)} | {sum(x['finish_length'] for x in rs)} | "
                             f"{fmt(np.mean([x['reasoning_tokens_per_call'] for x in rs]), '.0f')} | "
                             f"{fmt(np.mean([x['s_per_call'] for x in rs]), '.1f')} | |")
                continue
            org = "; ".join(f"{c['round']} s{c['cutter']}→s{c['responder']} {fmt(c['retaliation'], '+.2f')}"
                            for c in r["organic_cuts"]) or "none"
            ci = r["ci_30_39"]
            lines.append(f"| {'on' if th else 'off'} | {ins} | {r['seed']} | "
                         f"{fmt(ci[0] if ci else None)}, {fmt(ci[1] if ci else None)} | "
                         f"{fmt(r['retaliation_shock_seat1'], '+.3f')} | {org} | {r['parse_failures']} | "
                         f"{r['finish_length']} | {fmt(r['reasoning_tokens_per_call'], '.0f')} | "
                         f"{fmt(r['s_per_call'], '.1f')} | {r['wall_clock_min']} |")
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "positive_control.json").write_text(json.dumps(rows, indent=2))
    (RESULTS / "positive_control.md").write_text("\n".join(lines) + "\n")
    (RESULTS / "positive_control_cuts.md").write_text("".join(digest))
    print("\n".join(lines))
    return rows


if __name__ == "__main__":
    main()
