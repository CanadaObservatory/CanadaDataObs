# Colour theory for the 17-country comparator palette — research overview

**Date:** 2026-06-21 · **Branch:** `site-review-2026-06` · synthesised from six commissioned research briefs.

## The problem this addresses

Canada Observatory needs **~17 fixed categorical identity colours** for comparator
countries — **Canada = maroon (locked)**, **US = blue (locked)**, plus 15 OECD peers —
shown mostly as **thin lines on a white background**, **colour-blind-safe**
(deuteranopia/protanopia the priority), in a **restrained "civic" register**. Our
current method is **max-min search over CIEDE2000 distance with Machado-2009 CVD
simulation**. 17 exceeds the **~8–12 simultaneously-distinguishable ceiling**, so some
hue families must repeat and a few pairs land too similar. We have a grey-until-the-
reader-activates-it UI (`_includes/peer-legend-colours.html`, `meta.fixedColor`) that
means clashes only ever appear between two countries a reader deliberately co-shows.

**Headline finding (all six briefs agree):** our pipeline already *is* the
state-of-the-art recipe. The literature (Glasbey, qualpalr, Colorgorical, Petroff)
packages it better and offers four concrete, low-risk upgrades — change the optimisation
*space*, fold CVD into the *objective* (not a post-hoc check), use *lightness* as the
disambiguating channel, and stop trying to make all 17 distinct at once.

---

## 1. How colour and colour-difference are defined

### Colour spaces (where to measure distance)

| Space | What it is | Verdict for us |
|---|---|---|
| **sRGB / HSL / HSV** | Device/intuitive spaces | **Never** measure distinctness here — distance ≠ perception; HSL can't hold constant visual weight. |
| **CIELAB / CIELCh** | The familiar perceptual default; newsroom & Tableau-10 working space | OK as a working space, but **non-uniform in the blue region** — it over/understates differences exactly where our 17 lines crowd. This is why CIEDE2000 exists as a patch. |
| **CAM02-UCS / CAM16-UCS** (Luo & Li) | Colour-appearance-model uniform space (J′a′b′); Euclidean ΔE′ ≈ perceived difference | **Recommended optimisation space.** Fitted across *both* large and small differences, so equal Euclidean steps = equal perceived difference everywhere — exactly what a max-min search needs. Used by viridis and glasbey. |
| **DIN99d** | Another uniform space | qualpalr's default; more uniform than Lab; fine alternative to CAM02-UCS. |
| **OKLab / OKLCH** (Ottosson 2020) | Pragmatic CSS-native uniform space | **Best for *nudging*** — fixes CIELAB's blue-purple hue drift, hue-stable interpolation, perceptually-even L/C/H steps. Slightly less validated for difference *magnitude* than CAM02-UCS. |
| Jzazbz / IPT / ICtCp | HDR/wide-gamut uniform spaces | Not needed for an sRGB civic site. |

### Colour-difference metrics

- **ΔE\*76** — plain CIELAB Euclidean. Badly non-uniform (over-weights blues). Avoid.
- **ΔE94, CIEDE2000 (ΔE00)** — corrections layered onto CIELAB. CIEDE2000 is the CIE
  standard pairwise metric (lightness/chroma/hue weighting + a blue-region hue-rotation
  term). **But:** it is *non-Euclidean and discontinuous* (not a true metric — it can
  break the triangle-inequality assumptions an optimiser relies on) and was **fitted to
  small, near-threshold differences**, so it gives diminishing returns at the *large*
  differences that separate categorical colours.
- **Euclidean ΔE′ in CAM02-UCS / CAM16-UCS** — the modern choice. Lives in the same
  uniform space the CVD simulation runs in, behaves as a true metric for max-min, and is
  valid across large and small differences.

> **Key upgrade:** move the distance computation out of CIEDE2000 and into **Euclidean
> ΔE′ in CAM02-UCS**, so the distance metric is *consistent with the space the Machado
> simulation runs in*. This is exactly Petroff (2021)'s choice (the matplotlib
> tol/petroff default cycles). A few lines via `colorspacious`.

### CVD (colour-vision-deficiency) models

- **Brettel 1997 / Viénot 1999** — dichromacy-only, interpolation-based. Older.
- **Machado, Oliveira & Fernandes 2009** — **the standard**, and what we already use.
  Physiologically motivated, models *anomalous trichromacy at graded severity 0–100*,
  per-type matrices (protan/deutan/tritan).
