#!/usr/bin/env python3
"""Refresh the profile from GitHub. Requires only Python's standard library."""
from __future__ import annotations

import hashlib
import json
import re
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from profile_data import Client, DataError, collect, impact_markdown, replace_section
from render_profile import dashboard, footer, header, impact

ROOT = Path(__file__).resolve().parents[1]


def write_changed(path: Path, text: str):
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(text)
        name = tmp.name
    os.replace(name, path)


def main():
    today = datetime.now(timezone.utc).date()
    snapshot = collect(Client(os.environ.get("GITHUB_TOKEN", "")), "Miko997", today)
    readme = ROOT.joinpath("README.md").read_text(encoding="utf-8")
    readme = replace_section(readme, "IMPACT", impact_markdown(snapshot))
    fingerprint = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()[:12]
    readme = re.sub(r"(assets/generated/(?:contribution-core(?:-static)?|open-source-impact)\.svg)(?:\?v=[0-9a-f]+)?",
                    lambda m: m[1] + "?v=" + fingerprint, readme)
    # Collect and render everything before writing: partial/API failures retain good data.
    outputs = {
        "data/public-activity.json": json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        "assets/generated/contribution-core.svg": dashboard(snapshot),
        "assets/generated/contribution-core-static.svg": dashboard(snapshot, animated=False),
        "assets/generated/open-source-impact.svg": impact(snapshot),
        "assets/hextech-header.svg": header(),
        "assets/hextech-footer.svg": footer(),
        "README.md": readme,
    }
    for name, content in outputs.items():
        write_changed(ROOT / name, content)
    stats = snapshot["stats"]
    print(f"Verified {snapshot['login']}: {stats['last_365']} contributions / 365d; "
          f"{stats['all_time']} all-time; streak {stats['streak']['current']} / best {stats['streak']['longest']}; "
          f"{len(snapshot['upstream']['merged'])} merged upstream PRs.")
    print("Only published aggregate calendar data and explicitly public PR metadata were retained.")


if __name__ == "__main__":
    try:
        main()
    except (DataError, KeyError, TypeError, ValueError) as exc:
        print(f"Profile refresh failed: {exc}", file=sys.stderr)
        sys.exit(1)
