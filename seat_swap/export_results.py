"""Small derived files for the repo (raw run directories stay local).

    uv run --project seat_swap python -m seat_swap.export_results

prices_all.csv     one row per round of every positive-control game (posctl-*, posctl2-*) and
                   every uninstructed pilot: run_id, condition, thinking, instruction, seed, round,
                   price_seat0, price_seat1, shock
pilot_excerpts.md  for each uninstructed pilot, seat 1's notes (PLANS, INSIGHTS), its observations
                   and its reasoning at rounds 1, 15, 30, 45 and 60; reasoning trimmed to its first
                   and last 400 characters
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from seat_swap.prompts import parse_response
from seat_swap.run_report import read_jsonl

RUNS = Path(__file__).resolve().parent / "runs"
RESULTS = Path(__file__).resolve().parent / "results"
GAME_PATTERNS = ("*_posctl-*", "*_posctl2-*", "*_pilot-uninstructed_*")
EXCERPT_ROUNDS = (1, 15, 30, 45, 60)
TRIM = 400


def condition(cfg: dict) -> tuple[str, str, str]:
    thinking = "on" if cfg["seats"][0]["thinking"] else "off"
    instruction = cfg.get("instruction_id") or "none"
    kind = "pilot" if cfg["phase"].startswith("pilot") else "posctl"
    warm = "_cartelwarmup" if cfg.get("warmup") == "cartel" else ""
    return f"{kind}_{instruction}_think{thinking}{warm}", thinking, instruction


def trim(text: str) -> str:
    text = text.strip()
    if len(text) <= 2 * TRIM:
        return text
    return f"{text[:TRIM]}\n[… {len(text) - 2 * TRIM} characters omitted …]\n{text[-TRIM:]}"


def quote(text: str) -> str:
    return "\n".join("> " + line for line in (text or "(empty)").splitlines()) or "> (empty)"


def main() -> None:
    dirs = sorted({d for pat in GAME_PATTERNS for d in RUNS.glob(pat) if (d / "status.json").exists()})
    rows, excerpts = [], ["# Uninstructed pilots: seat 1 at rounds 1, 15, 30, 45, 60\n",
                          "Pilot games (60 rounds, no shock, P0 prompt, no instruction); not Phase A. "
                          f"Reasoning is trimmed to its first and last {TRIM} characters.\n"]
    for d in dirs:
        cfg = json.loads((d / "config.json").read_text())
        cond, thinking, instruction = condition(cfg)
        for r in read_jsonl(d / "rounds.jsonl"):
            rows.append({"run_id": cfg["run_id"], "condition": cond, "thinking": thinking, "instruction": instruction,
                         "seed": cfg["seed"], "round": r["round"], "price_seat0": r["prices"][0],
                         "price_seat1": r["prices"][1], "shock": int(bool(r["shock"]))})
        if not cfg["phase"].startswith("pilot"):
            continue
        prices = {r["round"]: r["prices"] for r in read_jsonl(d / "rounds.jsonl")}
        calls = {(c["round"], c["seat"]): c for c in read_jsonl(d / "calls.jsonl") if c["parse_ok"]}
        excerpts.append(f"\n## `{cfg['run_id']}` (thinking {thinking})\n")
        for t in EXCERPT_ROUNDS:
            c = calls.get((t, 1))
            if c is None:
                excerpts.append(f"\n### Round {t}\n\n(no parsed call)\n")
                continue
            parsed = parse_response(c["raw_completion"], notes_on=True)
            excerpts.append(f"\n### Round {t}: seat 1 chose {c['parsed_price']:.2f} "
                            f"(round prices {prices[t][0]:.2f} / {prices[t][1]:.2f})\n")
            excerpts.append(f"\n**Observations**\n\n{quote(trim(parsed.thoughts))}\n")
            excerpts.append(f"\n**PLANS.txt**\n\n{quote(c['notes_text']['plans'])}\n")
            excerpts.append(f"\n**INSIGHTS.txt**\n\n{quote(c['notes_text']['insights'])}\n")
            if c.get("reasoning_text"):
                excerpts.append(f"\n**Reasoning** ({len(c['reasoning_text'])} characters)\n\n{quote(trim(c['reasoning_text']))}\n")
    RESULTS.mkdir(exist_ok=True)
    with open(RESULTS / "prices_all.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (RESULTS / "pilot_excerpts.md").write_text("".join(excerpts))
    games = sorted({r["run_id"] for r in rows})
    print(f"{len(games)} games, {len(rows)} rows -> prices_all.csv; pilot excerpts -> pilot_excerpts.md")


if __name__ == "__main__":
    main()
