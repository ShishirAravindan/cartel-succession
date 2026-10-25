"""Post-hoc analyses (Kickoff 09 §2), **post hoc, not pre-registered**, over P1, P1b and P2/P3.

    uv run --project seat_swap python -m seat_swap.posthoc

Writes seat_swap/results/posthoc.md and posthoc.json. Every outcome is recomputed from the logged prices
(snapshot_T150 + rounds.jsonl) with `metrics.py`; the pre-registered ones (joins, enforces, re_formed) are checked
against each manifest's summary. Sections:
    1 effective sample size: duplicate newcomer price paths T+1..T+60 per arm, key tests on unique paths only;
      identical base paths
    2 post-shock recovery: newcomer / market CI over T+34..T+60, back_at_cartel, split by re_formed
    3 clean_punish and clean_punish_return next to enforces
    4 P1b paired by seed: McNemar exact (two-sided); P1b-alone Fisher; exact 95% CIs per arm
    5 P3 shock visibility: incumbent below 1.70 at T+29
P2/P3 raw runs live in the `cartel-succession-p23` worktree (gitignored); their manifests give absolute paths.
`load_games` is shared with figures.py and p1c_analysis.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, fisher_exact

from seat_swap import metrics as M
from seat_swap.p1 import THRESHOLD
from seat_swap.p1_report import prices_of
from seat_swap.positive_control import RESULTS
from seat_swap.run_report import read_jsonl

RUNS = Path(__file__).resolve().parent / "runs"
P23_RUNS = Path(__file__).resolve().parents[2] / "cartel-succession-p23" / "seat_swap" / "runs"
MANIFESTS = {
    "P1": RUNS / "p1_20261024-192633.json",
    "P1b": RUNS / "p1b_20261024-234550.json",
    "P2": P23_RUNS / "p23_sib_20261025-002242.json",
    "P3": P23_RUNS / "p23_oth_20261025-002243.json",
}
T = 150
LABEL = "*Post hoc, not pre-registered.*"
OUTCOMES = ["joins", "enforces", "re_formed", "clean_punish", "clean_punish_return", "back_at_cartel"]


def outcome(f, *args, **kw):
    """None when the game stopped before the outcome's window filled."""
    try:
        v = f(*args, **kw)
    except KeyError:
        return None
    return bool(v) if isinstance(v, (bool, np.bool_)) else float(v)


def game_record(family: str, arm: str, seed: int, d: Path, summary: dict) -> dict:
    p = prices_of(d, T, T)
    last = max(p)
    g = {"family": family, "arm": arm, "seed": seed, "dir": str(d), "status": summary.get("status"), "last_round": last - T,
         "joins": outcome(M.joins, p, T), "enforces": outcome(M.enforces, p, T, THRESHOLD),
         "re_formed": outcome(M.re_formed, p, T, THRESHOLD),
         "post_ci_newcomer": outcome(M.post_shock_ci, p, T), "post_ci_market": outcome(M.post_shock_ci, p, T, seat=None),
         "back_at_cartel": outcome(M.back_at_cartel, p, T), "clean_punish": outcome(M.clean_punish, p, T),
         "clean_punish_return": outcome(M.clean_punish_return, p, T),
         "incumbent_T29": p.get(T + 29, [None])[0],
         "path": [p[r][1] for r in range(T + 1, T + 61) if r in p],
         "path_incumbent": [p[r][0] for r in range(T + 1, T + 61) if r in p],
         "ci_newcomer": [float(M.ci(p[r][1])) for r in range(T + 1, T + 61) if r in p]}
    for k in ("joins", "enforces", "re_formed"):  # pre-registered outcomes must match the run's own summary
        if summary.get(k) is not None:
            assert summary[k] == g[k], (family, arm, seed, k, summary[k], g[k])
    return g


def load_games(families=("P1", "P1b", "P2", "P3"), manifests=None) -> list[dict]:
    manifests = {**MANIFESTS, **(manifests or {})}
    games = []
    for fam in families:
        m = json.loads(Path(manifests[fam]).read_text())
        for key, s in sorted(m["arms"].items()):
            seed, arm = key.split("/")
            if not s.get("dir"):
                continue
            games.append(game_record(fam, arm, int(seed), Path(s["dir"]), s))
    return games


def base_paths(families=("P1", "P1b")) -> dict:
    out = {}
    for fam in families:
        m = json.loads(MANIFESTS[fam].read_text())
        for seed, b in m["base"].items():
            rows = read_jsonl(RUNS / b["run_id"] / "rounds.jsonl")
            out[f"{fam}/{seed}"] = tuple(tuple(r["prices"]) for r in rows)
    return out


