#!/usr/bin/env python3
"""Iteration 6 — the FULL outline of all twelve spikes (owner direction 2026-06-25).

The existing outline family only traces the OUTER edge: `outline_mono` is a single
zig-zag silhouette; `outline_cells` is twelve OPEN chevrons (the outer part of each
point). This adds the missing register — each of the twelve spikes stroked as its own
COMPLETE closed cell, so the internal structure (the leaf's skeleton) reads as line
art. Two centre treatments, because the owner removed the central hub in iter-5:

  * 'full'  — each spike runs tip -> valley -> CENTRE -> valley (cells meet at centre);
  * 'ring'  — each spike is tip -> valley -> valley (a triangle) closed by an inner
              12-gon along the valley ring, leaving a clean open centre (no hub).

Geometry is identical to _gen5.py (same TIPS / LR,SR,RIN), so this is the same star.
Run: python3 _gen6.py && qlmanage -t -s 1100 -o . board6.svg
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"
WEDGE_COLORS = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]  # leaf wedge order

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


def spikes():
    """Yield (tip, vr, vl, kind, wedge_colour) for each of the 12 spikes."""
    m = len(TIPS)
    for k in range(m):
        a, kind, wc = TIPS[k]
        a_next = TIPS[(k + 1) % m][0]
        a_next = a_next if a_next > a else a_next + 360
        a_prev = TIPS[(k - 1) % m][0]
        a_prev = a_prev if a_prev < a else a_prev - 360
        R = LR if kind == "L" else SR
        yield (pt(C, a, R), pt(C, (a + a_next) / 2, RIN),
               pt(C, (a + a_prev) / 2, RIN), kind, wc)


def cell_d(tip, vr, vl, mode):
    if mode == "full":   # tip -> valley -> centre -> valley (meets at centre)
        return (f"M{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}"
                f"L{f(C[0])} {f(C[1])}L{f(vl[0])} {f(vl[1])}Z")
    return (f"M{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}"   # ring: triangle
            f"L{f(vl[0])} {f(vl[1])}Z")


def disc(g):
    return f'<circle cx="50" cy="50" r="48" fill="{g}"/>' if g else ""


def body_mono(stroke, mode, w=2.2, ground=None):
    b = disc(ground)
    for tip, vr, vl, kind, wc in spikes():
        b += (f'<path d="{cell_d(tip, vr, vl, mode)}" fill="none" stroke="{stroke}" '
              f'stroke-width="{f(w)}" stroke-linejoin="round" stroke-linecap="round"/>')
    return b


def body_cells(mode, short=SLATE, w=2.4, ground=None):
    b = disc(ground)
    for tip, vr, vl, kind, wc in spikes():
        col = wc if kind == "L" else short
        b += (f'<path d="{cell_d(tip, vr, vl, mode)}" fill="none" stroke="{col}" '
              f'stroke-width="{f(w)}" stroke-linejoin="round" stroke-linecap="round"/>')
    return b


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + body + "</svg>\n")


# ---- the variants ----------------------------------------------------------
MARKS = {
    # full = spikes meet at the centre (faithful to the filled mark's structure)
    "star12-fulloutline-navy.svg":        body_mono(NAVY, "full"),
    "star12-fulloutline-maroon.svg":      body_mono(MAROON, "full"),
    "star12-fulloutline-seal.svg":        body_mono(OFFWH, "full", ground=MAROON),
    "star12-fulloutline-cells.svg":       body_cells("full", short=SLATE, w=2.4),
    "star12-fulloutline-cells-navy.svg":  body_cells("full", short=OFFWH, w=2.4, ground=NAVY),
    # ring = open centre (no hub); each spike a triangle + inner 12-gon
    "star12-ringoutline-navy.svg":        body_mono(NAVY, "ring"),
    "star12-ringoutline-cells.svg":       body_cells("ring", short=SLATE, w=2.4),
    "star12-ringoutline-cells-navy.svg":  body_cells("ring", short=OFFWH, w=2.4, ground=NAVY),
}
for name, b in MARKS.items():
    open(os.path.join(OUT, name), "w").write(svg(b))
    print("wrote", name)


# ---- comparison board ------------------------------------------------------
def card(x, y, s, body, bg):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{bg}"/>'
            f'<g transform="translate({x},{y}) scale({s/100})">{body}</g>')


def label(x, y, t, fill="#17324D", size=11, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{t}</text>')


ROWS = [
    ("fulloutline-navy",       body_mono(NAVY, "full"),                 "light"),
    ("fulloutline-maroon",     body_mono(MAROON, "full"),              "light"),
    ("fulloutline-seal",       body_mono(OFFWH, "full", ground=MAROON), "self"),
    ("fulloutline-cells",      body_cells("full", short=SLATE, w=2.4),  "light"),
    ("fulloutline-cells-navy", body_cells("full", short=OFFWH, w=2.4, ground=NAVY), "self"),
    ("ringoutline-navy",       body_mono(NAVY, "ring"),                 "light"),
    ("ringoutline-cells",      body_cells("ring", short=SLATE, w=2.4),  "light"),
    ("ringoutline-cells-navy", body_cells("ring", short=OFFWH, w=2.4, ground=NAVY), "self"),
]
SIZES = [120, 56, 32, 20]
LIGHT, NAVYBG = "#F7F4EE", "#17324D"
pad, lblw, gap, rowh = 24, 150, 22, 150
W = lblw + sum(SIZES) + gap * len(SIZES) + pad * 2
H = pad * 2 + 40 + rowh * len(ROWS)
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="white"/>',
         label(pad, pad + 14, "Iteration 6 — full outline of the twelve spikes "
               "(full = to centre · ring = open centre)", size=15)]
for r, (name, body, mode) in enumerate(ROWS):
    cy = pad + 40 + r * rowh
    parts.append(label(pad, cy + rowh / 2, name, size=12))
    cx = pad + lblw
    for s in SIZES:
        bg = NAVYBG if mode == "self" else LIGHT
        y = cy + (120 - s) / 2 + 8
        parts.append(card(cx, y, s, body, bg))
        parts.append(label(cx + s / 2, cy + 132, f"{s}px", size=9,
                           fill="#6B7280", anchor="middle"))
        cx += s + gap
parts.append("</svg>")
open(os.path.join(OUT, "board6.svg"), "w").write("".join(parts))
print("wrote board6.svg")
