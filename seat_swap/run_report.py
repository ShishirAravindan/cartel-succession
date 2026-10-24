"""Summarise one run directory: status, call stats, cost, backends, CI trace.

    uv run --project seat_swap python -m seat_swap.run_report seat_swap/runs/<run_id> [...]
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from seat_swap.metrics import ci


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()] if path.exists() else []


def summarise(run_dir: Path) -> dict:
    calls = read_jsonl(run_dir / "calls.jsonl")
    rounds = read_jsonl(run_dir / "rounds.jsonl")
    status = json.loads((run_dir / "status.json").read_text())
    done = [c for c in calls if c["raw_completion"] is not None]
    usage = [c["usage"] or {} for c in done]
    reasoning = [((u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0) for u in usage]
    return {
        "run_id": run_dir.name,
        "status": status["status"], "detail": status["detail"], "rounds": status["rounds_completed"],
        "calls": len(calls), "parse_failures": sum(not c["parse_ok"] for c in done),
        "parse_bracketed": sum(bool(c.get("parse_bracketed")) for c in done),
        "call_errors": sum(c["raw_completion"] is None for c in calls),  # transport or fatal; see "error"
        "finish_reasons": dict(Counter(c["finish_reason"] for c in done)),
        "served_by": dict(Counter(c["served_provider"] for c in done)),
        "mean_s_per_call": float(np.mean([c["latency_s"] for c in done])) if done else None,
        "mean_prompt_tokens": float(np.mean([u.get("prompt_tokens") or 0 for u in usage])) if usage else None,
        "mean_completion_tokens": float(np.mean([u.get("completion_tokens") or 0 for u in usage])) if usage else None,
        "mean_reasoning_tokens": float(np.mean(reasoning)) if reasoning else None,
        "calls_with_reasoning_text": sum(bool(c.get("reasoning_text")) for c in done),
        "total_cost_usd": float(sum(u.get("cost") or 0 for u in usage)),
        "ci_trace": [[round(float(x), 2) for x in ci(r["prices"])] for r in rounds],
        "price_trace": [r["prices"] for r in rounds],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dirs", nargs="+")
    args = ap.parse_args()
    for d in args.run_dirs:
        s = summarise(Path(d))
        trace = s.pop("ci_trace")
        prices = s.pop("price_trace")
        print(json.dumps(s, indent=2))
        print("round  p0    p1    ci0    ci1")
        for t, (p, c) in enumerate(zip(prices, trace), start=1):
            print(f"{t:>5}  {p[0]:.2f}  {p[1]:.2f}  {c[0]:+.2f}  {c[1]:+.2f}")


if __name__ == "__main__":
    main()
