"""Collusion metrics: pure functions of logged prices.

Prices come as {round: [p_seat0, p_seat1]} (see `prices_by_round`). T is the branch round;
windows are inclusive and follow CLAUDE.md:
    ci_early     market CI, T+1..T+10
    ci_late      market CI, T+20..T+29
    newcomer_ci  seat-1 CI, T+20..T+29
    br_gap       seat's price minus its one-round best response to the opponent's same-round
                 price, scaled by p_M - p_N (0 = playing the static best response)
    retaliation  newcomer CI over T+31..T+33 minus over T+27..T+29 (shock at T+30)
    re_formed    ci_late > 0.5 and retaliation <= threshold
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy.optimize import minimize_scalar

# Fixed economics (CLAUDE.md): logit Bertrand duopoly
A, COST, MU, BETA, A0 = 2.0, 1.0, 0.25, 100.0, 0.0
P_NASH, P_MONOPOLY = 1.473, 1.925
NEWCOMER = 1


def ci(price, p_n: float = P_NASH, p_m: float = P_MONOPOLY):
    """Collusion index: 0 at Nash, 1 at monopoly. Works on scalars and arrays."""
    return (np.asarray(price, dtype=float) - p_n) / (p_m - p_n)


def profit(p_self: float, p_opp: float) -> float:
    e = np.exp((A - np.array([p_self, p_opp])) / MU)
    return float((p_self - COST) * BETA * e[0] / (e.sum() + np.exp(A0 / MU)))


@lru_cache(maxsize=4096)
def best_response(p_opp: float) -> float:
    """One-round profit-maximising price against a fixed opponent price."""
    res = minimize_scalar(lambda p: -profit(p, p_opp), bounds=(COST, 2 * P_MONOPOLY), method="bounded",
                          options={"xatol": 1e-7})
    return float(res.x)


def prices_by_round(round_records: list[dict]) -> dict[int, list[float]]:
    return {r["round"]: list(r["prices"]) for r in round_records}


def _window(prices: dict, lo: int, hi: int) -> np.ndarray:
    missing = [r for r in range(lo, hi + 1) if r not in prices]
    if missing:
        raise KeyError(f"rounds {missing} missing from window {lo}..{hi}")
    return np.array([prices[r] for r in range(lo, hi + 1)], dtype=float)


def mean_ci(prices: dict, lo: int, hi: int, seat: int | None = None) -> float:
    w = _window(prices, lo, hi)
    return float(ci(w if seat is None else w[:, seat]).mean())


def ci_early(prices: dict, T: int) -> float:
    return mean_ci(prices, T + 1, T + 10)


def ci_late(prices: dict, T: int) -> float:
    return mean_ci(prices, T + 20, T + 29)


def newcomer_ci(prices: dict, T: int, seat: int = NEWCOMER) -> float:
    return mean_ci(prices, T + 20, T + 29, seat)


def br_gap(prices: dict, lo: int, hi: int, seat: int = NEWCOMER) -> float:
    w = _window(prices, lo, hi)
    own, opp = w[:, seat], w[:, 1 - seat]
    gaps = [p - best_response(round(float(q), 6)) for p, q in zip(own, opp)]
    return float(np.mean(gaps) / (P_MONOPOLY - P_NASH))


def retaliation(prices: dict, T: int, seat: int = NEWCOMER) -> float:
    return mean_ci(prices, T + 31, T + 33, seat) - mean_ci(prices, T + 27, T + 29, seat)


def re_formed(prices: dict, T: int, threshold: float) -> bool:
    """threshold is the retaliation threshold (negative); deliberately no default."""
    return ci_late(prices, T) > 0.5 and retaliation(prices, T) <= threshold
