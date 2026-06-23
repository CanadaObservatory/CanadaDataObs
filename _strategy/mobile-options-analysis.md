# Mobile Experience — Options Analysis & Plan

**Status:** analysis for owner review (2026-06-23). No code written yet.
**Scope:** how Canada Observatory's interactive Plotly charts behave on phone-width
screens (~360–430px), why they degrade, and the realistic options to improve them —
with effort, risk, and a phased recommendation.

This is the site's single biggest remaining UX gap (flagged in the SESSION-7 polishing
review). The chrome (navbar→hamburger, hero, the six topic cards, prose, tables of
contents) already adapts well; **the charts are the problem**, because Plotly figures
are laid out for the ~700–900px desktop content column and that layout is baked in at
render time.

---

## 1. What actually breaks on mobile (observed at 375px)

| # | Symptom | Where | Severity |
|---|---------|-------|----------|
| 1 | **Right-side legend crushes the plot** — the 17-country peer charts reserve `margin.r=175` for a vertical 18-entry legend; at 375px that legend eats ~40% of the width and the plot is squeezed to the left half | every `peer_comparison_line` / `_by_age` chart (~40 charts: economics, housing, income, fiscal, health, environment, science) | **High** |
| 2 | **Source notes clip off the right edge** — notes are Plotly annotations (`xref="paper"`, fixed `font.size`, no wrapping); at narrow width the line runs past the plot ("…are projectic…") | nearly every chart (peer lines, bars, maps) — the site-wide source-note + brand-attribution pattern | **High** (universal) |
| 3 | **Scorecard clips both sides** — `ranking_strip`/`page_snapshot` has fixed left row-labels and right "value · rank · median" labels; both get cut at 375px | top of every peer-comparison page | **High** |
| 4 | **Fixed pixel heights** — peer charts are 600px tall (sized so the 18-entry legend fits on desktop); fine vertically on mobile, but compounds #1 (tall + narrow plot = a sliver) | peer charts | Medium |
| 5 | **Right-anchored colourbar + control buttons** on maps (hover on/off, colourbar) crowd the narrow frame | choropleth/bubble maps (population, geography, housing, income, crime) | Medium |
| 6 | **Range buttons / sliders / dropdowns** are small tap targets and can wrap/overlap the title or source note at narrow width | slider charts, dropdown maps, the pyramid year-slider | Medium |
| 7 | **Dense multi-line charts** (12-type crime, religion long-run) are hard to read small regardless of layout | crime-safety, religion | Low (inherent) |

The throughline: **#1, #2, #3 are layout problems, not size problems.** Making the
figure "fit" the screen width (Plotly `responsive:true`) does *not* fix them — the
legend still sits on the right, the annotation still clips, the labels still overflow.

---

## 2. Why it's hard (the constraints)

- **Plotly has no internal media queries.** Margins, legend position/orientation,
  annotation coordinates and font sizes are fixed values in the figure JSON. They do
  not respond to viewport width.
- **Quarto bakes figures at build time.** Each `fig.show()` emits static JSON + a
  one-shot render script. There is no per-request server to emit a mobile variant.
- **One figure must serve both desktop and mobile** (same HTML is sent to every
  device). So responsiveness has to happen **client-side after load**, or be a
  compromise layout that works acceptably at both widths.
- **Source notes are *inside* Plotly** (annotations), partly because the brand line is
  appended by the `Figure.show` interceptor in `charts.py`. Plotly annotations don't
  wrap to the viewport; `<br>` only breaks where we hard-code it.
- **The AMD/requirejs gotcha** (`window.Plotly` is undefined under Quarto's bundle —
  use `requirejs('plotly')`) and **async chart render** (charts paint after
  `DOMContentLoaded`, so a script must bounded-poll) — both already solved in the
  existing includes and must be respected by any new one.

---

## 3. The options

### Option A — Responsive relayout via a site-wide JS include  ⭐ (recommended core)
A new `_includes/mobile-layout.html` (`include-after-body`), mirroring the proven
pattern of `peer-legend-colours.html` / `yaxis-autoscale.html`:
- On load **and** on a debounced `resize`, check `matchMedia('(max-width: 600px)')`.
- For each rendered chart (bounded-poll for async), when narrow, `Plotly.relayout`:
  move the legend **below** (`orientation:'h'`, `y` negative, centered), drop
  `margin.r` to ~10 and raise `margin.b`, shrink/hide the range-button row, and nudge
  the source-note annotation down with the legend. Cache the original layout so
  widening **restores** the desktop view exactly.
