#!/usr/bin/env python3
"""Iteration 4 — 12-point star locked to the leaf's six rays.

Short points sit on the EXACT angular positions of the leaf's six skeleton rays
(from C=(50,44)); a longer point bisects each gap between them. The six rays are
unevenly spaced (the leaf is an irregular hexagon, gaps 48-83 degrees), so the
12-point star is subtly irregular — it carries the leaf's true geometry.
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"
COLORS = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]

LC = (50.0, 44.0)
OUTER = [(3.9, -39.1), (97.5, -38.3), (142.9, 24.2),
         (113.6, 114.6), (-12.3, 115.7), (-42.9, 24.2)]
LEAF_D = open(os.path.join(OUT, "_leafpath.txt")).read().strip() \
    if os.path.exists(os.path.join(OUT, "_leafpath.txt")) else None


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(c, a_deg, r):
    a = math.radians(a_deg)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


def ray_angle(V):
    return math.degrees(math.atan2(V[0] - LC[0], -(V[1] - LC[1]))) % 360.0


SHORT = sorted(ray_angle(v) for v in OUTER)            # the six leaf rays
LONG = []                                              # bisector of each gap
for i in range(6):
    a, b = SHORT[i], SHORT[(i + 1) % 6]
    if b < a:
        b += 360
    LONG.append(((a + b) / 2) % 360)

# interleaved tip list (angle, kind)
TIPS = sorted([(a, "S") for a in SHORT] + [(a, "L") for a in LONG])


def irregular_star_path(c, long_r, short_r, rin):
    m = len(TIPS)
    d = []
    for k in range(m):
        a, kind = TIPS[k]
        a2 = TIPS[(k + 1) % m][0]
        if a2 <= a:
            a2 += 360
        va = (a + a2) / 2
        R = long_r if kind == "L" else short_r
        o, v = pt(c, a, R), pt(c, va, rin)
        d.append(("M" if k == 0 else "L") + f"{f(o[0])} {f(o[1])}")
        d.append(f"L{f(v[0])} {f(v[1])}")
    return "".join(d) + "Z"


def facet_rays(c, long_r, short_r, stroke, w):
    """Lines centre->each tip. The SHORT rays = the leaf's exact skeleton."""
    s = ""
    for a, kind in TIPS:
        R = (long_r if kind == "L" else short_r) - 1.5
        q = pt(c, a, R)
        s += (f'<line x1="{f(c[0])}" y1="{f(c[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
              f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"/>')
    return s


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + body + "</svg>\n")


# ---- variants --------------------------------------------------------------
def seal(long_r=47, short_r=30, rin=14):
    c = (50, 50)
    return svg(f'<circle cx="50" cy="50" r="48" fill="{MAROON}"/>'
               f'<path d="{irregular_star_path(c, long_r, short_r, rin)}" fill="{OFFWH}"/>'
               + facet_rays(c, long_r, short_r, MAROON, 1.0)
               + f'<circle cx="50" cy="50" r="2.8" fill="{MAROON}"/>'
               f'<circle cx="50" cy="50" r="1.2" fill="{OFFWH}"/>')


def observatory(long_r=47, short_r=30, rin=14):
    c = (50, 50)
    return svg(f'<circle cx="50" cy="50" r="47" fill="none" stroke="{WHEAT}" stroke-width="2"/>'
               f'<path d="{irregular_star_path(c, long_r, short_r, rin)}" fill="{NAVY}"/>'
               + facet_rays(c, long_r, short_r, OFFWH, 1.0)
               + f'<circle cx="50" cy="50" r="3.6" fill="{OFFWH}"/>'
               f'<circle cx="50" cy="50" r="1.5" fill="{NAVY}"/>')


def cells_colour(long_r=47, short_r=30, rin=13, long_col=WHEAT):
    """Short points (= the six leaf rays) carry... the wedge colours flanking
    each ray; long points off-white. We colour each kite by its tip's nearest
    leaf colour, short tips coloured, long tips off-white, on an off-white disc."""
    c = (50, 50)
    body = f'<circle cx="50" cy="50" r="48" fill="{OFFWH}"/>'
    m = len(TIPS)
    ci = 0
    for k in range(m):
        a, kind = TIPS[k]
        a2 = TIPS[(k + 1) % m][0]
        if a2 <= a:
            a2 += 360
        a0 = TIPS[(k - 1) % m][0]
        if a0 >= a:
            a0 -= 360
        R = long_r if kind == "L" else short_r
        tip = pt(c, a, R)
        vl, vr = pt(c, (a + a0) / 2, rin), pt(c, (a + a2) / 2, rin)
        if kind == "S":
            col = COLORS[ci % 6]
            ci += 1
        else:
            col = long_col
        body += (f'<path d="M{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}'
                 f'L{f(c[0])} {f(c[1])}L{f(vl[0])} {f(vl[1])}Z" fill="{col}"/>')
    body += f'<circle cx="50" cy="50" r="3" fill="{MAROON}"/>'
    body += f'<circle cx="50" cy="50" r="1.3" fill="{OFFWH}"/>'
    return svg(body)


