"""Embed vendored brand artwork without network dependencies or redrawn geometry."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)


@lru_cache(maxsize=32)
def icon_source(name: str) -> str:
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name):
        raise ValueError("Invalid brand icon name")
    return (ROOT / "assets/brands/icons" / f"{name}.svg").read_text()


def brand_icon(name: str, x: float, y: float, width: float, height: float) -> str:
    """Fit the supplied symbol into its existing button slot, retaining its paint."""
    root = ET.fromstring(icon_source(name))
    if root.tag != f"{{{SVG}}}svg" or "viewBox" not in root.attrib:
        raise ValueError(f"Brand icon requires an SVG viewBox: {name}")
    for key, value in {"x": x, "y": y, "width": width, "height": height}.items():
        root.set(key, str(value))
    root.set("preserveAspectRatio", "xMidYMid meet")
    root.set("aria-hidden", "true")
    for node in root.iter():
        if node.text is not None and not node.text.strip():
            node.text = None
        if node.tail is not None and not node.tail.strip():
            node.tail = None
    return ET.tostring(root, encoding="unicode")
