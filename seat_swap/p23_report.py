"""P2/P3 report (Kickoff 08 §4) from the manifests written by seat_swap.p23.

    uv run --project seat_swap python -m seat_swap.p23_report seat_swap/runs/p23_sib_<id>.json seat_swap/runs/p23_oth_<id>.json

Recomputes every metric from each branch's snapshot_T150 + rounds.jsonl (p1_report.arm_metrics, the
same metrics.py functions as P1). Writes seat_swap/results/p23.md and p23.json. P1's same-model rows
for the ladder come from seat_swap/results/p1.json (same 15 seeds).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scipy.stats import fisher_exact

from seat_swap.model_config import MODELS
from seat_swap.p1_report import arm_metrics, excerpt, mean, notes_at, wall
from seat_swap.positive_control import RESULTS, fmt
from seat_swap.render import _tokenizer
from seat_swap.run_report import read_jsonl

COUNTS = ["joins", "enforces", "overpriced", "re_formed"]
LABEL = {"same": "same (Qwen3-14B, P1)", "sib": "sibling (Qwen3-8B, P2)", "oth": "other family (gpt-oss-20b, P3)"}


def seat_stats(dirs: list[Path], seat: int) -> dict:
    """s/call, reasoning tokens/call (the seat's own tokenizer) and generated tokens over a seat's LLM calls."""
    lat, rt, gen = [], [], []
    for d in dirs:
        for c in read_jsonl(Path(d) / "calls.jsonl"):
            if c["raw_completion"] is None or c["seat"] != seat or c["provider"] != "vllm":
                continue
            lat.append(c["latency_s"])
            tok = _tokenizer(c["model"], c["model_revision"])
            rt.append(len(tok.encode(c["reasoning_text"], add_special_tokens=False)) if c.get("reasoning_text") else 0)
            gen.append((c.get("usage") or {}).get("completion_tokens") or 0)
    return {"calls": len(lat), "s_per_call": mean(lat), "reasoning_tokens_per_call": mean(rt),
            "generated_tokens": sum(gen)}


def main(argv=None) -> dict:
    paths = [Path(a) for a in (argv or sys.argv[1:])]
    p1 = json.loads((RESULTS / "p1.json").read_text())
    T = p1["T"]
    rows, fams = [], {}
    for path in paths:
        m = json.loads(path.read_text())
        fams[m["family"]] = m
        for key, a in m["arms"].items():
            seed, arm = key.split("/")
            r = {"seed": int(seed), "arm": arm, "family": m["family"], "status": a.get("status"), "error": a.get("error")}
            if a.get("dir"):
                r.update(arm_metrics(Path(a["dir"]), T, arm))
            rows.append(r)
    rows.sort(key=lambda r: (r["family"], r["arm"].split("_")[1] != "history", r["seed"]))
    arms = [a for f in fams.values() for a in f["arm_names"]]
    L = ["# P2/P3 results (Kickoff 08)", "", "Manifests: " + ", ".join(f"`{p.name}`" for p in paths) +
         f". Seeds: P1's 15 base seeds ({min(p1['passing'])}–{max(p1['passing'])}), branched at T = {T}.", "",
         "## Per arm", "", "| arm | newcomer | games completed | " + " | ".join(COUNTS) + " | mean newcomer_ci | mean br_gap | mean retaliation | first_hold mean (n never) |",
         "|---|---|---|" + "---|" * len(COUNTS) + "---|---|---|---|"]
    out = {"counts": {}}
    for arm in arms:
        rs = [r for r in rows if r["arm"] == arm]
        fh = [r["first_hold"] - T for r in rs if r.get("first_hold") is not None]
        never = sum(1 for r in rs if r.get("last_round") and r.get("first_hold") is None)
        out["counts"][arm] = {k: [sum(bool(r.get(k)) for r in rs), sum(r.get(k) is not None for r in rs)] for k in COUNTS}
        L.append(f"| {arm} | {fams[rs[0]['family']]['newcomer_model']} | {sum(r.get('arm_status') == 'completed' for r in rs)}/{len(rs)} | " +
                 " | ".join("{}/{}".format(*out["counts"][arm][k]) for k in COUNTS) +
                 f" | {fmt(mean([r.get('newcomer_ci') for r in rs]))} | {fmt(mean([r.get('br_gap') for r in rs]))} | "
                 f"{fmt(mean([r.get('retaliation') for r in rs]), '+.3f')} | {fmt(mean(fh), '.1f')} ({never}) |")

    # the replacement ladder
    ladder = {"same": {i: [r for r in p1["rows"] if r["arm"] == f"same_{i}"] for i in ("history", "full")}}
    for f in fams:
        ladder[f] = {i: [r for r in rows if r["arm"] == f"{f}_{i}"] for i in ("history", "full")}
    c = lambda rs, k: f"{sum(bool(r.get(k)) for r in rs)}/{sum(r.get(k) is not None for r in rs)}"
    L += ["", "## Replacement ladder (same 15 seeds; joins, re_formed)", "",
          "| newcomer | history: joins | history: re_formed | full: joins | full: re_formed | Fisher full > history (one-sided p) |",
          "|---|---|---|---|---|---|"]
    out["ladder"] = {}
    for f, d in ladder.items():
        h, fu = d["history"], d["full"]
        a, b = sum(bool(r.get("re_formed")) for r in fu), sum(bool(r.get("re_formed")) for r in h)
        p = fisher_exact([[a, len(fu) - a], [b, len(h) - b]], alternative="greater")[1] if h and fu else None
        out["ladder"][f] = {"history_joins": c(h, "joins"), "history_re_formed": c(h, "re_formed"),
                            "full_joins": c(fu, "joins"), "full_re_formed": c(fu, "re_formed"), "fisher_p": p}
        L.append(f"| {LABEL[f]} | {c(h, 'joins')} | {c(h, 're_formed')} | {c(fu, 'joins')} | {c(fu, 're_formed')} | "
                 f"{fmt(p, '.3f')} |")

    # seed level
    L += ["", "## Seed level", "",
          "| arm | seed | status (last round) | newcomer_ci | br_gap | retaliation | first_hold | joins | enforces | overpr. | re_formed |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    yn = lambda v: "–" if v is None else ("yes" if v else "no")
    for r in rows:
        L.append(f"| {r['arm']} | {r['seed']} | {r.get('arm_status', r['status'])} (T+{r.get('last_round')}) | "
                 f"{fmt(r.get('newcomer_ci'))} | {fmt(r.get('br_gap'))} | {fmt(r.get('retaliation'), '+.3f')} | "
                 f"{'never' if r.get('first_hold') is None else 'T+' + str(r['first_hold'] - T)} | {yn(r.get('joins'))} | "
                 f"{yn(r.get('enforces'))} | {yn(r.get('overpriced'))} | {yn(r.get('re_formed'))} |")

    # notes: one excerpt per newcomer model (lowest seed of its full arm)
    L += ["", "## Newcomer notes (lowest seed, `*_full`)", ""]
    for f, m in fams.items():
        r = next((r for r in rows if r["arm"] == f"{f}_full" and r.get("arm_dir")), None)
        if r:
            d = Path(r["arm_dir"])
            L += [f"- **{f}_full s{r['seed']} ({m['newcomer_model']})**, T+1: {excerpt(notes_at(d, T + 1))}",
                  f"  - T+31 (round after the shock): {excerpt(notes_at(d, T + 31))}"]

    # timing per app
    L += ["", "## Timing", "", "| family | seat | model | LLM calls | s/call | reasoning tok/call | generated tokens | first – last call (UTC) |",
          "|---|---|---|---|---|---|---|---|"]
    out["timing"] = {}
    for f, m in fams.items():
        dirs = [Path(r["arm_dir"]) for r in rows if r["family"] == f and r.get("arm_dir")]
        w = wall(dirs)
        for seat, model in ((1, m["newcomer_model"]), (0, "Qwen/Qwen3-14B")):
            st = seat_stats(dirs, seat)
            out["timing"][f"{f}/seat{seat}"] = {**st, "wall": w}
            L.append(f"| {f} | {seat} | {model} | {st['calls']} | {fmt(st['s_per_call'], '.1f')} | "
                     f"{fmt(st['reasoning_tokens_per_call'], '.0f')} | {st['generated_tokens']} | "
                     f"{w[0][11:19] if w else '–'} – {w[1][11:19] if w else '–'} |")

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "p23.json").write_text(json.dumps({"rows": rows, **out}, indent=2, default=str))
    (RESULTS / "p23.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return out


if __name__ == "__main__":
    main()
