"""P2 / P3 (Kickoff 08, plan §12 at `prereg-p23b`): different-model newcomers branched from P1's base snapshots.

    uv run --project seat_swap python -m seat_swap.p23 sib --dry-run --runs-root /tmp/x    # zero API calls
    uv run --project seat_swap python -m seat_swap.p23 sib                                  # P2: Qwen3-8B
    uv run --project seat_swap python -m seat_swap.p23 oth                                  # P3: gpt-oss-20b

No base: every P1 base seed (200-214, all passed P1's gate) is branched at T = 150 into
`<family>_history` and `<family>_full`, 30 games at once. The P1 base runs are read from the main
checkout by absolute path (P1_RUNS) and never written; new runs go to --runs-root. Writes the
manifest p23_<family>_<stamp>.json in the runs root.
"""

from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock

from seat_swap.branch import RUNS_ROOT, SELLER_MODELS, run_branch
from seat_swap.model_config import MODEL_NAME
from seat_swap.p1 import T, THRESHOLD
from seat_swap.providers import RawCompletions

# P1 base games; the P2/P3 runs were launched from a second worktree whose runs/ held a copy of them
P1_RUNS = RUNS_ROOT
P1_MANIFEST = P1_RUNS / "p1_20261024-192633.json"
# 60 rounds x 2 seats = 119 calls; headroom for up to 3 newcomer retries per round (prereg-p23b)
MAX_CALLS_ARM = 200
FAMILIES = {"sib": ["sib_history", "sib_full"], "oth": ["oth_history", "oth_full"]}


def main(argv=None) -> dict:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("family", choices=list(FAMILIES))
    ap.add_argument("--dry-run", action="store_true", help="scripted sellers, zero API calls")
    ap.add_argument("--runs-root", type=Path, default=RUNS_ROOT)
    args = ap.parse_args(argv)
    p1 = json.loads(P1_MANIFEST.read_text())
    seeds = p1["passing"]
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = args.runs_root / f"p23_{args.family}_{stamp}.json"
    args.runs_root.mkdir(parents=True, exist_ok=True)
    m = {"created": stamp, "family": args.family, "newcomer_model": SELLER_MODELS[args.family], "dry_run": args.dry_run,
         "T": T, "threshold": THRESHOLD, "prereg": "prereg-p23b", "p1_manifest": str(P1_MANIFEST), "seeds": seeds,
         "base": {str(s): p1["base"][str(s)] for s in seeds}, "arm_names": FAMILIES[args.family], "arms": {}}
    lock = Lock()

    def write():
        with lock:
            path.write_text(json.dumps(m, indent=2))

    if not args.dry_run:  # both endpoints up before 30 games start (covers a cold start on either app)
        for model in (MODEL_NAME, SELLER_MODELS[args.family]):
            print(f"{model}: ready after {RawCompletions.from_env(model).wait_ready()}s", flush=True)

    def job(j):
        seed, arm = j
        base_dir = P1_RUNS / p1["base"][str(seed)]["run_id"]
        try:
            d, s = run_branch(base_dir, T, arm, dry_run=args.dry_run, threshold=THRESHOLD,
                              max_calls=None if args.dry_run else MAX_CALLS_ARM, dry_seat0="grim",
                              dry_seat1="copier", runs_root=args.runs_root)
            m["arms"][f"{seed}/{arm}"] = {"dir": str(d), **s}
        except BaseException as e:  # noqa: BLE001  record and keep the other games going
            m["arms"][f"{seed}/{arm}"] = {"status": "error", "error": repr(e)}
        write()

    jobs = [(s, a) for s in seeds for a in FAMILIES[args.family]]
    write()
    with ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        list(ex.map(job, jobs))
    for arm in FAMILIES[args.family]:
        rs = [m["arms"][f"{s}/{arm}"] for s in seeds]
        c = lambda k: sum(bool(r.get(k)) for r in rs)
        print(f"{arm}: completed {sum(r['status'] == 'completed' for r in rs)}/{len(rs)}  joins {c('joins')}  "
              f"enforces {c('enforces')}  overpriced {c('overpriced')}  re_formed {c('re_formed')}")
    print(f"manifest: {path}")
    return m


if __name__ == "__main__":
    main()
