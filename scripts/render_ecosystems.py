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
    "google-deepmind/mujoco": ("mujoco", "MuJoCo", "multibody"),
    "PixarAnimationStudios/OpenUSD": ("openusd", "OpenUSD", "scene"),
    "ros2/rclcpp": ("ros2", "ROS 2", "ros2"),
    "ros2/rviz": ("rviz", "RViz", "viewport"),
    "ros-perception/point_cloud_transport": ("ros-perception", "ROS Perception", "points"),
}


def ecosystem_filename(item: dict) -> str:
    slug, _, _ = PLAQUES[item["repo"]]
    return f"assets/generated/ecosystem-{slug}.svg"


def motif(kind: str) -> str:
    """Original geometry for forces, joints, scene graphs and perception."""
    shapes = {
        "newton": ('<path d="M-12 3L-5-1 2 3V11L-5 15-12 11Z"/>'
                   '<path d="M-12 3L-5 7 2 3M-5 7V15M-5-1V-6H9M5-10L9-6 5-2"/>'
                   '<path d="M8 8L13 5" stroke="#ceb88a"/>'),
        "ros2": ('<path d="M-12 13H2M-8 13V5L-1-2 8 2 13-4M9-7L15-3 12 1"/>'
                 '<circle cx="-8" cy="5" r="2.5" fill="#182237"/>'
                 '<circle cx="-1" cy="-2" r="2.5" fill="#182237"/>'
                 '<circle cx="8" cy="2" r="2.5" fill="#182237" stroke="#ceb88a"/>'),
        "multibody": ('<path d="M-12 10L-3 1 8 7M-3 1L3-9"/>'
                      '<circle cx="-12" cy="10" r="3"/><circle cx="-3" cy="1" r="3"/>'
                      '<circle cx="8" cy="7" r="4" stroke="#ceb88a"/><path d="M-1-10L7-8"/>'),
        "scene": ('<path d="M-10-5L0-10 10-5V6L0 11-10 6ZM-10-5L0 0 10-5M0 0V11"/>'
                  '<path d="M-14 0V10L-4 15M14 0V10L4 15" stroke="#ceb88a"/>'),
        "viewport": ('<path d="M-14-9H14V11H-14ZM-14-4H14M-5 6L2-1 9 6M2-1V8"/>'
                     '<path d="M-6 15H6M0 11V15" stroke="#ceb88a"/>'),
        "points": ('<path d="M-14 10L0-9 14 10M-10 13H10" stroke-opacity=".45"/>'
                   '<circle cx="0" cy="-7" r="1.5"/><circle cx="-5" cy="1" r="1.4"/>'
                   '<circle cx="5" cy="3" r="1.4"/><circle cx="-9" cy="8" r="1.4"/>'
                   '<circle cx="0" cy="9" r="1.7" stroke="#ceb88a"/><circle cx="10" cy="10" r="1.4"/>'),
    }
    return ('<g transform="translate(28 20)" fill="none" stroke="#ad9ce0" '
            'stroke-width="1.25" stroke-linejoin="round" stroke-linecap="round">'
            + shapes[kind] + '</g>')


def plaque(item: dict) -> str:
    _, label, kind = PLAQUES[item["repo"]]
    # The muted brass seam and clipped corners refer to machined instrument labels.
    # This narrow frame remains subordinate to the activity and original project art.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">{escape(item['name'])} — {escape(item['description'])}</title>
<desc id="desc">Original technical plaque linked to publicly verified upstream work.</desc>
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
