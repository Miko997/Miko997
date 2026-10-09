#!/usr/bin/env python3
"""Link immutable copies of the finished header images from the README.

Run after rendering/compositing, because GitHub's image CDN can ignore query
strings on mutable filenames. Canonical files remain the art build outputs.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('signature-header', 'signature-header-mobile',
         'signature-header-animated', 'signature-header-mobile-animated')

def main():
    aliases = {}
    for stem in NAMES:
        data = (ROOT / 'assets' / (stem + '.webp')).read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        name = f'{stem}--{sha[:12]}.webp'
        target = ROOT / 'assets' / name
        if not target.exists():
            target.write_bytes(data)
        elif target.read_bytes() != data:
            raise RuntimeError('Header asset hash collision')
        aliases[stem] = {'file': name, 'sha256': sha, 'bytes': len(data)}
    path = ROOT / 'README.md'
    pattern = r'assets/(signature-header(?:-mobile)?(?:-animated)?)(?:--[0-9a-f]{12})?\.webp'
    readme = re.sub(pattern, lambda m: 'assets/' + aliases[m[1]]['file'], path.read_text())
    path.write_text(readme)
    (ROOT / 'assets/header-manifest.json').write_text(json.dumps(aliases, indent=2) + '\n')
    print('README linked to four immutable header images.')

if __name__ == '__main__':
    main()
