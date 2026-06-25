#!/usr/bin/env python3
"""Iteration 7 — full outline, refined (owner feedback 2026-06-25).

Fixes three problems with iter-6's full outline:
  1. LINE TOO THICK  -> thinner strokes (default 1.5; board shows 1.2/1.5/1.8).
  2. INCONSISTENT COLOURS at the inner connections -> iter-6 stroked each spike as a
     CLOSED kite, so the shared valley->centre spokes were drawn TWICE in two colours
     (arbitrary last-wins). Here the structure is drawn in TWO clean passes:
        (a) the inner SKELETON (12 valley->centre spokes) ONCE, in a single neutral;
        (b) the 12 point CHEVRONS (valley->tip->valley) each in ONE colour.
     Every line now has exactly one defined colour.
  3. A SPIKE VANISHING into a same-colour ground (navy point on navy) -> the colour
     ('cells') version sits on OFF-WHITE, neutral = slate, and gold -> deep ochre so the
     warm point holds contrast on light. (Mono versions are unaffected.)

Same geometry as _gen5/_gen6 (TIPS, LR/SR/RIN). Run: python3 _gen7.py && \
qlmanage -t -s 1200 -o . board7.svg
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"
OCHRE = "#A8842F"  # deep ochre — the gold stop that holds a thin stroke on light
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


RAYS = [ray_angle(v) for v in OUTER]
_tips = [(a, "S", None) for a in RAYS]
for i in range(6):
    a, b = RAYS[i], RAYS[(i + 1) % 6]
    if b < a:
        b += 360
    _tips.append((((a + b) / 2) % 360, "L", WEDGE_COLORS[i]))
TIPS = sorted(_tips, key=lambda t: t[0])

C = (50.0, 50.0)
LR, SR, RIN = 47.0, 29.0, 13.0
M = len(TIPS)


def valley_pts():
    """12 valley points (vs[k] sits between tip k and tip k+1), at radius RIN."""
    vs = []
    for k in range(M):
        a = TIPS[k][0]
        an = TIPS[(k + 1) % M][0]
        an = an if an > a else an + 360
        vs.append(pt(C, (a + an) / 2, RIN))
    return vs


VS = valley_pts()


def chevron(k):
    """point k as vl -> tip -> vr (open V); returns (d, kind, wedge_colour)."""
    a, kind, wc = TIPS[k]
    tip = pt(C, a, LR if kind == "L" else SR)
    vl, vr = VS[(k - 1) % M], VS[k]
    d = (f"M{f(vl[0])} {f(vl[1])}L{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}")
    return d, kind, wc


def stroke(d, col, w):
    return (f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{f(w)}" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def disc(g):
    return f'<circle cx="50" cy="50" r="48" fill="{g}"/>' if g else ""


def body(skeleton_col, point_col, w=1.5, ground=None, skel_w=None, skel_col=None):
    """point_col(kind, wedge)->hex.  skeleton drawn ONCE in skel_col (default skeleton_col)."""
    skel_w = skel_w if skel_w is not None else w
    skel_col = skel_col if skel_col is not None else skeleton_col
    b = disc(ground)
    for v in VS:                                   # (a) inner skeleton, one pass
        b += stroke(f"M{f(v[0])} {f(v[1])}L{f(C[0])} {f(C[1])}", skel_col, skel_w)
    for k in range(M):                             # (b) coloured chevrons, one each
        d, kind, wc = chevron(k)
        b += stroke(d, point_col(kind, wc), w)
    return b


def svg(b):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + b + "</svg>\n")


def mono(c):
    return lambda kind, wc: c


def cells_light(kind, wc):
    if kind == "S":
        return SLATE
    return OCHRE if wc == GOLD else wc            # gold -> ochre on light


WT = 1.5  # chosen default weight

MARKS = {
    "star12-fulloutline-navy.svg":   svg(body(NAVY,   mono(NAVY),   WT)),
    "star12-fulloutline-maroon.svg": svg(body(MAROON, mono(MAROON), WT)),
    "star12-fulloutline-seal.svg":   svg(body(OFFWH,  mono(OFFWH),  WT, ground=MAROON)),
    # colour version on OFF-WHITE (no same-colour-as-ground vanishing); faint slate skeleton
    "star12-fulloutline-cells.svg":  svg(body(SLATE, cells_light, WT, ground=OFFWH,
                                              skel_col="#B9BCC4", skel_w=1.2)),
}
for name, data in MARKS.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)


# ---- board: weight comparison + the refined set ----------------------------
def card(x, y, s, b, bg):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{bg}"/>'
            f'<g transform="translate({x},{y}) scale({s/100})">{b}</g>')


def label(x, y, t, fill="#17324D", size=12, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{t}</text>')


parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 760">',
         '<rect width="980" height="760" fill="white"/>',
         label(24, 34, "Iter 7 — refined full outline: thinner · one-pass neutral "
               "skeleton · colour on off-white", size=16)]

# weight comparison (navy)
parts.append(label(24, 70, "Weight (navy):", size=12))
x = 150
for w in (1.2, 1.5, 1.8, 2.2):
    parts.append(card(x, 56, 120, body(NAVY, mono(NAVY), w), OFFWH))
    parts.append(label(x + 60, 190, f"w={w}" + (" (iter-6)" if w == 2.2 else ""),
                       size=10, fill="#6B7280", anchor="middle"))
    x += 150

# the refined set at WT, three sizes
rows = [
    ("fulloutline-navy",   body(NAVY,   mono(NAVY),   WT),               OFFWH),
    ("fulloutline-maroon", body(MAROON, mono(MAROON), WT),               OFFWH),
    ("fulloutline-seal",   body(OFFWH,  mono(OFFWH),  WT, ground=MAROON), "self"),
    ("fulloutline-cells",  body(SLATE, cells_light, WT, ground=OFFWH,
                                skel_col="#B9BCC4", skel_w=1.2),          "self"),
]
y0 = 230
for r, (name, b, bg) in enumerate(rows):
    cy = y0 + r * 128
    parts.append(label(24, cy + 64, name, size=12))
    x = 200
    for s in (120, 56, 32, 20):
        ground = OFFWH if bg != "self" else "#FFFFFF"
        parts.append(card(x, cy + (120 - s) / 2, s, b, ground if bg != "self" else "#FFFFFF"))
        parts.append(label(x + s / 2, cy + 122, f"{s}px", size=9, fill="#6B7280",
                           anchor="middle"))
        x += s + 26
parts.append("</svg>")
open(os.path.join(OUT, "board7.svg"), "w").write("".join(parts))
print("wrote board7.svg")
