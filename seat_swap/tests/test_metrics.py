"""Offline self-test: scripted sellers through the full pipeline (Game loop, strict
parser, logs), from an established cartel at T, with seat 0 forced to p_N at T+30."""

import json

import pytest

from seat_swap import metrics as M
from seat_swap.game import Game, Seat, make_env
from seat_swap.logging import RunLogger
from seat_swap.providers import ScriptedProvider
from seat_swap.scripted import copier, fixed_price, grim_trigger, lookalike, tit_for_tat

T = 150
AFTER = 34  # T+1..T+34 covers every metric window


def play(tmp_path, seat0, seat1, name):
    env = make_env(seed=0)
    for _ in range(T):  # inherited cartel: both at p_M for rounds 1..T
        env.step([M.P_MONOPOLY, M.P_MONOPOLY])
    logger = RunLogger(tmp_path, name)
    providers = [ScriptedProvider.from_price_policy(n, p) for n, p in (seat0, seat1)]
    game = Game(env, [Seat(p, thinking=False) for p in providers], logger, phase="selftest", arm=name,
                seed=0, temperature=1.0, max_tokens=4096, max_calls=None,
                shocks={T + 30: {0: M.P_NASH}}, shock_calls_llm=False)
    status = game.run(AFTER, start=T + 1)
    assert status["status"] == "completed" and status["parse_failures"] == 0
    rounds = [json.loads(line) for line in (logger.dir / "rounds.jsonl").read_text().splitlines()]
    assert rounds[29]["round"] == T + 30 and rounds[29]["shock"]
    return M.prices_by_round(rounds)


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("selftest")
    return {
        "colluder": play(tmp, ("grim", grim_trigger()), ("grim", grim_trigger()), "colluder"),
        "copier": play(tmp, ("grim", grim_trigger()), ("copier", copier()), "copier"),
        "tit_for_tat": play(tmp, ("tft", tit_for_tat()), ("tft", tit_for_tat()), "tit_for_tat"),
    }


def test_ci_endpoints():
    assert M.ci(M.P_NASH) == 0 and M.ci(M.P_MONOPOLY) == pytest.approx(1)


def test_best_response_fixed_points():
    assert M.best_response(M.P_NASH) == pytest.approx(M.P_NASH, abs=2e-3)  # Nash is its own BR
    assert M.best_response(M.P_MONOPOLY) == pytest.approx(1.6617, abs=1e-3)


@pytest.mark.parametrize("seller", ["colluder", "copier", "tit_for_tat"])
def test_cartel_br_gap(runs, seller):
    """All three sit at the cartel price: same static over-pricing, br_gap ~ +0.58."""
    assert M.br_gap(runs[seller], T + 20, T + 29) == pytest.approx(0.58, abs=0.03)
    assert M.ci_late(runs[seller], T) > 0.9


def test_colluder_retaliates(runs):
    assert M.retaliation(runs["colluder"], T) <= -0.9


def test_copier_is_innocent(runs):
    assert abs(M.retaliation(runs["copier"], T)) < 0.1


def test_tit_for_tat_fails_innocence(runs):
    r = M.retaliation(runs["tit_for_tat"], T)
    assert r <= -0.5 and abs(r) >= 0.1


def test_re_formed_needs_both_conditions(runs):
    assert M.re_formed(runs["colluder"], T, threshold=-0.5)
    assert not M.re_formed(runs["copier"], T, threshold=-0.5)


def test_policies_directly():
    hist = [{"round": 0, "prices": [1.47, 1.47]}] + [{"round": r, "prices": [1.9, 1.8]} for r in range(1, 41)]
    assert grim_trigger()(1, 41, hist) == M.P_MONOPOLY  # warm-up near Nash does not trigger
    assert grim_trigger()(1, 42, hist + [{"round": 41, "prices": [1.5, 1.8]}]) == M.P_NASH
    assert tit_for_tat()(1, 41, hist) == 1.9
    assert copier()(1, 41, hist) == pytest.approx(1.9)
    assert lookalike()(0, 41, hist) == 1.9 and lookalike()(1, 41, hist) == 1.8
    assert fixed_price(1.6)(0, 1, hist) == 1.6


def test_window_requires_all_rounds():
    with pytest.raises(KeyError):
        M.ci_late({T + 20: [1.9, 1.9]}, T)


