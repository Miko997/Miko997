"""Static evidence plaques with locally vendored official project artwork."""
from __future__ import annotations

from html import escape

from profile_data import curated_upstream
from brand_icons import brand_icon

WIDTH, HEIGHT = 148, 68

# Repository identity is stable; display copy and geometry are intentionally small.
PLAQUES = {
    "newton-physics/newton": ("newton", "Newton Physics", "newton"),
    "google-deepmind/mujoco": ("mujoco", "MuJoCo", "mujoco"),
    "PixarAnimationStudios/OpenUSD": ("openusd", "OpenUSD", "openusd"),
    "ros2/rclcpp": ("ros2", "ROS 2", "ros2"),
    "ros2/rviz": ("rviz", "RViz", "rviz"),
    "ros-perception/point_cloud_transport": ("ros-perception", "ROS Perception", "ros-perception"),
}


def ecosystem_filename(item: dict) -> str:
    slug, _, _ = PLAQUES[item["repo"]]
    return f"assets/generated/ecosystem-{slug}.svg"


def plaque(item: dict) -> str:
    _, label, kind = PLAQUES[item["repo"]]
    # The official MuJoCo wordmark and RViz splash have wider proportions than
    # the square symbols. Fit their complete artwork into the same top band.
    icon_width = {"newton": 43, "mujoco": 64, "rviz": 43}.get(kind, 28)
    seam_start = max(53, 14 + icon_width + 11)
    # The muted brass seam and clipped corners refer to machined instrument labels.
    # This narrow frame remains subordinate to the activity and original project art.
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">{escape(item['name'])} — {escape(item['description'])}</title>
<desc id="desc">Official project artwork on a plaque linked to publicly verified upstream work.</desc>
<defs>
 <linearGradient id="plate" x2=".9" y2="1"><stop stop-color="#171b2b"/><stop offset="1" stop-color="#0b101a"/></linearGradient>
 <linearGradient id="seam"><stop stop-color="#9b8054" stop-opacity=".65"/><stop offset=".45" stop-color="#605579" stop-opacity=".6"/><stop offset="1" stop-color="#364158" stop-opacity=".3"/></linearGradient>
</defs>
<path d="M.5.5H134L147.5 14V67.5H12L.5 56Z" fill="url(#plate)" stroke="#30374a"/>
<path d="M1 1H134L147 14M147 67H12L1 56" fill="none" stroke="url(#seam)"/>
<path d="M{seam_start} 22H129" stroke="#343749" stroke-width=".7"/>
<path d="M120 20L127 20" stroke="#9b8054" stroke-width=".8" opacity=".65"/>
{brand_icon(kind, 14, 6, icon_width, 28)}
<text x="14" y="53" fill="#e8e7f5" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="600">{escape(label)}</text>
</svg>'''


def ecosystem_assets(snapshot: dict) -> dict[str, str]:
    """Return only plaques backed by the same verified evidence as the README."""
    return {ecosystem_filename(item): plaque(item) for item in curated_upstream(snapshot)
            if item["repo"] in PLAQUES}