- **Critical implementation gotcha:** apply Machado/CVD matrices to **linear sRGB**
  (gamma-decode first), never gamma-encoded sRGB — a common bug that darkens and
  corrupts the simulation. Validate against **DaltonLens** reference code.

### The CVD-robust distance (Petroff's ΔE_cvd)

The single most important metric idea in the briefs:

```
ΔE_cvd(c1, c2) = min over {normal, protan, deutan, tritan}
                 AND over severities s ∈ {1..100}
                 of  ΔE′( sim_s(c1), sim_s(c2) )      # ΔE′ in CAM02-UCS
```

Then **maximise the minimum ΔE_cvd over all pairs**. Taking the **severity minimum**
matters: a pair can be safe at full dichromacy yet **collide at ~50 % severity**. We
currently risk missing exactly those mid-severity collisions. At minimum, check
**deutan + protan at severity ≈50 and ≈100**.

---

## 2. How colormaps are constructed — and what transfers to categorical

**Sequential/diverging perceptually-uniform colormaps** (viridis, magma, inferno,
plasma — Smith & van der Walt, built in CAM02-UCS with `viscm`) are made by laying a
path through a uniform space and enforcing two invariants:

1. **Monotonic lightness** (a clean J′ ramp), and
2. **Uniform perceptual spacing** (constant arc-length / constant ΔE per step).

- **cividis** (Nunez, Anderton & Renslow; `cmaputil`) adds CVD-optimisation: linearise
  lightness, simulate CVD, then minimise chroma/hue variation along the red-green
  confusion axis so a deuteranope and a normal viewer see almost the same image. **Its
  lever is keeping information on the blue–yellow axis** (preserved under red-green CVD)
  plus a monotone brightness ramp.
- **Moreland diverging** maps interpolate through a neutral midpoint in **Msh space**
  (polar CIELAB) to avoid Mach bands.
- **Kovesi ColorCET** equalises perceptual contrast (ΔE) along the whole map.

**What transfers to our categorical problem:**

- Measure distance in a **uniform space, after CVD simulation** — the cividis insight.
- **Lightness is the most CVD-robust separating channel** (red-green CVD collapses the
  a-axis but preserves lightness). This is *the* lever for our too-similar pairs.
- **Categorical inverts the sequential rule:** instead of *monotone* lightness you want
  *maximal spread* across lightness + hue + chroma — but **bound each axis to a band**
  for a harmonious, restrained register.

---

## 3. Algorithms & tools for maximally-distinct categorical palettes

### The core algorithm — greedy max-min (farthest-point), Glasbey et al. 2007

Discretise a perceptual space to a grid; iteratively **add the colour whose minimum
distance to all already-chosen colours is largest**. The worst pair governs categorical
legibility, so you optimise *that*. Deterministic given a seed; degrades gracefully as N
grows (first colours most distinct). Two refinements:

- For a **fixed N like 17**, greedy is order-dependent and front-loads quality — a
  **simulated-annealing / hill-climbing global pass** finds a better global optimum.
- Pure max-min **plateaus** once one worst pair is fixed. Use **lexicographic max-min**
  (fix worst pair, then 2nd-worst, …) or a **soft "energy" objective**
  (minimise Σ 1/ΔE_cvd^p) so the optimiser keeps improving secondary pairs.

### Hand-tuned vetted sets (use as seeds / sanity anchors, all CVD-safe, all ≤ ~9)

- **Okabe-Ito (8)** — scientific gold standard (Nature Methods, Wilke default).
  `#E69F00 #56B4E9 #009E73 #F0E442 #0072B2 #D55E00 #CC79A7 #000000`.
- **Paul Tol SRON** — `muted` (9): `#332288 #88CCEE #44AA99 #117733 #999933 #DDCC77
  #CC6677 #882255 #AA4499` (+ `#DDDDDD`); `bright` (7), `vibrant` (7), `high-contrast`
  (3). **`muted` is the closest off-the-shelf CVD-safe set to our size** and a strong
  tonally-restrained spine. <https://personal.sron.nl/~pault/>
- **Tableau 10/20** (Maureen Stone, CIELAB) — the canonical demonstration of
  **lightness-laddering**: the 20 is built as light/dark *pairs* of the 10, doubling the
  palette without new hues. The direct precedent for our 17-into-fewer-hues fix.