# ---------- statistics ----------

def rate(k: int, n: int) -> dict:
    if n == 0:
        return {"k": 0, "n": 0, "rate": None, "lo": None, "hi": None}
    ci = binomtest(k, n).proportion_ci(confidence_level=0.95, method="exact")
    return {"k": k, "n": n, "rate": k / n, "lo": ci.low, "hi": ci.high}


def fisher_greater(k1, n1, k2, n2) -> float:
    """One-sided Fisher exact p, group 1 rate > group 2 rate."""
    return float(fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="greater")[1])


def fisher_two(k1, n1, k2, n2) -> float:
    return float(fisher_exact([[k1, n1 - k1], [k2, n2 - k2]])[1])


def mcnemar_exact(a: list[bool], b: list[bool]) -> dict:
    """Two-sided exact McNemar on paired booleans: binomial test on the discordant pairs."""
    only_a = sum(x and not y for x, y in zip(a, b))
    only_b = sum(y and not x for x, y in zip(a, b))
    n = only_a + only_b
    p = 1.0 if n == 0 else float(binomtest(only_a, n, 0.5).pvalue)
    return {"only_first": only_a, "only_second": only_b, "discordant": n, "p_two_sided": p}


def count(games, key) -> tuple[int, int]:
    vals = [g[key] for g in games if g[key] is not None]
    return sum(vals), len(vals)


def select(games, arm=None, family=None):
    fams = None if family is None else ({family} if isinstance(family, str) else set(family))
    return [g for g in games if (arm is None or g["arm"] == arm) and (fams is None or g["family"] in fams)]


def unique_paths(games) -> list[dict]:
    """First game (by family, seed) of each distinct newcomer path T+1..T+60."""
    seen, out = set(), []
    for g in sorted(games, key=lambda g: (g["family"], g["seed"])):
        key = tuple(g["path"])
        if key not in seen:
            seen.add(key)
            out.append(g)
    return out


def duplicates(games) -> dict:
    groups = {}
    for g in games:
        groups.setdefault(tuple(g["path"]), []).append(f"{g['family']}/s{g['seed']}")
    dup = [v for v in groups.values() if len(v) > 1]
    disagree = []
    for v in dup:  # do duplicates agree on the outcomes (the incumbent's path can still differ)?
        gs = [g for g in games if f"{g['family']}/s{g['seed']}" in v]
        for k in OUTCOMES:
            if len({g[k] for g in gs}) > 1:
                disagree.append({"group": v, "outcome": k})
    return {"n": len(games), "unique": len(groups), "in_duplicate_groups": sum(len(v) for v in dup),
            "groups": dup, "outcome_disagreements": disagree}


# ---------- analyses ----------

ARM_ORDER = ["control", "lookalike", "same_none", "same_history", "same_full", "same_notes",
             "sib_history", "sib_full", "oth_history", "oth_full",
             "notes_rule_return", "notes_rule_noreturn", "notes_status"]
SAMPLES = [("P1", "P1"), ("P1b", "P1b"), ("P1+P1b", ("P1", "P1b")), ("P2", "P2"), ("P3", "P3")]


def arm_samples(games):
    """(sample label, arm, games) for every arm present in each sample; pooled rows only for arms in both P1 and P1b."""
    out = []
    for label, fam in SAMPLES:
        for arm in ARM_ORDER:
            gs = select(games, arm, fam)
            if not gs:
                continue
            if label == "P1+P1b" and len({g["family"] for g in gs}) < 2:
                continue
            out.append((label, arm, gs))
    return out


