"""Blinded packets for the notes-reading analysis (docs/notes_reading/protocol.md).

    uv run --project seat_swap python -m seat_swap.notes_packets

Writes seat_swap/results/notes_reading/: packets_A.md (the 30 distinct inherited notes), packets_B_<k>.md
(74 games in 5 batches), packets_B_rel.md (10 games coded twice) and key.json (ID -> arm, seed, model and
the computed fields). Coders get only packet files; key.json stays with the analysis.
"""

from __future__ import annotations

import difflib
import json
import random
import tempfile
from pathlib import Path

from seat_swap import metrics as M
from seat_swap.p1_report import prices_of
from seat_swap.run_report import read_jsonl

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "seat_swap" / "results"
P23_RESULTS = RESULTS / "p23.json"
OUT = RESULTS / "notes_reading"
T = 150
ARMS = {"same_full", "same_notes", "sib_full", "oth_full"}
HISTORY_ARMS = {"same_history", "sib_history", "oth_history"}  # amendment 2: the comparison group (pass C)
MODEL = {"same_full": "Qwen3-14B", "same_notes": "Qwen3-14B", "sib_full": "Qwen3-8B", "oth_full": "gpt-oss-20b",
         "same_history": "Qwen3-14B", "sib_history": "Qwen3-8B", "oth_history": "gpt-oss-20b"}
SEED = 20261025
N_BATCHES, N_REL = 5, 10
MAX_REASONING = 12000


def notes_text(n: dict | None) -> str:
    if not n:
        return "(none)"
    return f"PLANS:\n{n.get('plans', '').strip()}\n\nINSIGHTS:\n{n.get('insights', '').strip()}"


def call_at(d: Path, rnd: int, seat: int = 1) -> dict | None:
    """The accepted call of a seat in a round (last attempt that parsed)."""
    ok = [c for c in read_jsonl(d / "calls.jsonl") if c["round"] == rnd and c["seat"] == seat and c["parse_ok"]]
    return ok[-1] if ok else None


def games(arms=ARMS) -> list[dict]:
    rows = []
    for sample, path in (("P1", RESULTS / "p1.json"), ("P1b", RESULTS / "p1b.json"), ("P23", P23_RESULTS)):
        for r in json.loads(path.read_text())["rows"]:
            if r["arm"] in arms and r.get("arm_dir") and r.get("re_formed") is not None:
                d = Path(r["arm_dir"])
                rows.append({"sample": sample, "arm": r["arm"], "seed": r["seed"], "model": MODEL[r["arm"]],
                             "dir": d if d.is_absolute() else ROOT / d, "enforces": r["enforces"],
                             "re_formed": r["re_formed"], "retaliation": r["retaliation"]})
    return rows


def main(argv=None) -> None:
    import sys
    if (argv if argv is not None else sys.argv[1:]) == ["history"]:
        return history_packets()
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    gs = games()
    key = {"A": {}, "B": {}}

    # pass A: the distinct inherited notes (seat 1 at T depends only on the base seed)
    inherited = {}
    for g in gs:
        snap = json.loads((g["dir"] / f"snapshot_T{T}.json").read_text())
        g["inherited"] = snap["notes"][1]
        inherited.setdefault(g["seed"], snap["notes"][1])
    seeds = sorted(inherited)
    rng.shuffle(seeds)
    a_ids = {s: f"N{i + 1:02d}" for i, s in enumerate(seeds)}
    lines = ["# Pass A packets: inherited notes", ""]
    for s in seeds:
        key["A"][a_ids[s]] = {"seed": s}
        lines += [f"## {a_ids[s]}", "", "```", notes_text(inherited[s]), "```", ""]
    (OUT / "packets_A.md").write_text("\n".join(lines))

    # pass B: one packet per game
    rng.shuffle(gs)
    blocks = {}
    for i, g in enumerate(gs):
        gid = f"G{i + 1:03d}"
        d = g["dir"]
        p = prices_of(d, T, T)
        held, dec, nxt, first = call_at(d, T + 30), call_at(d, T + 31), call_at(d, T + 32), call_at(d, T + 1)
        reasoning = (dec or {}).get("reasoning_text") or "(none)"
        if len(reasoning) > MAX_REASONING:
            reasoning = reasoning[:MAX_REASONING] + " …[truncated]"
        inh = notes_text(g["inherited"])
        t1 = notes_text((first or {}).get("notes_text"))
        key["B"][gid] = {k: g[k] for k in ("sample", "arm", "seed", "model", "enforces", "re_formed", "retaliation")} | {
            "price_T31_33": [p[T + k][1] for k in (31, 32, 33)],
            "copy_share_T1": round(difflib.SequenceMatcher(None, inh, t1).ratio(), 3),
            "inherited_chars": len(inh), "reasoning_chars": len(reasoning)}
        table = "\n".join(f"T+{k}: newcomer {p[T + k][1]:.2f}, competitor {p[T + k][0]:.2f}"
                          + ("  (competitor forced to 1.47 this round)" if k == 30 else "") for k in range(25, 35))
        blocks[gid] = "\n".join([
            f"## {gid}", "",
            "### Inherited notes at T (what the newcomer received)", "```", inh, "```", "",
            "### Notes the newcomer held going into T+31 (written by it at T+30)", "```",
            notes_text((held or {}).get("notes_text")), "```", "",
            "### Prices", "```", table, "```", "",
            f"### Newcomer reasoning at T+31 (chosen price {(dec or {}).get('parsed_price')})", "```", reasoning, "```", "",
            "### Notes the newcomer wrote at T+31", "```", notes_text((dec or {}).get("notes_text")), "```", "",
            "### Notes the newcomer wrote at T+32", "```", notes_text((nxt or {}).get("notes_text")), "```", ""])
    ids = list(blocks)
    for k in range(N_BATCHES):
        part = ids[k::N_BATCHES]
        (OUT / f"packets_B_{k + 1}.md").write_text(f"# Pass B packets, batch {k + 1}\n\n" + "\n".join(blocks[i] for i in part))
    rel = sorted(rng.sample(ids, N_REL))
    (OUT / "packets_B_rel.md").write_text("# Pass B packets, reliability set\n\n" + "\n".join(blocks[i] for i in rel))
    key["B_rel"] = rel
    (OUT / "key.json").write_text(json.dumps(key, indent=2))
    print(f"pass A: {len(seeds)} notes; pass B: {len(ids)} games in {N_BATCHES} batches; reliability {rel}")



