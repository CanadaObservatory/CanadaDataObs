#!/usr/bin/env python3
"""Generator for the snowflake-star study (CanObs).

Builds an N-pointed mark whose arms are drawn as snowflake dendrites — a
generalization of the radial ray-burst that threads `leaf-botanical-cells`
(six off-white rays from the centre C). Point count is symbolic:
  10 = the provinces
  11 = the polestar (Canada) + 10 provinces
  13 = 10 provinces + 3 territories
"""
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# --- palette (from brand/palette.md) ---
MAROON  = "#7A263A"
NAVY    = "#17324D"
OFFWH   = "#F7F4EE"
LAKE    = "#2A7F9E"
BOREAL  = "#3F6F5E"
GOLD    = "#C2972F"
SLATE   = "#6B7280"
WHEAT   = "#D9B36C"
CELLS6  = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]  # the cells-leaf wedge order

C = (50.0, 50.0)


def pt(c, a_deg, r):
    a = math.radians(a_deg)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def seg(p, q, stroke, w, extra=""):
    return (f'<line x1="{f(p[0])}" y1="{f(p[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
            f'stroke="{stroke}" stroke-width="{w}" stroke-linecap="round"{extra}/>')


def dendrite_arm(c, a, R, r0=5.0, branches=((0.5, 0.24), (0.74, 0.16)),
                 term=0.13, bangle=60.0):
    """Return segment list (p,q) for one frost-fern arm pointing at angle a."""
    segs = []
    tip = pt(c, a, R)
    base = pt(c, a, r0)
    segs.append((base, tip))                       # spine
    for frac, lw in branches:                      # paired side spurs (hex 60deg)
        bp = pt(c, a, r0 + frac * (R - r0))
        for s in (+1, -1):
            segs.append((bp, pt(bp, s * bangle, R * lw)))
    for s in (+1, -1):                             # terminal fork
        segs.append((tip, pt(tip, s * bangle, R * term)))
    return segs


def svg(body, vb=100):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb} {vb}">\n'
            + body + "\n</svg>\n")


def disc(r=48, fill=MAROON):
    return f'<circle cx="50" cy="50" r="{r}" fill="{fill}"/>'


# ---------------------------------------------------------------- builders

def star_dendrite(N, stroke, w, R=39.0, r0=5.0, on_disc=None,
                  short=(), short_R=0.78, drop_lower=()):
    """N dendrite arms, top-first clockwise. `short`/`drop_lower` = arm indices
    rendered as smaller 'territory' arms."""
    parts = []
    if on_disc:
        parts.append(disc(fill=on_disc))
    for k in range(N):
        a = k * 360.0 / N
        rr = R * short_R if k in short else R
        br = ((0.5, 0.24),) if k in drop_lower else ((0.5, 0.24), (0.74, 0.16))
        for p, q in dendrite_arm(C, a, rr, r0=r0, branches=br):
            parts.append(seg(p, q, stroke, w))
    # small nucleus ring at centre
    parts.append(f'<circle cx="50" cy="50" r="2.6" fill="none" '
                 f'stroke="{stroke}" stroke-width="{w}"/>')
    return svg("".join(parts))


def northstar_path(c, R, rin, fill):
    p = pt(c, 0, R)
    d = [f"M{f(p[0])} {f(p[1])}"]
    d.append(f"L{f(c[0]+rin*0.55)} {f(c[1]-rin*0.55)}")
    # simple 4-point polestar reused from mark-northstar, scaled
    pts = [(0, R), (45, rin), (90, R), (135, rin),
           (180, R), (225, rin), (270, R), (315, rin)]
    d = []
    for i, (ang, rr) in enumerate(pts):
        x, y = pt(c, ang, rr)
        d.append(("M" if i == 0 else "L") + f"{f(x)} {f(y)}")
    d.append("Z")
    return f'<path d="{"".join(d)}" fill="{fill}"/>'


