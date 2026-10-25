"""List every number in a draft file that does not appear in a reference file (default docs/pi_review.md).

    python3 paper/tools/numcheck.py paper/sections/results.typ [docs/pi_review.md]

A miss is not an error by itself: styling values, section numbers, seeds and numbers sourced from docs/log.md (pilots,
base gate, costs) are expected misses. Read each miss and confirm its source.
"""
import re
import sys

draft = open(sys.argv[1]).read()
ref = open(sys.argv[2] if len(sys.argv) > 2 else "docs/pi_review.md").read()
norm = lambda s: s.replace("−", "-").replace("–", "-")  # noqa: E731
draft, ref = norm(draft), norm(ref)
pat = r"\d+/\d+|[+-]?\d*\.\d+|\d+"
known = set(re.findall(pat, ref))
miss = []
for m in re.finditer(pat, draft):
    t = m.group()
    if t in known or t.lstrip("+") in known or ("+" + t) in known:
        continue
    miss.append((t, draft[max(0, m.start() - 40):m.end() + 20].replace("\n", " ")))
print(len(re.findall(pat, draft)), "numeric tokens;", len(miss), "not found in reference:")
for t, c in miss:
    print(f"  {t!r:10} …{c}…")
