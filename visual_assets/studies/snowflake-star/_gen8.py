#!/usr/bin/env python3
"""Iteration 8 — cells outline: inner vs outer colour priority (owner 2026-06-25).

iter-7 drew the inner skeleton FAINT grey; the owner found the faded inner lines (where
the spokes overlap toward the centre) awkward/unintentional. This replaces the fade with
a DEFINITE priority — each inner spoke takes a real colour:

  * OUTER priority — the spoke takes its LONG (outer) point's area colour, so the six
    colour points read as full wedges all the way to the centre; short points stay slate.
  * INNER priority — the spoke takes its SHORT (inner) point's colour (slate), so the
    inner star is a clean slate snowflake and colour sits only on the six outer tips.

Long & short points strictly alternate, so every valley spoke borders exactly one of
each — the priority is unambiguous. Off-white ground, gold->deep ochre. _gen7 geometry.
Run: python3 _gen8.py && qlmanage -t -s 1100 -o . board8.svg
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))
MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"
OCHRE = "#A8842F"
WEDGE_COLORS = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]
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
    _t.append((((a + b) / 2) % 360, "L", WEDGE_COLORS[i]))
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


def chev_d(k):
    a, kind, wc = TIPS[k]
    tip = pt(C, a, LR if kind == "L" else SR)
    vl, vr = VS[(k - 1) % M], VS[k]
    return (f"M{f(vl[0])} {f(vl[1])}L{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}")


def spoke_d(k):
    v = VS[k]
    return f"M{f(v[0])} {f(v[1])}L{f(C[0])} {f(C[1])}"


def long_wedge_at(k):
    """colour of the LONG point bordering valley k (long & short alternate)."""
    a, kind, wc = TIPS[k]
    return onlight(wc) if kind == "L" else onlight(TIPS[(k + 1) % M][2])


def body(priority, w=1.5):
    b = f'<circle cx="50" cy="50" r="48" fill="{OFFWH}"/>'
    for k in range(M):                                 # inner spokes (definite colour)
        col = long_wedge_at(k) if priority == "outer" else SLATE
        b += stroke(spoke_d(k), col, w)
    for k in range(M):                                 # outer chevrons
        a, kind, wc = TIPS[k]
        col = onlight(wc) if kind == "L" else SLATE
        b += stroke(chev_d(k), col, w)
    return b


def body_faded(w=1.5):                                  # iter-7, for the before/after
    b = f'<circle cx="50" cy="50" r="48" fill="{OFFWH}"/>'
    for k in range(M):
        b += stroke(spoke_d(k), "#B9BCC4", 1.2)
    for k in range(M):
        a, kind, wc = TIPS[k]
        b += stroke(chev_d(k), onlight(wc) if kind == "L" else SLATE, w)
    return b


def svg(b):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + b + "</svg>\n")


MARKS = {
    "star12-fulloutline-cells-outer.svg": svg(body("outer")),
    "star12-fulloutline-cells-inner.svg": svg(body("inner")),
}
for n, d in MARKS.items():
    open(os.path.join(OUT, n), "w").write(d)
    print("wrote", n)


# ---- comparison board ------------------------------------------------------
def card(x, y, s, b, bg="#FFFFFF"):
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="4" fill="{bg}"/>'
            f'<g transform="translate({x},{y}) scale({s/100})">{b}</g>')


def label(x, y, t, fill="#17324D", size=12, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{t}</text>')


rows = [
    ("iter-7 faded skeleton (the awkward one)", body_faded()),
    ("OUTER priority — colour wedges to centre", body("outer")),
    ("INNER priority — slate inner, colour tips", body("inner")),
]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 560">',
         '<rect width="720" height="560" fill="white"/>',
         label(24, 34, "Iter 8 — cells outline: inner vs outer colour priority "
               "(definite lines, no fade)", size=15)]
y0 = 60
for r, (name, b) in enumerate(rows):
    cy = y0 + r * 160
    parts.append(label(24, cy + 70, name, size=12))
    x = 330
    for s in (130, 64, 36):
        parts.append(card(x, cy + (130 - s) / 2, s, b))
        parts.append(label(x + s / 2, cy + 142, f"{s}px", size=9, fill="#6B7280",
                           anchor="middle"))
        x += s + 30
parts.append("</svg>")
open(os.path.join(OUT, "board8.svg"), "w").write("".join(parts))
print("wrote board8.svg")
