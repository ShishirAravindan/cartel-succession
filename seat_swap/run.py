"""Play one main-line game (Phase 0 / A / smoke tests).

    uv run --project seat_swap python -m seat_swap.run --dry-run --rounds 5
    uv run --project seat_swap python -m seat_swap.run --rounds 30 --max-calls 80 --thinking off
    uv run --project seat_swap python -m seat_swap.run --provider modal --rounds 10 --max-calls 24
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from seat_swap.game import Game, Seat, git_state, make_env
from seat_swap.logging import RunLogger
from seat_swap.metrics import P_NASH
from seat_swap.model_config import SAMPLING
from seat_swap.prompts import INSTRUCTIONS
from seat_swap.providers import OpenRouterChat, RawCompletions, ScriptedProvider
from seat_swap.scripted import POLICIES, ramp_policy

DEFAULT_MODEL = "qwen/qwen3-14b"
RUNS_ROOT = Path(__file__).resolve().parent / "runs"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="scripted sellers, zero API calls")
    ap.add_argument("--dry-seat0", choices=["ramp", *POLICIES], default="ramp", help="dry-run seller in seat 0")
    ap.add_argument("--dry-seat1", choices=["ramp", *POLICIES], default="ramp", help="dry-run seller in seat 1")
    ap.add_argument("--max-calls", type=int, default=None, help="hard stop on model calls (required unless --dry-run)")
    ap.add_argument("--rounds", type=int, default=30)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--provider", choices=["openrouter", "modal"], default="openrouter",
                    help="modal = our vLLM endpoint serving seat_swap/model_config.py (ignores --model)")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter id for both seats")
    ap.add_argument("--thinking", choices=["on", "off"], default="off")
    ap.add_argument("--notes", choices=["on", "off"], default="on")
    ap.add_argument("--temperature", type=float, default=None, help="default: model_config.SAMPLING for the thinking mode")
    ap.add_argument("--max-tokens", type=int, default=None, help="default: model_config.SAMPLING for the thinking mode")
    ap.add_argument("--phase", default="smoke")
    ap.add_argument("--arm", default="main")
    ap.add_argument("--instruction", choices=sorted(INSTRUCTIONS), default=None,
                    help="extra system-prompt instruction (Phase 0 instructed pair only)")
    ap.add_argument("--warmup", choices=["nash", "cartel"], default="nash",
                    help="round-0 prices: near Nash (default) or both at 1.92 (positive control v2 only)")
    ap.add_argument("--shock-round", type=int, default=None,
                    help="force seat 0 to p_N in this round (its LLM is not called that round)")
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
    sampling = dict(SAMPLING[thinking])
    if args.temperature is not None:
        sampling["temperature"] = args.temperature
    if args.max_tokens is not None:
        sampling["max_tokens"] = args.max_tokens
    env = make_env(args.seed, notes_on=notes_on, instruction=INSTRUCTIONS.get(args.instruction), warmup=args.warmup)
    if args.dry_run:
        providers = [ScriptedProvider.from_price_policy(
            name, ramp_policy(env.lower_prices[0], env.upper_prices[0]) if name == "ramp" else POLICIES[name](),
            notes_on) for name in (args.dry_seat0, args.dry_seat1)]
    elif args.provider == "modal":
        providers = [RawCompletions.from_env() for _ in range(2)]
        print(f"vllm endpoint ready after {providers[0].wait_ready()}s")
    else:
        providers = [OpenRouterChat(args.model, sampling["temperature"], sampling["max_tokens"], thinking)
                     for _ in range(2)]
    model_tag = f"dry-{args.dry_seat0}-{args.dry_seat1}" if args.dry_run else providers[0].model.split("/")[-1].lower()
    run_id = args.run_id or (
        f"{time.strftime('%Y%m%d-%H%M%S')}_{args.phase}_{model_tag}"
        f"_think{args.thinking}_s{args.seed}"
    )
    logger = RunLogger(args.runs_root, run_id)
    game = Game(env, [Seat(p, thinking) for p in providers], logger, phase=args.phase, arm=args.arm,
                seed=args.seed, temperature=sampling["temperature"], max_tokens=sampling["max_tokens"],
                top_p=sampling["top_p"], top_k=sampling["top_k"],
                max_calls=args.max_calls, parallel=not args.sequential,
                shocks={args.shock_round: {0: P_NASH}} if args.shock_round else None,
                shock_calls_llm=False if args.shock_round else None)
    logger.config(game.config({"rounds": args.rounds, "dry_run": args.dry_run, "allow_dirty": args.allow_dirty,
                               "instruction_id": args.instruction, "shock_round": args.shock_round,
                               "warmup": args.warmup,
                               "shock_calls_llm": False if args.shock_round else None}))
    status = game.run(args.rounds, snapshot_at=set(args.snapshot_at) | {args.rounds})
    print(f"{run_id}: {status}")
    print(f"   {logger.dir}")
    return status


if __name__ == "__main__":
    main()
