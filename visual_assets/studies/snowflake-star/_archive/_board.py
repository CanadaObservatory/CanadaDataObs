#!/usr/bin/env python3
"""Compose a contact board: each mark at large (on its own ground) + at 32/20px."""
import os
OUT = os.path.dirname(os.path.abspath(__file__))
OFFWH, NAVY = "#F7F4EE", "#17324D"

rows = [
    ("star13-dendrite-seal.svg", "13 — provinces + territories (seal)"),
    ("star11-canada-seal.svg",   "11 — polestar Canada + 10 provinces"),
    ("star10-dendrite-seal.svg", "10 — the provinces (seal)"),
    ("star13-compass-seal.svg",  "13 — compass star (seal)"),
    ("star11-compass.svg",       "11 — compass / observatory"),
    ("star13-dendrite-navy.svg", "13 — display register (navy/line)"),
    ("star13-cells.svg",         "13 — cells-colour hybrid (leaf lineage)"),
]

def inner(name):
    s = open(os.path.join(OUT, name)).read()
    return s.split(">", 1)[1].rsplit("</svg>", 1)[0]

W, RH = 760, 150
H = 60 + RH * len(rows)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif">']
out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
out.append(f'<text x="30" y="38" font-size="22" fill="{NAVY}" font-weight="700">CanObs · snowflake-star study</text>')
y = 60
for name, label in rows:
    g = inner(name)
    # large on light, large on navy, then small 36 and 22 on light
    out.append(f'<g transform="translate(30,{y+10})"><svg width="120" height="120" viewBox="0 0 100 100">{g}</svg></g>')
    out.append(f'<rect x="170" y="{y+10}" width="120" height="120" fill="{NAVY}"/>')
    out.append(f'<g transform="translate(170,{y+10})"><svg width="120" height="120" viewBox="0 0 100 100">{g}</svg></g>')
    out.append(f'<g transform="translate(320,{y+52})"><svg width="40" height="40" viewBox="0 0 100 100">{g}</svg></g>')
    out.append(f'<g transform="translate(375,{y+60})"><svg width="24" height="24" viewBox="0 0 100 100">{g}</svg></g>')
    out.append(f'<text x="420" y="{y+72}" font-size="16" fill="{NAVY}">{label}</text>')
    out.append(f'<text x="420" y="{y+94}" font-size="12" fill="#6B7280">{name}</text>')
    y += RH
out.append("</svg>")
open(os.path.join(OUT, "board.svg"), "w").write("\n".join(out))
print("wrote board.svg", W, H)
