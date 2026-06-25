#!/usr/bin/env python3
import os
OUT = os.path.dirname(os.path.abspath(__file__))
NAVY = "#17324D"
rows = [
    ("c13-alt-seal.svg", "13 — alternating long/short (seal)"),
    ("c11-alt-obs.svg", "11 — alternating, observatory"),
    ("c13-territories-seal.svg", "13 — 10 long provinces + 3 short territories"),
    ("c11-canada-seal.svg", "11 — long Canada point (north) + 10"),
    ("c11-sharp-seal.svg", "11 — deeper alternation, sharp"),
    ("c10-alt-obs.svg", "10 — provinces, observatory"),
    ("c13-alt-cells.svg", "13 — cells-colour compass (hybrid)"),
]
def inner(n):
    s = open(os.path.join(OUT, n)).read()
    return s.split(">", 1)[1].rsplit("</svg>", 1)[0]
W, RH = 760, 150
H = 60 + RH*len(rows)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#fff"/>',
     f'<text x="30" y="38" font-size="22" fill="{NAVY}" font-weight="700">CanObs · compass-star iteration 2</text>']
y = 60
for n, lab in rows:
    g = inner(n)
    o.append(f'<g transform="translate(30,{y+10})"><svg width="120" height="120" viewBox="0 0 100 100">{g}</svg></g>')
    o.append(f'<rect x="170" y="{y+10}" width="120" height="120" fill="{NAVY}"/>')
    o.append(f'<g transform="translate(170,{y+10})"><svg width="120" height="120" viewBox="0 0 100 100">{g}</svg></g>')
    o.append(f'<g transform="translate(320,{y+52})"><svg width="40" height="40" viewBox="0 0 100 100">{g}</svg></g>')
    o.append(f'<g transform="translate(375,{y+60})"><svg width="24" height="24" viewBox="0 0 100 100">{g}</svg></g>')
    o.append(f'<text x="420" y="{y+72}" font-size="16" fill="{NAVY}">{lab}</text>')
    o.append(f'<text x="420" y="{y+94}" font-size="12" fill="#6B7280">{n}</text>')
    y += RH
o.append("</svg>")
open(os.path.join(OUT, "board2.svg"), "w").write("\n".join(o))
print("wrote board2.svg")
