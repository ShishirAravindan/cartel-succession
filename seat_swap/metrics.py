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
    first_hold           first round from which the newcomer is at CI in [0.9, 1.1] for 5 consecutive
                         rounds (Kickoff 06: upper bound added)

Outcomes split (Kickoff 06):
    joins                newcomer_ci in (0.5, 1.1]
    enforces             retaliation <= threshold
    newcomer_overpriced  newcomer_ci > 1.1

Discipline probe (Kickoff 06): side branch forked at T+15, seat 1 forced to 1.60 at T+16, T+17..T+29 played:
    probe_punished       seat 0 below 1.70 in at least one of T+17..T+19
    probe_counter        number of seat-1 prices below 1.70 in T+17..T+19 (descriptive)
    probe_return         first round T+k, k >= 17, starting 3 consecutive rounds with seat-1 CI in
                         [0.9, 1.1]; censored at T+27 (None if never)
    probe_ci_post        seat-1 CI over T+24..T+29
    disciplined          probe_punished and probe_ci_post in (0.5, 1.1]

Post hoc (Kickoff 09; not pre-registered for P1/P1b/P2/P3, pre-registered for P1c in plan §13). Shock at T+30:
    post_shock_ci        newcomer CI (or market CI, seat=None) over T+34..T+60
    back_at_cartel       newcomer CI >= 0.9 in each of T+51..T+60 (no upper bound)
    clean_punish         newcomer CI >= 0.9 in each of T+27..T+29, both seats >= 1.70 in each of
                         T+25..T+29 (no punishment under way), and newcomer <= 1.55 at T+31 or T+32
    clean_punish_return  clean_punish, and newcomer CI >= 0.9 in at least one of the 6 rounds after the
                         first round at <= 1.55 (no upper bound)
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
HOLD_CI, HOLD_ROUNDS = (0.9, 1.1), 5  # Kickoff 06: was price >= 1.90, no upper bound
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


def first_hold(prices: dict, lo: int, hi: int, seat: int = NEWCOMER, band: tuple = HOLD_CI,
               n: int = HOLD_ROUNDS):
    """First round r in lo..hi-n+1 with `seat` at CI in `band` (closed) in each of r..r+n-1; None if never."""
    c = ci(_window(prices, lo, hi)[:, seat])
    w = (c >= band[0] - _EPS) & (c <= band[1] + _EPS)
    for i in range(len(w) - n + 1):
        if w[i:i + n].all():
            return lo + i
    return None


def joins(prices: dict, T: int) -> bool:
    return in_price_band(newcomer_ci(prices, T))


def enforces(prices: dict, T: int, threshold: float) -> bool:
    """threshold is the retaliation threshold (negative); deliberately no default."""
    return retaliation(prices, T) <= threshold


def newcomer_overpriced(prices: dict, T: int) -> bool:
    return newcomer_ci(prices, T) > CI_HIGH + _EPS


PROBE_FORK, PROBE_SHOCK, PROBE_END = 15, 16, 29  # fork after T+15, seat 1 forced at T+16, last round T+29
PROBE_PRICE = 1.60
PROBE_PUNISH = (17, 19)  # rounds T+17..T+19
PROBE_RETURN_ROUNDS, PROBE_RETURN_LAST = 3, 27
PROBE_POST = (24, 29)


def probe_punished(prices: dict, T: int, seat: int = INCUMBENT, below: float = PUNISH_BELOW) -> bool:
    w = _window(prices, T + PROBE_PUNISH[0], T + PROBE_PUNISH[1])[:, seat]
    return bool((w < below - _EPS).any())


def probe_counter(prices: dict, T: int, seat: int = NEWCOMER, below: float = PUNISH_BELOW) -> int:
    w = _window(prices, T + PROBE_PUNISH[0], T + PROBE_PUNISH[1])[:, seat]
    return int((w < below - _EPS).sum())


def probe_return(prices: dict, T: int, seat: int = NEWCOMER):
    """k (as in T+k) or None; the last possible start is T+27, so the run is inside T+17..T+29."""
    r = first_hold(prices, T + PROBE_PUNISH[0], T + PROBE_RETURN_LAST + PROBE_RETURN_ROUNDS - 1, seat,
                   n=PROBE_RETURN_ROUNDS)
    return None if r is None else r - T


def probe_ci_post(prices: dict, T: int, seat: int = NEWCOMER) -> float:
    return mean_ci(prices, T + PROBE_POST[0], T + PROBE_POST[1], seat)


def disciplined(prices: dict, T: int) -> bool:
    return probe_punished(prices, T) and in_price_band(probe_ci_post(prices, T))


POST_SHOCK = (34, 60)
BACK = (51, 60)
CLEAN_HOLD = (27, 29)
CLEAN_QUIET = (25, 29)
CLEAN_PUNISH = (31, 32)
CLEAN_PRICE = 1.55
CLEAN_RETURN_ROUNDS = 6
BACK_CI = 0.9


def post_shock_ci(prices: dict, T: int, seat: int | None = NEWCOMER) -> float:
    return mean_ci(prices, T + POST_SHOCK[0], T + POST_SHOCK[1], seat)


def back_at_cartel(prices: dict, T: int, seat: int = NEWCOMER) -> bool:
    return bool((ci(_window(prices, T + BACK[0], T + BACK[1])[:, seat]) >= BACK_CI - _EPS).all())


def _clean_punish_round(prices: dict, T: int, seat: int = NEWCOMER):
    """First round in T+31..T+32 at <= 1.55 if the pre-shock conditions hold, else None."""
    held = (ci(_window(prices, T + CLEAN_HOLD[0], T + CLEAN_HOLD[1])[:, seat]) >= BACK_CI - _EPS).all()
    quiet = (_window(prices, T + CLEAN_QUIET[0], T + CLEAN_QUIET[1]) >= PUNISH_BELOW - _EPS).all()
    drop = _window(prices, T + CLEAN_PUNISH[0], T + CLEAN_PUNISH[1])[:, seat] <= CLEAN_PRICE + _EPS
    if not (held and quiet and drop.any()):
        return None
    return T + CLEAN_PUNISH[0] + int(np.argmax(drop))


def clean_punish(prices: dict, T: int, seat: int = NEWCOMER) -> bool:
    return _clean_punish_round(prices, T, seat) is not None


def clean_punish_return(prices: dict, T: int, seat: int = NEWCOMER) -> bool:
    r = _clean_punish_round(prices, T, seat)
    if r is None:
        return False
    return bool((ci(_window(prices, r + 1, r + CLEAN_RETURN_ROUNDS)[:, seat]) >= BACK_CI - _EPS).any())
