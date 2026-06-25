#!/usr/bin/env python3
"""Iteration 5 — the 12-point star, colour approaches + outline family.

Active design: 12-point star whose 6 SHORT points sit on the leaf's six skeleton
rays and whose 6 LONG points bisect the gaps. The bisectors point through the
CENTRES of the leaf's six colour wedges — so the leaf-faithful colour map is
LONG points = the six area colours, SHORT points (on the ray boundaries) = neutral.

All marks here have the central hub/pivot dot REMOVED (owner 2026-06-19) to balance
the star / snowflake / compass readings — points converge to a clean centre.
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"
# leaf wedge colours, in OUTER order (gold, navy, lake, maroon, boreal, slate)
WEDGE_COLORS = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]

LC = (50.0, 44.0)
OUTER = [(3.9, -39.1), (97.5, -38.3), (142.9, 24.2),
         (113.6, 114.6), (-12.3, 115.7), (-42.9, 24.2)]


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(c, a_deg, r):
    a = math.radians(a_deg)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


def ray_angle(V):
    return math.degrees(math.atan2(V[0] - LC[0], -(V[1] - LC[1]))) % 360.0


# Build the 12 tips, each: (angle, kind 'S'/'L', wedge-colour-or-None)
RAYS = [ray_angle(v) for v in OUTER]                     # six boundaries
_tips = [(a, "S", None) for a in RAYS]
for i in range(6):                                       # six wedge centres
    a, b = RAYS[i], RAYS[(i + 1) % 6]
    if b < a:
        b += 360
    _tips.append((((a + b) / 2) % 360, "L", WEDGE_COLORS[i]))
TIPS = sorted(_tips, key=lambda t: t[0])


def kites(c, long_r, short_r, rin, colour_of):
    """Yield (d, colour) for each of the 12 kites. colour_of(kind, wedge_col)->hex."""
    m = len(TIPS)
    for k in range(m):
        a, kind, wc = TIPS[k]
        a_next = TIPS[(k + 1) % m][0]
        a_next = a_next if a_next > a else a_next + 360
        a_prev = TIPS[(k - 1) % m][0]
        a_prev = a_prev if a_prev < a else a_prev - 360
        R = long_r if kind == "L" else short_r
        tip = pt(c, a, R)
        vr = pt(c, (a + a_next) / 2, rin)
        vl = pt(c, (a + a_prev) / 2, rin)
        d = (f"M{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}"
             f"L{f(c[0])} {f(c[1])}L{f(vl[0])} {f(vl[1])}Z")
        yield d, colour_of(kind, wc), (a, kind)


def outline_path(c, long_r, short_r, rin):
    """Single zig-zag silhouette outline (tips + valleys), for the outline family."""
    m = len(TIPS)
    d = []
    for k in range(m):
        a, kind, _ = TIPS[k]
        a_next = TIPS[(k + 1) % m][0]
        a_next = a_next if a_next > a else a_next + 360
        R = long_r if kind == "L" else short_r
        o = pt(c, a, R)
        v = pt(c, (a + a_next) / 2, rin)
        d.append(("M" if k == 0 else "L") + f"{f(o[0])} {f(o[1])}")
        d.append(f"L{f(v[0])} {f(v[1])}")
    return "".join(d) + "Z"


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + body + "</svg>\n")


C = (50.0, 50.0)
LR, SR, RIN = 47.0, 29.0, 13.0


def filled(colour_of, ground=None, stroke=None, sw=0.9):
    """stroke = thin separator on every kite (the leaf's off-white skeleton),
    so each colour reads even against a same-colour ground."""
    body = f'<circle cx="50" cy="50" r="48" fill="{ground}"/>' if ground else ""
    sa = (f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"'
          if stroke else "")
    for d, col, _ in kites(C, LR, SR, RIN, colour_of):
        body += f'<path d="{d}" fill="{col}"{sa}/>'
    return svg(body)


def outline_mono(stroke, w=2.4, ground=None):
    body = f'<circle cx="50" cy="50" r="48" fill="{ground}"/>' if ground else ""
    body += (f'<path d="{outline_path(C, LR, SR, RIN)}" fill="none" stroke="{stroke}" '
             f'stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')
    return svg(body)


def outline_cells(short_stroke=NAVY, w=2.4, ground=None):
    """Each point a coloured chevron (valley-tip-valley); long=wedge colour."""
    body = f'<circle cx="50" cy="50" r="48" fill="{ground}"/>' if ground else ""
    m = len(TIPS)
    for k in range(m):
        a, kind, wc = TIPS[k]
        a_next = TIPS[(k + 1) % m][0]
        a_next = a_next if a_next > a else a_next + 360
        a_prev = TIPS[(k - 1) % m][0]
        a_prev = a_prev if a_prev < a else a_prev - 360
        R = LR if kind == "L" else SR
        tip = pt(C, a, R)
        vr = pt(C, (a + a_next) / 2, RIN)
        vl = pt(C, (a + a_prev) / 2, RIN)
        col = wc if kind == "L" else short_stroke
        body += (f'<path d="M{f(vl[0])} {f(vl[1])}L{f(tip[0])} {f(tip[1])}'
                 f'L{f(vr[0])} {f(vr[1])}" fill="none" stroke="{col}" '
                 f'stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>')
    return svg(body)


# ---- colour approaches -----------------------------------------------------
def leaf(kind, wc):                 # leaf-faithful: long=wedge colour, short=off-white
    return wc if kind == "L" else OFFWH


def leaf_navyshort(kind, wc):       # long=wedge colour, short=navy (for light grounds)
    return wc if kind == "L" else NAVY


def duo(long_c, short_c):
    return lambda kind, wc: long_c if kind == "L" else short_c


def mono(c):
    return lambda kind, wc: c


files = {
    # --- A. leaf-faithful colour map (long = the six area colours) -----------
    "star12-leaf-navy.svg":  filled(leaf, ground=NAVY, stroke=OFFWH, sw=0.9),
    "star12-leaf-seal.svg":  filled(leaf, ground=MAROON, stroke=OFFWH, sw=0.9),
    # short points off-white (the snowflake), outlined slate so they read on
    # light AND so navy appears only once (its single long point) — owner note
    "star12-leaf-light.svg": filled(leaf, ground=OFFWH, stroke=SLATE, sw=0.8),

    # --- B. two-tone: larger vs smaller, each one colour --------------------
    "star12-duo-navy-gold.svg":   filled(duo(NAVY, WHEAT), ground=OFFWH),
    "star12-duo-maroon-navy.svg": filled(duo(MAROON, NAVY), ground=OFFWH),
    "star12-duo-seal.svg":        filled(duo(OFFWH, WHEAT), ground=MAROON),  # long offwhite, short wheat

    # --- C. mono / solid (one colour) --------------------------------------
    "star12-solid-maroon.svg": filled(mono(MAROON)),
    "star12-solid-navy.svg":   filled(mono(NAVY)),
    "star12-solid-seal.svg":   filled(mono(OFFWH), ground=MAROON),

    # --- D. outline family (like the leaf outline) -------------------------
    "star12-outline-navy.svg":   outline_mono(NAVY),
    "star12-outline-maroon.svg": outline_mono(MAROON),
    "star12-outline-cells.svg":  outline_cells(short_stroke=NAVY),
}
for name, data in files.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)
