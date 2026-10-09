"""Embed vendored brand artwork without network dependencies or redrawn geometry."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = "http://www.w3.org/2000/svg"
ICON_TINT = "#aa91ff"
ET.register_namespace("", SVG)


@lru_cache(maxsize=32)
def icon_source(name: str) -> str:
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name):
        raise ValueError("Invalid brand icon name")
    return (ROOT / "assets/brands/icons" / f"{name}.svg").read_text()


def brand_icon(name: str, x: float, y: float, width: float, height: float) -> str:
    """Fit original artwork to its slot and tint its rendered alpha silhouette."""
    root = ET.fromstring(icon_source(name))
    if root.tag != f"{{{SVG}}}svg" or "viewBox" not in root.attrib:
        raise ValueError(f"Brand icon requires an SVG viewBox: {name}")
    # A deterministic slot namespace keeps source paint/clip IDs isolated when
    # different icons (or the same icon at different sizes) share one SVG.
    slot = sha256(f"{name}:{x}:{y}:{width}:{height}".encode()).hexdigest()[:12]
    prefix = f"brand-{name}-{slot}-"
    ids = {node.attrib["id"]: prefix + node.attrib["id"]
           for node in root.iter() if "id" in node.attrib}
    for node in root.iter():
        for key, value in list(node.attrib.items()):
            if key == "id":
                node.set(key, ids[value])
            elif key.endswith("href") and value.startswith("#"):
                node.set(key, "#" + ids.get(value[1:], value[1:]))
            else:
                node.set(key, re.sub(r"url\(#([^)]*)\)",
                                    lambda match: f"url(#{ids.get(match[1], match[1])})", value))

    artwork = ET.Element(f"{{{SVG}}}g", {"filter": f"url(#{prefix}theme-tint)"})
    for child in list(root):
        if child.tag not in {f"{{{SVG}}}defs", f"{{{SVG}}}title", f"{{{SVG}}}desc"}:
            root.remove(child)
            artwork.append(child)
    defs = ET.SubElement(root, f"{{{SVG}}}defs")
    paint = ET.SubElement(defs, f"{{{SVG}}}filter", {
        "id": prefix + "theme-tint", "x": "-10%", "y": "-10%",
        "width": "120%", "height": "120%", "filterUnits": "objectBoundingBox",
        "color-interpolation-filters": "sRGB",
    })
    ET.SubElement(paint, f"{{{SVG}}}feFlood", {"flood-color": ICON_TINT, "result": "theme-color"})
    # SourceAlpha includes vector antialiasing, raster transparency and any
    # original masks. Compositing never paints the transparent canvas.
    ET.SubElement(paint, f"{{{SVG}}}feComposite", {
        "in": "theme-color", "in2": "SourceAlpha", "operator": "in",
    })
    root.append(artwork)
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
