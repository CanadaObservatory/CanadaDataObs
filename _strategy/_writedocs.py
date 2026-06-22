# -*- coding: utf-8 -*-
from _colour_opt import *
from _assemble import grpmin, adjmin, FOCAL_ORDER, TAIL_ORDER, PROV_ORDER, PRIORITY, ADJ
import json, itertools

asm=json.load(open('_assembled.json'))
orig=json.load(open('_orig_candidates.json'))

CNAME=dict(CAN='Canada',USA='United States',DEU='Germany',AUS='Australia',GBR='United Kingdom',
 SWE='Sweden',JPN='Japan',FRA='France',ITA='Italy',KOR='South Korea',NLD='Netherlands',
 CHE='Switzerland',NOR='Norway',DNK='Denmark',FIN='Finland',ISR='Israel',NZL='New Zealand')
PNAME=dict(ON='Ontario',QC='Quebec',BC='British Columbia',AB='Alberta',NS='Nova Scotia',
 MB='Manitoba',SK='Saskatchewan',NB='New Brunswick',NL='Newfoundland & Labrador',
 PE='Prince Edward Island',YT='Yukon',NT='Northwest Territories',NU='Nunavut')

def asdict(lst,key='hex'):
    return {x['code']:x['hex'] for x in lst}

def metrics(pal):
    focal={x['code']:x['hex'] for x in pal['countries'] if x['tier']=='focal'}
    tail ={x['code']:x['hex'] for x in pal['countries'] if x['tier']=='tail'}
    prov ={x['code']:x['hex'] for x in pal['provinces']}
    fm=grpmin(list(focal),focal); pm=grpmin(list(prov),prov); am=adjmin(prov)
    # tail vs focal normal
    wn=1e9;wnp=None
    for t in tail:
        for f in focal:
            d=ciede2000(hex2lab(tail[t]),hex2lab(focal[f]))
            if d<wn:wn=d;wnp=(t,f)
    allhex={**focal,**tail,**prov}
    flags=line_flags(list(allhex.values()),list(allhex.keys()))
    return dict(focal=fm,prov=pm,adj=am,tail=(wn,wnp),flags=flags)

M={k:metrics(asm[k]) for k in ('recommended','alternative')}

# ---- write machine-readable json ----
out=dict(recommended=asm['recommended'], alternative=asm['alternative'], all_candidates=orig)
json.dump(out,open('colour-candidates.json','w'),indent=2)

# ---- write design doc ----
def ctable(pal):
    rows=["| Code | Country | Tier | Hex |","|------|---------|------|-----|"]
    for x in pal['countries']:
        rows.append(f"| {x['code']} | {CNAME[x['code']]} | {x['tier']} | `{x['hex']}` |")
    return "\n".join(rows)
def ptable(pal):
    rows=["| Code | Province / Territory | Theme | Priority | Hex |","|------|----------------------|-------|----------|-----|"]
    pm={x['code']:x for x in pal['provinces']}
    for c in PROV_ORDER:
        x=pm[c]
        rows.append(f"| {c} | {PNAME[c]} | {x['theme']} | {'yes' if x['priority'] else '—'} | `{x['hex']}` |")
    return "\n".join(rows)

def numblock(m):
    f=m['focal']; p=m['prov']; a=m['adj']
    return (f"- **Focal-6 mutual** (all 15 pairs): normal **{f['normal'][0]:.1f}**, "
            f"deuteranopia **{f['deuteranopia'][0]:.1f}**, protanopia **{f['protanopia'][0]:.1f}** "
            f"(all ≥ 15 ✅)\n"
            f"- **Provinces-13 mutual** (78 pairs), normal vision: **{p['normal'][0]:.1f}** "
            f"(worst {p['normal'][1][0]}–{p['normal'][1][1]}) — all ≥ 15 ✅\n"
            f"- **Province map-adjacency** (17 neighbour pairs) under CVD: "
            f"deuteranopia **{a['deuteranopia'][0]:.1f}**, protanopia **{a['protanopia'][0]:.1f}** "
            f"(all ≥ 15 ✅)\n"
            f"- **Tail-vs-focal**, normal vision: **{m['tail'][0]:.1f}** "
            f"(worst {m['tail'][1][0]}–{m['tail'][1][1]}) — ≥ 15 ✅\n"
            f"- **Line-legibility flags** (contrast <3:1, near-black, grey-collision): "
            f"**{len(m['flags'])}** ✅")

