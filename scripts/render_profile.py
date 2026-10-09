"""Self-contained SVGs: real numbers are rendered on refresh; only light animates."""
from __future__ import annotations

import math
from datetime import date, timedelta
from html import escape

BG = "#090912"
PANEL = "#111020"
TEXT = "#f1f0ff"
MUTED = "#aaa7c4"
VIOLET = "#a77bff"
BLUE = "#55b9ff"
LEVELS = ["#191729", "#383063", "#6343ab", "#9565e6", "#73b9ff"]


def text(x, y, value, size=18, fill=TEXT, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{escape(str(value))}</text>')


def start(width, height, title, description, animated=True):
    motion = """
      @keyframes breathe {0%,100%{opacity:.52}50%{opacity:.95}}
      @keyframes flame {0%,100%{transform:scale(.97,1);opacity:.87}50%{transform:scale(1.04,1.05);opacity:1}}
      @keyframes flow {to{stroke-dashoffset:-360}}
      .pulse{animation:breathe 5s ease-in-out infinite}
      .fire{animation:flame 2.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center bottom}
      .orbit{animation:flow 28s linear infinite}
      @media(prefers-reduced-motion:reduce){.pulse,.fire,.orbit{animation:none!important}}
    """ if animated else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>
  <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#8b5cf6"/><stop offset=".5" stop-color="#29213c"/><stop offset="1" stop-color="#258edf"/></linearGradient>
  <linearGradient id="energy" x1="0" x2="1" y1="0" y2="1"><stop stop-color="#ac6cff"/><stop offset=".55" stop-color="#7955ff"/><stop offset="1" stop-color="#50c4ff"/></linearGradient>
  <linearGradient id="flame" x1="0" x2=".6" y1="0" y2="1"><stop stop-color="#d5bbff"/><stop offset=".35" stop-color="#a166ff"/><stop offset=".73" stop-color="#6d5bff"/><stop offset="1" stop-color="#42bdff"/></linearGradient>
  <radialGradient id="aura"><stop stop-color="#513183" stop-opacity=".38"/><stop offset="1" stop-color="#0b0916" stop-opacity="0"/></radialGradient>
  <filter id="glow" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
  <style>text{{font-family:Inter,Segoe UI,Arial,sans-serif}}.mono{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;letter-spacing:2px}}{motion}</style>
