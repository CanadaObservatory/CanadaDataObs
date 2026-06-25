#!/usr/bin/env python3
"""Iteration 2 — compass-star family only.

Feedback: dendrite reads as a cluttered 'sun'. Keep the compass/observatory
direction; break the sunburst by giving points ALTERNATING lengths (long/short),
and add radial facet lines (the leaf's 'shadow' rays) so it reads as a compass
rose, not a sun. Cells-colour hybrid kept as a coloured compass.
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"
CELLS6 = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]
C = (50.0, 50.0)


def pt(c, a_deg, r):
    a = math.radians(a_deg)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def star_polygon(radii, rin):
    """Continuous star outline: N outer vertices (radii[k] at angle k*360/N),
    N inner valley vertices at rin between them. Returns path 'd'."""
    N = len(radii)
    d = []
    for k in range(N):
        a_out = k * 360.0 / N
        a_in = (k + 0.5) * 360.0 / N
        o = pt(C, a_out, radii[k])
        i = pt(C, a_in, rin)
        d.append(("M" if k == 0 else "L") + f"{f(o[0])} {f(o[1])}")
        d.append(f"L{f(i[0])} {f(i[1])}")
    return "".join(d) + "Z"


def facet_lines(radii, stroke, w, r0=0.0):
    """Radial division lines centre->tip (the leaf 'shadow' rays) = compass facets."""
    N = len(radii)
    out = []
    for k in range(N):
        a = k * 360.0 / N
        p, q = pt(C, a, r0), pt(C, a, radii[k] - 1.5)
        out.append(f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" '
                   f'y2="{f(q[1])}" stroke="{stroke}" stroke-width="{w}" '
                   f'stroke-linecap="round"/>')
    return "".join(out)


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + body + "</svg>\n")


def disc(fill=MAROON, r=48):
    return f'<circle cx="50" cy="50" r="{r}" fill="{fill}"/>'


def hub(fill, r=4.2, ring=None, rw=1.4):
    s = f'<circle cx="50" cy="50" r="{r}" fill="{fill}"/>'
    if ring:
        s = f'<circle cx="50" cy="50" r="{r+1.6}" fill="none" stroke="{ring}" stroke-width="{rw}"/>' + s
    return s


# ---- radius patterns -------------------------------------------------------
def alternating(N, long_r, short_r, short_idx=None):
    """short_idx = explicit set of short points; else alternate by parity."""
    if short_idx is None:
        return [short_r if k % 2 else long_r for k in range(N)]
    return [short_r if k in short_idx else long_r for k in range(N)]


# ---- builders --------------------------------------------------------------
def compass_seal(radii, rin, facet_w=1.1):
    """Off-white star on maroon disc; maroon facet rays show the disc through."""
    body = disc(MAROON)
    body += f'<path d="{star_polygon(radii, rin)}" fill="{OFFWH}"/>'
    body += facet_lines(radii, MAROON, facet_w)
    body += hub(MAROON, r=3.0)
    body += f'<circle cx="50" cy="50" r="1.3" fill="{OFFWH}"/>'
    return svg(body)


def compass_light(radii, rin, fill=NAVY, ring=WHEAT, facet=OFFWH, facet_w=1.0):
    body = ""
    if ring:
        body += f'<circle cx="50" cy="50" r="47" fill="none" stroke="{ring}" stroke-width="2"/>'
    body += f'<path d="{star_polygon(radii, rin)}" fill="{fill}"/>'
    body += facet_lines(radii, facet, facet_w)
    body += hub(OFFWH, r=4.0)
    body += f'<circle cx="50" cy="50" r="1.6" fill="{fill}"/>'
    return svg(body)


def compass_cells(radii, rin):
    """Each point filled with its area colour (leaf-cells lineage)."""
    N = len(radii)
    body = f'<circle cx="50" cy="50" r="48" fill="{OFFWH}"/>'
    for k in range(N):
        a_out = k * 360.0 / N
        a_l = (k - 0.5) * 360.0 / N
        a_r = (k + 0.5) * 360.0 / N
        tip = pt(C, a_out, radii[k])
        vl = pt(C, a_l, rin)
        vr = pt(C, a_r, rin)
        col = CELLS6[k % len(CELLS6)]
        d = f"M{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}L50 50L{f(vl[0])} {f(vl[1])}Z"
        body += f'<path d="{d}" fill="{col}"/>'
    body += f'<circle cx="50" cy="50" r="3.2" fill="{MAROON}"/>'
    body += f'<circle cx="50" cy="50" r="1.4" fill="{OFFWH}"/>'
    return svg(body)


# ---- the set ---------------------------------------------------------------
files = {
    # 13 alternating long/short, seal
    "c13-alt-seal.svg": compass_seal(alternating(13, 46, 24), rin=15),
    # 11 alternating, observatory (navy + wheat ring)
    "c11-alt-obs.svg": compass_light(alternating(11, 46, 25), rin=15),
    # 13 = 10 long provinces + 3 short territories (north: top three points)
    "c13-territories-seal.svg":
        compass_seal(alternating(13, 46, 26, short_idx={0, 1, 12}), rin=15),
    # 11 = a long Canada point at top (north) + 10 (alternating below)
    "c11-canada-seal.svg":
        compass_seal([48] + [24 if k % 2 else 40 for k in range(1, 11)], rin=15),
    # 13 alternating cells-colour compass (hybrid kept)
    "c13-alt-cells.svg": compass_cells(alternating(13, 46, 26), rin=14),
    # deeper alternation (short = 40%) for a sharper compass-rose read, 11 seal
    "c11-sharp-seal.svg": compass_seal(alternating(11, 47, 19), rin=12),
    # 10 alternating, observatory
    "c10-alt-obs.svg": compass_light(alternating(10, 46, 24), rin=14),
}

for name, data in files.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)

# ---- iteration 2b: sharper alternation to fully de-sun the 13s -------------
extra = {
    "c13-sharp-seal.svg": compass_seal(alternating(13, 47, 17), rin=10),
    "c13-sharp-obs.svg": compass_light(alternating(13, 46, 18), rin=10),
    "c13-sharp-cells.svg": compass_cells(alternating(13, 47, 19), rin=10),
    "c13-territories-sharp.svg":
        compass_seal(alternating(13, 47, 18, short_idx={0, 1, 12}), rin=11),
}
for name, data in extra.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)
