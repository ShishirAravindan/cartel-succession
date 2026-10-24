#!/usr/bin/env python3
"""Embed the story's authoring sources so index.html stays self-contained."""
from pathlib import Path
import re
import json
ROOT = Path(__file__).resolve().parent
html = (ROOT/'index.html').read_text()
for name, start, end in [('story.css', '/* STORY_STYLE_START */', '/* STORY_STYLE_END */'),
                         ('story.js', '/* STORY_CODE_START */', '/* STORY_CODE_END */')]:
    pattern = re.escape(start) + r'.*?' + re.escape(end)
    html, n = re.subn(pattern, lambda _: start+'\n'+(ROOT/name).read_text()+'\n'+end, html, flags=re.S)
    if n != 1:
        raise RuntimeError(f'Expected one pair of {name} markers')
report=json.loads((ROOT.parent/'seat_swap/results/p1.json').read_text())
keys=['seed','arm','joins','enforces','overpriced','re_formed','disciplined','probe_punished']
notes=next(line for line in (ROOT.parent/'seat_swap/results/p1.md').read_text().splitlines() if line.startswith('- **same_full s200, inherited'))
payload={'csv':(ROOT.parent/'seat_swap/results/p1_prices.csv').read_text(), 'report':{'T':report['T'],'manifest':report['manifest'],'rows':[{k:r[k] for k in keys} for r in report['rows']]},'notes':notes.split('**: ',1)[1]}
html,n=re.subn(r'(<script id="p1-data" type="application/json">).*?(</script>)',lambda m:m[1]+json.dumps(payload,ensure_ascii=False).replace('</','<\\/')+m[2],html,flags=re.S)
if n!=1: raise RuntimeError('Expected one p1-data block')
(ROOT/'index.html').write_text(html)
