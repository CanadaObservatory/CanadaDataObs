#!/usr/bin/env python3
"""Iteration 3 — leaf -> star morph.

Insight: leaf-botanical-cells IS a 6-ray radial burst from centre C=(50,44),
CLIPPED to a leaf silhouette. Drop the clip and the leaf is already a 6-point
cells star. So the leaf can fade naturally into the compass star — same rays
(the 'shadow'), same six colours, same centre. The star's facet lines ARE the
leaf's skeleton rays.

Builds two filmstrips (cells / observatory) + standalone 'skeleton star' marks.
"""
import math, os
OUT = os.path.dirname(os.path.abspath(__file__))

MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"
LAKE, BOREAL, GOLD, SLATE, WHEAT = "#2A7F9E", "#3F6F5E", "#C2972F", "#6B7280", "#D9B36C"

# --- the leaf's own geometry (verbatim from leaf-botanical-cells.svg) ---
LEAF_D = ("M 50.0 4.0 Q 50.0 4.0 50.4 5.1 L 51.9 9.2 Q 53.2 13.0 55.0 11.5 L 56.6 10.3 "
 "Q 57.5 9.5 57.6 10.7 L 57.9 15.0 Q 58.2 19.0 60.4 17.5 L 62.5 16.2 Q 63.5 15.5 63.3 16.7 "
 "L 61.7 26.1 Q 60.5 33.0 64.5 29.6 L 69.1 25.8 Q 70.0 25.0 70.3 26.1 L 70.9 27.9 Q 71.5 30.0 74.2 27.0 "
 "L 82.2 17.9 Q 83.0 17.0 83.1 18.2 L 83.6 22.2 Q 84.0 26.0 86.1 25.6 L 87.8 25.2 Q 89.0 25.0 88.4 26.0 "
 "L 83.2 34.1 Q 79.5 40.0 83.9 41.3 L 88.8 42.7 Q 90.0 43.0 89.3 44.0 L 86.8 47.6 Q 84.5 51.0 85.1 51.8 "
 "L 85.4 52.2 Q 86.0 53.0 84.9 53.3 L 73.7 56.7 Q 66.0 59.0 60.1 59.4 L 54.0 59.9 Q 52.0 60.0 51.7 61.3 "
 "L 51.4 62.2 Q 51.2 63.0 51.2 63.8 L 50.8 87.2 Q 50.8 88.0 50.1 88.0 L 49.9 88.0 Q 49.2 88.0 49.2 87.2 "
 "L 48.8 63.8 Q 48.8 63.0 48.6 62.2 L 48.3 61.3 Q 48.0 60.0 46.0 59.9 L 39.9 59.4 Q 34.0 59.0 26.3 56.7 "
 "L 15.1 53.3 Q 14.0 53.0 14.6 52.2 L 14.9 51.8 Q 15.5 51.0 13.2 47.6 L 10.7 44.0 Q 10.0 43.0 11.2 42.7 "
 "L 16.1 41.3 Q 20.5 40.0 16.8 34.1 L 11.6 26.0 Q 11.0 25.0 12.2 25.2 L 13.9 25.6 Q 16.0 26.0 16.4 22.2 "
 "L 16.9 18.2 Q 17.0 17.0 17.8 17.9 L 25.8 27.0 Q 28.5 30.0 29.1 27.9 L 29.7 26.1 Q 30.0 25.0 30.9 25.8 "
 "L 35.5 29.6 Q 39.5 33.0 38.3 26.1 L 36.7 16.7 Q 36.5 15.5 37.5 16.2 L 39.6 17.5 Q 41.8 19.0 42.1 15.0 "
 "L 42.4 10.7 Q 42.5 9.5 43.4 10.3 L 45.0 11.5 Q 46.8 13.0 48.1 9.2 L 49.6 5.1 Q 50.0 4.0 50.0 4.0 Z")
LC = (50.0, 44.0)
OUTER = [(3.9, -39.1), (97.5, -38.3), (142.9, 24.2),
         (113.6, 114.6), (-12.3, 115.7), (-42.9, 24.2)]
COLORS = [GOLD, NAVY, LAKE, MAROON, BOREAL, SLATE]


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pt(c, a_deg, r):
    a = math.radians(a_deg)
    return (c[0] + r * math.sin(a), c[1] - r * math.cos(a))