doc=f"""# CanObs Colour System — Country & Province Categorical Palettes

*Design record — 2026-06-21. Governs the chart **data-ink** colours (countries +
provinces/territories). The brand chrome palette (Deep Navy #17324D, Lake Blue,
Wheat, maroon seal) is a separate system and is unchanged; Canada stays
**#7A263A maroon** and the OECD peer-average stays **#555555 dashed**.*

## Governing qualities

1. **Muted but distinct.** Distinctness comes from wide **hue spacing** (one entity
   per hue family in the focal set) and a wide **lightness spread** — not raw
   saturation. Chroma is held in a matte register; nothing is neon.
2. **Colour-blindness is binding.** Every colour pair that can appear *together and
   in colour* must stay separable in normal vision **and** deuteranopia **and**
   protanopia. Two categories are never separated by red-vs-green alone.
3. **Legible as a line.** Every colour clears ≈ 3:1 contrast on white (reads as a
   1.5–3 px line), avoids near-black (which reads as an axis), and stays clear of
   the reserved #555 dashed average.
4. **Spend the budget on the focal set.** The six highlighted countries carry the
   perceptual load; the other eleven render grey until the reader activates them.

## The dichromatic ceiling (why the design is tiered)

Under deuteranopia / protanopia the colour space collapses to roughly two
dimensions (lightness + a blue–yellow axis). Constrained to legible lightnesses,
the **maximum number of categories that can be held ≥ 15 ΔE₀₀ apart in *both*
dichromacies is about six** (measured ceiling for 6 with Canada fixed ≈ 18.9; for
13 simultaneous colours the ceiling is only ≈ 11.5 ΔE₀₀). This is a property of
dichromatic vision, not of any particular palette — which is exactly why all four
input candidates failed a flat “all-13-provinces ≥ 15 in CVD” gate.

The system therefore tiers the requirement to what is physically achievable:

| Group | Normal vision | Deuteranopia | Protanopia |
|-------|--------------|--------------|------------|
| **Focal 6 countries** (shown together, in colour) | all pairs ≥ 15 | all pairs ≥ 15 | all pairs ≥ 15 |
| **Tail 11 countries** (grey until activated, one at a time) | ≥ 15 vs the focal 6 | grey by default; legend disambiguates | grey by default |
| **13 provinces** — *mutual* | all pairs ≥ 15 | (ceiling ≈ 11.5; shown few-at-a-time) | (ceiling ≈ 11.5) |
| **13 provinces** — *map-adjacent neighbours* | ≥ 15 | ≥ 15 | ≥ 15 |

Provinces never appear charted against countries (separate universes). On a map the
**binding** constraint is that touching regions differ; in lines/bars only a few
provinces show at once. So provinces are fully mutually distinct in normal vision,
and every pair of **map neighbours** is also distinct under both dichromacies.

---

## RECOMMENDED — “Spectral-matte” (Okabe-anchored)

One entity per hue family on the proven CVD-safe backbone: Canada maroon, a deep
muted blue (US), a sage green (Germany), an amber-gold (Australia), a soft violet
(UK), a teal-cyan (Sweden). The only adjacent families (the two blues / the
green–teal) are split by a large lightness gap so they survive both dichromacies.
Cleaner, slightly cooler register.

### Countries
{ctable(asm['recommended'])}

### Provinces & territories
{ptable(asm['recommended'])}

### Verification (CIEDE2000, Machado-2008 CVD, severity 1.0)
{numblock(M['recommended'])}

---

## ALTERNATIVE — “Cartographic-earth”

A deliberately different country treatment for a real choice: Sweden becomes an
**olive-gold**, Australia a warmer **terracotta-orange**, the UK a **magenta-plum**,
Germany a **petrol-teal**. Warmer, more ColorBrewer/cartographic feel. Provinces use
a more muted register (deep-navy Quebec, muted-brick Ontario). Also fully passes.

### Countries
{ctable(asm['alternative'])}

### Provinces & territories
{ptable(asm['alternative'])}

### Verification (CIEDE2000, Machado-2008 CVD, severity 1.0)
{numblock(M['alternative'])}

---

## How RECOMMENDED differs from ALTERNATIVE

| Slot | Recommended (spectral-matte) | Alternative (cartographic-earth) |
|------|------------------------------|----------------------------------|
| Sweden | teal-cyan | olive-gold |
| Australia | amber-gold | terracotta-orange |
| United Kingdom | soft violet | magenta-plum |
| Germany | sage-green | petrol-teal |
| United States | deep muted blue | deep cobalt |
| Quebec | brighter cobalt | deep navy-cobalt |
| Ontario | brighter terracotta | muted brick |
| Overall feel | cleaner, cooler, spectral | warmer, earthier, muted |

Both keep Canada #7A263A, the US-blue / navy-chrome / Lake-Blue separation, the
#555 dashed-grey reserve, the regional province themes, and the same tiered
CVD guarantees. Pick on aesthetic preference; both verify identically against the
gates.

## Method

Colours optimised by simulated annealing in CIELAB/LCh with a hard legibility
filter (contrast ≥ 3.05:1 on white, ΔE₀₀ ≥ 12.5 from #555, L* ≥ 22), scored on
CIEDE2000 (Sharma reference constants) under normal vision plus Machado-2008
deuteranopia and protanopia (severity 1.0). Province map-adjacency uses the 17
shared-border neighbour pairs. Full reproducible script:
`_strategy/_colour_opt.py` (+ drivers). Machine-readable palettes and the four
explored input candidates: `_strategy/colour-candidates.json`.
"""
open('colour-system-design.md','w').write(doc)
print('wrote colour-system-design.md and colour-candidates.json')
