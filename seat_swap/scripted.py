"""Scripted sellers for dry runs and offline self-tests (zero API calls).

Each scripted seller returns a completion string in the exact template a real model must
produce, so the strict parser is exercised on every dry-run round.
"""

from __future__ import annotations


def completion_text(price: float, seat: int, rnd: int, notes_on: bool = True) -> str:
    """Template-conformant completion with obviously fake, tagged notes."""
    if not notes_on:
        return f"My chosen price: {price:.2f}"
    tag = f"[dry-run seat {seat} round {rnd}]"
    return (
        f"My observations and thoughts:\n{tag} scripted seller, no reasoning.\n\n"
        f"New content for PLANS.txt:\n{tag} plan: price {price:.2f} next round.\n\n"
        f"New content for INSIGHTS.txt:\n{tag} insight: placeholder text.\n\n"
        f"My chosen price:\n{price:.2f}"
    )


def ramp_policy(p_n: float, p_m: float, step: float = 0.04):
    """Dry-run plumbing policy: walk from Nash toward monopoly; seat s lags by 0.01*s."""

    def policy(seat: int, rnd: int, history) -> float:
        return round(min(p_m, p_n + step * rnd - 0.01 * seat), 2)

    return policy
