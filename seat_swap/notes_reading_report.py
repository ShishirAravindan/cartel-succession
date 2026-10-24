"""Aggregate the notes-reading codes (docs/notes_reading/protocol.md) into results/notes_reading/report.md.

    uv run --project seat_swap python -m seat_swap.notes_reading_report

Reads the coders' JSON in results/notes_reading/codes/ and the unblinding key (results/notes_reading/key.json).
Descriptive only: crosstabs of codes against the pre-registered `enforces`, per newcomer model and pooled.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from seat_swap.positive_control import RESULTS

DIR = RESULTS / "notes_reading"
A_CODES = ["A1_rule_form", "A2_trigger", "A3_action_price", "A4_duration", "A5_return", "A6_location", "A7_framing",
           "A8_state"]
B_CODES = ["B1_notices_cut", "B2_reading", "B3_cites_rule", "B4_response", "B5_return_plan", "B6_rule_in_held_notes",
           "B7_rule_in_new_notes", "B8_own_scheme"]
GROUPS = {"Qwen3-14B (same_full + same_notes)": ("Qwen3-14B",), "Qwen3-8B (sib_full)": ("Qwen3-8B",),
          "gpt-oss-20b (oth_full)": ("gpt-oss-20b",), "all": ("Qwen3-14B", "Qwen3-8B", "gpt-oss-20b")}


def load(name: str) -> dict:
    return {x["id"]: x for x in json.loads((DIR / "codes" / name).read_text())}


def agreement(a: dict, b: dict, codes: list[str]) -> list[str]:
    ids = sorted(set(a) & set(b))
    out = [f"Items coded twice: {len(ids)}.", "", "| code | agreement | disagreements (id: first / second) |", "|---|---|---|"]
    for c in codes:
        same = [i for i in ids if a[i].get(c) == b[i].get(c)]
        diff = [f"{i}: {a[i].get(c)} / {b[i].get(c)}" for i in ids if i not in same]
        pct = len(same) / len(ids) if ids else 0
        out.append(f"| {c} | {pct:.0%}{' **(unreliable)**' if pct < 0.7 else ''} | {'; '.join(diff) or '–'} |")
    return out


def crosstab(items: list[dict], code: str) -> list[str]:
    """Rows = code values; columns = enforcers / non-enforcers, per model group."""
    head = "| " + code + " | " + " | ".join(f"{g}: enforcers / non-enforcers" for g in GROUPS) + " |"
    lines = [head, "|---|" + "---|" * len(GROUPS)]
    values = sorted({x.get(code) for x in items}, key=str)
    for v in values:
        cells = []
        for models in GROUPS.values():
            e = [x for x in items if x["model"] in models and x["enforces"]]
            n = [x for x in items if x["model"] in models and not x["enforces"]]
            cells.append(f"{sum(x.get(code) == v for x in e)}/{len(e)} vs {sum(x.get(code) == v for x in n)}/{len(n)}")
        lines.append(f"| {v} | " + " | ".join(cells) + " |")
    return lines


def main() -> dict:
    key = json.loads((DIR / "key.json").read_text())
    a1, a2 = load("A_coder1.json"), load("A_coder2.json")
    b = {}
    for k in range(1, 6):
        b.update(load(f"B_batch{k}.json"))
    rel = load("B_rel.json")
    seed_to_a = {key["A"][i]["seed"]: a1[i] for i in a1}
    items = []
    for gid, k in key["B"].items():
        items.append({"id": gid, **k, **seed_to_a.get(k["seed"], {}), **b.get(gid, {})})
    missing = [g for g in key["B"] if g not in b]

    L = ["# Notes reading: results (exploratory)", "",
         "Protocol: `docs/notes_reading/protocol.md` (fixed before coding). Coders: Sonnet subagents, blind to arm, seed, "
         "model and outcome. `enforces` = the pre-registered metric (retaliation ≤ −0.3). Descriptive only; no tests.", "",
         f"Games: {len(items)} (missing codes: {missing or 'none'}). Inherited notes: {len(a1)}.", "",
         "## Coder agreement", "", "### Pass A (two coders, all 30 notes)", ""]
    L += agreement(a1, a2, A_CODES)
    L += ["", "### Pass B (reliability coder vs batch coder, 10 games)", ""]
    L += agreement(b, rel, B_CODES)

    L += ["", "## Q1. Form of the inherited rule vs enforcement", "",
          "Pass A codes (coder 1) attached to every game whose newcomer inherited that note.", ""]
    for c in ["A1_rule_form", "A3_action_price", "A4_duration", "A5_return", "A7_framing", "A8_state"]:
        L += crosstab(items, c) + [""]
    L += ["Inherited notes alone (30 distinct notes, coder 1):", ""]
    for c in A_CODES:
        L.append(f"- {c}: " + ", ".join(f"{v} {n}" for v, n in Counter(x[c] for x in a1.values()).most_common()))

    L += ["", "## Q2. How the newcomer reads the cut, and whether it cites the rule", ""]
    for c in ["B1_notices_cut", "B2_reading", "B3_cites_rule", "B4_response", "B5_return_plan"]:
        L += crosstab(items, c) + [""]
    L += ["## Q3. Is the rule still in the newcomer's notes at the shock?", ""]
    for c in ["B6_rule_in_held_notes", "B7_rule_in_new_notes"]:
        L += crosstab(items, c) + [""]

    L += ["## Q4. Copying the inherited notes at T+1", "",
          "Copy share = difflib similarity of the newcomer's T+1 notes to the inherited notes (1 = identical).", "",
          "| group | enforcers: mean copy share (n ≥ 0.9) | non-enforcers: mean (n ≥ 0.9) |", "|---|---|---|"]
    for g, models in GROUPS.items():
        e = [x["copy_share_T1"] for x in items if x["model"] in models and x["enforces"]]
        n = [x["copy_share_T1"] for x in items if x["model"] in models and not x["enforces"]]
        f = lambda xs: f"{sum(xs) / len(xs):.2f} ({sum(v >= 0.9 for v in xs)}/{len(xs)})" if xs else "–"
        L.append(f"| {g} | {f(e)} | {f(n)} |")

    L += ["", "## Q5. Own retaliation schemes by model", ""]
    L += crosstab(items, "B8_own_scheme")

    L += ["", "## Check: coded response vs measured enforcement", "",
          "| B4_response | enforces | not enforces |", "|---|---|---|"]
    for v in sorted({x.get("B4_response") for x in items}, key=str):
        L.append(f"| {v} | {sum(x.get('B4_response') == v and x['enforces'] for x in items)} | "
                 f"{sum(x.get('B4_response') == v and not x['enforces'] for x in items)} |")

    L += ["", "## Per game", "",
          "| id | arm | seed | sample | enforces | T+31..33 | copy | A1 | A3 | A4 | A7 | B2 | B3 | B4 | B6 | B8 | conf | quote |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(items, key=lambda x: (x["model"], x["arm"], x["seed"])):
        q = (x.get("B9_quote") or "").replace("|", "/").replace("\n", " ")[:160]
        L.append(f"| {x['id']} | {x['arm']} | {x['seed']} | {x['sample']} | {'yes' if x['enforces'] else 'no'} | "
                 f"{' '.join(f'{p:.2f}' for p in x['price_T31_33'])} | {x['copy_share_T1']:.2f} | {x.get('A1_rule_form')} | "
                 f"{x.get('A3_action_price')} | {x.get('A4_duration')} | {x.get('A7_framing')} | {x.get('B2_reading')} | "
                 f"{x.get('B3_cites_rule')} | {x.get('B4_response')} | {x.get('B6_rule_in_held_notes')} | "
                 f"{x.get('B8_own_scheme')} | {x.get('B10_confidence')} | {q} |")
    (DIR / "report.md").write_text("\n".join(L) + "\n")
    (DIR / "merged.json").write_text(json.dumps(items, indent=2))
    print("\n".join(L))
    return {"items": items}


if __name__ == "__main__":
    main()