def effective_sample(games) -> dict:
    per_arm = {f"{lbl}/{arm}": duplicates(gs) for lbl, arm, gs in arm_samples(games)}
    tests = {}

    def test(name, a_games, b_games, key, a_label, b_label):
        row = {}
        for which, (ga, gb) in {"all": (a_games, b_games), "unique": (unique_paths(a_games), unique_paths(b_games))}.items():
            ka, na = count(ga, key)
            kb, nb = count(gb, key)
            row[which] = {a_label: [ka, na], b_label: [kb, nb], "p_one_sided": fisher_greater(ka, na, kb, nb)}
        tests[name] = row

    pooled = ("P1", "P1b")
    test("pooled same_full > same_history, re_formed", select(games, "same_full", pooled),
         select(games, "same_history", pooled), "re_formed", "same_full", "same_history")
    test("P1b same_notes > same_history, re_formed", select(games, "same_notes", "P1b"),
         select(games, "same_history", "P1b"), "re_formed", "same_notes", "same_history")
    test("P1 same_history > same_none, joins", select(games, "same_history", "P1"),
         select(games, "same_none", "P1"), "joins", "same_history", "same_none")
    bp = base_paths()
    groups = {}
    for k, v in bp.items():
        groups.setdefault(v, []).append(k)
    all_cartel = sum(all(p == (1.92, 1.92) for p in v[1:]) for v in bp.values())
    base = {"n": len(bp), "unique": len(groups), "largest_group": max(len(v) for v in groups.values()),
            "groups": [v for v in groups.values() if len(v) > 1],
            "all_1.92_from_round_1": all_cartel}
    return {"per_arm": per_arm, "tests": tests, "base": base}


def recovery(games) -> list[dict]:
    rows = []
    for lbl, arm, gs in arm_samples(games):
        for split in (True, False, None):
            sub = [g for g in gs if split is None or g["re_formed"] is split]
            sub = [g for g in sub if g["post_ci_newcomer"] is not None]
            if not sub:
                continue
            k, n = count(sub, "back_at_cartel")
            rows.append({"sample": lbl, "arm": arm, "re_formed": {True: "yes", False: "no", None: "all"}[split], "n": n,
                         "post_ci_newcomer": float(np.mean([g["post_ci_newcomer"] for g in sub])),
                         "post_ci_market": float(np.mean([g["post_ci_market"] for g in sub])),
                         "back_at_cartel": k})
    return rows


def punish_table(games) -> list[dict]:
    rows = []
    for lbl, arm, gs in arm_samples(games):
        r = {"sample": lbl, "arm": arm}
        for k in ("enforces", "clean_punish", "clean_punish_return", "re_formed", "joins", "back_at_cartel"):
            r[k] = rate(*count(gs, k))
        rows.append(r)
    return rows


def paired_p1b(games) -> dict:
    by = {a: {g["seed"]: g for g in select(games, a, "P1b")} for a in ("same_history", "same_full", "same_notes", "control")}
    seeds = sorted(set.intersection(*(set(v) for v in by.values())))
    out = {"seeds": seeds, "mcnemar": {}, "fisher_p1b": {}, "rates": {}}
    for arm in ("same_notes", "same_full"):
        for key in ("re_formed", "clean_punish"):
            pairs = [(by[arm][s][key], by["same_history"][s][key]) for s in seeds
                     if by[arm][s][key] is not None and by["same_history"][s][key] is not None]
            out["mcnemar"][f"{arm} vs same_history, {key}"] = {**mcnemar_exact(*zip(*pairs)), "pairs": len(pairs)}
            ka, na = count(list(by[arm].values()), key)
            kb, nb = count(list(by["same_history"].values()), key)
            out["fisher_p1b"][f"{arm} vs same_history, {key}"] = {
                arm: [ka, na], "same_history": [kb, nb],
                "p_one_sided": fisher_greater(ka, na, kb, nb), "p_two_sided": fisher_two(ka, na, kb, nb)}
    for arm, gs in by.items():
        out["rates"][arm] = {k: rate(*count(list(gs.values()), k)) for k in OUTCOMES}
    return out


def shock_visibility(games) -> dict:
    out = {}
    for fam in ("P2", "P3"):
        gs = select(games, family=fam)
        invisible = [g for g in gs if g["incumbent_T29"] is not None and g["incumbent_T29"] < M.PUNISH_BELOW - 1e-9]
        out[fam] = {"invisible": [f"{g['arm']}/s{g['seed']}" for g in invisible], "arms": {}}
        for arm in sorted({g["arm"] for g in gs}):
            a = select(gs, arm)
            vis = [g for g in a if g not in invisible]
            out[fam]["arms"][arm] = {k: {"all": list(count(a, k)), "visible_only": list(count(vis, k))} for k in OUTCOMES}
    return out


# ---------- report ----------

def frac(k, n):
    return f"{k}/{n}"


def fr(r):
    return f"{r['k']}/{r['n']}" if r["n"] else "–"


def ci_txt(r):
    return f"{r['k']}/{r['n']} [{r['lo']:.2f}, {r['hi']:.2f}]" if r["n"] else "–"


def p_txt(p):
    return f"{p:.4f}" if p >= 0.0001 else f"{p:.1e}"