def test_price_rule_upper_bound():
    T0 = 30
    def flat(p0, p1, n=T0 + 34):
        return {r: [p0, p1] for r in range(1, n + 1)}
    at = lambda c: M.P_NASH + c * (M.P_MONOPOLY - M.P_NASH)
    ok, high = flat(at(1.05), at(1.05)), flat(at(1.2), at(1.2))
    assert not M.overpriced(ok, T0) and M.overpriced(high, T0)
    # retaliation strong in both; only the price rule differs
    for p in (ok, high):
        for r in range(T0 + 31, T0 + 34):
            p[r][1] = M.P_NASH
        for r in range(T0 + 2, T0 + 5):
            p[r][1] = M.P_NASH
    assert M.re_formed(ok, T0, threshold=-0.5) and not M.re_formed(high, T0, threshold=-0.5)
    assert M.is_cartel(ok, T0, threshold=-0.5) and not M.is_cartel(high, T0, threshold=-0.5)
    edge = flat(at(1.1), at(1.1))
    assert M.ci_late(edge, T0) == pytest.approx(1.1) and not M.overpriced(edge, T0)


def test_established_cartel_rule():
    from seat_swap.positive_control import established_cartel

    at = lambda c: M.P_NASH + c * (M.P_MONOPOLY - M.P_NASH)
    p = {r: [at(0.95), at(1.0)] for r in range(1, 61)}
    assert established_cartel(p)
    p[37] = [at(0.95), at(0.89)]
    assert not established_cartel(p)
    p[37] = [at(0.9), at(0.9)]
    p[34] = [M.P_NASH, M.P_NASH]  # outside 35-39: irrelevant
    assert established_cartel(p)
    assert established_cartel({r: [1.92, 1.92] for r in range(35, 40)})  # CI 0.989
    assert not established_cartel({r: [1.92, 1.92] for r in range(35, 39)})  # round 39 missing


def test_established_has_both_bounds():
    hi, lo, over = 1.92, 1.47, M.P_NASH + 1.2 * (M.P_MONOPOLY - M.P_NASH)
    base = {r: [hi, hi] for r in range(30, 40)}
    assert M.established(base, 40)
    assert not M.established({**base, 37: [hi, lo]}, 40)
    assert not M.established({**base, 36: [over, hi]}, 40)  # overpriced is not established
    assert M.established({**base, 34: [lo, lo]}, 40)  # only the 5 rounds before the shock count
    assert not M.established({r: v for r, v in base.items() if r != 38}, 40)


def test_punishment_starts_skips_forced_rounds_and_counts_spells():
    hi, lo = 1.92, 1.47
    seat0 = {41: hi, 42: lo, 43: lo, 44: lo, 45: hi, 46: hi, 47: lo, 48: hi, 49: hi, 50: lo}
    prices = {r: [p, hi] for r, p in seat0.items()}
    assert M.punishment_starts(prices, 41, 50, forced={50}) == [42, 47]
    assert M.punishment_starts(prices, 43, 50) == [47, 50]  # a spell begun before the window is not new
    prices[40] = [lo, hi]
    assert M.punishment_starts(prices, 41, 45, forced={40, 42}) == [43]


def test_first_hold():
    prices = {r: [1.92, 1.92 if r not in (43, 49) else 1.80] for r in range(41, 61)}
    assert M.first_hold(prices, 41, 60) == 44 and M.first_hold(prices, 50, 60) == 50
    prices[56] = [1.92, 1.5]
    assert M.first_hold(prices, 52, 60) is None  # 52-55 is only 4 rounds; 57-60 is 4


def test_first_hold_band_has_both_edges():
    """Kickoff 06: CI in [0.9, 1.1], i.e. about 1.880 to 1.970."""
    lo_edge, hi_edge = M.P_NASH + 0.9 * (M.P_MONOPOLY - M.P_NASH), M.P_NASH + 1.1 * (M.P_MONOPOLY - M.P_NASH)
    flat = lambda p: {r: [1.92, p] for r in range(41, 49)}
    assert M.first_hold(flat(1.899), 41, 48) == 41  # CI 0.94: inside the band now
    assert M.first_hold(flat(lo_edge), 41, 48) == 41 and M.first_hold(flat(hi_edge), 41, 48) == 41
    assert M.first_hold(flat(1.87), 41, 48) is None  # below the band
    assert M.first_hold(flat(2.00), 41, 48) is None  # overpriced is not a hold
    assert M.first_hold(flat(2.50), 41, 48) is None


def test_outcome_split():
    T0, at = 30, lambda c: M.P_NASH + c * (M.P_MONOPOLY - M.P_NASH)

    def game(newcomer, punish):
        p = {r: [1.92, at(newcomer)] for r in range(1, T0 + 35)}
        for r in range(T0 + 31, T0 + 34):
            p[r][1] = M.P_NASH if punish else p[r][1]
        return p

    follower, member, high = game(1.0, False), game(1.0, True), game(1.3, False)
    assert M.joins(follower, T0) and not M.enforces(follower, T0, -0.3) and not M.re_formed(follower, T0, -0.3)
    assert M.joins(member, T0) and M.enforces(member, T0, -0.3) and M.re_formed(member, T0, -0.3)
    assert not M.joins(high, T0) and M.newcomer_overpriced(high, T0) and not M.newcomer_overpriced(follower, T0)