files = {
    "star12-seal.svg": seal(),
    "star12-obs.svg": observatory(),
    "star12-cells.svg": cells_colour(),
    "star12-cells-v2.svg": cells_colour(long_col=OFFWH),
    "star12-cells-v3.svg": cells_colour(long_col=NAVY),
    "star12-seal-sharp.svg": seal(long_r=48, short_r=24, rin=11),
    "star12-obs-sharp.svg": observatory(long_r=48, short_r=24, rin=11),
}
for name, data in files.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)

# ---- alignment proof: star over faded leaf, leaf rays drawn as guides -------
LEAF_D = ("M 50.0 4.0 Q 50.0 4.0 50.4 5.1 L 51.9 9.2 Q 53.2 13.0 55.0 11.5 L 56.6 10.3 Q 57.5 9.5 57.6 10.7 L 57.9 15.0 Q 58.2 19.0 60.4 17.5 L 62.5 16.2 Q 63.5 15.5 63.3 16.7 L 61.7 26.1 Q 60.5 33.0 64.5 29.6 L 69.1 25.8 Q 70.0 25.0 70.3 26.1 L 70.9 27.9 Q 71.5 30.0 74.2 27.0 L 82.2 17.9 Q 83.0 17.0 83.1 18.2 L 83.6 22.2 Q 84.0 26.0 86.1 25.6 L 87.8 25.2 Q 89.0 25.0 88.4 26.0 L 83.2 34.1 Q 79.5 40.0 83.9 41.3 L 88.8 42.7 Q 90.0 43.0 89.3 44.0 L 86.8 47.6 Q 84.5 51.0 85.1 51.8 L 85.4 52.2 Q 86.0 53.0 84.9 53.3 L 73.7 56.7 Q 66.0 59.0 60.1 59.4 L 54.0 59.9 Q 52.0 60.0 51.7 61.3 L 51.4 62.2 Q 51.2 63.0 51.2 63.8 L 50.8 87.2 Q 50.8 88.0 50.1 88.0 L 49.9 88.0 Q 49.2 88.0 49.2 87.2 L 48.8 63.8 Q 48.8 63.0 48.6 62.2 L 48.3 61.3 Q 48.0 60.0 46.0 59.9 L 39.9 59.4 Q 34.0 59.0 26.3 56.7 L 15.1 53.3 Q 14.0 53.0 14.6 52.2 L 14.9 51.8 Q 15.5 51.0 13.2 47.6 L 10.7 44.0 Q 10.0 43.0 11.2 42.7 L 16.1 41.3 Q 20.5 40.0 16.8 34.1 L 11.6 26.0 Q 11.0 25.0 12.2 25.2 L 13.9 25.6 Q 16.0 26.0 16.4 22.2 L 16.9 18.2 Q 17.0 17.0 17.8 17.9 L 25.8 27.0 Q 28.5 30.0 29.1 27.9 L 29.7 26.1 Q 30.0 25.0 30.9 25.8 L 35.5 29.6 Q 39.5 33.0 38.3 26.1 L 36.7 16.7 Q 36.5 15.5 37.5 16.2 L 39.6 17.5 Q 41.8 19.0 42.1 15.0 L 42.4 10.7 Q 42.5 9.5 43.4 10.3 L 45.0 11.5 Q 46.8 13.0 48.1 9.2 L 49.6 5.1 Q 50.0 4.0 50.0 4.0 Z")
proof = [f'<circle cx="50" cy="44" r="46" fill="#F2EEE6"/>']
proof.append(f'<path d="{LEAF_D}" fill="{SLATE}" opacity="0.18"/>')
for v in OUTER:                                   # the leaf rays, from the leaf centre
    ang = ray_angle(v)
    q = pt(LC, ang, 30)
    proof.append(f'<line x1="50" y1="44" x2="{f(q[0])}" y2="{f(q[1])}" stroke="{MAROON}" '
                 f'stroke-width="1.4" stroke-dasharray="2 1.6" stroke-linecap="round"/>')
proof.append(f'<path d="{irregular_star_path(LC, 44, 30, 13)}" fill="none" '
             f'stroke="{NAVY}" stroke-width="1.4"/>')
for a, kind in TIPS:                               # mark short (leaf-ray) tips
    if kind == "S":
        o = pt(LC, a, 30)
        proof.append(f'<circle cx="{f(o[0])}" cy="{f(o[1])}" r="1.8" fill="{MAROON}"/>')
open(os.path.join(OUT, "star12-proof.svg"), "w").write(svg("".join(proof)))
print("wrote star12-proof.svg  (short tips = dashed leaf rays)")