def render(es, rec, pun, paired, vis) -> str:
    L = ["# Post-hoc analyses (Kickoff 09 §2)", "",
         "**Post hoc, not pre-registered.** Generated by `seat_swap.posthoc` from the run logs (P1, P1b, P2 = Qwen3-8B "
         "newcomer, P3 = gpt-oss-20b newcomer). Outcomes are recomputed from prices with `metrics.py`; `joins`, "
         "`enforces` and `re_formed` match each run's own summary. Rounds are relative to T = 150; shock at T+30. "
         "Games that stopped before an outcome's window are left out of its denominator (P2 `sib_full` s212, aborted at T+17).",
         "", "Definitions (`metrics.py`): `back_at_cartel` = newcomer CI ≥ 0.9 in each of T+51..T+60 (no upper bound). "
         "`clean_punish` = newcomer CI ≥ 0.9 in each of T+27..T+29, both seats ≥ 1.70 in each of T+25..T+29, and newcomer "
         "≤ 1.55 at T+31 or T+32. `clean_punish_return` = `clean_punish`, then newcomer CI ≥ 0.9 in at least one of the 6 "
         "rounds after the first round at ≤ 1.55 (the kickoff's `clean_punish_and_return`). Post-shock CI = mean over "
         "T+34..T+60.", ""]

    L += ["## 1. Effective sample size", "", LABEL, "",
          "Seeds whose newcomer price path T+1..T+60 is identical to another seed's in the same arm.", "",
          "| sample / arm | games | unique paths | games in duplicate groups | duplicate groups |", "|---|---|---|---|---|"]
    for k, v in es["per_arm"].items():
        groups = "; ".join("=".join(s.split("/")[1] for s in g) if len({s.split('/')[0] for s in g}) == 1 else "=".join(g)
                           for g in v["groups"]) or "–"
        L.append(f"| {k} | {v['n']} | {v['unique']} | {v['in_duplicate_groups']} | {groups} |")
    dis = [(k, d) for k, v in es["per_arm"].items() for d in v["outcome_disagreements"]]
    L += ["", f"Duplicate groups whose outcomes differ (same newcomer path, different incumbent path): {len(dis)}."
          + ("" if not dis else " " + "; ".join(f"{k} {d['outcome']} {'='.join(d['group'])}" for k, d in dis)), "",
          "Key tests on all games vs on unique paths only (one-sided Fisher exact, first arm higher):", "",
          "| test | all games | p | unique paths only | p |", "|---|---|---|---|---|"]
    for name, row in es["tests"].items():
        cells = []
        for w in ("all", "unique"):
            a, b = [k for k in row[w] if k != "p_one_sided"]
            cells += [f"{a} {frac(*row[w][a])} vs {b} {frac(*row[w][b])}", p_txt(row[w]["p_one_sided"])]
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    b = es["base"]
    L += ["", f"Base games (P1 + P1b, rounds 1..150): {b['n']} seeds, {b['unique']} distinct price paths "
          f"(largest identical group {b['largest_group']}); {b['all_1.92_from_round_1']} of {b['n']} are 1.92/1.92 in every "
          "round after the warm-up. The bases differ only in the notes, not in prices: effectively one cartel state.", ""]
    L += [f"One line: deduplicating identical paths leaves the pooled `same_full` vs `same_history` test at p = "
          f"{p_txt(es['tests']['pooled same_full > same_history, re_formed']['unique']['p_one_sided'])}.", ""]

    L += ["## 2. Post-shock recovery", "", LABEL, "",
          "| sample | arm | re_formed | n | newcomer CI T+34..T+60 | market CI T+34..T+60 | back_at_cartel |",
          "|---|---|---|---|---|---|---|"]
    for r in rec:
        L.append(f"| {r['sample']} | {r['arm']} | {r['re_formed']} | {r['n']} | {r['post_ci_newcomer']:+.2f} | "
                 f"{r['post_ci_market']:+.2f} | {r['back_at_cartel']}/{r['n']} |")
    pool = {(r["arm"], r["re_formed"]): r for r in rec if r["sample"] == "P1+P1b"}
    yes, no = pool.get(("same_full", "yes")), pool.get(("same_full", "no"))
    if yes and no:
        L += ["", f"One line: pooled `same_full` newcomers that re-formed average CI {yes['post_ci_newcomer']:+.2f} after "
              f"the shock ({yes['back_at_cartel']}/{yes['n']} back at the cartel), vs {no['post_ci_newcomer']:+.2f} "
              f"({no['back_at_cartel']}/{no['n']}) for those that did not.", ""]

    L += ["## 3. Clean punishment", "", LABEL, "",
          "| sample | arm | enforces | clean_punish | clean_punish_return | re_formed |", "|---|---|---|---|---|---|"]
    for r in pun:
        L.append(f"| {r['sample']} | {r['arm']} | {fr(r['enforces'])} | {fr(r['clean_punish'])} | "
                 f"{fr(r['clean_punish_return'])} | {fr(r['re_formed'])} |")
    pe = {(r["sample"], r["arm"]): r for r in pun}
    sf = pe.get(("P1+P1b", "same_full"))
    if sf:
        L += ["", f"One line: pooled `same_full` has {fr(sf['enforces'])} `enforces` and {fr(sf['clean_punish'])} "
              f"`clean_punish`, of which {sf['clean_punish_return']['k']} return to CI ≥ 0.9 within 6 rounds.", ""]

    L += ["## 4. P1b paired by seed", "", LABEL, "",
          f"Seeds {paired['seeds'][0]}–{paired['seeds'][-1]} ({len(paired['seeds'])}), each with `same_history`, "
          "`same_full` and `same_notes` on the same base.", "",
          "| comparison | only first arm | only same_history | McNemar exact p (two-sided) | P1b Fisher one-sided p | two-sided p |",
          "|---|---|---|---|---|---|"]
    for k, v in paired["mcnemar"].items():
        f = paired["fisher_p1b"][k]
        L.append(f"| {k} | {v['only_first']} | {v['only_second']} | {p_txt(v['p_two_sided'])} | "
                 f"{p_txt(f['p_one_sided'])} | {p_txt(f['p_two_sided'])} |")
    L += ["", "Rates with exact (Clopper–Pearson) 95% CIs, P1b alone:", "",
          "| arm | " + " | ".join(OUTCOMES) + " |", "|---|" + "---|" * len(OUTCOMES)]
    for arm, rs in paired["rates"].items():
        L.append(f"| {arm} | " + " | ".join(ci_txt(rs[k]) for k in OUTCOMES) + " |")
    m = paired["mcnemar"]["same_notes vs same_history, re_formed"]
    L += ["", f"One line: on `re_formed`, `same_notes` and `same_history` disagree in {m['discordant']} of "
          f"{m['pairs']} seeds: {m['only_first']} favour `same_notes`, {m['only_second']} `same_history` "
          f"(p = {p_txt(m['p_two_sided'])}).", ""]

    L += ["## 5. P3 shock visibility", "", LABEL, "",
          "Shock invisible = the incumbent was already below 1.70 at T+29 (punishing), so its forced 1.47 at T+30 changed little.", ""]
    for fam, v in vis.items():
        L.append(f"- {fam}: {len(v['invisible'])} games invisible: {', '.join(v['invisible']) or 'none'}.")
    L += ["", "| family | arm | outcome | all games | shock visible only |", "|---|---|---|---|---|"]
    for fam, v in vis.items():
        for arm, ks in v["arms"].items():
            for k in OUTCOMES:
                L.append(f"| {fam} | {arm} | {k} | {frac(*ks[k]['all'])} | {frac(*ks[k]['visible_only'])} |")
    p3 = vis["P3"]["arms"]
    L += ["", f"One line: with the invisible-shock games removed, P3 `oth_full` `re_formed` is "
          f"{frac(*p3['oth_full']['re_formed']['visible_only'])} and `oth_history` "
          f"{frac(*p3['oth_history']['re_formed']['visible_only'])}.", ""]
    return "\n".join(L)


def main():
    games = load_games()
    es, rec, pun = effective_sample(games), recovery(games), punish_table(games)
    paired, vis = paired_p1b(games), shock_visibility(games)
    slim = [{k: v for k, v in g.items() if k not in ("path", "path_incumbent", "ci_newcomer", "dir")} for g in games]
    out = {"label": "post hoc, not pre-registered", "games": slim, "effective_sample": es, "recovery": rec,
           "punish": pun, "paired_p1b": paired, "shock_visibility": vis}
    (RESULTS / "posthoc.json").write_text(json.dumps(out, indent=1))
    (RESULTS / "posthoc.md").write_text(render(es, rec, pun, paired, vis))
    print(f"wrote {RESULTS / 'posthoc.md'} ({len(games)} games)")


if __name__ == "__main__":
    main()
