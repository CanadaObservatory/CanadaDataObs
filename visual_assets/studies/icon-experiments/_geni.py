#!/usr/bin/env python3
"""Icon experiments (owner 2026-06-25), for consideration only — live favicon/ untouched.

The web-app (apple-touch) icon = full-bleed maroon square + the off-white LINE leaf at
stroke-width 5, scale 0.72. The favicon = the same leaf on a maroon DISC (sw 5, scale
0.78). The `outline/` leaf family is the SAME leaf path at sw 2.4. So "thinner line" and
"the outline of the leaf" are the same lever — stroke weight. Two boards:

  board_appicon — (A) line weight 5 / 4.2 / 3.5 / 2.4 on the maroon SQUARE; (B) the CELLS
                  leaf as the icon, on maroon / off-white / navy grounds.
  board_favicon — the leaf OUTLINE given the favicon workup at small sizes (disc + bare),
                  vs the current seal.

Files are written SHARP-cornered (like the live apple-touch.svg — iOS rounds them); the
boards round the corners so the preview matches the phone.
"""
import os
OUT = os.path.dirname(os.path.abspath(__file__))
MAROON, NAVY, OFFWH = "#7A263A", "#17324D", "#F7F4EE"

LEAF = ("M 50.0 4.0 Q 50.0 4.0 50.4 5.1 L 51.9 9.2 Q 53.2 13.0 55.0 11.5 L 56.6 10.3 "
        "Q 57.5 9.5 57.6 10.7 L 57.9 15.0 Q 58.2 19.0 60.4 17.5 L 62.5 16.2 Q 63.5 15.5 "
        "63.3 16.7 L 61.7 26.1 Q 60.5 33.0 64.5 29.6 L 69.1 25.8 Q 70.0 25.0 70.3 26.1 "
        "L 70.9 27.9 Q 71.5 30.0 74.2 27.0 L 82.2 17.9 Q 83.0 17.0 83.1 18.2 L 83.6 22.2 "
        "Q 84.0 26.0 86.1 25.6 L 87.8 25.2 Q 89.0 25.0 88.4 26.0 L 83.2 34.1 Q 79.5 40.0 "
        "83.9 41.3 L 88.8 42.7 Q 90.0 43.0 89.3 44.0 L 86.8 47.6 Q 84.5 51.0 85.1 51.8 "
        "L 85.4 52.2 Q 86.0 53.0 84.9 53.3 L 73.7 56.7 Q 66.0 59.0 60.1 59.4 L 54.0 59.9 "
        "Q 52.0 60.0 51.7 61.3 L 51.4 62.2 Q 51.2 63.0 51.2 63.8 L 50.8 87.2 Q 50.8 88.0 "
        "50.1 88.0 L 49.9 88.0 Q 49.2 88.0 49.2 87.2 L 48.8 63.8 Q 48.8 63.0 48.6 62.2 "
        "L 48.3 61.3 Q 48.0 60.0 46.0 59.9 L 39.9 59.4 Q 34.0 59.0 26.3 56.7 L 15.1 53.3 "
        "Q 14.0 53.0 14.6 52.2 L 14.9 51.8 Q 15.5 51.0 13.2 47.6 L 10.7 44.0 Q 10.0 43.0 "
        "11.2 42.7 L 16.1 41.3 Q 20.5 40.0 16.8 34.1 L 11.6 26.0 Q 11.0 25.0 12.2 25.2 "
        "L 13.9 25.6 Q 16.0 26.0 16.4 22.2 L 16.9 18.2 Q 17.0 17.0 17.8 17.9 L 25.8 27.0 "
        "Q 28.5 30.0 29.1 27.9 L 29.7 26.1 Q 30.0 25.0 30.9 25.8 L 35.5 29.6 Q 39.5 33.0 "
        "38.3 26.1 L 36.7 16.7 Q 36.5 15.5 37.5 16.2 L 39.6 17.5 Q 41.8 19.0 42.1 15.0 "
        "L 42.4 10.7 Q 42.5 9.5 43.4 10.3 L 45.0 11.5 Q 46.8 13.0 48.1 9.2 L 49.6 5.1 "
        "Q 50.0 4.0 50.0 4.0 Z")
OUTER = [(3.9, -39.1), (97.5, -38.3), (142.9, 24.2),
         (113.6, 114.6), (-12.3, 115.7), (-42.9, 24.2)]
WEDGE = ["#C2972F", "#17324D", "#2A7F9E", "#7A263A", "#3F6F5E", "#6B7280"]
_uid = [0]


def uid():
    _uid[0] += 1
    return f"c{_uid[0]}"


def line_leaf(stroke, sw):
    return (f'<path d="{LEAF}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="round"/>')


def cells_leaf():
    i = uid()
    d = f'<defs><clipPath id="{i}"><path d="{LEAF}"/></clipPath></defs>'
    d += f'<g clip-path="url(#{i})">'
    for k in range(6):
        x1, y1 = OUTER[k]
        x2, y2 = OUTER[(k + 1) % 6]
        d += f'<path d="M 50 44 L {x1} {y1} L {x2} {y2} Z" fill="{WEDGE[k]}"/>'
    for x, y in OUTER:
        d += f'<line x1="50" y1="44" x2="{x}" y2="{y}" stroke="{OFFWH}" stroke-width="1.6"/>'
    return d + "</g>"


