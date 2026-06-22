# How we chose the Canada Observatory chart colours

*A meta-story / design record — 2026-06-22. How a data site picks colours for 17
countries and 13 provinces when the human eye can only tell ~10 apart at once.*

---

## TL;DR

Canada Observatory compares Canada against 16 peer countries and across its own 13
provinces and territories — almost always as **lines on a white background**. We needed
a fixed, deliberate colour for each, **safe for colour-blind readers**, calm enough to
feel like one civic system rather than a default rainbow. The catch: **17 (or 13)
distinct colours is more than anyone can distinguish simultaneously** — the perceptual
ceiling is about 8–12. So the real design problem isn't "find 17 perfect colours"
(impossible); it's "manage a set bigger than the ceiling without it falling apart."

The result: a measured, colour-blind-tested palette with a **global minimum perceptual
distance of ΔE 15.7** (up from 12.1 in the old defaults), every colour legible as a thin
line on white (the old set failed that for 12 of 17), Canada in the brand maroon, and a
two-tier "focal + grey-until-activated" structure that keeps any single view under the
ceiling by construction.

---

## 1. The problem, precisely

Three lists need categorical colours:

- **Comparator countries — 17.** Canada plus 16 OECD peers, shown as overlapping time-series lines.
- **Provinces & territories — 13.** Lines (tuition, migration, crime…) and the occasional filled map.
- *(The six thematic brand areas and the sequential map scales were already solved and untouched.)*

Requirements, in priority order:

1. **Colour-blind safe.** ~8% of men have red–green colour-blindness; categories must
   never be told apart by red-vs-green alone, and should survive deuteranopia/protanopia.
2. **Legible as a thin line on white.** Pale or low-contrast colours vanish at 1.5–3 px on a white page.
3. **Distinct.** Each pair should be far enough apart to follow when several lines overlap.
4. **Coherent & restrained.** A sober "civic atlas" feel — not a saturated dashboard rainbow.
5. **Brand-aware, but separate.** Canada = the brand maroon; otherwise this is a *data-ink*
   system, deliberately distinct from the brand *chrome* palette (navy/lake/wheat).
6. **Cultural anchors where free.** Canada→red, US→blue read instantly; past those, flag
   colours collide or fail on white, so association is an anchor for two, not a rule for all.

## 2. Why a separate data-ink palette

The brand palette (Deep Navy, Lake Blue, Deep Maroon, Boreal, Prairie Gold…) is tuned for
*chrome* — navbar, headings, the seal — where contrast and mood matter more than mutual
distinctness. Data ink has the opposite job: many colours that must be told apart at a
glance. Forcing the eight brand colours to also serve as 17+ data colours would either
break distinctness or make charts look like the UI. So Canada keeps the brand maroon
(`#7A263A`) as its one shared anchor, and the rest is a purpose-built categorical system.

## 3. Background research: how colour and colour-difference are actually defined

We commissioned a six-part research sweep (full notes: `colour-theory-overview.md`). The
essentials:

- **Colour is three independent dials.** *Hue* (which colour), *lightness* (how light/dark),
  *chroma/saturation* (how vivid vs grey). The named "types" — pastel, muted, jewel, neon,
  earth — are just *regions* of the lightness × chroma plane. Pastel and muted are
  neighbours (both low chroma); they differ only in lightness.
- **Distance must be measured in a perceptual space.** RGB/hex spacing lies. The field
  measures colour difference with **CIEDE2000 (ΔE)** in CIELAB, or better, Euclidean
  distance in **CAM02-UCS** — uniform spaces where "twice the number means twice as
  different." We used CIEDE2000.
- **Colour-blindness is simulated, not guessed.** The **Machado (2009)** matrices model
  deuteranopia/protanopia at any severity; you transform a colour to how a colour-blind
  viewer sees it, *then* measure distance.