- **Pros:** one central file; zero per-chart edits; works on the ~140 already-baked
  charts; desktop untouched; reuses the solved requirejs/poll machinery.
- **Cons:** real JS to get right; must classify chart types (peer line vs bar vs map)
  to relayout each correctly; relayout-on-resize can flash; doesn't *wrap* a long
  source note (it can move/shrink it, not reflow it — see Option C).
- **Effort:** medium. **Risk:** medium (broad surface; needs the full
  preview_resize-per-family verification sweep). **Fixes:** #1, #3, #4, partial #2/#5/#6.

### Option B — Mobile-friendly defaults baked into the builders
Change `charts.py` defaults (legend below, smaller margins) so figures ship
mobile-tolerant.
- **Pros:** clean at the source; no JS.
- **Cons:** it would degrade the *desktop* layout (the right legend + 600px height were
  deliberately tuned so 18 entries fit without a scroll-stealing overflow — see
  CLAUDE.md); you can't satisfy both widths from one static layout. **Effort:** low.
  **Risk:** high (regresses desktop). **Verdict:** not on its own.

### Option C — Move source notes out of Plotly into Quarto markdown captions
Render the source/brand line as a markdown caption under each figure (CSS-wrappable)
instead of a Plotly annotation.
- **Pros:** genuinely *wraps* on any width — the only clean fix for #2; also lightens
  every chart's bottom margin. **Cons:** large refactor across ~140 call sites + the
  `Figure.show` brand-attribution interceptor; re-introduces the inline-code HTML-escape
  gotcha for the brand `<br>`. **Effort:** high. **Risk:** medium. **Fixes:** #2 (fully).
- *Lighter variant:* keep notes in Plotly but **auto-shorten on mobile** via Option A
  (e.g., drop the parenthetical, or reduce font) — 80% of the benefit, 20% of the work.

### Option D — Legend reduction on mobile (peer charts)
On narrow viewports, show only Canada + the active comparators + average in the legend
and hide the 10 grey peers (still reachable via a small "+ more countries" control).
- **Pros:** directly cuts the 18-entry crush driving #1. **Cons:** changes the
  interaction model on mobile (the legend *is* the peer toggle today). **Effort:**
  medium. **Risk:** medium. Best **combined with** Option A's legend-below.

### Option E — `responsive:true` / autosize
Set Plotly responsive so figures track container width.
- **Pros:** trivial. **Cons:** only resizes; does **not** fix legend/margin/annotation
  layout. **Verdict:** worth turning on as a baseline, but it is not the fix.

