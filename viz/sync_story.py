#!/usr/bin/env python3
"""Embed story sources and committed evidence; write only viz/index.html."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent
html = (ROOT / 'index.html').read_text()
for name, start, end in [
    ('story.css', '/* STORY_STYLE_START */', '/* STORY_STYLE_END */'),
    ('story.js', '/* STORY_CODE_START */', '/* STORY_CODE_END */'),
]:
    html, count = re.subn(
        re.escape(start) + r'.*?' + re.escape(end),
        lambda _: start + '\n' + (ROOT / name).read_text() + '\n' + end,
        html, flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f'Expected one pair of {name} markers')
results = ROOT.parent / 'seat_swap' / 'results'
report = json.loads((results / 'p1.json').read_text())
keys = ['seed', 'arm', 'joins', 'enforces', 'overpriced', 're_formed', 'disciplined', 'probe_punished']
notes = next(line for line in (results / 'p1.md').read_text().splitlines()
             if line.startswith('- **same_full s200, inherited'))
payload = {
    'csv': (results / 'p1_prices.csv').read_bytes().decode('utf-8'),
    'report': {'T': report['T'], 'manifest': report['manifest'],
               'rows': [{key: row[key] for key in keys} for row in report['rows']]},
    'notes': notes.split('**: ', 1)[1],
}
encoded = json.dumps(payload, ensure_ascii=False).replace('<', r'\u003c')
html, count = re.subn(
    r'(<script id="p1-data" type="application/json">).*?(</script>)',
    lambda match: match[1] + encoded + match[2], html, flags=re.S,
)
if count != 1:
    raise RuntimeError('Expected one p1-data block')
(ROOT / 'index.html').write_text(html)