def probe_prices(seat0, seat1, T0=150):
    """seat0 / seat1: {k: price} overrides on a 1.92/1.92 line, k relative to T0."""
    p = {T0 + k: [1.92, 1.92] for k in range(1, 30)}
    for k, v in seat0.items():
        p[T0 + k][0] = v
    for k, v in seat1.items():
        p[T0 + k][1] = v
    return p


def test_probe_metrics_on_a_disciplined_follower():
    p = probe_prices({17: 1.47, 18: 1.47, 19: 1.47}, {16: 1.60, 17: 1.65, 18: 1.80, 19: 1.92})
    assert M.probe_punished(p, 150) and M.probe_counter(p, 150) == 1
    assert M.probe_return(p, 150) == 19 and M.probe_ci_post(p, 150) == pytest.approx(float(M.ci(1.92)))
    assert M.disciplined(p, 150)


def test_probe_metrics_edges():
    # punishment outside T+17..T+19 does not count; 1.70 itself is not below the trigger
    assert not M.probe_punished(probe_prices({16: 1.47, 20: 1.47}, {16: 1.60}), 150)
    assert not M.probe_punished(probe_prices({17: 1.70}, {16: 1.60}), 150)
    # newcomer stays low: never returns, not disciplined even though punished
    low = {k: 1.60 for k in range(16, 30)}
    p = probe_prices({17: 1.47}, low)
    assert M.probe_punished(p, 150) and M.probe_counter(p, 150) == 3
    assert M.probe_return(p, 150) is None and not M.disciplined(p, 150)
    # returns at high price but nobody punished: not disciplined
    assert not M.disciplined(probe_prices({}, {16: 1.60}), 150)
    # censoring: a 3-round hold starting at T+27 counts, one starting at T+28 cannot exist
    late = probe_prices({17: 1.47}, {**{k: 1.60 for k in range(16, 27)}, 27: 1.92, 28: 1.92, 29: 1.92})
    assert M.probe_return(late, 150) == 27
    later = probe_prices({17: 1.47}, {**{k: 1.60 for k in range(16, 28)}})
    assert M.probe_return(later, 150) is None
    # overpriced return is not a return
    assert M.probe_return(probe_prices({}, {k: 2.10 for k in range(16, 30)}), 150) is None


def branch_prices(seat1, seat0=None, T0=150):
    """60-round branch on a 1.92/1.92 line, shock at T0+30; overrides {k: price}, k relative to T0."""
    p = {T0 + k: [1.92, 1.92] for k in range(1, 61)}
    p[T0 + 30][0] = M.P_NASH
    for k, v in (seat0 or {}).items():
        p[T0 + k][0] = v
    for k, v in seat1.items():
        p[T0 + k][1] = v
    return p


def test_clean_punish_and_return():
    punish3 = {31: 1.47, 32: 1.47, 33: 1.47}
    p = branch_prices(punish3)
    assert M.clean_punish(p, 150) and M.clean_punish_return(p, 150) and M.back_at_cartel(p, 150)
    # punishes but never forgives: clean, no return, not back
    p = branch_prices({k: 1.47 for k in range(31, 61)})
    assert M.clean_punish(p, 150) and not M.clean_punish_return(p, 150) and not M.back_at_cartel(p, 150)
    # late drop (T+33), a 1.60 drop, or a punishment under way at T+25 are not clean
    assert not M.clean_punish(branch_prices({33: 1.47}), 150)
    assert not M.clean_punish(branch_prices({31: 1.60, 32: 1.60}), 150)
    assert not M.clean_punish(branch_prices(punish3, seat0={25: 1.47}), 150)
    assert not M.clean_punish(branch_prices({25: 1.65, **punish3}), 150)
    # not holding the band at T+27..T+29
    assert not M.clean_punish(branch_prices({28: 1.80, **punish3}), 150)
    # 1.55 itself counts; drop at T+32 anchors the 6-round return window T+33..T+38
    assert M.clean_punish(branch_prices({31: 1.55}), 150)
    late = {32: 1.47, **{k: 1.47 for k in range(33, 39)}, 39: 1.92}
    assert M.clean_punish(branch_prices(late), 150) and not M.clean_punish_return(branch_prices(late), 150)


def test_post_shock_ci_and_back_at_cartel_edges():
    p = branch_prices({})
    assert M.post_shock_ci(p, 150) == pytest.approx(float(M.ci(1.92)))
    assert M.post_shock_ci(p, 150, seat=None) == pytest.approx(float(M.ci(1.92)))
    assert not M.back_at_cartel(branch_prices({60: 1.80}), 150)
    assert M.back_at_cartel(branch_prices({k: 2.50 for k in range(51, 61)}), 150)  # no upper bound
    assert M.back_at_cartel(branch_prices({50: 1.47}), 150)  # T+50 is outside the window
