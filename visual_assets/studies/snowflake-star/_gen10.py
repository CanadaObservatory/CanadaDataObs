#!/usr/bin/env python3
"""Iteration 10 — cells outline, inner-priority: which NEUTRAL? (owner 2026-06-25).

Outer-priority is dropped (the six colour spokes meeting at the dead centre overlap
messily). Inner-priority is the keeper, BUT its neutral was slate — and slate is one of
the six area colours (the Education/Science point), so the neutral collided with a
coloured point. The neutral must be un-confusable with any of the six → a near-white.
The catch: the colour version needs a light ground (dark points must read), so a
near-white neutral fights that ground. Scope the trade-off across candidates, on both an
off-white and a pure-white ground:

  slate  — reference (the clash)        white #FFFFFF       off-white #F7F4EE (brand)
                                        border-grey #D9DEE5 (brand "faded white")

Long points keep the six area colours (slate stays, but now appears ONCE, on its point);
short points + inner spokes take the chosen neutral. _gen8 geometry, weight 1.5.
Run: python3 _gen10.py && qlmanage -t -s 1150 -o . board10.svg
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))
NAVY, LAKE, MAROON, BOREAL = "#17324D", "#2A7F9E", "#7A263A", "#3F6F5E"
SLATE, GOLD, OFFWH = "#6B7280", "#C2972F", "#F7F4EE"
OCHRE = "#A8842F"
WEDGE = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]
LC = (50.0, 44.0)
OUTER = [(3.9, -39.1), (97.5, -38.3), (142.9, 24.2),
         (113.6, 114.6), (-12.3, 115.7), (-42.9, 24.2)]


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(c, a, r):
    a = math.radians(a)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


def ray_angle(V):
    return math.degrees(math.atan2(V[0] - LC[0], -(V[1] - LC[1]))) % 360.0


RAYS = [ray_angle(v) for v in OUTER]
_t = [(a, "S", None) for a in RAYS]
for i in range(6):
    a, b = RAYS[i], RAYS[(i + 1) % 6]
    if b < a:
        b += 360
    _t.append((((a + b) / 2) % 360, "L", WEDGE[i]))
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


def onlight(wc):
    return OCHRE if wc == GOLD else wc


def stroke(d, col, w=1.5):
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def inner(neutral, w=1.5):
    """inner-priority cells: spokes + short points = neutral; long points = area colour."""
    b = ""
    for v in VS:                                       # spokes -> neutral
        b += stroke(f"M{f(v[0])} {f(v[1])}L{f(C[0])} {f(C[1])}", neutral, w)
    for k in range(M):                                 # chevrons
        a, kind, wc = TIPS[k]
        tip = pt(C, a, LR if kind == "L" else SR)
        vl, vr = VS[(k - 1) % M], VS[k]
        col = onlight(wc) if kind == "L" else neutral
        b += stroke(f"M{f(vl[0])} {f(vl[1])}L{f(tip[0])} {f(tip[1])}"
                    f"L{f(vr[0])} {f(vr[1])}", col, w)
    return b


def svg(b):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + b + "</svg>\n")


NEUTRALS = [
    ("slate-ref",   "#6B7280", "reference — clashes with the slate point"),
    ("white",       "#FFFFFF", "pure white"),
    ("offwhite",    "#F7F4EE", "brand off-white = the page ground"),
    ("bordergrey",  "#D9DEE5", "brand 'faded white' (Border Grey)"),
]
# write the three real candidates (skip the slate reference)
for name, hexc, _ in NEUTRALS[1:]:
    open(os.path.join(OUT, f"star12-fulloutline-cells-inner-{name}.svg"),
         "w").write(svg(inner(hexc)))
    print("wrote", f"star12-fulloutline-cells-inner-{name}.svg")

# recommended canonical: white inner on a baked-in off-white disc, so the white snowflake
# reads on ANY light page (incl. the white site body), not just on a warm ground.
DISC = '<circle cx="50" cy="50" r="48" fill="#F7F4EE"/>'
open(os.path.join(OUT, "star12-fulloutline-cells.svg"),
     "w").write(svg(DISC + inner("#FFFFFF")))
print("wrote star12-fulloutline-cells.svg (canonical: white inner + off-white disc)")


# ---- board: each neutral on off-white AND pure-white grounds ----------------
def card(x, y, s, b, bg):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{bg}" '
            f'stroke="#E3E0D8"/>'
            f'<g transform="translate({x},{y}) scale({s/100})">{b}</g>')


def label(x, y, t, fill="#17324D", size=12, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{t}</text>')


parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 720">',
         '<rect width="640" height="720" fill="white"/>',
         label(20, 30, "Iter 10 — inner-priority cells: which neutral? "
               "(left col = off-white ground · right = pure white)", size=14),
         label(250, 56, "off-white ground", size=10, fill="#6B7280", anchor="middle"),
         label(450, 56, "white ground", size=10, fill="#6B7280", anchor="middle")]
y = 70
for name, hexc, note in NEUTRALS:
    b = inner(hexc)
    parts.append(label(20, y + 70, name, size=12))
    parts.append(label(20, y + 86, note, size=9, fill="#6B7280"))
    parts.append(card(170, y, 130, b, "#F7F4EE"))      # off-white ground
    parts.append(card(370, y, 130, b, "#FFFFFF"))      # pure white ground
    parts.append(card(520, y + 45, 44, b, "#F7F4EE"))  # small, off-white
    y += 162
parts.append("</svg>")
open(os.path.join(OUT, "board10.svg"), "w").write("".join(parts))
print("wrote board10.svg")
