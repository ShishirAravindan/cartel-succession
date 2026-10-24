"""P1 report (Kickoff 06 §5) from the manifest written by seat_swap.p1.

    uv run --project seat_swap python -m seat_swap.p1_report seat_swap/runs/p1_<id>.json

Writes seat_swap/results/p1.md, p1.json (seed-level rows) and p1_prices.csv (every round of every
arm and probe, newcomer and incumbent). Prices per round are listed in p1.md for the lowest-numbered
passing seed (plan §5.3). Works on a partial manifest (base only, or arms still running).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

from seat_swap import metrics as M
from seat_swap.p1 import P1_ARMS, THRESHOLD
from seat_swap.positive_control import RESULTS, fmt
from seat_swap.run_report import read_jsonl

EXCERPT_CHARS = 700
_tok = None


def tokens(text: str) -> int:
    global _tok
    if _tok is None:
        from transformers import AutoTokenizer

        from seat_swap.render import TOKENIZER_MODEL, TOKENIZER_REVISION
        _tok = AutoTokenizer.from_pretrained(TOKENIZER_MODEL, revision=TOKENIZER_REVISION)
    return len(_tok.encode(text))


def call_stats(dirs: list[Path], seat=None) -> dict:
    """Mean s/call and reasoning tokens/call (pinned tokenizer on the think block) over LLM calls."""
    lat, rt = [], []
    for d in dirs:
        for c in read_jsonl(Path(d) / "calls.jsonl"):
            if c["raw_completion"] is None or c["provider"] != "vllm" or (seat is not None and c["seat"] != seat):
                continue
            lat.append(c["latency_s"])
            rt.append(tokens(c["reasoning_text"]) if c.get("reasoning_text") else 0)
    return {"calls": len(lat), "s_per_call": float(np.mean(lat)) if lat else None,
            "reasoning_tokens_per_call": float(np.mean(rt)) if rt else None}


def wall(dirs: list[Path]) -> tuple[str, str] | None:
    ts = [c["timestamp"] for d in dirs for c in read_jsonl(Path(d) / "calls.jsonl") if c.get("timestamp")]
    return (min(ts), max(ts)) if ts else None


def prices_of(d: Path, T: int, snap_round: int) -> dict:
    snap = json.loads((d / f"snapshot_T{snap_round}.json").read_text())
    p = {row["round"]: list(row["prices"]) for row in snap["history"]}
    p.update(M.prices_by_round(read_jsonl(d / "rounds.jsonl")))
    return p


def notes_at(d: Path, rnd: int, seat: int = 1) -> dict | None:
    c = next((c for c in read_jsonl(d / "calls.jsonl") if c["round"] == rnd and c["seat"] == seat and c["parse_ok"]), None)
    return None if not c else {"round": rnd, "price": c["parsed_price"], **(c["notes_text"] or {})}


def excerpt(n: dict | None) -> str:
    if not n:
        return "(none)"
    text = f"PLANS: {n.get('plans', '')} INSIGHTS: {n.get('insights', '')}".replace("\n", " ")
    return f"round {n['round']} (price {n['price']:.2f}): " + text[:EXCERPT_CHARS] + ("…" if len(text) > EXCERPT_CHARS else "")


def series(p: dict, lo: int, hi: int, marks=()) -> str:
    return " ".join(f"{p[r][1]:.2f}({p[r][0]:.2f}{'*' if r in marks else ''})" for r in range(lo, hi + 1) if r in p)


def safe(f, *a):
    try:
        return f(*a)
    except KeyError:  # window not reached (game stopped early): censored
        return None


def arm_metrics(d: Path, T: int, arm: str) -> dict:
    p = prices_of(d, T, T)
    last = max(p)
    st = json.loads((d / "status.json").read_text()) if (d / "status.json").exists() else {"status": "incomplete"}
    out = {"arm_status": st["status"], "last_round": last - T, "arm_dir": str(d),
           "ci_early": safe(M.ci_early, p, T), "ci_late": safe(M.ci_late, p, T), "newcomer_ci": safe(M.newcomer_ci, p, T),
           "br_gap": safe(M.br_gap, p, T + 20, T + 29), "retaliation": safe(M.retaliation, p, T),
           "re_formed": safe(M.re_formed, p, T, THRESHOLD), "joins": safe(M.joins, p, T),
           "enforces": safe(M.enforces, p, T, THRESHOLD), "overpriced": safe(M.newcomer_overpriced, p, T),
           "established": M.established(p, T + 30) if last >= T + 29 else None,
           "first_hold": M.first_hold(p, T + 1, last) if last >= T + 5 else None,
           "first_hold_censored_at": None if last >= T + 60 else last - 4 - T}
    if arm != "lookalike":
        out["punishments_pre"] = safe(M.punishment_starts, p, T + 1, T + 29)
        out["punishments_post"] = M.punishment_starts(p, T + 31, last) if last >= T + 31 else None
        out["punishments_post_through"] = last - T
    return out


def probe_metrics(d: Path, T: int) -> dict:
    p = prices_of(d, T, T + M.PROBE_FORK)
    st = json.loads((d / "status.json").read_text()) if (d / "status.json").exists() else {"status": "incomplete"}
    return {"probe_status": st["status"], "probe_dir": str(d), "probe_last_round": max(p) - T,
            "probe_punished": safe(M.probe_punished, p, T), "probe_counter": safe(M.probe_counter, p, T),
            "probe_return": safe(M.probe_return, p, T), "probe_ci_post": safe(M.probe_ci_post, p, T),
            "disciplined": safe(M.disciplined, p, T), "probe_newcomer_ci_pre": safe(M.mean_ci, p, T + 11, T + 15, 1)}


def mean(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return float(np.mean(xs)) if xs else None


def main(argv=None) -> dict:
    args = argv or sys.argv[1:]
    path = Path(args[0])
    out_dir = Path(args[1]) if len(args) > 1 else RESULTS  # second argument: other output directory
    m = json.loads(path.read_text())
    T, seeds, passing = m["T"], m["seeds"], m.get("passing", [])
    L = [f"# P1 results (manifest `{path.name}`)", "", "## Base", "",
         "| seed | base run | status | cartel_ci 121–150 | enforcement_retaliation | pass |", "|---|---|---|---|---|---|"]
    for s in seeds:
        b, e = m["base"].get(str(s), {}), m["enforce"].get(str(s), {})
        L.append(f"| {s} | `{b.get('run_id', '–')}` | {b.get('status', '–')} | {fmt(e.get('cartel_ci'), '+.3f')} | "
                 f"{fmt(e.get('enforcement_retaliation'), '+.3f')} | {'yes' if e.get('is_cartel') else 'no'} |")
    L.append(f"\nGate: **{len(passing)}/{len(seeds)}** pass (need {m['gate_min']}): "
             f"{'PASS' if m.get('gate_pass') else 'FAIL'}. Passing seeds: {passing}.")

    rows = []
    runs_root = path.parent
    probe_of = {}
    for d in runs_root.glob("*_probe_discipline_*"):
        if (d / "config.json").exists():
            probe_of[json.loads((d / "config.json").read_text())["parent_run_id"]] = d
    base_ids = {b["run_id"]: int(seed) for seed, b in m["base"].items()}
    arm_dirs = {}
    for d in runs_root.glob("*_phaseB_*"):
        if (d / "config.json").exists():
            c = json.loads((d / "config.json").read_text())
            if c["parent_run_id"] in base_ids and c["arm"] in P1_ARMS:
                arm_dirs[(base_ids[c["parent_run_id"]], c["arm"])] = d
    for seed in passing:
        for arm in P1_ARMS:
            d = arm_dirs.get((seed, arm))
            if d is None:
                rows.append({"seed": seed, "arm": arm, "arm_status": "not started",
                             "error": m.get("arms", {}).get(f"{seed}/{arm}", {}).get("error")})
                continue
            row = {"seed": seed, "arm": arm, **arm_metrics(d, T, arm)}
            pd = probe_of.get(d.name)
            row.update(probe_metrics(pd, T) if pd else {"probe_status": "not started"})
            rows.append(row)
    rows.sort(key=lambda r: (P1_ARMS.index(r["arm"]), r["seed"]))
    if rows:
        L += ["", "## Per arm (counts over passing seeds with a finished branch)", "",
              "| arm | games | joins | enforces | overpriced | re_formed | disciplined | probe_punished | established at shock |",
              "|---|---|---|---|---|---|---|---|---|"]
        for arm in P1_ARMS:
            rs = [r for r in rows if r["arm"] == arm]
            ps = [r for r in rows if r["arm"] == arm and r.get("probe_status") == "completed"]
            # count over seeds whose game reached the metric's window; n = denominator
            c = lambda k, rr: f"{sum(bool(r.get(k)) for r in rr)}/{sum(r.get(k) is not None for r in rr)}"
            L.append(f"| {arm} | {len(rs)} | {c('joins', rs)} | {c('enforces', rs)} | {c('overpriced', rs)} | "
                     f"{c('re_formed', rs)} | {c('disciplined', ps)} | {c('probe_punished', ps)} | {c('established', rs)} |")
        L += ["", "Means (main line; probe):", "",
              "| arm | newcomer_ci | br_gap | retaliation | first_hold (T+k, never excluded; n never) | "
              "punishments pre / post | probe_counter | probe_return (n never) | probe_ci_post |",
              "|---|---|---|---|---|---|---|---|---|"]
        for arm in P1_ARMS:
            rs = [r for r in rows if r["arm"] == arm]
            fh = [r["first_hold"] - T for r in rs if r.get("first_hold") is not None]
            never = sum(1 for r in rs if r.get("last_round") and r.get("first_hold") is None)
            pret = [r["probe_return"] for r in rs if r.get("probe_return") is not None]
            pnever = sum(1 for r in rs if r.get("probe_status") == "completed" and r.get("probe_return") is None)
            pun = "n/a" if arm == "lookalike" else (
                f"{fmt(mean([len(r['punishments_pre']) for r in rs if r.get('punishments_pre') is not None]), '.2f')} / "
                f"{fmt(mean([len(r['punishments_post']) for r in rs if r.get('punishments_post') is not None]), '.2f')}")
            L.append(f"| {arm} | {fmt(mean([r.get('newcomer_ci') for r in rs]))} | {fmt(mean([r.get('br_gap') for r in rs]))} | "
                     f"{fmt(mean([r.get('retaliation') for r in rs]), '+.3f')} | {fmt(mean(fh), '.1f')} ({never}) | {pun} | "
                     f"{fmt(mean([r.get('probe_counter') for r in rs]), '.2f')} | {fmt(mean(pret), '.1f')} ({pnever}) | "
                     f"{fmt(mean([r.get('probe_ci_post') for r in rs]))} |")
        L += ["", "## Seed level", "",
              "| arm | seed | status (last round) | newcomer_ci | br_gap | retaliation | joins | enforces | overpr. | re_formed | "
              "first_hold | pun. pre / post | probe: status | newc. CI T+11–15 | punished | counter | return | ci_post | disciplined |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            pun = "n/a" if r["arm"] == "lookalike" else (
                f"{'–' if r.get('punishments_pre') is None else len(r['punishments_pre'])} / "
                f"{'–' if r.get('punishments_post') is None else len(r['punishments_post'])}")
            yn = lambda k: "–" if r.get(k) is None else ("yes" if r[k] else "no")
            L.append(f"| {r['arm']} | {r['seed']} | {r.get('arm_status')} (T+{r.get('last_round')}) | {fmt(r.get('newcomer_ci'))} | {fmt(r.get('br_gap'))} | "
                     f"{fmt(r.get('retaliation'), '+.3f')} | {yn('joins')} | {yn('enforces')} | {yn('overpriced')} | "
                     f"{yn('re_formed')} | {'never' if r.get('first_hold') is None else 'T+' + str(r['first_hold'] - T)} | "
                     f"{pun} | {r.get('probe_status')} (T+{r.get('probe_last_round')}) | {fmt(r.get('probe_newcomer_ci_pre'))} | {yn('probe_punished')} | "
                     f"{r.get('probe_counter', '–')} | {'never' if r.get('probe_return') is None else 'T+' + str(r['probe_return'])} | "
                     f"{fmt(r.get('probe_ci_post'))} | {yn('disciplined')} |")

        # prices, notes
        show = min(passing) if passing else None
        L += ["", f"## Prices per round, seed {show} (newcomer price, incumbent in brackets; * = forced)", ""]
        for r in rows:
            if r["seed"] != show:
                continue
            if r.get("arm_dir"):
                p = prices_of(Path(r["arm_dir"]), T, T)
                L.append(f"- **{r['arm']}** main T+1..T+60: {series(p, T + 1, T + 60, {T + 30})}")
            if r.get("probe_dir"):
                p = prices_of(Path(r["probe_dir"]), T, T + M.PROBE_FORK)
                L.append(f"  - probe T+11..T+29 (seat 1 forced at T+16): {series(p, T + 11, T + 29)}")
        L += ["", "## Notes", ""]
        for r in rows:
            if r["arm"] == "same_full" and r["seed"] == show and r.get("arm_dir"):
                snap = json.loads((Path(r["arm_dir"]) / f"snapshot_T{T}.json").read_text())
                n = snap["notes"][1]
                L.append(f"- **same_full s{show}, inherited seat-1 notes at T**: PLANS: "
                         f"{n['plans'][:EXCERPT_CHARS]} INSIGHTS: {n['insights'][:EXCERPT_CHARS]}".replace("\n", " "))
        for arm in ("same_history", "same_full"):
            for r in rows:
                if r["arm"] != arm or not r.get("probe_dir") or not r.get("probe_punished"):
                    continue
                d = Path(r["probe_dir"])
                p = prices_of(d, T, T + M.PROBE_FORK)
                first = next(k for k in range(T + 17, T + 30) if k in p and p[k][0] < M.PUNISH_BELOW)
                L.append(f"- **{arm} s{r['seed']} probe**, round after first punishment (T+{first - T}): "
                         f"{excerpt(notes_at(d, first + 1))}")
                break

    # timing
    groups = {"base": [path.parent / m["base"][str(s)]["run_id"]
                       for s in seeds if str(s) in m["base"] and m["base"][str(s)].get("status") == "completed"],
              "enforce": [Path(e["dir"]) for e in m["enforce"].values() if e.get("dir")],
              "arms": [Path(r["arm_dir"]) for r in rows if r.get("arm_dir")],
              "probes": [Path(r["probe_dir"]) for r in rows if r.get("probe_dir")]}
    L += ["", "## Timing", "", "| stage | games | LLM calls | s/call | reasoning tok/call | first call – last call (UTC) |",
          "|---|---|---|---|---|---|"]
    timing = {}
    for g, dirs in groups.items():
        if not dirs:
            continue
        st, w = call_stats(dirs), wall(dirs)
        timing[g] = {**st, "wall": w}
        L.append(f"| {g} | {len(dirs)} | {st['calls']} | {fmt(st['s_per_call'], '.1f')} | "
                 f"{fmt(st['reasoning_tokens_per_call'], '.0f')} | {w[0][11:19] if w else '–'} – {w[1][11:19] if w else '–'} |")
    if groups["arms"]:
        nc = call_stats([Path(r["arm_dir"]) for r in rows if r["arm"] != "control" and r.get("arm_dir")], seat=1)
        L.append(f"\nNewcomer (seat 1, non-control arms): {fmt(nc['s_per_call'], '.1f')} s/call, "
                 f"{fmt(nc['reasoning_tokens_per_call'], '.0f')} reasoning tok/call.")
        timing["newcomer"] = nc

    out_dir.mkdir(exist_ok=True)
    out = {"manifest": path.name, "T": T, "passing": passing, "base": m["base"], "enforce": m["enforce"],
           "rows": rows, "timing": timing}
    (out_dir / "p1.json").write_text(json.dumps(out, indent=2, default=str))
    (out_dir / "p1.md").write_text("\n".join(L) + "\n")
    with open(out_dir / "p1_prices.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["line", "arm", "seed", "round", "rel_round", "newcomer_price", "incumbent_price", "forced"])
        for r in rows:
            for line, key, snap_r in (("main", "arm_dir", T), ("probe", "probe_dir", T + M.PROBE_FORK)):
                if not r.get(key):
                    continue
                d = Path(r[key])
                if not (d / "rounds.jsonl").exists():
                    continue
                for row in read_jsonl(d / "rounds.jsonl"):
                    w.writerow([line, r["arm"], r["seed"], row["round"], row["round"] - T, row["prices"][1],
                                row["prices"][0], ";".join(row["forced"]) or ""])
    print("\n".join(L))
    return out


if __name__ == "__main__":
    main()
