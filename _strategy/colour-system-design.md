# CanObs Colour System — Country & Province Categorical Palettes

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
| Code | Country | Tier | Hex |
|------|---------|------|-----|
| CAN | Canada | focal | `#7A263A` |
| USA | United States | focal | `#1B517D` |
| DEU | Germany | focal | `#5F916F` |
| AUS | Australia | focal | `#B17C11` |
| GBR | United Kingdom | focal | `#9C84D2` |
| SWE | Sweden | focal | `#208486` |
| JPN | Japan | tail | `#DF6C7A` |
| FRA | France | tail | `#4E7EAE` |
| ITA | Italy | tail | `#446F20` |
| KOR | South Korea | tail | `#944E98` |
| NLD | Netherlands | tail | `#D1804F` |
| CHE | Switzerland | tail | `#964A27` |
| NOR | Norway | tail | `#1496C3` |
| DNK | Denmark | tail | `#9E6685` |
| FIN | Finland | tail | `#695B9C` |
| ISR | Israel | tail | `#726F3B` |
| NZL | New Zealand | tail | `#35633D` |

### Provinces & territories
| Code | Province / Territory | Theme | Priority | Hex |
|------|----------------------|-------|----------|-----|
| ON | Ontario | terracotta | yes | `#C95A40` |
| QC | Quebec | cobalt | yes | `#0079D1` |
| BC | British Columbia | spruce | yes | `#2C600A` |
| AB | Alberta | wheat-gold | yes | `#BF8629` |
| NS | Nova Scotia | sea-teal | yes | `#419489` |
| MB | Manitoba | russet-earth | — | `#793F3C` |
| SK | Saskatchewan | ochre-clay | — | `#945F23` |
| NB | New Brunswick | petrol-green | — | `#017953` |
| NL | Newfoundland & Labrador | deep-blue-teal | — | `#016B6D` |
| PE | Prince Edward Island | aqua | — | `#08A1C1` |
| YT | Yukon | slate | — | `#596F7B` |
| NT | Northwest Territories | arctic-blue-grey | — | `#8195AB` |
| NU | Nunavut | violet-grey | — | `#6B6197` |

### Verification (CIEDE2000, Machado-2008 CVD, severity 1.0)
- **Focal-6 mutual** (all 15 pairs): normal **16.2**, deuteranopia **16.1**, protanopia **16.2** (all ≥ 15 ✅)
- **Provinces-13 mutual** (78 pairs), normal vision: **15.0** (worst QC–YT) — all ≥ 15 ✅
- **Province map-adjacency** (17 neighbour pairs) under CVD: deuteranopia **15.0**, protanopia **15.1** (all ≥ 15 ✅)
- **Tail-vs-focal**, normal vision: **15.2** (worst NLD–AUS) — ≥ 15 ✅
- **Line-legibility flags** (contrast <3:1, near-black, grey-collision): **0** ✅

---

## ALTERNATIVE — “Cartographic-earth”

A deliberately different country treatment for a real choice: Sweden becomes an
**olive-gold**, Australia a warmer **terracotta-orange**, the UK a **magenta-plum**,
Germany a **petrol-teal**. Warmer, more ColorBrewer/cartographic feel. Provinces use
a more muted register (deep-navy Quebec, muted-brick Ontario). Also fully passes.

### Countries
| Code | Country | Tier | Hex |
|------|---------|------|-----|
| CAN | Canada | focal | `#7A263A` |
| USA | United States | focal | `#145A84` |
| DEU | Germany | focal | `#1C7973` |
| AUS | Australia | focal | `#D37C6A` |
| GBR | United Kingdom | focal | `#C96BAF` |
| SWE | Sweden | focal | `#837800` |
| JPN | Japan | tail | `#BB4D5D` |
| FRA | France | tail | `#1A98E0` |
| ITA | Italy | tail | `#24874D` |
| KOR | South Korea | tail | `#8A51A3` |
| NLD | Netherlands | tail | `#BD8A3B` |
| CHE | Switzerland | tail | `#91584A` |
| NOR | Norway | tail | `#069EBD` |
| DNK | Denmark | tail | `#9F5F72` |
| FIN | Finland | tail | `#6868B2` |
| ISR | Israel | tail | `#547040` |
| NZL | New Zealand | tail | `#03A384` |

### Provinces & territories
| Code | Province / Territory | Theme | Priority | Hex |
|------|----------------------|-------|----------|-----|
| ON | Ontario | terracotta | yes | `#BD7366` |
| QC | Quebec | cobalt | yes | `#035096` |
| BC | British Columbia | spruce | yes | `#2D600D` |
| AB | Alberta | wheat-gold | yes | `#B88D17` |
| NS | Nova Scotia | sea-teal | yes | `#479388` |
| MB | Manitoba | russet-earth | — | `#773D3A` |
| SK | Saskatchewan | ochre-clay | — | `#99602C` |
| NB | New Brunswick | petrol-green | — | `#037853` |
| NL | Newfoundland & Labrador | deep-blue-teal | — | `#006B6D` |
| PE | Prince Edward Island | aqua | — | `#02A1BF` |
| YT | Yukon | slate | — | `#5C6E7E` |
| NT | Northwest Territories | arctic-blue-grey | — | `#85969F` |
| NU | Nunavut | violet-grey | — | `#7D699A` |

### Verification (CIEDE2000, Machado-2008 CVD, severity 1.0)
- **Focal-6 mutual** (all 15 pairs): normal **22.5**, deuteranopia **15.0**, protanopia **15.5** (all ≥ 15 ✅)
- **Provinces-13 mutual** (78 pairs), normal vision: **15.0** (worst QC–YT) — all ≥ 15 ✅
- **Province map-adjacency** (17 neighbour pairs) under CVD: deuteranopia **15.1**, protanopia **15.1** (all ≥ 15 ✅)
- **Tail-vs-focal**, normal vision: **15.2** (worst DNK–GBR) — ≥ 15 ✅
- **Line-legibility flags** (contrast <3:1, near-black, grey-collision): **0** ✅

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