- **ColorBrewer** Set1/Set2/Dark2 — classic, but cap ~8–12, few CVD-safe.

### Generators (how each works + N=17 CVD-safe invocation)

| Tool | Mechanism | Run for N=17 |
|---|---|---|
| **`glasbey`** (lmcinnes, Python) — **best fit** | Greedy max-min in **CAM02-UCS**; native CVD mode does the max-min in a **CVD-simulated** space; **seed-and-extend** support | `glasbey.extend_palette(['#<maroon>','#1F77B4', …pinned], palette_size=17, colorblind_safe=True, cvd_type='deuteranomaly', cvd_severity=100, lightness_bounds=(35,75), chroma_bounds=(28,68))`. Re-run with `cvd_type='protanomaly'`; keep the set whose worst pair is best across both. Test `cvd_severity=50` too (sev 100 constrains choices, can hurt normal-vision distinctness). Bump `optimize_palette_search_radius≈50`. |
| **`qualpalr`** (R; JOSS) | Max-min in **DIN99d**, projects candidates into a **CVD-simulated subspace** first; native `metric='ciede2000'`, multi-type CVD, **`extend` seed hook**, HSL/LCHab bounds; `analyze_palette()` reports CIEDE2000 across normal + each CVD type | The published tool **closest to our exact pipeline** (CIEDE2000 + multi-type CVD + extend). Use as generator *and* independent cross-check. |
| **`colorcet`** glasbey_* (HoloViz) | Pre-baked 256-colour Glasbey maps: `glasbey`, `glasbey_bw`, `glasbey_dark` (L<70 removed for light bg), `glasbey_light`, `glasbey_cool/warm`, **`glasbey_category10`** (seeds Category10 then extends) | Take first 17, or use as a seed for `extend_palette`. `glasbey_category10` is a ready model for "keep fixed colours, extend distinctly". |
| **`distinctipy`** (Python) | Random-candidate farthest-point; `colorblind_type` re-scores in CVD space | `get_colors(17, exclude_colors=[…], colorblind_type='Deuteranomaly')`. Also `color_distance` / `simulate_colors` to audit our existing 17. |
| **Colorgorical** (Brown VRL; web + code) | Semi-random sampling scoring **CIEDE2000 distance + Name Difference + Name Uniqueness + Pair Preference** | Best when you want **discriminable *and* harmonious/nameable** — ideal for the **5 always-coloured comparators** (US/AUS/GER/UK/SWE) where nameability ("the orange one") matters. Sliders + hue-range + start-palette. <http://vrl.cs.brown.edu/color> |
| **`coloropt`** / Tsitsulin (Python) | Powell-method optimisation in LCHab over a multi-objective cost: distinctness (CIEDE2000) + greyscale separability + CVD separability (Tol transforms) + contrast vs black/white | Ships ready 6/12-colour sets with explicit **register bounds** (`normal`: C 50–75, L 40–75) that match a restrained civic tone. <http://tsitsul.in/blog/coloropt/> |
| **iwanthue** (medialab) | k-means or force-vector repulsion in CIELAB; built-in colorblind modes | Fast interactive exploration of constrained-gamut spreads. |
| **Palettailor** | Simulated annealing over point-distinctness + name-difference + class discrimination | Reference if we want preference-aware harmony beyond pure ΔE. |
| **Petroff 2021** sequences | Pre-derived 6/8/10 CVD-safe cycles (now matplotlib tol/petroff) | Caps at 10 — *informs* but doesn't *solve* 17. Concrete reusable params below. |

**Petroff concrete parameters to reuse:** min perceptual distance **20 / 18 / 16** for
6 / 8 / 10-colour sets; lightness **J′ ∈ [40, 84]** with min lightness spread
**ΔJ′ ≈ 3.6–5**; cap lightness below **~L\*84.6** (Smith & Szafir) so marker/line shape
stays legible and colours contrast with white.

---

## 4. Mixing & extending palettes

**Rule zero: interpolate/mix in Lab, OKLab, or LCh — never sRGB/HSL** (sRGB gives muddy,
dark, uneven midpoints).