### Option F — "Expand chart" affordance
A tap-to-fullscreen (or rotate-to-landscape hint) for the densest charts/maps.
- **Pros:** gives complex charts real room without compromising the inline layout.
  **Cons:** extra UI; opt-in per chart. **Effort:** medium. **Verdict:** Phase 3 polish
  for maps + the 12-line crime chart (#7), not a general fix.

### Option G — Triage & accept
Fix the universal, cheap wins (source-note clip, scorecard) and accept that the densest
17-line charts are simply compact on a 375px screen (true of most peer data sites).
- **Verdict:** the realistic *floor*; Phase 1 below is this plus the legend fix.

### Option H — Static (pre-rendered) chart images on mobile  (the social-card synergy) ⭐ strong complement
Render each figure to a mobile-optimized static image at build time and serve the image
(not the interactive Plotly div) on narrow viewports. **Directly reuses / generalizes
`pipeline/social_cards.py`**, which already exports static chart images (Radio-Canada
embedded, 4 formats) — one static-export pipeline then serves social cards, a universal
"download / share this chart as an image" affordance, *and* mobile fallbacks. (Owner's
idea, 2026-06-23.)
- **Pros:** perfect mobile layout (the image is composed for the width — no legend
  crush, no clipping, no tap-target problems); **much lighter + faster**, especially on
  the heavy inlined-geojson map pages (no multi-MB payload, no per-chart Plotly JS) — the
  single biggest performance win available on the worst pages; sidesteps every
  interactive-layout problem at once; reuses an investment we want for launch anyway.
- **Cons / hard parts:**
  - **Loses interactivity — the site's core promise** ("interactive metrics"): no
    hover-for-value, no country toggle, no zoom. Mitigated by a **tap-to-interact** escape
    hatch (compose with Option F): static by default, tap → the live chart.
  - **Maps are simultaneously the worst fit *and* the worst offenders.** A static
    all-Canada map at phone width is unreadable (tracts/DAs are specks); "zoom to your
    neighbourhood" — the entire point of the tract/DA/CMA maps — is gone. So static helps
    map *load* but guts map *usefulness*. Maps need real interactivity (relayout/zoom),
    not a static frame. (A real static-map mobile solution would be a different, larger
    build: postal-code/geolocate → a pre-cropped neighbourhood image.)
  - **One state per image:** dropdown / slider / selector charts (substance-use, govt
    composition, diversity, the pyramid, geography pickers) capture a single state — you'd
    export the default only, or N images per state (costly).
  - **CI infra:** needs a **Linux rasterizer** in CI (kaleido) — `qlmanage` is macOS-only
    (already a noted TODO in the social-card work). Weekly data refresh ⇒ regenerate
    images weekly ⇒ build time + storage.
  - **Don't ship both:** swapping interactive↔static must avoid sending *both* to every
    device (doubles weight, hurts mobile) — needs a real conditional load (`<picture>` /
    lazy swap, or a JS injector keyed on viewport).
- **Best for:** single-state static charts (ranked bars, single-series lines, the
  scorecard) where interactivity adds little — and as a site-wide **"share / download as
  image"** feature (desktop too). **Worst for:** maps and any selector/slider/hover-led
  chart. **Effort:** high (pipeline + CI + swap mechanism). **Risk:** medium.

### Option I — Vector tiles + MapLibre for the data maps  (the CensusMapper approach) ⭐ the maps answer
CensusMapper — the best mobile census-map experience in Canada — is built on **MapLibre
GL + custom deck.gl extensions (WebGL/GPU) vector maps**, with custom Canada-wide
**vector tiles** served by a **Martin tile server** (verified: von Bergmann,
"CensusMapper 2.0", doodles.mountainmath.ca, May 2026). It's smooth on mobile because
vector tiles load **incrementally** — only the visible area at the current zoom, in KB —
and the **GPU** renders pan/zoom. That's the opposite of our maps, which **inline
multi-MB GeoJSON into Plotly `Choroplethmapbox` and render on the CPU, all at once**.
That inlined-GeoJSON design is the root of our map mobile pain (load, memory, layout) —
and maps are exactly what Options A and H *can't* properly fix (relayout doesn't shrink
the payload; a static map image can't zoom to a neighbourhood).
- **Scope — whole site, not a mobile-only layer:** this swaps the map *engine*, so
  desktop renders MapLibre too. You wouldn't keep two implementations of one map — and
  wouldn't want to, since desktop *also* benefits (the heavy tract/DA pages load faster
  and zoom smoother everywhere). That's the key contrast with Options A and H, which are
  mobile-*targeted* and leave the desktop charts untouched. The flip side: it means
  touching maps that currently work fine on desktop, applying the `file://` trade-off
  everywhere, and committing to MapLibre as *the* map engine — which could eventually
  absorb both the Plotly choropleths and the Leaflet elevation page, unifying three map
  approaches into one.
- **Static-site adaptation (no backend needed):** we don't need Martin. Build the
  tract/DA/CMA layers once into a single **PMTiles** archive (Protomaps;
  `tippecanoe` GeoJSON→tiles) and render with **MapLibre GL JS** (open source, no Mapbox
  token). PMTiles serves by **HTTP range requests from plain static hosting — GitHub
  Pages works** — the serverless equivalent of their tile server. Result:
  CensusMapper-class smooth mobile maps, KB initial payload, full zoom-to-your-street
  interactivity, on our existing static deploy.
- **Pros:** the *principled* fix for the heaviest pages; the single biggest mobile win
  (KB vs multi-MB); keeps full interactivity (what static images lose); one modern engine
  (MapLibre) we already have a cousin of (the Leaflet elevation page).
- **Cons / trade-offs:**
  - **Breaks the `file://` workflow.** Range-requested PMTiles need a real HTTP server;
    they won't load from an HTML file opened directly off disk. The project *deliberately*
    inlines GeoJSON so map pages work from `file://` (the reason the heavy tract maps are
    separate pages). Vector tiles mean giving that up for those pages — fine on the
    deployed GitHub Pages site, but a real policy change.
  - **A second map stack** alongside Plotly (tile build pipeline + per-map rewrite from
    `Choroplethmapbox` to MapLibre layers + brand restyle).
  - **Effort:** high (tile pipeline + per-map-type port). **Risk:** medium. Best done
    map-family by map-family, heaviest first (the tract/DA neighbourhood pages).