# --- leaf interior (the burst), optionally clipped --------------------------
def burst(rays_len=None, ray_stroke=OFFWH, ray_w=1.6, fill=True):
    """The 6 cells wedges + 6 skeleton rays. rays_len overrides ray endpoints."""
    s = ""
    if fill:
        for i in range(6):
            a, b = OUTER[i], OUTER[(i + 1) % 6]
            s += (f'<path d="M{f(LC[0])} {f(LC[1])} L{f(a[0])} {f(a[1])} '
                  f'L{f(b[0])} {f(b[1])} Z" fill="{COLORS[i]}"/>')
    for a in OUTER:
        if rays_len is None:
            x2, y2 = a
        else:
            ang = math.atan2(a[0] - LC[0], -(a[1] - LC[1]))
            x2 = LC[0] + rays_len * math.sin(ang)
            y2 = LC[1] - rays_len * math.cos(ang)
        s += (f'<line x1="{f(LC[0])}" y1="{f(LC[1])}" x2="{f(x2)}" y2="{f(y2)}" '
              f'stroke="{ray_stroke}" stroke-width="{ray_w}" stroke-linecap="round"/>')
    return s


# --- generic compass star (cells or solid) ----------------------------------
def cells_star(N, c, long_r, short_r, rin, facet=OFFWH, facet_w=1.3, seed_angles=None):
    """N-point compass with each point a cells colour; white facet rays in valleys."""
    angs = seed_angles if seed_angles else [k * 360.0 / N for k in range(N)]
    s = ""
    for k in range(N):
        a = angs[k]
        a_l = a - 180.0 / N
        a_r = a + 180.0 / N
        R = long_r if k % 2 == 0 else short_r
        tip = pt(c, a, R)
        vl, vr = pt(c, a_l, rin), pt(c, a_r, rin)
        col = COLORS[k % 6]
        s += (f'<path d="M{f(tip[0])} {f(tip[1])}L{f(vr[0])} {f(vr[1])}'
              f'L{f(c[0])} {f(c[1])}L{f(vl[0])} {f(vl[1])}Z" fill="{col}"/>')
    for k in range(N):                       # facet rays = the skeleton
        a = angs[k] + 180.0 / N
        q = pt(c, a, rin)
        s += (f'<line x1="{f(c[0])}" y1="{f(c[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
              f'stroke="{facet}" stroke-width="{facet_w}" stroke-linecap="round"/>')
    s += f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="3" fill="{MAROON}"/>'
    s += f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="1.3" fill="{OFFWH}"/>'
    return s


def solid_star(N, c, long_r, short_r, rin, fill=NAVY, facet=OFFWH, facet_w=1.2):
    d = []
    for k in range(N):
        R = long_r if k % 2 == 0 else short_r
        o = pt(c, k * 360.0 / N, R)
        i = pt(c, (k + 0.5) * 360.0 / N, rin)
        d.append(("M" if k == 0 else "L") + f"{f(o[0])} {f(o[1])}")
        d.append(f"L{f(i[0])} {f(i[1])}")
    s = f'<path d="{"".join(d)}Z" fill="{fill}"/>'
    for k in range(N):                       # facet rays = the skeleton
        q = pt(c, k * 360.0 / N, (long_r if k % 2 == 0 else short_r) - 1.5)
        s += (f'<line x1="{f(c[0])}" y1="{f(c[1])}" x2="{f(q[0])}" y2="{f(q[1])}" '
              f'stroke="{facet}" stroke-width="{facet_w}" stroke-linecap="round"/>')
    s += f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="4" fill="{OFFWH}"/>'
    s += f'<circle cx="{f(c[0])}" cy="{f(c[1])}" r="1.6" fill="{fill}"/>'
    return s


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + body + "</svg>\n")


# === frames =================================================================
def frame_leaf(ghost=1.0):
    return svg(f'<defs><clipPath id="L"><path d="{LEAF_D}"/></clipPath></defs>'
               f'<g clip-path="url(#L)" opacity="{ghost}">{burst()}</g>')


def frame_breakout():
    """Leaf still filled, but the skeleton rays burst beyond the silhouette."""
    return svg(f'<defs><clipPath id="L2"><path d="{LEAF_D}"/></clipPath></defs>'
               f'<g clip-path="url(#L2)" opacity="0.5">{burst(fill=True, ray_w=0)}</g>'
               f'<path d="{LEAF_D}" fill="none" stroke="{SLATE}" stroke-width="0.6" opacity="0.5"/>'
               + burst(rays_len=47, ray_stroke=MAROON, ray_w=1.6, fill=False))


