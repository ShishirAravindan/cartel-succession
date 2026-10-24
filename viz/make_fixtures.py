#!/usr/bin/env python3
"""Offline numerical fixtures only: no providers, experiment runner, or network."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import types

ROOT = Path(__file__).resolve().parents[1]
T = 150


def source(ref, path):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{ref}:{path}'], text=True)


def module(name, text):
    result = types.ModuleType(name)
    sys.modules[name] = result
    exec(compile(text, f'<git:{name}>', 'exec'), result.__dict__)
    return result


class Forgiving:
    """Literal numeric instruction, with cuts during/just after punishment ignored."""
    def __init__(self):
        self.remaining = 0
        self.cooldown = 0

    def __call__(self, seat, rnd, history):
        if self.remaining:
            self.remaining -= 1
            if not self.remaining:
                self.cooldown = 2  # return decision, then observation of that return round
            return 1.47
        if self.cooldown:
            self.cooldown -= 1
            return 1.92
        if (len(history) >= 2 and history[-1]['prices'][1-seat] < 1.70
                and min(history[-2]['prices']) >= 1.90):
            self.remaining = 2
            return 1.47
        return 1.92


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-ref', default='prereg-p1',
                        help='Repo revision containing the frozen probe metrics (default: prereg-p1).')
    args = parser.parse_args()
    revision = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', args.reference_ref], text=True).strip()
    # Read the repository's own frozen Python without checking out or editing that branch.
    texts = {p: source(revision, p) for p in (
        'seat_swap/metrics.py', 'seat_swap/scripted.py', 'llm-cartel/environment/oligopoly.py')}
    package = types.ModuleType('seat_swap')
    package.__path__ = []
    sys.modules['seat_swap'] = package
    m = module('seat_swap.metrics', texts['seat_swap/metrics.py'])
    s = module('seat_swap.scripted', texts['seat_swap/scripted.py'])
    env_module = module('viz_reference_environment', texts['llm-cartel/environment/oligopoly.py'])
    env = env_module.OligopolyGame(a0=0, ais=[2, 2], costs=[1, 1], mu=.25, beta=100., verbose=False)
    pairs = [(1.473, 1.473), (1.925, 1.925), (1.92, 1.92), (1.47, 1.92), (1.92, 1.47),
             (1.60, 1.92), (1.92, 1.60), (1., 1.), (1., 2.5), (2.5, 1.), (2., 2.5),
             (2.5, 2.), (1.70, 1.90), (1.90, 1.70), (1.699, 1.90), (1.90, 1.699),
             (1.473, 2.5), (2.5, 1.473), (1.80, 1.89), (2.89, 2.89)]
    market = []
    for prices in pairs:
        _, q, profit, _, _ = env.step(list(prices))
        assert all(abs(profit[i] - m.profit(prices[i], prices[1-i])) < 1e-10 for i in range(2))
        market.append(dict(prices=prices, quantities=q, profits=profit))

    def newcomer(name):
        if name == 'copier':
            return s.copier()
        if name == 'enforcer':
            return Forgiving()
        if name == 'anchored':
            return s.fixed_price(2.20)
        if name == 'follower':
            return s.fixed_price(1.92)
        return lambda seat, rnd, h: max(1., h[-1]['prices'][1-seat] - .03)

    def metrics(h, probe=False):
        p = m.prices_by_round(h)
        if probe:
            return dict(probe_punished=m.probe_punished(p, T), probe_counter=m.probe_counter(p, T),
                        probe_return=m.probe_return(p, T), probe_ci_post=m.probe_ci_post(p, T),
                        disciplined=m.disciplined(p, T))
        return dict(ci_early=m.ci_early(p, T), ci_late=m.ci_late(p, T), newcomer_ci=m.newcomer_ci(p, T),
                    br_gap=m.br_gap(p, T+20, T+29), retaliation=m.retaliation(p, T),
                    joins=m.joins(p, T), enforces=m.enforces(p, T, -.3),
                    overpriced=m.newcomer_overpriced(p, T), re_formed=m.re_formed(p, T, -.3),
                    established=m.established(p, T+30), first_hold=m.first_hold(p, T+1, T+60),
                    punishment_pre=m.punishment_starts(p, T+1, T+29, forced=[T+30]),
                    punishment_post=m.punishment_starts(p, T+31, T+60, forced=[T+30]))

    games = []
    for name in ['copier', 'enforcer', 'anchored', 'follower', 'undercutter']:
        arm = 'lookalike' if name == 'anchored' else 'same_history'
        inc = s.lookalike() if arm == 'lookalike' else Forgiving()
        new = newcomer(name)
        h = [dict(round=r, prices=[1.92, 1.92], forced={}) for r in range(T-29, T+1)]
        fork = None
        for r in range(T+1, T+61):
            forced = {'0': m.P_NASH} if r == T+30 else {}
            p0 = forced['0'] if forced else inc(0, r, h)
            p1 = new(1, r, h)
            h.append(dict(round=r, prices=[p0, p1], forced=forced))
            if r == T+15:
                fork = (copy.deepcopy(h), copy.deepcopy(inc), copy.deepcopy(new))
        ph, pi, pn = fork
        for r in range(T+16, T+30):
            forced = {'1': 1.60} if r == T+16 else {}
            p0 = pi(0, r, ph)
            p1 = 1.60 if forced else pn(1, r, ph)
            ph.append(dict(round=r, prices=[p0, p1], forced=forced))
        games.append(dict(preset=name, arm=arm, main=h, probe=ph,
                          metrics=metrics(h), probe_metrics=metrics(ph, True)))
    fixture = dict(schema_version=1, reference_revision=revision,
                   sources={p: hashlib.sha256(t.encode()).hexdigest() for p, t in texts.items()},
                   tolerance=1e-6, market=market, games=games)
    output = ROOT/'viz'/'fixtures.json'
    serialized = json.dumps(fixture, indent=2, allow_nan=False)
    output.write_text(serialized + '\n')
    # A generated byte-equivalent JSON copy lets index.html work directly over file://.
    html = ROOT/'viz'/'index.html'
    if html.exists():
        content, count = re.subn(r'(<script id="fixture-data" type="application/json">).*?(</script>)',
                                lambda match: match[1] + '\n' + serialized + '\n' + match[2],
                                html.read_text(), flags=re.S)
        if count != 1:
            raise RuntimeError('index.html must have exactly one fixture-data script')
        html.write_text(content)
    print(f'Wrote 20 market pairs and 5 scripted games from {revision}; synced embedded JSON.')


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