# ---- shape BODIES (inner content, viewBox 0 0 100 100) ----------------------
def sq_line_body(sw, rx=0, scale=0.72):
    return (f'<rect width="100" height="100" rx="{rx}" fill="{MAROON}"/>'
            f'<g transform="translate(50,50) scale({scale}) translate(-50,-46)">'
            f'{line_leaf(OFFWH, sw)}</g>')


def sq_cells_body(ground, rx=0, scale=0.72):
    return (f'<rect width="100" height="100" rx="{rx}" fill="{ground}"/>'
            f'<g transform="translate(50,50) scale({scale}) translate(-50,-46)">'
            f'{cells_leaf()}</g>')


def disc_line_body(sw, scale=0.78):
    return (f'<circle cx="50" cy="50" r="47" fill="{MAROON}"/>'
            f'<g transform="translate(50,50) scale({scale}) translate(-50,-46)">'
            f'{line_leaf(OFFWH, sw)}</g>')


def bare_line_body(stroke, sw, scale=0.92):
    return (f'<g transform="translate(50,50) scale({scale}) translate(-50,-46)">'
            f'{line_leaf(stroke, sw)}</g>')


def svg(b):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            + b + "</svg>\n")


# ---- candidate files (sharp corners, like the live icons) -------------------
FILES = {
    "appicon-line-sw5.svg": sq_line_body(5),       # = current apple-touch
    "appicon-line-sw4.2.svg": sq_line_body(4.2),
    "appicon-line-sw3.5.svg": sq_line_body(3.5),
    "appicon-line-sw2.4.svg": sq_line_body(2.4),   # outline weight on the square
    # cells: only off-white kept (maroon/navy each eat their same-colour segment — dropped)
    "appicon-cells-offwhite.svg": sq_cells_body(OFFWH),
    "favicon-seal-sw5.svg": disc_line_body(5),     # = current favicon
    "favicon-outline-disc-sw2.4.svg": disc_line_body(2.4),
    "favicon-outline-bare-maroon.svg": bare_line_body(MAROON, 2.4),
}
for n, b in FILES.items():
    open(os.path.join(OUT, n), "w").write(svg(b))
    print("wrote", n)


# ---- boards ----------------------------------------------------------------
def card(x, y, s, body, bg=None):
    r = (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{max(2,s*0.16):.1f}" '
         f'fill="{bg}"/>') if bg else ""
    return r + f'<g transform="translate({x},{y}) scale({s/100})">{body}</g>'


def lab(x, y, t, fill="#17324D", size=12, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{t}</text>')


def board(fname, title, sections, sizes, W, rowh, big, cardbg=None):
    content = [lab(20, 30, title, size=16, weight="bold")]
    y = 56
    for hdr, rows in sections:
        content.append(lab(20, y, hdr, size=13, weight="bold"))
        y += 22
        for rlabel, body in rows:
            content.append(lab(20, y + big / 2, rlabel, size=11))
            x = 200
            for s in sizes:
                content.append(card(x, y + (big - s) / 2, s, body, cardbg))
                content.append(lab(x + s / 2, y + big + 12, f"{s}px", size=9,
                                   fill="#6B7280", anchor="middle"))
                x += s + 28
            y += rowh
        y += 16
    H = int(y + 10)
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">'
           f'<rect width="{W}" height="{H}" fill="white"/>' + "".join(content) + "</svg>")
    open(os.path.join(OUT, fname), "w").write(out)
    print("wrote", fname, "->", W, "x", H)


# app-icon: bodies with rounded corners (rx=22) to mimic the phone
board("board_appicon.svg",
      "Web-app icon experiments  (maroon square; corners rounded as on iOS)",
      [("A · Line weight   (current = 5;  the 'outline' family = 2.4)",
        [("sw 5  (current)", sq_line_body(5, rx=22)),
         ("sw 4.2", sq_line_body(4.2, rx=22)),
         ("sw 3.5", sq_line_body(3.5, rx=22)),
         ("sw 2.4  (outline)", sq_line_body(2.4, rx=22))]),
       ("B · Cells leaf as the icon   (which ground?)",
        [("on maroon  (maroon cell vanishes)", sq_cells_body(MAROON, rx=22)),
         ("on off-white", sq_cells_body(OFFWH, rx=22)),
         ("on navy", sq_cells_body(NAVY, rx=22))])],
      sizes=[140, 60, 40, 26], W=600, rowh=172, big=140)

board("board_favicon.svg",
      "Favicon workup — the leaf OUTLINE at small sizes  (vs the current seal)",
      [("Maroon disc  (browser-tab favicon context)",
        [("seal  sw 5  (current)", disc_line_body(5)),
         ("outline  sw 2.4", disc_line_body(2.4))]),
       ("Bare outline leaf  (maroon stroke, no disc)",
        [("outline  sw 2.4", bare_line_body(MAROON, 2.4))])],
      sizes=[64, 48, 32, 16], W=560, rowh=92, big=64, cardbg="#F4F2EC")
