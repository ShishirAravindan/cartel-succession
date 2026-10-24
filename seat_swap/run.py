"""Play one main-line game (Phase 0 / A / smoke tests).

    uv run --project seat_swap python -m seat_swap.run --dry-run --rounds 5
    uv run --project seat_swap python -m seat_swap.run --rounds 30 --max-calls 80 --thinking off
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from seat_swap.game import Game, Seat, git_state, make_env
from seat_swap.logging import RunLogger
from seat_swap.providers import OpenRouterChat, ScriptedProvider
from seat_swap.scripted import ramp_policy

DEFAULT_MODEL = "qwen/qwen3-8b"
RUNS_ROOT = Path(__file__).resolve().parent / "runs"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="scripted sellers, zero API calls")
    ap.add_argument("--max-calls", type=int, default=None, help="hard stop on model calls (required unless --dry-run)")
    ap.add_argument("--rounds", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter id for both seats")
    ap.add_argument("--thinking", choices=["on", "off"], default="off")
    ap.add_argument("--notes", choices=["on", "off"], default="on")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--phase", default="smoke")
    ap.add_argument("--arm", default="main")
    ap.add_argument("--snapshot-at", type=int, nargs="*", default=[])
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--runs-root", default=str(RUNS_ROOT))
    ap.add_argument("--sequential", action="store_true")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="run live on uncommitted code (recorded in config; avoid for real results)")
    return ap


def main(argv=None) -> dict:
    args = build_parser().parse_args(argv)
    if not args.dry_run and args.max_calls is None:
        sys.exit("--max-calls is required for live runs")
    if not args.dry_run and git_state()["dirty"] and not args.allow_dirty:
        sys.exit("working tree is dirty: commit first so the run's git sha points at the code it ran "
                 "(or pass --allow-dirty)")
    notes_on, thinking = args.notes == "on", args.thinking == "on"
    env = make_env(args.seed, notes_on=notes_on)
    if args.dry_run:
        policy = ramp_policy(env.lower_prices[0], env.upper_prices[0])
        providers = [ScriptedProvider.from_price_policy("ramp", policy, notes_on) for _ in range(2)]
    else:
        providers = [OpenRouterChat(args.model, args.temperature, args.max_tokens, thinking) for _ in range(2)]
    run_id = args.run_id or (
        f"{time.strftime('%Y%m%d-%H%M%S')}_{args.phase}_{'dry' if args.dry_run else args.model.split('/')[-1]}"
        f"_think{args.thinking}_s{args.seed}"
    )
    logger = RunLogger(args.runs_root, run_id)
    game = Game(env, [Seat(p, thinking) for p in providers], logger, phase=args.phase, arm=args.arm,
                seed=args.seed, temperature=args.temperature, max_tokens=args.max_tokens,
                max_calls=args.max_calls, parallel=not args.sequential)
    logger.config(game.config({"rounds": args.rounds, "dry_run": args.dry_run, "allow_dirty": args.allow_dirty}))
    status = game.run(args.rounds, snapshot_at=set(args.snapshot_at) | {args.rounds})
    print(f"{run_id}: {status}")
    print(f"   {logger.dir}")
    return status


if __name__ == "__main__":
    main()
