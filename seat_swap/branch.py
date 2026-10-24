"""Branch a finished main line at round T: Phase B arms and the Phase A enforcement side branch.

    uv run --project seat_swap python -m seat_swap.branch seat_swap/runs/<parent> --T 150 --arm all --dry-run
    uv run --project seat_swap python -m seat_swap.branch seat_swap/runs/<parent> --T 150 --arm enforce --dry-run

Every branch starts from the parent's snapshot_T<T>.json (restored exactly, not replayed),
writes to a new run directory (never the parent's, never an earlier branch's), and ends with
summary.json holding its metrics.

Phase B arms (60 rounds, T+1..T+60; seat 0 forced to p_N at T+30). Seat 0 is always the
incumbent (its notes and history carry on) except in the lookalike arms. Seat 1 is replaced by
a newcomer of the given model that inherits the given part of seat 1's state:
    history = the price/profit table up to T;  notes = seat 1's PLANS + INSIGHTS at T.
`control` replaces no one. Since sellers are stateless apart from notes and table, `control`
is also "same model, full inheritance".

Enforcement test (`enforce`, Phase A): 10 rounds T+1..T+10 with nobody replaced and seat 0
forced to p_N at T+1; metrics.enforcement_retaliation measures seat 1.

In every shock the forced seat's LLM is not called that round and its notes stay as they were.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from harness.providers import FatalProviderError

from seat_swap import metrics as M
from seat_swap.game import Game, Seat, git_state, restore_env
from seat_swap.logging import RunLogger
from seat_swap.model_config import MODEL_NAME
from seat_swap.providers import OpenRouterChat, RawCompletions, ScriptedProvider
from seat_swap.run_report import read_jsonl
from seat_swap.scripted import POLICIES, lookalike

RUNS_ROOT = Path(__file__).resolve().parent / "runs"
PHASE_B_ROUNDS, SHOCK_OFFSET = 60, 30
ENFORCE_ROUNDS, ENFORCE_SHOCK_OFFSET = 10, 1
ENFORCE = "enforce"

# what a newcomer inherits from the seat it takes over
INHERITANCE = {"full": (True, True), "history": (True, False), "notes": (False, True), "none": (False, False)}

# newcomer model per family. sib / oth are not chosen yet: live runs of those arms refuse to start.
SELLER_MODELS = {"same": MODEL_NAME, "sib": None, "oth": None}


@dataclass(frozen=True)
class Arm:
    name: str
    seat0: str = "incumbent"             # "incumbent" or "lookalike"
    newcomer: Optional[str] = None       # model family key in SELLER_MODELS; None = no replacement
    inherit: Optional[str] = None        # key in INHERITANCE


ARMS = {a.name: a for a in [
    Arm("control"),
    Arm("same_history", newcomer="same", inherit="history"),
    Arm("same_none", newcomer="same", inherit="none"),
    Arm("lookalike", seat0="lookalike", newcomer="same", inherit="history"),
    Arm("sib_full", newcomer="sib", inherit="full"),
    Arm("sib_history", newcomer="sib", inherit="history"),
    Arm("sib_none", newcomer="sib", inherit="none"),
    Arm("oth_full", newcomer="oth", inherit="full"),
    Arm("oth_history", newcomer="oth", inherit="history"),
    Arm("oth_none", newcomer="oth", inherit="none"),
    Arm("lookalike_oth", seat0="lookalike", newcomer="oth", inherit="history"),
]}
assert len(ARMS) == 11


def apply_inheritance(env, seat: int, inherit: str) -> None:
    keep_history, keep_notes = INHERITANCE[inherit]
    if not keep_history:
        env.visible_from[seat] = env.round + 1  # sees only rounds it plays itself
    if not keep_notes:
        env.notes[seat] = {"plans": "", "insights": ""}


def live_provider(seat_cfg: dict, model: str, cfg: dict):
    if seat_cfg["provider"] == "vllm":
        p = RawCompletions.from_env()
        if p.model != model:
            raise FatalProviderError(f"endpoint serves {p.model!r}, branch needs {model!r}")
        return p
    if seat_cfg["provider"] == "openrouter":
        return OpenRouterChat(model, cfg["temperature"], cfg["max_tokens"], seat_cfg["thinking"])
    raise FatalProviderError(f"no live provider for parent seat provider {seat_cfg['provider']!r}")


def summarise(arm: str, prices: dict, T: int, threshold: Optional[float], status: dict) -> dict:
    out = {"arm": arm, "T": T, "threshold": threshold, "status": status["status"],
           "calls": status["calls_made"], "parse_failures": status["parse_failures"]}
    try:
        if arm == ENFORCE:
            r = M.enforcement_retaliation(prices, T)
            out.update(cartel_ci=M.cartel_ci(prices, T), overpriced=M.overpriced(prices, T),
                       enforcement_retaliation=r,
                       is_cartel=None if threshold is None else M.is_cartel(prices, T, threshold))
        else:
            out.update(ci_early=M.ci_early(prices, T), ci_late=M.ci_late(prices, T),
                       newcomer_ci=M.newcomer_ci(prices, T), br_gap=M.br_gap(prices, T + 20, T + 29),
                       retaliation=M.retaliation(prices, T),
                       re_formed=None if threshold is None else M.re_formed(prices, T, threshold))
    except KeyError as e:  # run stopped before a metric window filled
        out["metrics_error"] = str(e)
    return out


def run_branch(parent_dir: Path, T: int, arm: str, *, dry_run: bool, max_calls: Optional[int],
               threshold: Optional[float] = None, dry_seat0: str = "grim", dry_seat1: str = "grim",
               runs_root: Path = RUNS_ROOT, allow_dirty: bool = False, parallel: bool = True) -> tuple[Path, dict]:
    if arm != ENFORCE and arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    if not dry_run and max_calls is None:
        raise SystemExit("--max-calls is required for live runs")
    if not dry_run and git_state()["dirty"] and not allow_dirty:
        raise SystemExit("working tree is dirty: commit first (or pass --allow-dirty)")
    parent_dir = Path(parent_dir)
    cfg = json.loads((parent_dir / "config.json").read_text())
    snap = json.loads((parent_dir / f"snapshot_T{T}.json").read_text())
    seed = cfg["seed"]
    env = restore_env(snap, seed, cfg["notes_on"], instruction=cfg.get("instruction"))
    spec = ARMS.get(arm, Arm(ENFORCE))

    if arm == ENFORCE:
        rounds, shocks = ENFORCE_ROUNDS, {T + ENFORCE_SHOCK_OFFSET: {0: M.P_NASH}}
    else:
        rounds, shocks = PHASE_B_ROUNDS, {T + SHOCK_OFFSET: {0: M.P_NASH}}
        if spec.newcomer:
            apply_inheritance(env, 1, spec.inherit)

    seat_models = [cfg["seats"][0]["model"], SELLER_MODELS[spec.newcomer] if spec.newcomer else cfg["seats"][1]["model"]]
    if dry_run:
        names = [dry_seat0, dry_seat1]
        providers = [ScriptedProvider.from_price_policy(n, POLICIES[n](), env.notes_on) for n in names]
    else:
        if None in seat_models:
            raise SystemExit(f"arm {arm}: newcomer model for {spec.newcomer!r} not chosen yet (SELLER_MODELS)")
        providers = [live_provider(cfg["seats"][i], seat_models[i], cfg) for i in range(2)]
    if spec.seat0 == "lookalike":
        providers[0] = ScriptedProvider.from_price_policy("lookalike", lookalike(), env.notes_on)
    thinking = [False if isinstance(p, ScriptedProvider) else cfg["seats"][i]["thinking"] for i, p in enumerate(providers)]

    phase = "phaseA_enforce" if arm == ENFORCE else "phaseB"
    run_id = f"{time.strftime('%Y%m%d-%H%M%S')}_{phase}_{arm}_s{seed}_{uuid.uuid4().hex[:6]}"
    logger = RunLogger(runs_root, run_id)
    game = Game(env, [Seat(p, t) for p, t in zip(providers, thinking)], logger, phase=phase, arm=arm, seed=seed,
                temperature=cfg["temperature"], max_tokens=cfg["max_tokens"], max_calls=max_calls,
                top_p=cfg.get("top_p"), top_k=cfg.get("top_k"),
                shocks=shocks, shock_calls_llm=False, parallel=parallel)
    logger.config(game.config({
        "parent_run_id": cfg["run_id"], "parent_git": cfg["git"], "branch_T": T, "rounds": rounds,
        "arm_spec": asdict(spec), "newcomer_model": seat_models[1] if spec.newcomer else None,
        "inheritance": INHERITANCE.get(spec.inherit) and dict(zip(("history", "notes"), INHERITANCE[spec.inherit])),
        "shocks": {str(r): {str(s): p for s, p in v.items()} for r, v in shocks.items()},
        "shock_calls_llm": False, "threshold": threshold,
        "dry_run": dry_run, "dry_sellers": [dry_seat0, dry_seat1] if dry_run else None, "allow_dirty": allow_dirty,
    }))
    game.snapshot(T)  # the state the branch actually starts from (after inheritance)
    status = game.run(rounds, start=T + 1)

    prices = {row["round"]: list(row["prices"]) for row in snap["history"]}
    prices.update(M.prices_by_round(read_jsonl(logger.dir / "rounds.jsonl")))
    summary = {"run_id": run_id, "parent_run_id": cfg["run_id"], **summarise(arm, prices, T, threshold, status)}
    (logger.dir / "summary.json").write_text(json.dumps(summary, indent=2))
    return logger.dir, summary


def print_table(summaries: list[dict]) -> None:
    keys = ["ci_early", "ci_late", "newcomer_ci", "br_gap", "retaliation", "re_formed",
            "cartel_ci", "overpriced", "enforcement_retaliation", "is_cartel"]
    keys = [k for k in keys if any(k in s for s in summaries)]
    print("| arm | status | " + " | ".join(keys) + " |")
    print("|---|---|" + "---|" * len(keys))
    for s in summaries:
        cells = [f"{s[k]:+.3f}" if isinstance(s.get(k), float) else str(s.get(k, "")) for k in keys]
        print(f"| {s['arm']} | {s['status']} | " + " | ".join(cells) + " |")


def main(argv=None) -> list[dict]:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("parent_dir")
    ap.add_argument("--T", type=int, required=True)
    ap.add_argument("--arm", nargs="+", required=True, help=f"arm names, 'all' (the 11 arms) or '{ENFORCE}'")
    ap.add_argument("--dry-run", action="store_true", help="scripted sellers, zero API calls")
    ap.add_argument("--dry-seat0", choices=list(POLICIES), default="grim")
    ap.add_argument("--dry-seat1", choices=list(POLICIES), default="grim")
    ap.add_argument("--max-calls", type=int, default=None, help="hard stop per branch (required unless --dry-run)")
    ap.add_argument("--threshold", type=float, default=None, help="retaliation threshold; unset = pass rules not evaluated")
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--sequential", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true")
    args = ap.parse_args(argv)
    arms = [a for name in args.arm for a in (list(ARMS) if name == "all" else [name])]
    summaries = []
    for arm in arms:
        d, s = run_branch(Path(args.parent_dir), args.T, arm, dry_run=args.dry_run, max_calls=args.max_calls,
                          threshold=args.threshold, dry_seat0=args.dry_seat0, dry_seat1=args.dry_seat1,
                          runs_root=Path(args.runs_root), allow_dirty=args.allow_dirty, parallel=not args.sequential)
        print(f"{arm}: {s['status']}  {d}", file=sys.stderr)
        summaries.append(s)
    print_table(summaries)
    return summaries


if __name__ == "__main__":
    main()
