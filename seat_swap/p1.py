"""P1 main run (Kickoff 06, docs/plan.md): planted base, enforcement test, gate, arms, discipline probes.

    uv run --project seat_swap python -m seat_swap.p1 base --dry-run --runs-root /tmp/x     # zero API calls
    uv run --project seat_swap python -m seat_swap.p1 arms --dry-run --runs-root /tmp/x --manifest /tmp/x/p1_<id>.json
    uv run --project seat_swap python -m seat_swap.p1 selftest                               # both stages, dry, asserts
    uv run --project seat_swap python -m seat_swap.p1 base --phase p1b ...                   # Kickoff 07 replication
    uv run --project seat_swap python -m seat_swap.p1 rebranch --phase p1c --manifest runs/p1b_<id>.json  # Kickoff 09

`--phase` picks the seeds, the arms and whether probes run (PHASES): `p1` (Kickoff 06) or `p1b`
(Kickoff 07: seeds 215-229, control / same_history / same_full / same_notes, no probes). Stage arms
reads the phase from the manifest.

Stage `base`: 15 base games (seeds 200-214; two `forgive` incumbents, warm-up 1.92/1.92, 150 rounds,
thinking on) in parallel, then each seed's 10-round enforcement side branch (threshold -0.3). Writes
the manifest p1_<id>.json in the runs root and prints the base table and the gate (>= 8/15 pass).

Stage `arms` (separate, so status.md can be committed after the gate): refuses unless the gate
passed; launches every passing seed x the five P1 arms at once; each arm, on writing its T+15
snapshot, launches its discipline probe straight away. Prints the control kill check.

Stage `rebranch` (Kickoff 09, P1c): no new base. Copies an earlier manifest's base, enforcement and gate
into a new manifest <phase>_<id>.json (the earlier manifest is only read) and runs stage arms on it with
the phase's arms.

After the arms: the control kill check (only if the phase has `control`), and a flag if more than 2 games
in any arm did not reach T+33 (Kickoff 09).

Dry runs: base and enforcement grim/grim; arms and probes grim seat 0 vs copier seat 1 (the
lookalike arm keeps its scripted non-reacting seat 0). The selftest asserts probe_punished is true
in every incumbent arm and false in lookalike.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

from seat_swap import run
from seat_swap.branch import ENFORCE, RUNS_ROOT, run_branch, run_probe

SEEDS = list(range(200, 215))
T = 150
THRESHOLD = -0.3
GATE_MIN = 8
P1_ARMS = ["control", "same_history", "same_none", "same_full", "lookalike"]
P1B_ARMS = ["control", "same_history", "same_full", "same_notes"]
P1C_ARMS = ["notes_rule_return", "notes_rule_noreturn", "notes_status"]
PHASES = {"p1": {"seeds": SEEDS, "arms": P1_ARMS, "probes": True},
          "p1b": {"seeds": list(range(215, 230)), "arms": P1B_ARMS, "probes": False},
          "p1c": {"seeds": list(range(215, 230)), "arms": P1C_ARMS, "probes": False}}
SHORT_MAX = 2  # Kickoff 09: flag an arm with more than 2 games that did not reach T+33
MAX_CALLS = {"base": 340, "enforce": 30, "arm": 135, "probe": 32}  # with headroom for retries


def write(manifest: dict, path: Path, lock: Lock) -> None:
    with lock:
        path.write_text(json.dumps(manifest, indent=2))


def stage_base(runs_root: Path, dry_run: bool, seeds=None, rounds: int = T, gate_min: int = GATE_MIN,
               phase: str = "p1") -> Path:
    seeds = seeds or PHASES[phase]["seeds"]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = runs_root / f"{phase}_{stamp}.json"
    lock = Lock()
    manifest = {"created": stamp, "phase": phase, "dry_run": dry_run, "T": rounds, "threshold": THRESHOLD,
                "seeds": seeds, "gate_min": gate_min, "arm_names": PHASES[phase]["arms"],
                "run_probes": PHASES[phase]["probes"], "base": {}, "enforce": {}, "arms": {}, "probes": {}}
    tag = "dry-grim-grim" if dry_run else "qwen3-14b"

    def base(seed):
        run_id = f"{stamp}_{phase}-base_{tag}_thinkon_s{seed}"
        argv = ["--rounds", str(rounds), "--seed", str(seed), "--instruction", "forgive", "--warmup", "cartel",
                "--thinking", "on", "--phase", f"{phase}-base", "--run-id", run_id, "--runs-root", str(runs_root)]
        argv += ["--dry-run", "--dry-seat0", "grim", "--dry-seat1", "grim"] if dry_run else \
            ["--provider", "modal", "--max-calls", str(MAX_CALLS["base"])]
        try:
            status = run.main(argv)
        except BaseException as e:  # noqa: BLE001
            status = {"status": "error", "error": repr(e)}
        manifest["base"][str(seed)] = {"run_id": run_id, **status}
        write(manifest, path, lock)
        if status["status"] != "completed":
            return
        try:
            d, s = run_branch(runs_root / run_id, rounds, ENFORCE, dry_run=dry_run, threshold=THRESHOLD,
                              max_calls=None if dry_run else MAX_CALLS["enforce"], runs_root=runs_root)
            manifest["enforce"][str(seed)] = {"dir": str(d), **s}
        except BaseException as e:  # noqa: BLE001
            manifest["enforce"][str(seed)] = {"status": "error", "error": repr(e)}
        write(manifest, path, lock)

    with ThreadPoolExecutor(max_workers=len(seeds)) as ex:
        list(ex.map(base, seeds))
    manifest["passing"] = [s for s in seeds if manifest["enforce"].get(str(s), {}).get("is_cartel")]
    manifest["gate_pass"] = len(manifest["passing"]) >= gate_min
    write(manifest, path, lock)
    print_base(manifest)
    print(f"manifest: {path}")
    return path


def print_base(m: dict) -> None:
    print("| seed | base status | cartel_ci 121-150 | overpriced | enforcement_retaliation | pass |")
    print("|---|---|---|---|---|---|")
    for s in m["seeds"]:
        b, e = m["base"].get(str(s), {}), m["enforce"].get(str(s), {})
        f = lambda k: f"{e[k]:+.3f}" if isinstance(e.get(k), float) else "–"
        print(f"| {s} | {b.get('status', '–')} | {f('cartel_ci')} | {e.get('overpriced', '–')} | "
              f"{f('enforcement_retaliation')} | {'yes' if e.get('is_cartel') else 'no'} |")
    print(f"gate: {len(m['passing'])}/{len(m['seeds'])} pass (need {m['gate_min']}) -> "
          f"{'PASS, arms may run' if m['gate_pass'] else 'FAIL, no arms'}")


def stage_arms(manifest_path: Path, runs_root: Path, dry_run: bool) -> dict:
    m = json.loads(manifest_path.read_text())
    if not m.get("gate_pass"):
        raise SystemExit(f"gate failed ({len(m.get('passing', []))}/{len(m['seeds'])}): no arms (plan §2)")
    if m["dry_run"] != dry_run:
        raise SystemExit("manifest and --dry-run disagree")
    lock = Lock()
    T_ = m["T"]
    arms = m.get("arm_names", P1_ARMS)  # P1 manifests predate the field
    run_probes = m.get("run_probes", True)
    probes = ThreadPoolExecutor(max_workers=len(m["passing"]) * len(arms))
    futures = []

    def probe(arm_dir: Path, seed: int, arm: str):
        try:
            d, s = run_probe(arm_dir, dry_run=dry_run, max_calls=None if dry_run else MAX_CALLS["probe"],
                             dry_seat0="grim", dry_seat1="copier", runs_root=runs_root)
            m["probes"][f"{seed}/{arm}"] = {"dir": str(d), **s}
        except BaseException as e:  # noqa: BLE001  record and keep the other games going
            m["probes"][f"{seed}/{arm}"] = {"status": "error", "error": repr(e)}
        write(m, manifest_path, lock)

    def arm_job(job):
        seed, arm = job
        base_dir = runs_root / m["base"][str(seed)]["run_id"]

        def fork(arm_dir):
            with lock:
                m["arms"][f"{seed}/{arm}"] = {"dir": str(arm_dir), "status": "running"}
                futures.append(probes.submit(probe, arm_dir, seed, arm))
            write(m, manifest_path, lock)

        try:
            d, s = run_branch(base_dir, T_, arm, dry_run=dry_run, threshold=THRESHOLD,
                              max_calls=None if dry_run else MAX_CALLS["arm"], dry_seat0="grim", dry_seat1="copier",
                              runs_root=runs_root, on_probe_fork=fork if run_probes else None)
            m["arms"][f"{seed}/{arm}"] = {"dir": str(d), **s}
        except BaseException as e:  # noqa: BLE001
            m["arms"][f"{seed}/{arm}"] = {**m["arms"].get(f"{seed}/{arm}", {}), "status": "error", "error": repr(e)}
        write(m, manifest_path, lock)

    jobs = [(s, a) for s in m["passing"] for a in arms]
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        list(ex.map(arm_job, jobs))
    for f in list(futures):
        f.result()
    probes.shutdown()
    write(m, manifest_path, lock)
    if "control" in arms:
        ctl = [m["arms"].get(f"{s}/control", {}).get("re_formed") for s in m["passing"]]
        m["control_re_formed"] = sum(bool(x) for x in ctl)
        m["kill"] = m["control_re_formed"] * 2 <= len(ctl)  # "most" = more than half
        print(f"control re_formed {m['control_re_formed']}/{len(ctl)} -> "
              f"{'KILL: newcomer arms cannot be read' if m['kill'] else 'ok'}")
    # retaliation needs T+31..T+33, so a game without it did not reach T+33
    m["short_games"] = {a: [s for s in m["passing"] if m["arms"].get(f"{s}/{a}", {}).get("retaliation") is None]
                        for a in arms}
    m["short_flag"] = [a for a, v in m["short_games"].items() if len(v) > SHORT_MAX]
    write(m, manifest_path, lock)
    print(f"games not reaching T+33: {m['short_games']} -> "
          f"{'FLAG: ' + ', '.join(m['short_flag']) if m['short_flag'] else 'ok'}")
    print(f"manifest: {manifest_path}")
    return m


def stage_rebranch(base_manifest: Path, phase: str, runs_root: Path, dry_run: bool) -> dict:
    b = json.loads(base_manifest.read_text())
    if b["dry_run"] != dry_run:
        raise SystemExit("manifest and --dry-run disagree")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = runs_root / f"{phase}_{stamp}.json"
    m = {"created": stamp, "phase": phase, "dry_run": dry_run, "base_manifest": str(base_manifest),
         **{k: b[k] for k in ("T", "threshold", "seeds", "gate_min", "base", "enforce", "passing", "gate_pass")},
         "arm_names": PHASES[phase]["arms"], "run_probes": PHASES[phase]["probes"], "arms": {}, "probes": {}}
    path.write_text(json.dumps(m, indent=2))
    return stage_arms(path, runs_root, dry_run)


def selftest() -> None:
    root = Path(tempfile.mkdtemp(prefix="p1_selftest_"))
    path = stage_base(root, dry_run=True, seeds=PHASES["p1b"]["seeds"][:2], rounds=40, gate_min=2, phase="p1b")
    m = stage_arms(path, root, dry_run=True)
    assert sorted(k.split("/")[1] for k in m["arms"]) == sorted(P1B_ARMS * 2) and not m["probes"]
    assert all(a["status"] == "completed" for a in m["arms"].values())
    print("selftest p1b ok: four arms per seed, no probes")
    before = path.read_text()
    m = stage_rebranch(path, "p1c", root, dry_run=True)
    assert path.read_text() == before and "kill" not in m and not m["short_flag"]
    assert sorted(k.split("/")[1] for k in m["arms"]) == sorted(P1C_ARMS * 2)
    assert all(a["status"] == "completed" for a in m["arms"].values())
    print("selftest p1c ok: three template arms per seed from the p1b bases, p1b manifest untouched")
    path = stage_base(root, dry_run=True, seeds=SEEDS[:2], rounds=40, gate_min=2)
    m = stage_arms(path, root, dry_run=True)
    assert len(m["arms"]) == len(m["probes"]) == 2 * len(P1_ARMS)
    for key, p in m["probes"].items():
        assert p["status"] == "completed", (key, p)
        want = not key.endswith("/lookalike")  # grim seat 0 punishes the forced 1.60; lookalike never reacts
        assert p["probe_punished"] is want, (key, p)
    print("selftest ok: grim seat 0 vs copier seat 1 -> probe_punished true; lookalike seat 0 -> false")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["base", "arms", "rebranch", "selftest"])
    ap.add_argument("--dry-run", action="store_true", help="scripted sellers, zero API calls")
    ap.add_argument("--manifest", type=Path, help="stage arms / rebranch: the manifest written by stage base")
    ap.add_argument("--phase", choices=list(PHASES), default="p1", help="stage base / rebranch: seeds, arms, probes")
    ap.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    args = ap.parse_args(argv)
    if args.stage == "selftest":
        return selftest()
    if args.stage == "base":
        return stage_base(args.runs_root, args.dry_run, phase=args.phase)
    if not args.manifest:
        sys.exit(f"stage {args.stage} needs --manifest")
    if args.stage == "rebranch":
        return stage_rebranch(args.manifest, args.phase, args.runs_root, args.dry_run)
    return stage_arms(args.manifest, args.runs_root, args.dry_run)


if __name__ == "__main__":
    main()