def star_canada_centre(N, stroke, w, R=39.0, on_disc=MAROON):
    """11 reading: polestar nucleus (Canada) + N province dendrite arms."""
    parts = [disc(fill=on_disc)]
    for k in range(N):
        a = k * 360.0 / N
        for p, q in dendrite_arm(C, a, R, r0=8.5):
            parts.append(seg(p, q, stroke, w))
    parts.append(northstar_path(C, 9.5, 3.4, stroke))   # the polestar = Canada
    return svg("".join(parts))


def compass_star(N, R=46.0, rin=18.0, fill=NAVY, ring=None):
    """Filled N-point compass/observatory star — survives small sizes."""
    d = []
    for k in range(N):
        a_out = k * 360.0 / N
        a_in = (k + 0.5) * 360.0 / N
        o = pt(C, a_out, R)
        i = pt(C, a_in, rin)
        d.append(("M" if k == 0 else "L") + f"{f(o[0])} {f(o[1])}")
        d.append(f"L{f(i[0])} {f(i[1])}")
    d.append("Z")
    parts = []
    if ring:
        parts.append(f'<circle cx="50" cy="50" r="47" fill="none" stroke="{ring}" stroke-width="2"/>')
    parts.append(f'<path d="{"".join(d)}" fill="{fill}"/>')
    parts.append(f'<circle cx="50" cy="50" r="6.5" fill="{OFFWH}"/>')
    parts.append(f'<circle cx="50" cy="50" r="2.4" fill="{fill}"/>')
    return svg("".join(parts))


def star_cells(N, R=42.0, r0=4.0):
    """Hybrid: N rays carrying the cells palette (lineage of the leaf)."""
    parts = [f'<circle cx="50" cy="50" r="48" fill="{OFFWH}"/>']
    for k in range(N):
        a = k * 360.0 / N
        col = CELLS6[k % len(CELLS6)]
        for p, q in dendrite_arm(C, a, R, r0=r0, branches=((0.55, 0.2),)):
            parts.append(seg(p, q, col, 2.4))
    parts.append(f'<circle cx="50" cy="50" r="3.2" fill="{MAROON}"/>')
    return svg("".join(parts))


# ---------------------------------------------------------------- write set
files = {
    # 13 = 10 provinces + 3 territories (the "ideal"): 3 top arms = smaller north
    "star13-dendrite-seal.svg":
        star_dendrite(13, OFFWH, 2.0, on_disc=MAROON,
                      short=(0, 1, 12), drop_lower=(0, 1, 12)),
    # 13 uniform, display register (navy line on off-white) — equal-members read
    "star13-dendrite-navy.svg":
        star_dendrite(13, NAVY, 2.2, on_disc=None, R=42),
    # 11 = polestar (Canada) + 10 provinces
    "star11-canada-seal.svg":
        star_canada_centre(10, OFFWH, 2.0),
    # 10 = the provinces
    "star10-dendrite-seal.svg":
        star_dendrite(10, OFFWH, 2.2, on_disc=MAROON, R=40),
    # 11 compass/observatory star, navy on off-white (small-size survivor)
    "star11-compass.svg":
        compass_star(11, ring=WHEAT),
    # 13 compass, maroon
    "star13-compass-seal.svg":
        compass_star(13, fill=OFFWH, rin=16, R=43,
                     ).replace(f'fill="{OFFWH}"/><path',
                               f'fill="{OFFWH}"/><path'),  # placeholder
    # 13 cells-colour hybrid (leaf lineage)
    "star13-cells.svg":
        star_cells(13),
}

# fix the maroon compass disc variant properly
files["star13-compass-seal.svg"] = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
    + disc(fill=MAROON)
    + compass_star(13, fill=OFFWH, rin=15.5, R=42).split(">", 1)[1].rsplit("</svg>", 1)[0]
    + "</svg>\n")

for name, data in files.items():
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(data)
    print("wrote", name)