- **The ~8–12 ceiling is real and physical.** Every authoritative qualitative palette
  (Okabe-Ito's 8, Paul Tol's ≤9, ColorBrewer's ~12) stops there, because beyond it
  colours collide — worse under colour-blindness, at small sizes, and on thin lines.
- **The state of the art for "maximally distinct N colours"** is exactly a max–min search
  in a perceptual space with colour-blindness folded in — the **Glasbey** algorithm, and
  tools like **Colorgorical**, **i-want-hue**, and **qualpalr**. Reassuringly, that is the
  method we had already built by hand.
- **What professionals do past the ceiling:** highlight-a-few-and-grey-the-rest (FT, The
  Economist), direct labels, small multiples, and **redundant encoding** (line dash/marker),
  plus **lightness as the separation channel** — the trick Tableau used to stretch its 10
  colours to 20, and the one axis that *survives* colour-blindness.

## 4. The method

A deterministic optimiser (pure Python, fully reproducible) that:

1. Builds candidate colours in **LCh** within each entity's allowed hue/lightness/chroma box.
2. Filters to **line-legible on white** (contrast ≥ 3:1) and clear of the reserved grey average.
3. Scores any palette by its **worst pair**, where each pair's distance is the *minimum*
   CIEDE2000 across **normal, deuteranopia, and protanopia** vision (so a pair only counts
   as "safe" if it survives colour-blindness).
4. **Maximises that minimum** (a max–min / farthest-point search) with random restarts,
   local search, and targeted repair of the current worst pair.

We chose a deterministic solver over an AI/agent approach precisely because this is exact
numeric optimisation — the math, not a model, should place the colours.

## 5. The journey (and why each step happened)

| Stage | Global min ΔE (normal) | What changed |
|---|---|---|
| **v0 — defaults** | **12.1** | matplotlib *tab20*; Canada bright red; 12 of 17 too pale for lines; Denmark≈NZ identical under colour-blindness (ΔE 1.4) |
| First categorical solve | ~12.3 | purpose-built, line-legible, colour-blind-aware |
| Province finessing (v1→v8) | — | hand-tuned region themes; resolved Québec/Saskatchewan, BC/NB, NWT/Nunavut, PEI/Alberta, Yukon, Manitoba/NB clashes |
| Focal register + Japan | ~12.4 | per-country muted/deep choice; **Japan promoted to a 7th comparator**; green cluster reworked |
| Purple cluster push | **14.1** | Israel/Finland/Korea pulled off the UK's purple (UK held fixed) |
| **Capstone — global re-solve** | **15.7** | all ten "grey-until-active" peers re-placed at once → the best achievable set |

Two ideas unlocked the big gains, both from the owner:

- **Mix registers for distinctness.** Don't lock every focal country to one "muted" or
  "deep" register — pick whichever is more distinct from the peers. (Australia stayed muted
  gold to clear the warm tails; Japan and Germany went deep.)
- **It's lines, not maps — so use lightness.** Comparator maps would be mostly empty (peers
  are scattered worldwide), so we optimise for *lines*. That frees the **lightness** axis:
  a deep-navy Korea and a sky-blue Sweden are distinguishable *even though both are "blue,"*
  by lightness — which is also the axis that survives colour-blindness.

## 6. Key principles we proved out

- **17 > the ceiling is a wall, not a bug.** We demonstrated three ways (push tails off the
  focal hues → they clump together; move three at a time → they bounce back) that the last
  few collisions can only be *relocated*, never removed. The honest fix is structural.
- **Grey-until-activated is the real answer.** By default only Canada + a few comparators +
  the average show in colour; the rest are grey until the reader clicks them — so two
  similar colours never appear together unless deliberately summoned, and the legend labels
  them when they do. This is what every newsroom does, and it keeps every view under the ceiling.
- **Lightness is the colour-blind-robust lever.** Red–green colour-blindness collapses hue
  but preserves lightness; same-family pairs are separated by value.
