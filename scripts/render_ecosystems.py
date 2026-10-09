"""Small original technical plaques for verified upstream contributions.

These are editorial motifs, not project logos. They use no external assets and
stay static so the header and activity remain the motion focus.
"""
from __future__ import annotations

from html import escape

from profile_data import curated_upstream

WIDTH, HEIGHT = 148, 68

# Repository identity is stable; display copy and geometry are intentionally small.
PLAQUES = {
    "newton-physics/newton": ("newton", "Newton Physics", "newton"),
    "ros2/rclcpp": ("ros2", "ROS 2", "ros2"),
    "microsoft/typespec": ("typespec", "TypeSpec", "typespec"),
    "conda-forge/staged-recipes": ("conda-forge", "conda-forge", "conda"),
    "mikedh/trimesh": ("trimesh", "trimesh", "mesh"),
}


def ecosystem_filename(item: dict) -> str:
    slug, _, _ = PLAQUES[item["repo"]]
    return f"assets/generated/ecosystem-{slug}.svg"


def motif(kind: str) -> str:
    """Original geometry: forces, articulated joints, types, packages and mesh."""
    shapes = {
        "newton": ('<path d="M-12 3L-5-1 2 3V11L-5 15-12 11Z"/>'
                   '<path d="M-12 3L-5 7 2 3M-5 7V15M-5-1V-6H9M5-10L9-6 5-2"/>'
                   '<path d="M8 8L13 5" stroke="#ceb88a"/>'),
        "ros2": ('<path d="M-12 13H2M-8 13V5L-1-2 8 2 13-4M9-7L15-3 12 1"/>'
                 '<circle cx="-8" cy="5" r="2.5" fill="#182237"/>'
                 '<circle cx="-1" cy="-2" r="2.5" fill="#182237"/>'
                 '<circle cx="8" cy="2" r="2.5" fill="#182237" stroke="#ceb88a"/>'),
        "typespec": ('<path d="M-9-6L-14 1-9 8M9-6L14 1 9 8M-2 9L3-7"/>'
                     '<path d="M-5 12H5" stroke="#ceb88a"/>'),
        "conda": ('<path d="M-11-3L-4-7 3-3V5L-4 9-11 5ZM-11-3L-4 1 3-3M-4 1V9"/>'
                  '<path d="M3 0L10-4 17 0V8L10 12 3 8M3 0L10 4 17 0M10 4V12" stroke="#ceb88a"/>'),
        "mesh": ('<path d="M-13 7L-7-7 6-9 14 3 6 13-13 7ZM-13 7L0 1 6 13M-7-7L0 1 6-9M0 1L14 3"/>'
                 '<path d="M0 1L6-9M0 1L6 13" stroke="#ceb88a"/>'),
    }
    return ('<g transform="translate(28 20)" fill="none" stroke="#ad9ce0" '
            'stroke-width="1.25" stroke-linejoin="round" stroke-linecap="round">'
            + shapes[kind] + '</g>')


def plaque(item: dict) -> str:
    _, label, kind = PLAQUES[item["repo"]]
    # The muted brass seam and clipped corners refer to machined instrument labels.
    # This narrow frame remains subordinate to the activity and original project art.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">{escape(item['name'])}</title>
<desc id="desc">Original technical motif accompanying a selected contribution to {escape(item['name'])}.</desc>
<defs>
 <linearGradient id="plate" x2=".9" y2="1"><stop stop-color="#171b2b"/><stop offset="1" stop-color="#0b101a"/></linearGradient>
 <linearGradient id="seam"><stop stop-color="#9b8054" stop-opacity=".65"/><stop offset=".45" stop-color="#605579" stop-opacity=".6"/><stop offset="1" stop-color="#364158" stop-opacity=".3"/></linearGradient>
</defs>
<path d="M.5.5H134L147.5 14V67.5H12L.5 56Z" fill="url(#plate)" stroke="#30374a"/>
<path d="M1 1H134L147 14M147 67H12L1 56" fill="none" stroke="url(#seam)"/>
<path d="M53 22H129" stroke="#343749" stroke-width=".7"/>
<path d="M120 20L127 20" stroke="#9b8054" stroke-width=".8" opacity=".65"/>
{motif(kind)}
<text x="14" y="53" fill="#e8e7f5" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="600">{escape(label)}</text>
</svg>'''


def ecosystem_assets(snapshot: dict) -> dict[str, str]:
    """Return only plaques backed by the same verified evidence as the README."""
    return {ecosystem_filename(item): plaque(item) for item in curated_upstream(snapshot)
            if item["repo"] in PLAQUES}
