#!/usr/bin/env python3
"""Build self-contained contact plaques; independent of the activity refresh.

Images cannot receive events from another image in a GitHub README. Their
quiet 20-second light cycle is independent; the entire label stays static.
"""
from __future__ import annotations
import hashlib
import json
from html import escape
from pathlib import Path

from brand_icons import brand_icon

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 144, 44
ICON_NAMES = {'archive': 'zenodo'}


def plaque(item: dict, animated: bool) -> str:
    title = escape(item['label'])
    small = len(item['label']) > 12
    pulse = ('<animate attributeName="opacity" values="0;0;.65;.2;.55;.24;.24;0;0" '
             'keyTimes="0;.34;.36;.385;.41;.44;.84;.89;1" dur="20s" repeatCount="indefinite"/>') if animated else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title">
<title id="title">{title}</title>
<defs>
<linearGradient id="metal" x2=".7" y2="1"><stop stop-color="#202537"/><stop offset="1" stop-color="#0d1320"/></linearGradient>
<linearGradient id="light"><stop stop-color="#bda1ff"/><stop offset=".52" stop-color="#8acaff"/><stop offset="1" stop-color="#7b67c9"/></linearGradient>
</defs>
<style>@media(prefers-reduced-motion:reduce){{.energy{{display:none}}}}</style>
<path d="M8 .5H135.5L143.5 8.5V35.5L135.5 43.5H8.5L.5 35.5V8Z" fill="url(#metal)" stroke="#354052"/>
<path d="M8 1H135L143 9M1 35L9 43H135" fill="none" stroke="#90734e" stroke-opacity=".65"/>
<path d="M37 8V35" stroke="#394254" stroke-width=".65"/>
{brand_icon(ICON_NAMES.get(item['icon'], item['icon']), 9, 10, 22, 22)}
<path d="M43 36H123L129 30" fill="none" stroke="#4e5176" stroke-width=".65"/>
<g class="energy" opacity="0"><path d="M43 36H123L129 30" fill="none" stroke="url(#light)" stroke-width="1.5"/><circle cx="132" cy="14" r="1.5" fill="#c0caff"/>{pulse}</g>
<text x="45" y="25" fill="#ececf7" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{'11.5' if small else '13'}" font-weight="500">{title}</text>
</svg>'''


def build():
    items = json.loads((ROOT / 'data/contact-links.json').read_text())
    out = ROOT / 'assets/links'
    out.mkdir(exist_ok=True)
    lines = ['<p>']
    for item in items:
        filenames = {}
        for animated in (True, False):
            svg = plaque(item, animated)
            digest = hashlib.sha256(svg.encode()).hexdigest()[:12]
            variant = '' if animated else '-static'
            name = f"{item['slug']}{variant}--{digest}.svg"
            (out / name).write_text(svg)
            filenames[animated] = './assets/links/' + name
        lines.append(f'<a href="{escape(item["url"], quote=True)}"><picture><source media="(prefers-reduced-motion: reduce)" srcset="{filenames[False]}" /><img src="{filenames[True]}" width="144" height="44" alt="{escape(item["label"], quote=True)}" /></picture></a>')
    lines.append('</p>')
    return '\n'.join(lines)

if __name__ == '__main__':
    from profile_data import replace_section
    readme = ROOT / 'README.md'
    readme.write_text(replace_section(readme.read_text(), 'CONTACTS', build()))
    print('Rebuilt contact plaques and README links.')