- **Register by context, one identity.** Provinces carry three tonal registers of the *same*
  hue — **muted** (default lines), **deep** (moodier), **pastel** (map fills) — chosen by medium.
- **Pastel washes out as a line on white** (low contrast) but reads beautifully as a large
  map fill — hence the register split.
- **The "paint-on-glass" aesthetic** (the muted-but-luminous look the owner admired in the
  Maul animated series) needs a *dark* ground to glow; on our white charts the same colours
  read rich-but-flat, so that quality is filed for an optional dark "showcase" surface, not
  the charts themselves.

## 7. The locked palette

**Comparator countries.** Focal seven always shown in colour; Canada = brand maroon.

| Country | Hex | | Country | Hex |
|---|---|---|---|---|
| Canada | `#7A263A` maroon | | Japan | `#753803` bronze |
| United States | `#0650A3` deep blue | | *— other 10 peers (grey until selected) —* | |
| Australia | `#C77109` gold | | France `#AC4B3E` · Italy `#006B63` · S. Korea `#3279DF` | |
| Germany | `#0B6B2D` deep forest | | Netherlands `#776500` · Switzerland `#776EA3` | |
| United Kingdom | `#B06487` rose-mauve | | Norway `#AD924A` · Denmark `#708538` · Finland `#33A0A0` | |
| Sweden | `#249FD0` sky blue | | Israel `#F16458` · New Zealand `#11A876` | |

**Provinces & territories (muted / line register).** ON `#A0543F` · QC `#225490` ·
BC `#27613F` · AB `#C0923C` · NS `#2C7C8E` · NB `#31A182` · MB `#788741` · SK `#6F79C2` ·
NL `#8C3A57` · PE `#EAB196` · YT `#7C949C` · NT `#9E92B0` · NU `#7C5A74`. (Deep and pastel
registers in `colour-registers.json`.)

The peer average is `#555555` dashed.

## 8. How it compares to the old defaults

| | v0 (tab20 defaults) | New (locked) |
|---|---|---|
| Normal-vision min ΔE | 12.1 (Finland–Israel) | **15.7** (US–Korea) |
| Colour-blind worst-mode min ΔE | 1.4 (Denmark ≈ NZ) | **6.0** |
| Line-legible on white (≥3:1) | 5 of 17 | **17 of 17** |
| Canada | generic red `#d62728` | brand maroon `#7A263A` |
| Japan | grey tab20 tail | focal comparator |

## 9. Honest limits

The worst colour-blind pair is still ΔE ~6 — the **irreducible** cost of 17 colours past
the perceptual ceiling, not a fixable flaw. It is handled by (a) grey-until-active, so those
two never co-appear by default, and (b) the planned redundant encoding (a per-country line
dash/marker) for the one or two stubborn pairs if both are ever shown together.

## 10. If we revisit it

The research flagged refinements that would buy *certainty*, not a categorical leap (we're
near the ceiling at 15.7):

1. Measure distance in **CAM02-UCS** (via `colorspacious`) instead of CIELAB — fixes
   blue-region non-uniformity where our three blues crowd.
2. **Fold colour-blindness into the objective** over multiple severities (~50 and 100), not
   a single post-hoc check.
3. **Correctness:** apply the Machado matrices to *linear* sRGB (our solver used gamma sRGB —
   a known, small variance).
4. **Cross-check** with `glasbey.extend_palette` (seeded with locked Canada/US) and
   `qualpalr` — independent confirmation we're at the true optimum.

## Files

- `_strategy/colour-registers.json` — authoritative values (countries + province registers).
- `_strategy/colour-theory-overview.md` — the background research, in full.
- `pipeline/config.py` — wired in (`COMPARATOR_COLORS`, `PEER_EXTRA_COLORS`, `CANADA_COLOR`,
  `PROVINCE_COLORS*`).
- `visual_assets/studies/chart-palette/` — reference images: country & province line
  references, the Canada province map, the v0-vs-new comparison.
