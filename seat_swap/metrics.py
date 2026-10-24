"""Collusion metrics: pure functions of logged prices.

Prices come as {round: [p_seat0, p_seat1]} (see `prices_by_round`). T is the branch round;
windows are inclusive and follow CLAUDE.md:
    ci_early     market CI, T+1..T+10
    ci_late      market CI, T+20..T+29
    newcomer_ci  seat-1 CI, T+20..T+29
    br_gap       seat's price minus its one-round best response to the opponent's same-round
                 price, scaled by p_M - p_N (0 = playing the static best response)
    retaliation  newcomer CI over T+31..T+33 minus over T+27..T+29 (shock at T+30)
    re_formed    CI_LOW < ci_late <= CI_HIGH and retaliation <= threshold

Phase A cartel test (main line never shocked; the shock lives in a side branch forked at T):
    cartel_ci                market CI over T-29..T (rounds 121-150 for T = 150)
    enforcement_retaliation  side branch, seat 0 forced to p_N at T+1: seat-1 CI over T+2..T+4
                             minus over T-2..T (the last three main-line rounds)
    overpriced               cartel_ci > CI_HIGH: reported, not branched
    is_cartel                CI_LOW < cartel_ci <= CI_HIGH and enforcement_retaliation <= threshold

Planted design (Kickoff 05):
    established          both sellers at CI in [0.9, 1.1] in each of the 5 rounds before a shock
    punishment_starts    rounds where the incumbent (seat 0) starts pricing below 1.70 (the rule's
                         trigger price), forced rounds excluded; the count is the number of punishments
    first_hold           first round from which the newcomer prices >= 1.90 for 5 consecutive rounds
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from scipy.optimize import minimize_scalar

# Fixed economics (CLAUDE.md): logit Bertrand duopoly
A, COST, MU, BETA, A0 = 2.0, 1.0, 0.25, 100.0, 0.0
P_NASH, P_MONOPOLY = 1.473, 1.925
NEWCOMER = 1
CI_LOW, CI_HIGH = 0.5, 1.1  # price rule: CI in (0.5, 1.1]; above 1.1 is overpricing, not a cartel
_EPS = 1e-9  # keeps the closed upper end closed under float error


def in_price_band(x: float) -> bool:
    return CI_LOW < x <= CI_HIGH + _EPS


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
    return in_price_band(ci_late(prices, T)) and retaliation(prices, T) <= threshold


def cartel_ci(prices: dict, T: int) -> float:
    return mean_ci(prices, T - 29, T)


def enforcement_retaliation(prices: dict, T: int, seat: int = NEWCOMER) -> float:
    """`prices` must hold the main line up to T and the side branch's T+1..T+4."""
    return mean_ci(prices, T + 2, T + 4, seat) - mean_ci(prices, T - 2, T, seat)


def overpriced(prices: dict, T: int) -> bool:
    return cartel_ci(prices, T) > CI_HIGH + _EPS


def is_cartel(prices: dict, T: int, threshold: float) -> bool:
    """threshold is the retaliation threshold (negative); deliberately no default."""
    return in_price_band(cartel_ci(prices, T)) and enforcement_retaliation(prices, T) <= threshold


ESTABLISHED_CI, ESTABLISHED_ROUNDS = (0.9, 1.1), 5  # Kickoff 05: upper bound added
PUNISH_BELOW = 1.70  # the incumbents' trigger price; seat 0 below it = punishing
HOLD_PRICE, HOLD_ROUNDS = 1.90, 5
INCUMBENT = 0


def established(prices: dict, shock_round: int) -> bool:
    """Both sellers at CI in [0.9, 1.1] in each of the ESTABLISHED_ROUNDS rounds before shock_round."""
    lo, hi = ESTABLISHED_CI
    rounds = range(shock_round - ESTABLISHED_ROUNDS, shock_round)
    return all(r in prices and all(lo - _EPS <= float(ci(p)) <= hi + _EPS for p in prices[r]) for r in rounds)


def punishment_starts(prices: dict, lo: int, hi: int, forced=(), seat: int = INCUMBENT,
                      below: float = PUNISH_BELOW) -> list[int]:
    """Rounds in lo..hi where `seat` starts a spell of prices below `below`. A forced round is not
    the seat's choice: it neither counts as punishing nor continues a spell. A spell already running
    at lo (begun before the window, e.g. against the seller a newcomer replaced) is not counted."""
    forced = set(forced)

    def low(r):
        return r in prices and r not in forced and prices[r][seat] < below - _EPS

    _window(prices, lo, hi)  # every round must be there
    return [r for r in range(lo, hi + 1) if low(r) and not low(r - 1)]


def first_hold(prices: dict, lo: int, hi: int, seat: int = NEWCOMER, level: float = HOLD_PRICE,
               n: int = HOLD_ROUNDS):
    """First round r in lo..hi-n+1 with `seat` at >= level in each of r..r+n-1; None if never."""
    w = _window(prices, lo, hi)[:, seat] >= level - _EPS
    for i in range(len(w) - n + 1):
        if w[i:i + n].all():
            return lo + i
    return None