def history_packets(n_batches: int = 4) -> None:
    """Pass C (amendment 2): the history-only newcomers at T+31, same packet layout minus inherited notes."""
    rng = random.Random(SEED + 1)
    gs = games(HISTORY_ARMS)
    rng.shuffle(gs)
    key, blocks = {}, {}
    for i, g in enumerate(gs):
        gid = f"H{i + 1:03d}"
        d = g["dir"]
        p = prices_of(d, T, T)
        held, dec, nxt = call_at(d, T + 30), call_at(d, T + 31), call_at(d, T + 32)
        reasoning = (dec or {}).get("reasoning_text") or "(none)"
        if len(reasoning) > MAX_REASONING:
            reasoning = reasoning[:MAX_REASONING] + " …[truncated]"
        key[gid] = {k: g[k] for k in ("sample", "arm", "seed", "model", "enforces", "re_formed", "retaliation")} | {
            "price_T31_33": [p[T + k][1] for k in (31, 32, 33)]}
        table = "\n".join(f"T+{k}: newcomer {p[T + k][1]:.2f}, competitor {p[T + k][0]:.2f}"
                          + ("  (competitor forced to 1.47 this round)" if k == 30 else "") for k in range(25, 35))
        blocks[gid] = "\n".join([
            f"## {gid}", "", "(This newcomer inherited the price history but no notes.)", "",
            "### Notes the newcomer held going into T+31 (written by it at T+30)", "```",
            notes_text((held or {}).get("notes_text")), "```", "",
            "### Prices", "```", table, "```", "",
            f"### Newcomer reasoning at T+31 (chosen price {(dec or {}).get('parsed_price')})", "```", reasoning, "```", "",
            "### Notes the newcomer wrote at T+31", "```", notes_text((dec or {}).get("notes_text")), "```", "",
            "### Notes the newcomer wrote at T+32", "```", notes_text((nxt or {}).get("notes_text")), "```", ""])
    ids = list(blocks)
    for k in range(n_batches):
        (OUT / f"packets_C_{k + 1}.md").write_text(f"# Pass C packets, batch {k + 1}\n\n" +
                                                   "\n".join(blocks[i] for i in ids[k::n_batches]))
    rel = sorted(rng.sample(ids, N_REL))
    (OUT / "packets_C_rel.md").write_text("# Pass C packets, reliability set\n\n" + "\n".join(blocks[i] for i in rel))
    (Path(tempfile.gettempdir()) / "notes_key_C.json").write_text(
        json.dumps({"C": key, "C_rel": rel}, indent=2))  # unblinding key kept out of the repo until coding is done
    print(f"pass C: {len(ids)} games in {n_batches} batches; reliability {rel}")


if __name__ == "__main__":
    main()
