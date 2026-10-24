"""Dry run (scripted sellers, zero API calls): print the prompt one seat reads at one round.

    uv run --project seat_swap python -m seat_swap.show_prompt --seat 1 --round 10
"""

from __future__ import annotations

import argparse
import json

from seat_swap.game import WINDOW, make_env
from seat_swap.prompts import parse_response
from seat_swap.render import QWEN3_8B, QWEN3_8B_REVISION, render
from seat_swap.scripted import completion_text, ramp_policy


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seat", type=int, default=1)
    ap.add_argument("--round", type=int, default=10, help="prompt read before choosing this round's price")
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--notes", choices=["on", "off"], default="on")
    ap.add_argument("--thinking", choices=["on", "off"], default="off")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    notes_on = args.notes == "on"

    env = make_env(args.seed, notes_on=notes_on, window=args.window)
    p_n, p_m = env.lower_prices[0], env.upper_prices[0]
    policy = ramp_policy(p_n, p_m)

    for t in range(1, args.round):
        prices = [policy(s, t, None) for s in range(env.nagents)]
        for s, price in enumerate(prices):
            parsed = parse_response(completion_text(price, s, t, notes_on), notes_on)
            assert parsed.ok and parsed.price == price, parsed
            env.notes[s] = {"plans": parsed.plans, "insights": parsed.insights}
        env.step(prices)

    messages = env.generate_prompt(args.seat)
    print(f"# convention: round t = t-th LLM decision; warm-up = Round 0; window = last {args.window} rounds")
    print(f"# seat {args.seat}, prompt before round {args.round}, notes {args.notes}, thinking {args.thinking}")
    print(f"# Nash {p_n:.3f}  monopoly {p_m:.3f}")
    print("\n===== messages JSON =====")
    print(json.dumps(messages, indent=2, ensure_ascii=False))
    print(f"\n===== rendered_prompt_local ({QWEN3_8B}@{QWEN3_8B_REVISION[:12]}, enable_thinking={args.thinking == 'on'}) =====")
    print(render(messages, enable_thinking=args.thinking == "on"), end="")
    print("<<END>>")


if __name__ == "__main__":
    main()