- **Tints / shades / tones (laddering)** — the harmonious way to extend a hue family
  when 17 forces repeats. `chroma.scale([base]).mode('oklab').correctLightness().colors(k)`
  or `chroma.bezier([light, base, dark]).scale().colors(k)`: varies only lightness/chroma
  so the extension reads as a coherent family.
- **Blending two colormaps:** `chroma.average([a, b], 'lab')` per index, or
  `chroma.mix(c1, c2, t, 'oklab')`, or colorjs.io `new Color(a).range(b,{space:'oklch'})`.
- **ΔE-bounded sampling:** colorjs.io `range(...).steps({space:'oklch', maxDeltaE: D, steps: N})`
  lays out a family with guaranteed perceptual spacing.

### Runtime tools (JS)

- **chroma.js** — all the primitives: `chroma.deltaE(a,b)` (CIEDE2000), `distance(a,b,'lab')`,
  `.set('oklch.l','*1.15')`, `.set('lch.h','+18')`, `scale().mode().correctLightness()`,
  `bezier()`, `mix()`, `average()`. <https://gka.github.io/chroma.js/>
- **colorjs.io** — colour-science-grade `deltaE2000(a,b,{kL,kC,kH})`, `range/steps`
  with `maxDeltaE`, WCAG21 + APCA contrast. <https://colorjs.io/>
- **Adobe Leonardo** (`@adobe/leonardo-contrast-colors`) — an **orthogonal lever we're
  not using**: generate/adjust each colour by **target WCAG contrast ratio vs white**
  (e.g. ≥3:1) so every line is legible, with a colorblind-safe cycling toggle. Works in
  CAM02-UCS-polar / OKLCH / LCh. <https://leonardocolor.io/>

### Python primitives

- **`colorspacious`** — the single most directly-applicable library: `cspace_convert`
  with `sRGB1+CVD` (Machado 2009, `cvd_type` + `severity`) → convert to `CAM02-UCS` →
  Euclidean `deltaE`. Does **both** the CVD sim and the distance in one place. This *is*
  Petroff's pipeline.
- **`colour-science`** — `delta_E(method='CAM16-UCS')` if we move to the newer space;
  also CIEDE2000.

---

## 5. Editorial + artistic practice (what pros do past the ceiling)

**The decisive practitioner finding: no serious newsroom asks readers to tell 17
categorical colours apart at once.** Datawrapper/YouGov ship 6; IBM Carbon / Tableau cap
10–14; past ~12, identification error climbs steeply. The universal answer to
"categories > colour ceiling" is **don't colour them all simultaneously**:

