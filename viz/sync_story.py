#!/usr/bin/env python3
"""Embed the story's authoring sources so index.html stays self-contained."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parent
html = (ROOT/'index.html').read_text()
for name, start, end in [('story.css', '/* STORY_STYLE_START */', '/* STORY_STYLE_END */'),
                         ('story.js', '/* STORY_CODE_START */', '/* STORY_CODE_END */')]:
    pattern = re.escape(start) + r'.*?' + re.escape(end)
    html, n = re.subn(pattern, lambda _: start+'\n'+(ROOT/name).read_text()+'\n'+end, html, flags=re.S)
    if n != 1:
        raise RuntimeError(f'Expected one pair of {name} markers')
(ROOT/'index.html').write_text(html)
