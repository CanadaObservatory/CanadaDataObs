#!/usr/bin/env python3
"""Iteration 9 — the mono full outline in every brand colour (owner 2026-06-25).

"All the choices on hand": the single-colour `fulloutline` mark rendered in each locked
palette colour. Dark inks sit on the transparent/light register (lines only, drop on any
light page); the light inks (off-white, wheat, gold) would vanish on off-white, so they
get a disc ground (navy, plus the maroon seal for off-white) — same split the brand
already uses. Geometry + weight (1.5) identical to _gen7/_gen8.
Run: python3 _gen9.py && qlmanage -t -s 1200 -o . board9.svg
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

# locked palette + tints (canonical hexes)
NAVY, LAKE, MAROON, BOREAL = "#17324D", "#2A7F9E", "#7A263A", "#3F6F5E"
SLATE, GOLD, OFFWH, WHEAT = "#6B7280", "#C2972F", "#F7F4EE", "#D9B36C"
OCHRE, LINKBLUE = "#A8842F", "#1F6E8C"   # deep-ochre (light-safe gold) + link-blue tint

LC = (50.0, 44.0)
OUTER = [(3.9, -39.1), (97.5, -38.3), (142.9, 24.2),
         (113.6, 114.6), (-12.3, 115.7), (-42.9, 24.2)]
WEDGE = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(c, a, r):
    a = math.radians(a)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


def ray_angle(V):
    return math.degrees(math.atan2(V[0] - LC[0], -(V[1] - LC[1]))) % 360.0


RAYS = [ray_angle(v) for v in OUTER]
_t = [(a, "S") for a in RAYS]
for i in range(6):
    a, b = RAYS[i], RAYS[(i + 1) % 6]
    if b < a:
        b += 360
    _t.append((((a + b) / 2) % 360, "L"))
TIPS = sorted(_t, key=lambda t: t[0])
M = len(TIPS)
C = (50.0, 50.0)
LR, SR, RIN = 47.0, 29.0, 13.0
VS = []
for k in range(M):
    a = TIPS[k][0]
    an = TIPS[(k + 1) % M][0]
    an = an if an > a else an + 360
    VS.append(pt(C, (a + an) / 2, RIN))


def stroke(d, col, w):
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def mono(col, ground=None, w=1.5):
    b = f'<circle cx="50" cy="50" r="48" fill="{ground}"/>' if ground else ""
    for v in VS:                                       # inner skeleton, one pass
        b += stroke(f"M{f(v[0])} {f(v[1])}L{f(C[0])} {f(C[1])}", col, w)
    for k in range(M):                                 # outer chevrons
        a, kind = TIPS[k]
        tip = pt(C, a, LR if kind == "L" else SR)
        vl, vr = VS[(k - 1) % M], VS[k]
        b += stroke(f"M{f(vl[0])} {f(vl[1])}L{f(tip[0])} {f(tip[1])}"
                    f"L{f(vr[0])} {f(vr[1])}", col, w)
    return b


def svg(b):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + b + "</svg>\n")


# colour name -> (hex, ground)   ground None = transparent (light register)
LIGHT = [("navy", NAVY), ("maroon", MAROON), ("lake", LAKE), ("boreal", BOREAL),
         ("slate", SLATE), ("ochre", OCHRE), ("linkblue", LINKBLUE)]
DARK = [("offwhite-on-navy", OFFWH, NAVY), ("wheat-on-navy", WHEAT, NAVY),
        ("gold-on-navy", GOLD, NAVY), ("seal", OFFWH, MAROON)]  # seal = offwhite/maroon

files = {f"star12-fulloutline-{n}.svg": svg(mono(c)) for n, c in LIGHT}
for n, c, g in DARK:
    files[f"star12-fulloutline-{n}.svg"] = svg(mono(c, ground=g))
for name, data in files.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)


# ---- swatch board ----------------------------------------------------------
def card(x, y, s, b, bg):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{bg}"/>'
            f'<g transform="translate({x},{y}) scale({s/100})">{b}</g>')


def label(x, y, t, fill="#17324D", size=12, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{t}</text>')


COLW, ROWH = 175, 168
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 700">',
         '<rect width="740" height="700" fill="white"/>',
         label(24, 34, "Iter 9 — mono full outline in every brand colour (110px + 40px)",
               size=16)]


def put(items, y0, light):
    for i, item in enumerate(items):
        col, row = i % 4, i // 4
        x = 28 + col * COLW
        y = y0 + row * ROWH
        if light:
            name, c = item
            body, bg = mono(c), "#F7F4EE"
        else:
            name, c, g = item
            body, bg = mono(c, ground=g), "#FFFFFF"
        parts.append(card(x, y, 110, body, bg))
        parts.append(card(x + 120, y + 35, 40, body, bg))
        parts.append(label(x + 55, y + 128, name, size=11, anchor="middle"))


parts.append(label(24, 70, "Dark inks — light register (transparent; drop on any light page)",
                   size=12, fill="#6B7280"))
put(LIGHT, 86, True)
parts.append(label(24, 86 + 2 * ROWH + 6,
                   "Light inks — on a disc (they vanish on off-white)",
                   size=12, fill="#6B7280"))
put(DARK, 86 + 2 * ROWH + 22, False)
parts.append("</svg>")
open(os.path.join(OUT, "board9.svg"), "w").write("".join(parts))
print("wrote board9.svg")