- **Bonus validation:** CensusMapper generates its social-preview images with a
  **Puppeteer** microservice — independent confirmation of the static-image / social-card
  direction in Option H.

---

## 4. Recommended phased plan

**Phase 1 — the JS responsive include (Option A) + autosize (E).** Highest ROI.
One `_includes/mobile-layout.html`. Targets the three High issues:
1. Peer-line legend → below, reclaim `margin.r` → plot gets full width.
2. Source note → moved with the legend and **auto-shortened/shrunk** on mobile
   (Option C-lite) so it stops clipping.
3. Scorecard → reflow labels (shrink/stack the right-hand value label; let the rows use
   full width). This one may need a small `ranking_strip` change since it's a bespoke
   layout.
Verify with `preview_resize` mobile + a screenshot per chart family (peer line, ranked
bar, scorecard, map, slider, dropdown).

**Phase 2 — source notes as wrapping captions (Option C, full)** *if* Phase-1
shrink/move proves insufficient. Bigger refactor; do it deliberately, not under the
polish umbrella.

**Phase 3 — densest-chart affordances:** legend reduction (D) on the busiest peer
charts and/or expand-to-fullscreen (F) for maps and the 12-line crime chart.

**On static images (Option H) — a strong *complement*, not a replacement.** Build the
static-export pipeline regardless (the social launch needs it); generalizing it unlocks
a "share / download as image" affordance everywhere **and** a clean mobile fallback for
the *non-interactive-dependent* charts (bars, single lines, scorecard) — ideally as
**static-by-default + tap-to-interact** (H + F). But it does **not** solve the maps,
which are both the worst mobile-layout offenders and the most zoom-dependent — so the
JS-relayout (Phase 1 / Option A) is still needed as the path that *keeps interactivity*
and covers maps + selector/slider charts. **Net: relayout for the live experience;
static-export as a parallel, multi-purpose investment (social + share + select mobile
fallbacks).** They compose well; neither alone is sufficient. The cleanest sequencing
may even be to build the static pipeline *first* (it's needed for launch anyway), ship
"share as image" + static fallbacks for the simple charts, then add the Phase-1 relayout
for the interactive charts (maps, selectors) that static can't serve.

**For the maps specifically — the worst mobile case — the long-term answer is Option I**
(vector tiles + MapLibre via PMTiles), not relayout: relayout fixes a map's *layout* but
not its multi-MB payload or zoom performance, and a static image can't zoom at all. Treat
Option I as a separate, later track from the Phase 1–3 chart work — heaviest map pages
first — weighed against the `file://` trade-off.

**Explicitly not doing:** Option B (regresses desktop).

---

## 5. Implementation notes (for whoever builds Phase 1)

- **Vehicle:** copy the structure of `_includes/peer-legend-colours.html` —
  `requirejs('plotly')` for the handle, bounded-poll until each `.plotly-graph-div`
  has `_fullLayout`, no-op on charts that don't match a known shape.
- **Trigger:** `matchMedia('(max-width: 600px)')` + a debounced `resize`/orientation
  listener. **Cache** each chart's desktop layout (`margin`, `legend`, annotation `y`)
  on first run so widening restores it byte-for-byte.
- **Classify** charts to relayout correctly: peer line (legend right→below), bar
  (source-note only), map (colourbar/controls), scorecard (bespoke). A `meta` tag on
  the figure (like the existing `meta.fixedColor`) could let builders self-label chart
  type for the script — cheap to add.
- **Respect** the legend-overflow rule (an overflowing Plotly legend grows a
  scroll-stealing bar — never let the mobile legend overflow; cap rows or wrap).
- **Don't** rely on `window.Plotly`; **do** guard every relayout in try/catch; **don't**
  thrash relayout on every resize pixel (debounce ~150ms).
- **Verification is mandatory per chart family** — mobile layout is exactly the kind of
  broad change where one family looks fixed and another breaks.

## 6. Quick reference — the code touch-points
- Peer layout + the 600px/`r=175` decisions: `pipeline/charts.py` `_apply_peer_line_layout`.
- Source-note annotations: the `source_note=` params + the `Figure.show` brand
  interceptor at the top of `charts.py`.
- Scorecard: `ranking_strip` / `page_snapshot` in `charts.py`, specs in `config.py SNAPSHOT_SPECS`.
- Existing include patterns to mirror: `_includes/peer-legend-colours.html`,
  `_includes/yaxis-autoscale.html` (registered in `_quarto.yml` under
  `format.html.include-after-body`).