</defs>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" fill="{BG}" stroke="url(#edge)"/>
<ellipse cx="{width*.82}" cy="{height*.35}" rx="{width*.35}" ry="{height*.7}" fill="url(#aura)"/>
'''


def header():
    parts = [start(1200, 280, "Miko Parkkinen — Simulation, robotics and systems engineering",
                   "Independent research, open source and real-time systems. Violet and blue technical identity.")]
    parts += ['<path d="M42 34h28m-28 0v22M1158 246h-28m28 0v-22" fill="none" stroke="#5a4a8f" stroke-width="2"/>',
              text(52, 67, "SIMULATION / ROBOTICS / PHYSICAL AI", 16, VIOLET, 600, extra='class="mono"'),
              text(48, 131, "MIKO PARKKINEN", 56, TEXT, 700),
              text(52, 170, "Software systems. Independent research. Open source.", 22, MUTED),
              '<path d="M52 200h620" stroke="url(#energy)" stroke-width="2"/>',
              text(52, 235, "BUILD  /  SIMULATE  /  VERIFY", 16, BLUE, 500, extra='class="mono"')]
    cx, cy = 992, 140
    for radius in (72, 108):
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#3c2c65" stroke-width="1"/>')
    parts.append(f'<circle class="orbit" cx="{cx}" cy="{cy}" r="108" fill="none" stroke="url(#energy)" stroke-width="2" stroke-dasharray="44 128 8 110"/>')
    for i in range(6):
        a = math.radians(i * 60 - 30)
        x, y = cx + 108 * math.cos(a), cy + 108 * math.sin(a)
        parts.append(f'<path d="M{cx} {cy}L{x:.1f} {y:.1f}" stroke="#31244f"/>')
        parts.append(f'<circle class="pulse" cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{BLUE if i%2 else VIOLET}" style="animation-delay:-{i}s"/>')
    crystal = '<path d="M992 83l32 35-7 62-25 24-25-24-7-62zM992 83v121m-32-86 32 19 32-19m-57 62 25-43 25 43" fill="#1b1535" stroke="url(#energy)" stroke-width="2"/>'
    parts += [crystal, '<path class="pulse" d="M992 88v110" stroke="#b195ff" stroke-width="5" filter="url(#glow)"/>', '</svg>']
    return "".join(parts)


def level(n, maximum):
    if n == 0:
        return 0
    return min(4, max(1, math.ceil(n * 4 / max(1, maximum))))


def dashboard(snapshot, animated=True):
    stats = snapshot["stats"]
    days = stats["days"]
    st = stats["streak"]
    visible = stats["visible_commits_365"]
    desc = (f"{stats['last_365']} contributions in 365 days, {stats['all_time']} all-time contributions, "
            f"{stats['active_days_365']} active days. Current contribution streak {st['current']} days, "
            f"longest {st['longest']} days. Daily totals follow the public GitHub calendar, including "
            "anonymized private activity only when enabled on the profile. Not all contributions are commits.")
    parts = [start(1200, 604, "Miko997 — Live contribution core", desc, animated)]
    parts += [text(38, 44, "CONTRIBUTION CORE", 17, VIOLET, 600, extra='class="mono"'),
              text(1162, 44, "MIKO997 / AUTO-REFRESH", 14, MUTED, anchor="end", extra='class="mono"'),
              '<path d="M38 65H1162M903 89V554" stroke="#282039"/>']
    for x, value, label in ((40, stats["last_365"], "CONTRIBUTIONS / 365D"),
                             (358, stats["all_time"], "ALL-TIME CONTRIBUTIONS"),
                             (684, stats["active_days_365"], "ACTIVE DAYS / 365")):
        parts += [text(x, 135, f"{value:,}", 48, TEXT, 650),
                  text(x+2, 165, label, 13, MUTED, extra='class="mono"')]
    parts += [text(42, 218, "Every day, recorded. Every change, counted.", 20, TEXT, 500)]
    first = date.fromisoformat(days[0][0])
    origin = first - timedelta(days=(first.weekday()+1) % 7)
    maximum = max(n for _, n in days) or 1
    last_month = None
    # Exactly 365 days: no padding days or future dates are invented.
    for idx, (iso, n) in enumerate(days):
        day = date.fromisoformat(iso)
        col, row = divmod((day-origin).days, 7)
        x, y = 72 + col*15.2, 273 + row*16
        if day.month != last_month and (idx == 0 or col < 52):
            parts.append(text(round(x, 1), 253, day.strftime("%b"), 13, MUTED))
            last_month = day.month
        shade = LEVELS[level(n, maximum)]
        tip = f"{iso}: {n} contribution{'s' if n != 1 else ''}"
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="11.5" height="12" rx="2.5" fill="{shade}"><title>{tip}</title></rect>')
        if n >= maximum*.65 and n:
            parts.append(f'<rect class="pulse" x="{x:.1f}" y="{y}" width="11.5" height="12" rx="2.5" fill="{shade}" filter="url(#glow)" style="animation-delay:-{idx%7}s"/>')
    for row, label in ((1, "M"), (3, "W"), (5, "F")):
        parts.append(text(43, 283+row*16, label, 12, MUTED))
    parts += [text(42, 409, f"{days[0][0]}  —  {days[-1][0]}", 13, MUTED),
              text(716, 410, "LESS", 10, MUTED, extra='class="mono"')]
    for i, color in enumerate(LEVELS):
        parts.append(f'<rect x="{760+i*18}" y="398" width="12" height="12" rx="2" fill="{color}"/>')
    parts.append(text(42, 452, "365-DAY ACTIVITY SIGNAL", 13, VIOLET, extra='class="mono"'))
    for idx, (_, n) in enumerate(days):
        x = 42 + idx*2.29
        parts.append(f'<rect x="{x:.2f}" y="464" width="1.65" height="{20 if n else 7}" rx=".7" fill="{LEVELS[level(n, maximum)]}"/>')
    parts.append('<path d="M38 511H876" stroke="#282039"/>')
    parts += [text(42, 541, "VISIBLE COMMIT CONTRIBUTIONS / 365D", 12, MUTED, extra='class="mono"'),
              text(872, 545, "Unavailable" if visible is None else f"{visible:,}", 24, BLUE, 600, anchor="end")]
    # The flame and orbital arcs move. The real streak number never flickers.
    cx, cy = 1041, 224
    parts += [f'<circle cx="{cx}" cy="{cy}" r="109" fill="url(#aura)"/>',
              f'<circle cx="{cx}" cy="{cy}" r="102" fill="none" stroke="#322347"/>',
              f'<circle class="orbit" cx="{cx}" cy="{cy}" r="102" fill="none" stroke="url(#energy)" stroke-width="2" stroke-dasharray="53 130 6 87"/>']
    flame = 'M1041 128C1052 157 1022 163 1035 184C1045 178 1054 169 1056 157C1086 191 1081 218 1059 230C1085 195 1040 193 1046 173C1013 202 1029 225 1041 234C1009 232 993 208 1006 183C1013 169 1026 159 1022 145C1030 148 1033 154 1035 157Z'
    opacity = "1" if st["current"] else ".3"
    parts.append(f'<g opacity="{opacity}"><path class="fire" d="{flame}" fill="url(#flame)"/><path class="fire" d="{flame}" fill="url(#flame)" filter="url(#glow)" opacity=".35"/></g>')
    parts += [text(cx, 290, st["current"], 56, TEXT, 700, anchor="middle"),
              text(cx, 349, "DAY STREAK", 14, VIOLET, 600, anchor="middle", extra='class="mono"'),
              text(cx, 374, "Contribution days", 15, MUTED, anchor="middle"),
              '<path d="M947 398h188" stroke="#322347"/>',
              text(cx, 450, st["longest"], 42, BLUE, 650, anchor="middle"),
              text(cx, 479, "LONGEST STREAK", 13, MUTED, anchor="middle", extra='class="mono"')]
    if st["current_end"]:
        parts.append(text(cx, 523, f"Through {st['current_end']}", 12, MUTED, anchor="middle"))
    parts += [text(40, 578, "PUBLISHED COUNTS ONLY  /  PRIVATE DETAILS NEVER REQUESTED", 12, MUTED, extra='class="mono"'),
              text(1161, 578, snapshot["as_of"], 12, MUTED, anchor="end"), '</svg>']
    return "".join(parts)


def impact(snapshot):
    merged, opened = snapshot["upstream"]["merged"], snapshot["upstream"]["open"]
    repos = len({p["repo"] for p in merged})
    parts = [start(1200, 178, "Public open-source impact", f"{len(merged)} merged upstream pull requests in {repos} public repositories. {len(opened)} open, not counted as merged.")]
    parts += [text(37, 38, "UPSTREAM / VERIFIED", 14, VIOLET, 600, extra='class="mono"')]
    for x, value, label in ((40, len(merged), "MERGED PRs"), (440, repos, "PUBLIC REPOSITORIES"), (840, len(opened), "OPEN / NOT MERGED")):
        parts += [text(x, 103, value, 44, TEXT, 650), text(x+2, 140, label, 14, MUTED, extra='class="mono"')]
    parts += ['<path d="M389 63v82M789 63v82" stroke="#312447"/>', '</svg>']
    return "".join(parts)


def footer():
    parts = [start(1200, 148, "Build. Simulate. Verify.", "Simulation architecture, robotics infrastructure and reproducible engineering.")]
    parts += [text(40, 66, "BUILD. SIMULATE. VERIFY.", 29, TEXT, 650),
              text(42, 107, "Simulation architecture / Robotics infrastructure / Reproducible engineering", 18, MUTED),
              '<path class="pulse" d="M944 51h60l16 23 26-44 27 70 21-26h62" fill="none" stroke="url(#energy)" stroke-width="2"/>', '</svg>']
    return "".join(parts)


def pending():
    return start(1200, 220, "Contribution core — awaiting verified data", "No example or estimated counts are displayed.") + text(42, 64, "CONTRIBUTION CORE", 19, VIOLET, extra='class="mono"') + text(42, 121, "Awaiting the first verified GitHub snapshot.", 27, TEXT, 600) + text(42, 165, "Counts are generated by the profile workflow, never copied from an example.", 19, MUTED) + "</svg>"
