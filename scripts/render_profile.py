"""A dated crystal calendar and layered plasma. Motion never changes the data.

Only Python's standard library is used by the scheduled refresh. Declarative
SVG morphing uses complete static contours when animation is unavailable.
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from html import escape

BG = "#090b12"
TEXT = "#f1f3ff"
MUTED = "#9ca9c4"
VIOLET = "#aa91ff"
BLUE = "#64c8ff"
LEVELS = ["#151c2b", "#424574", "#675cac", "#9485de", "#87caff"]


def text(x, y, value, size=18, fill=TEXT, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{escape(str(value))}</text>')


def start(width, height, title, description, animated=True):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<defs>
 <linearGradient id="plasma" x1="0" x2=".3" y1="0" y2="1"><stop stop-color="#9271ed"/><stop offset=".42" stop-color="#795ee8"/><stop offset=".78" stop-color="#63baf3"/><stop offset="1" stop-color="#cef4ff"/></linearGradient>
 <linearGradient id="filament" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#bcb0ff" stop-opacity=".1"/><stop offset=".45" stop-color="#bdbaff"/><stop offset="1" stop-color="#e4fbff"/></linearGradient>
 <radialGradient id="ignition"><stop stop-color="#e2f6ff" stop-opacity=".92"/><stop offset=".38" stop-color="#98dbff" stop-opacity=".65"/><stop offset=".7" stop-color="#77a3ff" stop-opacity=".26"/><stop offset="1" stop-color="#688bff" stop-opacity="0"/></radialGradient>
 <radialGradient id="aura"><stop stop-color="#7964e3" stop-opacity=".25"/><stop offset=".58" stop-color="#484dc3" stop-opacity=".12"/><stop offset="1" stop-color="#343b82" stop-opacity="0"/></radialGradient>
 <linearGradient id="face" x2=".2" y2="1"><stop stop-color="#d9e5ff" stop-opacity=".24"/><stop offset=".5" stop-color="#c4c8ff" stop-opacity=".01"/><stop offset="1" stop-color="#071426" stop-opacity=".3"/></linearGradient>
 <filter id="bloom" x="-60%" y="-30%" width="220%" height="170%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="5"/></filter>
 <filter id="soft" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.6"/></filter>
 <style>text{{font-family:Inter,"Segoe UI",Arial,sans-serif;font-variant-numeric:tabular-nums}}{motion_css() if animated else ''}</style>
</defs><rect width="{width}" height="{height}" fill="{BG}"/>
'''


# Sixteen advecting ribbons form a continuous plasma volume. Their centerlines
# carry travelling waves upward; they do not scale an icon. The path command
# topology is constant, so SMIL interpolates all eight phases smoothly.
def plasma_path(index, phase):
    side = index % 3 - 1
    height = 140 if side == 0 else 104 + (index % 4)*5
    spread = (index // 3 - 2) * 4.2
    left, right = [], []
    for step in range(13):
        z = step / 12
        wave = math.sin(z*7.5 - phase + index*.29)
        curl = math.sin(z*12 - phase*2 + index*.51)
        center = 83 + side*29*math.sin(z*2.6) + spread*(math.sin(z*math.pi)+.45*(1-z))
        center += z*(16*wave + 4*curl) + 6*z*z
        width = (7 + (index % 4)*2.2)*math.sin(math.pi*(.07 + z*.93))**.7
        width *= (1-.35*z)*(1+.2*math.sin(z*9-phase+index))
        y = 161-z*height
        left.append((center-width,y)); right.append((center+width,y))
    points = left + list(reversed(right))
    # Closed Catmull–Rom contour: rounded optical density bands instead of
    # visible polygon corners. All phases have identical command counts.
    d = [f'M{points[0][0]:.2f} {points[0][1]:.2f}']
    for j, a in enumerate(points):
        before, b, after = points[j-1], points[(j+1)%len(points)], points[(j+2)%len(points)]
        c1 = (a[0]+(b[0]-before[0])/6, a[1]+(b[1]-before[1])/6)
        c2 = (b[0]-(after[0]-a[0])/6, b[1]-(after[1]-a[1])/6)
        d.append(f'C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {b[0]:.2f} {b[1]:.2f}')
    return ''.join(d)+'Z'


CONTOURS = [
    (f'plasma{i}', 9.0, .11 + (i%4)*.04,
     [plasma_path(i, j*math.tau/8) for j in range(8)])
    for i in range(16)
]


def motion_css():
    rules = [
        '.plasma-still{display:none}',
        '@keyframes current{to{stroke-dashoffset:-1200}}',
        '@keyframes charge{0%,18%,65%,100%{opacity:0}35%{opacity:.55}48%{opacity:.12}}',
        '@keyframes rise{0%{transform:translate(0,0);opacity:0}22%{opacity:.7}75%{opacity:.2}100%{transform:translate(8px,-44px);opacity:0}}',
        '.current{animation:current 12s linear infinite}',
        '.charge{opacity:0;animation:charge 12s ease-in-out infinite}',
        '.spark{opacity:0;animation:rise 6s linear infinite}',
        '@media(prefers-reduced-motion:reduce){.current,.charge,.spark{animation:none!important;display:none}.plasma-motion{display:none}.plasma-still{display:inline}}',
    ]
    return ''.join(rules)


def flame(x, y, scale=1, active=True, animated=True):
    if not active:
        # Extinguished state: no colored fire, sparks or continuing motion.
        return (f'<g transform="translate({x},{y}) scale({scale})" aria-label="No current streak">'
                '<ellipse cx="83" cy="157" rx="25" ry="5" fill="#25304a"/>'
                '<path d="M58 155Q83 161 108 155" fill="none" stroke="#71809e" stroke-width="1.5"/></g>')
    out = [f'<g transform="translate({x},{y}) scale({scale})" aria-hidden="true">',
           '<ellipse cx="82" cy="113" rx="98" ry="78" fill="url(#aura)"/>']
    out.append('<defs>')
    for name, duration, _, paths in CONTOURS:
        out.append(f'<path id="{name}-still" d="{paths[0]}"/>')
        if animated:
            values = ';'.join(paths + [paths[0]])
            out.append(f'<path id="{name}-motion" d="{paths[0]}"><animate attributeName="d" dur="{duration}s" repeatCount="indefinite" calcMode="linear" values="{values}"/></path>')
    out.append('</defs>')
    for variant in (('motion','still') if animated else ('still',)):
        klass = f' class="plasma-{variant}"' if animated else ''
        out.append(f'<g{klass}>')
        for i, (name, _, opacity, paths) in enumerate(CONTOURS):
            ref = f' href="#{name}-{variant}"'
            if i % 3 == 0:
                out.append(f'<use{ref} fill="url(#plasma)" opacity="{opacity*1.9}" filter="url(#bloom)"/>')
            out.append(f'<use{ref} fill="url(#{"filament" if i%4 == 0 else "plasma"})" opacity="{opacity}"/>')
            if i % 4 == 0:
                out.append(f'<use{ref} fill="none" stroke="url(#filament)" stroke-width=".7" opacity=".18"/>')
        out.append('</g>')
    out.append('<ellipse cx="83" cy="149" rx="23" ry="17" fill="url(#ignition)" opacity=".72"/>')
    if animated:
        for i, (sx, sy) in enumerate(((59, 112), (104, 126), (87, 85), (120, 98))):
            out.append(f'<circle class="spark" cx="{sx}" cy="{sy}" r="{1+i%2*.4}" fill="#b5c9ff" style="animation-delay:-{i*1.7}s"/>')
    out += ['<ellipse cx="83" cy="165" rx="28" ry="3" fill="#4b7fb5" opacity=".22" filter="url(#soft)"/>', '</g>']
    return ''.join(out)


def level(n, maximum):
    """Monotonic sqrt quantization retains low-volume activity under outliers."""
    return 0 if n == 0 else min(4, max(1, math.ceil(math.sqrt(n / max(1, maximum)) * 4)))


def calendar(days, x, y, pitch, cell, maximum, animated=True, part=0, label_size=17):
    first = date.fromisoformat(days[0][0])
    origin = first - timedelta(days=(first.weekday()+1) % 7)
    out, points, inactive = [], [], []
    last_month = None
    # Every date is present exactly once, with its immutable count and title.
    for idx, (iso, n) in enumerate(days):
        day = date.fromisoformat(iso)
        col, row = divmod((day-origin).days, 7)
        px, py = round(x + col*pitch, 2), round(y + row*pitch, 2)
        if day.month != last_month:
            # Avoid the partial month's label colliding with the next month.
            if day.day == 1 or (idx == 0 and day.day < 23):
                out.append(text(px, y-18, day.strftime('%b'), label_size, MUTED))
            last_month = day.month
        shade = LEVELS[level(n, maximum)]
        tip = f"{iso}: {n} contribution{'s' if n != 1 else ''}"
        out.append(f'<g class="day" data-date="{iso}" data-count="{n}"><title>{tip}</title>'
                   f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="{shade}"/>')
        if n:
            # Faceted top and darker base give each recorded day a physical face.
            out.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="url(#face)"/>')
            out.append(f'<path d="M{px+2} {py+1.1}h{cell-4}" stroke="#e2e6ff" stroke-opacity=".32" stroke-width=".8"/>')
            points.append((px+cell/2, py+cell/2, iso, n))
        else:
            inactive.append(f'<rect x="{px-1}" y="{py-1}" width="{cell+2}" height="{cell+2}" rx="2" fill="black"/>')
        out.append('</g>')
    if animated and points:
        out.append(f'<defs><mask id="routes-{part}"><rect x="{x-3}" y="{y-3}" width="1120" height="{7*pitch+6}" fill="white"/>{"".join(inactive)}</mask></defs>')
        # A masked chronological route carries energy between real active days.
        # Empty dates are fully excluded, including antialias and glow margins.
        paths = [f'M{points[0][0]:g} {points[0][1]:g}']
        for a, b in zip(points, points[1:]):
            ax, ay, _, _ = a
            bx, by, _, _ = b
            mx = round((ax+bx)/2, 2)
            paths.append(f'C{mx:g} {ay:g} {mx:g} {by:g} {bx:g} {by:g}')
        if len(points) > 1:
            d = ' '.join(paths)
            out.append(f'<g mask="url(#routes-{part})" fill="none"><path d="{d}" stroke="#717bc3" stroke-width=".6" opacity=".13"/>')
            out.append(f'<path class="current" d="{d}" pathLength="1200" stroke="#9abfff" stroke-width="4" stroke-dasharray="38 1162" opacity=".5" filter="url(#soft)"/>')
            out.append(f'<path class="current" d="{d}" pathLength="1200" stroke="#e5f3ff" stroke-width="1.3" stroke-dasharray="14 1186" opacity=".9"/></g>')
        for i, (px, py, iso, n) in enumerate(points):
            delay = -(12 - i/max(1, len(points))*12)
            # A white rim propagates chronologically, never replacing base color.
            out.append(f'<rect class="charge" data-active-date="{iso}" x="{px-cell/2-.7:g}" y="{py-cell/2-.7:g}" width="{cell+1.4}" height="{cell+1.4}" rx="2.6" fill="none" stroke="#c8dfff" stroke-width="1" style="animation-delay:{delay:.3f}s"/>')
    for row, label in ((1, "M"), (3, "W"), (5, "F")):
        out.append(text(x-21, y+row*pitch+cell*.8, label, label_size-2, MUTED, anchor='end'))
    return ''.join(out)


def dashboard(snapshot, animated=True, compact=False):
    stats = snapshot['stats']
    days, st = stats['days'], stats['streak']
    width, height = (640, 684) if compact else (1200, 440)
    desc = (f"{stats['last_365']} contributions in 365 days, {days[0][0]} to {days[-1][0]}. "
            f"Current contribution streak {st['current']} days. Each cell is one exact GitHub date; "
            "brightness represents recorded contributions. Light only highlights active dates. "
            "Includes anonymous private contributions only when published by GitHub.")
    parts = [start(width, height, 'Miko997 — Contributions', desc, animated)]
    num_size = 62 if compact else 66
    parts += [text(32 if compact else 46, 96, f"{stats['last_365']:,}", num_size, weight=600),
              text(34 if compact else 48, 128, 'Contributions', 24 if compact else 21, MUTED)]
    if compact:
        parts += [flame(272, 4, .90, st['current'] > 0, animated),
                  text(470, 96, st['current'], 60, weight=600),
                  text(466, 128, 'Day streak', 24, MUTED)]
    else:
        parts += [flame(788, 9, 1.0, st['current'] > 0, animated),
                  text(991, 95, st['current'], 66, weight=600),
                  text(993, 127, 'Current streak', 21, MUTED)]
    start_day, end_day = (date.fromisoformat(days[i][0]) for i in (0, -1))
    period = f'{start_day:%d %b %Y} — {end_day:%d %b %Y}'
    parts += [text(34 if compact else 48, 168, period, 22, MUTED),
              f'<path d="M{32 if compact else 48} 192H{width-32 if compact else width-48}" stroke="#222a3d"/>']
    maximum = max(n for _, n in days) or 1
    if compact:
        # Split at a Sunday so both panels use identical Sunday-first weeks.
        split = 182
        while date.fromisoformat(days[split][0]).weekday() != 6:
            split += 1
        parts += [calendar(days[:split], 55, 247, 20.8, 15.5, maximum, animated, 0, 22),
                  calendar(days[split:], 55, 478, 20.8, 15.5, maximum, animated, 1, 22)]
        legend_x, legend_y = 395, 651
    else:
        parts.append(calendar(days, 70, 251, 20.5, 15.2, maximum, animated, 0, 22))
        legend_x, legend_y = 950, 417
    parts.append(text(legend_x-12, legend_y, 'Less', 20, MUTED, anchor='end'))
    for i, color in enumerate(LEVELS):
        parts.append(f'<rect x="{legend_x+i*22}" y="{legend_y-12}" width="15" height="15" rx="2" fill="{color}"/>')
    parts += [text(legend_x+117, legend_y, 'More', 20, MUTED), '</svg>']
    return ''.join(parts)


def impact(snapshot):
    """Legacy import compatibility; public showcase is ordinary linked text."""
    from profile_data import curated_upstream
    names = [item['name'] for item in curated_upstream(snapshot)]
    return start(1200, 100, 'Open source', 'Selected merged contributions.', False) + text(40, 59, '  ·  '.join(names), 27) + '</svg>'


def header():
    """Legacy static fallback. Production hero is rendered by scripts/art/."""
    return start(1200, 280, 'Miko Parkkinen', 'Simulation systems, robotics and research software.', False) + text(48, 128, 'Miko Parkkinen', 58, weight=600) + text(50, 184, 'Simulation systems · Robotics · Research software', 25, MUTED) + '</svg>'


def footer():
    return start(1200, 64, 'Miko Parkkinen', 'Simulation systems and research software.', False) + '</svg>'


def pending():
    return start(1200, 220, 'Contributions unavailable', 'No estimated counts are displayed.', False) + text(48, 117, 'Awaiting verified GitHub data.', 30) + '</svg>'