def frame_released():
    """Un-clipped to a disc: the 6-point cells burst that was always there."""
    return svg('<defs><clipPath id="D"><circle cx="50" cy="44" r="46"/></clipPath></defs>'
               f'<g clip-path="url(#D)">{burst()}</g>'
               f'<path d="{LEAF_D}" fill="none" stroke="{SLATE}" stroke-width="0.5" opacity="0.4"/>')


def frame_star6_cells():
    # 6-point cells star, all points equal (the leaf's own ray count), at LC
    return svg(cells_star(6, LC, 46, 46, 16))


def frame_star13_cells():
    return svg(cells_star(13, (50, 50), 47, 19, 11))


# observatory (navy) filmstrip on navy ground
def frame_leaf_navy():
    return (f'<defs><clipPath id="LN"><path d="{LEAF_D}"/></clipPath></defs>'
            f'<g clip-path="url(#LN)">{burst()}</g>')


def frame_skeleton_navy():
    """Just the 6 off-white skeleton rays on navy — the 'shadow' alone."""
    return burst(rays_len=44, ray_stroke=OFFWH, ray_w=2.0, fill=False) + \
        f'<circle cx="50" cy="44" r="3" fill="{OFFWH}"/>'


def frame_star6_navy():
    return solid_star(6, LC, 46, 46, 15, fill="none", facet=OFFWH, facet_w=2.0)


def frame_star13_navy():
    return solid_star(13, (50, 50), 46, 18, 10, fill=OFFWH, facet=NAVY, facet_w=1.0)


# === standalone marks worth keeping =========================================
standalone = {
    "skel-star6-cells.svg": frame_star6_cells(),
    "skel-star6-navy.svg": svg(f'<circle cx="50" cy="50" r="48" fill="{NAVY}"/>'
                               + solid_star(6, (50, 50), 44, 44, 14, fill="none",
                                            facet=OFFWH, facet_w=2.2)),
    "morph-star13-cells-facets.svg": frame_star13_cells(),
    "morph-star13-obs-facets.svg":
        svg(f'<circle cx="50" cy="50" r="47" fill="none" stroke="{WHEAT}" stroke-width="2"/>'
            + solid_star(13, (50, 50), 45, 18, 10, fill=NAVY, facet=OFFWH, facet_w=1.0)),
}
for name, data in standalone.items():
    open(os.path.join(OUT, name), "w").write(data)
    print("wrote", name)


# === filmstrip boards =======================================================
def strip(name, title, frames, bg):
    n = len(frames)
    cw, gap, pad = 150, 46, 30
    W = pad * 2 + cw * n + gap * (n - 1)
    H = 150
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{pad}" y="26" font-size="17" fill="{NAVY}" font-weight="700">{title}</text>']
    x = pad
    for i, (fr, cap) in enumerate(frames):
        o.append(f'<rect x="{x}" y="40" width="{cw}" height="{cw*0.66:.0f}" rx="6" fill="{bg}"/>')
        o.append(f'<g transform="translate({x+cw*0.17:.0f},42)"><svg width="{cw*0.66:.0f}" height="{cw*0.66:.0f}" viewBox="0 0 100 100">{fr}</svg></g>')
        o.append(f'<text x="{x+cw/2}" y="{40+cw*0.66+18:.0f}" font-size="11" fill="#6B7280" text-anchor="middle">{cap}</text>')
        if i < n - 1:
            ax = x + cw + gap / 2
            o.append(f'<text x="{ax}" y="{40+cw*0.33+4:.0f}" font-size="22" fill="{SLATE}" text-anchor="middle">→</text>')
        x += cw + gap
    o.append("</svg>")
    open(os.path.join(OUT, name), "w").write("\n".join(o))
    print("wrote", name, W, H)


strip("morph-cells.svg", "Leaf → cells compass star (the colours carry through)",
      [(frame_leaf(), "1 · the leaf"),
       (frame_breakout(), "2 · rays break out"),
       (frame_released(), "3 · un-clipped: a 6-point cells star"),
       (frame_star6_cells(), "4 · regularised 6-point"),
       (frame_star13_cells(), "5 · resampled to 13")],
      "#ffffff")

strip("morph-obs.svg", "Leaf → observatory star (the skeleton becomes the facets)",
      [(frame_leaf_navy(), "1 · the leaf"),
       (frame_skeleton_navy(), "2 · the skeleton alone"),
       (frame_star6_navy(), "3 · 6-ray line star"),
       (frame_star13_navy(), "5 · resampled to 13")],
      NAVY)