1. **Highlight-one, rest-grey** (FT / John Burn-Murdoch: *"a line of red in a sea of grey
   stands out; if every line is a different colour nothing stands out"*). **Our
   grey-until-activated peer system is exactly this pattern** and is endorsed by every
   brief — it converts an unsolvable 17-distinct problem into a solvable ~6-distinct one.
2. **Direct labelling at line ends** instead of a legend (Economist house style) — a
   colour-independent, WCAG "don't-rely-on-colour-alone" backstop for activated lines.
3. **Small multiples / faceting** when comparisons matter.
4. **Order colours by salience** — style guides fix which colour is used for a 1-, 2-,
   3-series chart (IBM Carbon applies its sequence strictly to maximise neighbour
   contrast; reserves a 3.5:1 contrast floor).
5. **Lightness-ladder shades of fewer hues** rather than adding new hues.

### Artistic theory (the *why* behind lightness)

- **Munsell HVC** — hue, value (lightness), chroma are three *independent* perceptual
  axes. Distinctness is **3-dimensional**: a near-identical-hue pair can be separated in
  **value or chroma without changing hue family**. This is the key to fitting 17
  categories into ~10 hue slots.
- **Albers' "vibrating" colours** — two colours of **equal value** read as similar and
  fight the eye **even across different hues**. *Equal-value pairs are the real clash
  risk, not equal-hue pairs.* So the highest-leverage fix for a clash is a **ΔL move**.
- **Itten's seven contrasts** — light-dark and saturation contrast separate same-family
  hues; hue contrast alone saturates at ~10–12.
- **Harmony schemes** (complementary 180°, triadic 120°, tetradic, analogous) are a hue
  *placement* / coherence overlay — **not** a way to manufacture 17 distinct slots. Use
  them only as soft constraints *after* distinctness is satisfied.
- **Restrained "tonal" palette = bounded lightness+chroma, hue spread.** This is the
  painter's mechanism for "many distinct yet coherent" and the algorithmic input
  glasbey/qualpalr/coloropt expect. **Lines on white need dark-to-mid value, moderate
  chroma** — pastels and very-light/low-chroma colours vanish on white, which narrows the
  usable Munsell volume and intensifies the 17-into-fewer problem.

### Nameability

Colorgorical / the c3 model (on the XKCD colour-name survey): colours mapping to
**different, unique colour names** are more discriminable and memorable. Matters more for
the **5 always-coloured comparators** than the grey-until-clicked peers.

---

## 6. Concrete recommendations for our problem

Our **CIEDE2000 + Machado + max-min** pipeline is methodologically correct and matches
best practice. The upgrades below are refinements, ordered by leverage-per-effort.

### Tier 1 — do these (low risk, high evidence)

1. **Switch the distance metric to Euclidean ΔE′ in CAM02-UCS** (via `colorspacious`),
   so distance lives in the *same uniform space* the Machado simulation runs in. This is
   Petroff's choice and removes CIEDE2000's blue-region non-uniformity (exactly where our
   lines crowd) and its non-Euclidean/discontinuity issues as a max-min objective. Keep
   CIEDE2000 as a familiar reporting/fallback metric.
2. **Fold CVD into the *objective* as ΔE_cvd, not a post-hoc check.** Maximise the
   *minimum* ΔE′ taken over {normal, deutan, protan} **and over severities ≈50 and 100**.
   The severity minimum catches the mid-severity collisions we're currently missing.
   Verify the Machado matrices are applied to **linear sRGB**.
3. **Add line-on-white lightness constraints** as a *second separation channel*: cap
   lightness around **L\* 70–75** (hard ceiling ~84.6) and enforce a **minimum lightness
   spread** so the set also works in greyscale and survives CVD. Lightness is the
   CVD-robust axis (cividis insight).
4. **Lean explicitly on the grey-until-activated UI as the real escape hatch.** The
   binding requirement is distinctness among the *few lines shown at once*, not all 17.
   So: **guarantee maximal mutual separation for the 5 named comparators**
   (US/Australia/Germany/UK/Sweden), and **assign the legend / co-show ordering so
   frequently-co-shown comparators never share a hue family** — let the 11 toggle-on peers
   be the ones allowed to repeat hue families.

### Tier 2 — replace the bespoke generator (cross-check, likely better global optimum)

5. **Run `glasbey.extend_palette`** seeded with the locked colours:
   ```python
   import glasbey
   pal = glasbey.extend_palette(
       ['#<canada-maroon>', '#1F77B4'],   # + any other pinned comparators
       palette_size=17, colorblind_safe=True,
       cvd_type='deuteranomaly', cvd_severity=100,
       lightness_bounds=(35, 75), chroma_bounds=(28, 68))
   ```
   Re-run with `cvd_type='protanomaly'` and keep the set whose **worst-case (deutan∧protan)
   min-ΔE** is best; also test `cvd_severity=50`. The bounds enforce the civic register.
6. **Cross-check with `qualpalr`** (R) — the published tool closest to our exact stack
   (CIEDE2000 + multi-type CVD + `extend`). If glasbey and qualpalr agree on the worst
   pairs, we know they're structural, not artefacts.
7. **Greedy front-loads quality and plateaus.** For a fixed N=17, finish with a
   **global pass** — lexicographic max-min or simulated annealing / `optimize_palette`
   hill-climbing — and/or a **soft energy objective** (min Σ 1/ΔE_cvd^p) so secondary
   pairs keep improving.

### Tier 3 — nudge the last too-similar pairs (the direct ask)

8. **Separate them in VALUE first, chroma second, hue last** (Albers' equal-value rule;
   lightness is CVD-robust). A ΔL move buys distinctness in *both* normal and CVD space
   at once and is the cheapest move that doesn't break harmony.
9. **Laddering in OKLCH** with chroma.js / colorjs.io: hold the hue family, push one
   colour's lightness up and the other's down (or split chroma), keeping them "related but
   distinct". Re-check `deltaE2000` on **both** normal and Machado-simulated versions;
   target **ΔE ≈ 12–15 for thin lines** (below ~10 = confusable, especially under CVD);
   iterate to convergence. Use a **"harmony leash"** (max ΔE from the anchor hue) so
   colours stay in their intended family.
10. **Redundant encoding for the irreducible 1–2 pairs.** At N=17 > ceiling, no
    pure-colour solution keeps every pair safe. For the unavoidable clashes add a **second
    channel** (per-country line dash/marker) and/or rely on the grey-until-active UX so
    they seldom co-appear. This is mandatory, not optional (Wilke ch. 20).

### Tier 4 — optional polish

11. **Adobe Leonardo contrast pass** — regenerate/adjust so every line clears a **≥3:1
    contrast ratio vs white**; an axis orthogonal to mutual distinctness that guarantees
    legibility.
12. **Colorgorical nameability pass** for the 5 always-coloured comparators (raise Name
    Difference + Pair Preference) so they're verbally referable and harmonious.
13. **Validate on REAL thin lines on white** (at the actual ~1.5–3 px stroke width, not
    big swatches — small-area colour reads as lower chroma, Itten's contrast of extension)
    in **Viz Palette / Datawrapper's simulator / Color Oracle / Coblis**, under Machado
    deutan + protan. Render the full 17×17 ΔE matrix on the simulated colours; the headline
    metric is the **single smallest off-diagonal pair**.

### Can anything beat our CIEDE2000 max-min search?

**Not categorically — we're hand-rolling glasbey/qualpalr.** The wins are in *details*,
not a different paradigm:

- **Better space:** CAM02-UCS Euclidean ΔE′ > CIELAB+CIEDE2000 for our crowded blues
  (the one change with the best evidence).
- **Better objective:** CVD *in* the objective, severity-swept; lexicographic/energy
  instead of plain max-min so it doesn't plateau.
- **Better tooling:** glasbey's seed-and-extend + global optimiser likely finds a higher
  worst-case floor than a bespoke greedy loop, and qualpalr gives an independent check.
- **The real ceiling is mathematical:** 17 > ~8–12 means **2–3 pairs will always sit
  below threshold**, so the audit + redundant encoding + the grey-until-active UX are the
  actual solution. No colour algorithm escapes this — every generator's "colourblind-safe"
  only means it *maximised* separation under simulation, not that all pairs are safe.

### Note on the comparator stress-test (China/India for air-quality/climate)

Adding China/India only ever puts **1–2 extra simultaneously-shown series** on those
specific charts — well within the ~8–12 ceiling — so it does **not** threaten the system.
The hard legend-size/scroll constraint is **orthogonal to colour** and unaffected by any
of the above.

---

## Key sources

- Petroff (2021), *Accessible Color Sequences for Data Visualization* — <https://arxiv.org/abs/2107.02270>
- Glasbey et al. (2007), *Colour displays for categorical images* — <https://onlinelibrary.wiley.com/doi/10.1002/col.20327>
- Machado, Oliveira & Fernandes (2009), CVD model — <https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/Machado_Oliveira_Fernandes_CVD_Vis2009_final.pdf>
- Gramazio et al. (2016), *Colorgorical* — <https://vis.cs.brown.edu/docs/pdf/Gramazio-2016-CCD.pdf> · tool: <http://vrl.cs.brown.edu/color>
- Tsitsulin, *Optimal qualitative colour palettes* — <http://tsitsul.in/blog/coloropt/>
- `glasbey` — <https://glasbey.readthedocs.io/> · `qualpalr` — <https://cran.r-project.org/web/packages/qualpalr/>
- `colorspacious` — <https://colorspacious.readthedocs.io/> · `colour-science` — <https://colour.readthedocs.io/>
- `colorcet` categorical — <https://colorcet.holoviz.org/user_guide/Categorical.html>
- chroma.js — <https://gka.github.io/chroma.js/> · colorjs.io — <https://colorjs.io/> · Adobe Leonardo — <https://leonardocolor.io/>
- DaltonLens (CVD implementation gotchas) — <https://daltonlens.org/understanding-cvd-simulation/>
- Paul Tol SRON schemes — <https://personal.sron.nl/~pault/> · Tableau 10 — <https://www.tableau.com/blog/colors-upgrade-tableau-10-56782>
- Datawrapper newsroom palette guide — <https://www.datawrapper.de/blog/colors-for-data-vis-style-guides> · IBM Carbon — <https://carbondesignsystem.com/data-visualization/color-palettes/>
- Viz Palette — <https://projects.susielu.com/viz-palette>
