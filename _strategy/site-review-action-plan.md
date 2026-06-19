# Site-review action plan (v0 review, 2026-06-18)

*Internal tracker for working through the owner's full-site review
(`DW_CanObs-site-review-2026-06-18.docx`). `_strategy/` is Quarto-ignored. Status keys:
☐ todo · ◐ in progress · ☑ done (working tree, uncommitted) · ⟳ needs owner decision ·
🔬 needs research. Line refs (`§N`) point to the extracted review.*

Locked global rules (owner, 2026-06-18): **sentence case site-wide**; **default load =
Canada + US + Australia + Germany + OECD average** (Sweden/UK coloured but unloaded).

---

## A. Global rules — fix once, apply everywhere (the leverage)

- ☑ **G3 Default comparators on peer lines** — `DEFAULT_VISIBLE_COMPARATORS = [USA, AUS, DEU]`
  in config.py; `peer_comparison_line` + `_by_age` default to it. Sweden/UK keep colour +
  legend-top rank but start `legendonly`; the 11 grey peers stay hidden. Per-chart
  overrides via `initial_visible=[...]`. *(§3, §118, §125, §137, …)*
- ☑ **G2 Remove defensive non-partisan boilerplate** (main + 10 neighbourhood pages,
  2026-06-18; one internal code comment left) — strip "this is descriptive / no
  good-or-bad reading / how high it *should* be is political / shown without a favourable
  direction / not a gap in this site / Descriptive only." Keep the principle ONLY on the
  Landing page + About. *(§64, §76, §98, §266, §290, §327, §336, §388, §418, §538)*
- ☑ **G1 Source-note standard** (bars left-anchored; all 6 map builders WRAP long source
  notes via `_wrap`/`_map_source_note` [yanchor=top, grows downward, b→80] so they no
  longer clip at the right edge or touch the map — screenshot-verified 2026-06-18.
  PLUS the Figure.show interceptor now wraps + top-anchors every source note site-wide, so
  notes hang below the slider/x-label, not into it (verified single_line / single_bar /
  history_lines / lines_over_time). Remaining: shorten non-pop map notes; spot-check
  stragglers (pyramid, happiness-factor)) — a single
  consistent placement that never overlaps the
  x-axis label, range slider, map bottom, legend, or clips at the right; never right-
  aligned on ranked bars (left or centre). Layout work across builders; verify per render.
  *(~30+ refs)*
- ◐ **G6 Right-edge x-padding** — `single_line` + the peer-line layout now add a ~2% right
  buffer so the latest point isn't flush against the edge (2026-06-18; verified population
  total + economics peer charts). `single_line_multi`/`single_bar` auto-range (already
  padded). *(§199, §203, §254, §300, §313, §338)*
- ◐ **G7 "Data current to" prominence** — pattern established: a bold inline-python line under
  the heading (`**Data current to {get_data_date(path)}.**`), done on the household-debt ranked
  chart (§208 → "2025"). **Caveat: it's per-chart, not global** — bespoke files (the unemployment
  map's computed `period`, CREA's HPI month) return None from `get_data_date`, so those get their
  own date var in the per-section pass (the unemployment line was reverted to avoid "None").
  *(§134, §178, §208, §230)*
- ☑ **G8 Title policy** — 179 `##`/`###` headings → sentence case site-wide via a reviewed
  script (proper nouns/acronyms preserved: Canada, GDP, CO2, US, Gini, PM2.5, R&D, USD…;
  navigational area-card links + page `title:` fields left as-is). 3 owner-flagged shortenings
  done (tuition / bond-yields / revenue-spending; no inbound links broke). Heading IDs are
  case-insensitive in Quarto so internal links still resolve. Remaining renames (elevation
  §439, air-quality §502) → per-section pass. *(§216, §330, §427)*
- ☑ **G9 Map colourbar titles** — 8 long single-value colourbar titles split with `<br>` to
  reclaim map width (income → 3 lines per §232; "dwelling"→"home" per §193; home-value, value÷
  income, unemployment, density, surface area). Verified: the home-value map's bar is now a
  narrow 2-line "Median home / value" and the map fills the column. Groups-map `% {label}` bars
  left as-is (not flagged). *(§190, §195, §232, §444)*
- ☐ **G10 Bar-vs-line guideline** — single-series counts/rates default to bars (NPR,
  low-income, federal headcount, executives, revenue/spending). Per-chart judgement.
  *(§31, §41, §251, §297, §315, §333, §460)*
- ☐ **G11 Pages stand alone** — remove cross-page "linking" sentences. *(§225, §538)*
- ☑ **G4 Legend scrollbar** — fixed: the by-age dropdown builder passes `extra_top=70` (menu
  room), which shrank the plot area below the 18-entry legend → overflow scrollbar. Height in
  `_apply_peer_line_layout` now adds that extra top back (`600 + max(0, extra_top-40)` → 630 for
  by-age), restoring the regular charts' plot/legend area. Verified: legend overflow now false on
  both economics by-age charts (was true); regular peer charts unchanged. *(§49, §53, §127)*
- 🔬 **G5 Y-axis scale navigation** — consistent default range + period-aware rescale
  (autoscale doesn't solve it). Affects inflation, borrowing costs, vaccination, … *(§37,
  §156, §159, §212, §377)*
- 🔬 **G12 Data-currency audit** — many "why does this end in 2023/24?" (US 2025, NAPS,
  productivity, life-expectancy, …). One pass to verify newest vintages. *(§123, §128,
  §130, §359, §372, §381, §404, §490, §504, §542)*

## B. Structure / reorganization (judgement, doable now)

- ☐ Economy: move **Quarterly GDP above** the international GDP comparison *(§121)*; split
  out **Trade** and **Currency** sub-sections *(§146, §148)*; **Borrowing Costs** its own
  page *(§214)*; business-investment cluster into a sub-section *(§140)*.
- ☐ Housing: reorder (lead with the most broadly useful charts), consider splitting +
  a dashboard-style landing; group Rent + Vacancy *(§173, §202)*.
- ☐ Health: split **Health of Canadians** vs **Health-Care System** *(§354, §380)*; fold
  Tobacco/Alcohol into Substance Use *(§386)*; reorganize Substance Use intro *(§387)*.
- ☐ Government: combine Gross/Net debt ranked bars into one dropdown *(§264)*; Defence its
  own sub-section *(§271)*.
- ☐ Environment: **Fire & Ice → two pages** *(§488)*; consider Protected ↔ Ecozones merge
  *(§458)*, Permafrost/Sea-ice placement *(§494)*.
- ⟳ Per-section landing pages? (overview + section visual identity) *(§24)*; blog/updates
  + civics-education under About *(§22, §23)*.

## C. Per-section text + chart fixes (Tier-1 sweep, after the globals)

Captured per page in the review; worked top-to-bottom. Highlights beyond the globals:
Landing (§13–20), Population (§30–58), Diversity/Religion/Citizenship/Languages
(§61–99), Crime (§100–112), Economy (§116–148), Cost of Living (§150–160), Housing
(§163–220), Income (§222–254), Government (§256–350), Health (§352–404), Well-being
(§407–413), Environment (§415–518), Education/Science (§522–552).

## D. Research + owner decision

- 🔬 **Colour system report** (countries *and* provinces) — purpose-built palette tying to
  the brand/visual identity + scientific-viz best practice. Owner wants a report before
  implementation. *(§4)* — the visual-identity colour assessment.
- 🔬 **Comparator stress-test** — are the 17 right? topic-specific additions (China/India
  for CO₂). *(§11)*
- 🔬 **Population-distribution visualization** — explore better ways than the current map;
  survey what others do. *(§423)*; reanalysis climate maps *(§468, §471)*; map parks /
  protected areas *(§461)*.
- 🔬 **Y-axis strategy** (G5) and **legend-scroll** (G4) deep fixes.

## E. New-topic backlog

**Confirmed earlier (2026-06-17):** tax structure & redistribution · household financial
stress · commute · productivity decomposition. **Added by this review:** voter turnout
(federal + provincial) *(§99)* · minimum wage real/nominal *(§224)* · income/wealth
distribution-over-time (age-pyramid style) *(§223)* · government science funding
NSERC/SSHRC/CIHR *(§547)* · tertiary attainment vs peers *(§535)* · representative-
institution tuition *(§536)* · military world map / Canada-vs-world population & area
*(§6, §112)* · CO₂ per GDP intensity *(§516)* · first-time-buyer & family-formation age
*(§9)*. All build-deferred; fold into the topic roadmap.

---

### Batch log
- **2026-06-18 #1:** action plan created; G3 default-comparators implemented; G2
  defensive-boilerplate sweep started (main section pages + source-note tags).
- **2026-06-18 #2:** G2 finished (10 neighbourhood pages, templated find-replace); G1
  started — all ranked/category bar source notes moved off the right edge to left-anchored.
- **2026-06-18 #3:** committed batches 1–2 (`58f08fe`, branch `site-review-2026-06`);
  then G1 maps — all 6 map builders' source notes spaced off the map bottom (uncommitted).
- **2026-06-18 #4:** owner flagged map source notes STILL clipping at the right — root
  cause was a long single line (vertical spacing can't fix a horizontal clip). Added
  `_wrap` (auto `<br>`) + `_map_source_note` (yanchor=top), b→80; the 6 map builders now
  wrap. Screenshot-verified on the diversity tract map (worst case: 5 lines, no clip).
- **2026-06-18 #10 (G4 + source-note clipping — ⭐RESUME HERE; context near full):**
  **G4 ✅** legend overflow fixed (`_apply_peer_line_layout` height `600+max(0,extra_top-40)`
  → 630 for by-age). **Source notes were clipping on bespoke `go.Figure` charts** (peer/builder
  charts fine) → the `Figure.show` interceptor now appends BRAND **INLINE**
  (`_wrap(f"{src}  ·  {BRAND}", 118)`) not on its own line, so notes stay ~1 line; + bumps
  substance-use bespoke b=70/80→120 and `lines_over_time` b=80→100. Verified clear (bottom+right)
  on substance-use + income. **UNCOMMITTED**; full bg render (/tmp/full_render3.log) propagating it.
  **⚠️ OPEN: owner confirms inline-vs-own-line brand** (inline is visible site-wide; if own-line,
  revert + per-chart margins). **NEXT:** verify render → run the clip-detector sweep on
  economics/environment/geography/crime/climate for stragglers → fix → COMMIT G4+clipping → then
  the per-section pass. (Clip-detector: per `.plotly-graph-div`, compare each Source `g.annotation`
  bbox vs the div bbox; bottom/right `>0` = clip.)
- **2026-06-18 #9 (G8 — sentence-case titles):** 179 `##`/`###` headings → sentence case via
  a reviewed script (acronyms/proper nouns preserved); 3 owner shortenings
  (tuition / bond-yields / revenue-spending). Verified on economics/housing/government/education.
  Source done; the other ~18 affected pages' _site refresh on the next full render.
- **2026-06-18 #8 (finish G1 — owner "(1)"):** trimmed 16 other-section map source notes
  (income/housing/geography) to provenance + essential caveats (owner-estimated, the
  affordability ratio, permafrost ~1995, bubble sizing). Verified the two stragglers:
  happiness-factor source now sits below its legend (§413); the population pyramid's
  bottom margin → 170 so its note clears the year slider (§45). Affected pages re-rendered.
  **G1 done.**
- **2026-06-18 #6 (G1 time-series — owner "(2)"):** the `Figure.show` interceptor now
  WRAPS + top-anchors + left-aligns every source note in ONE place — so notes hang BELOW
  the range slider / x-axis label instead of centring on it (the overlap cause). Removed
  `history_lines`' "Census year" x-title (the lone x-axis title, which the long note
  collided with). Screenshot-verified: population (single_line + single_bar sliders),
  religion long-run (history_lines + 5-line note), government spending (lines_over_time +
  bottom legend). Remaining: shorten non-population map notes; spot-check the pyramid (§45)
  and happiness-factor (§413).
- **2026-06-18 #5:** owner confirmed (0) the neighbourhood pages were just STALE (the wrap
  fix is in the shared builder, not yet re-rendered); (1) shortened all 15 population
  census/DA map source notes to provenance-only (agency + Census Profile table + metro),
  methodology stays in prose. Re-rendered all 15; screenshot-verified Vancouver DA (1 concise
  line, no clip). **New rule:** map source notes = provenance only, kept concise.
- Remaining maps (income/housing/geography/crime/economy) need the same concise-note pass.
- Next (owner: "(2)"): G1 time-series slider/label overlaps.
- **2026-06-18 #11 (autonomous batch, owner away):** worked all the SAFE/unambiguous review
  items in 3 commits — `e528327` lighter line loads (`initial_visible` on the busy peer charts)
  + per-page prose scrub (the specific lines quoted, not the already-removed generic boilerplate)
  + title renames; `fd69aef` owner-provided exact rewrites (economy/geography/housing/religion
  intros); `69fc559` chart-scale tweaks (vaccination 50% floor + drop 95% label, growth-rate
  y-max 5, NATO "minimum target", low-carbon x-start) + `stacked_area` margin. Full render
  exit 0. **Owner-decisions + remaining work catalogued in `site-review-session-2026-06-18.md`**
  (colour report, comparator stress-test, G5 y-axis-nav, structure/reorg, new-data builds,
  line-vs-bar calls, G12 currency batch + a "next autonomously" list). Branch 10 ahead, unpushed.
- **2026-06-19 (structure-and-data report — Phase 1):** implemented the approved
  `structure-and-data-recommendations.md`. **Done (9 commits, branch tip `c4c4955`):**
  `e575bd5` gross/net-debt dropdown (new `ranked_bar_select`) + defence sub-section
  (troops/reservists deferred — WB `MS.MIL.TOTL.P1` frozen at 2020); `13d230d` CO2/GDP
  intensity (OWID; Canada most-intensive of 17); `62d7a5e` per-capita gov employment toggle
  (`lines_over_time` measures now switches hover precision; §296 UI-text removed); `9225084`
  inflation-by-component bar (fetch_cpi side-output `statcan_cpi_components.csv`; `category_bar`);
  `5cd518d` "Canada in the world" pop chart (all 217 countries log-scale, 37th/top-17%;
  `fetch_world_population`; log-axis annotation-y gotcha); `0583b01` daytime-high warming option
  (AHCCD `temp_max`); `958b793` China/India CO2+PM2.5 global-context charts (SEPARATE from the
  17-peer lines; `fetch_co2_global_context` + `fetch_pm25_global_context`); `e90b261` source-note
  overflow fix (climate-change ×4 + protected ×1, concise provenance, verified at 525px);
  `c4c4955` removed leftover "Age group:" caption on `ranked_bar_by_age`. **+4 indicators
  (106→110.) All verified in rendered Quarto.** STILL OPEN in Phase 1: **Fire & Ice → Wildfire +
  Ice split** (§488, item 9 — nav + air-quality cross-link). NEXT: Fire/Ice split, then Phases
  2–5 (Phase 2 = Substance-Use reorg §386-7 + Health split §354/380 + min wage + CREA type
  dropdown). Colours AFTER. Broad safe-sweep (air-quality titles, well-being, ecozones hover)
  still partial.
- **2026-06-19 #2 (structural reorgs — owner: "yes, those structural changes are a logical
  next step"):** finished Phase 1 + the structural moves of Phase 2. `db5ae51` **Fire & Ice →
  Wildfire + Ice** (two pages; nav split under "Climate & Atmosphere"; air-quality cross-link →
  Wildfire; fire-ice.qmd removed). `c83987e` **Substance Use reorg** (§386-7): leads with
  "Tobacco, alcohol and cannabis" (the peer tobacco/alcohol chart MOVED off Health + the by-age
  chart); opioids → "## The opioid-toxicity crisis" with ### sub-sections; general intro; Health
  loses its tobacco/alcohol chart + a one-line pointer. `1602351` **Health split into TWO PAGES**
  (§354/§380 — owner picked separate pages via AskUserQuestion): health/index.qmd = "Health of
  Canadians" (life expectancy + recent decline + risk factors; KEEPS the full scorecard) + new
  health/health-care-system.qmd = "The Health-Care System" (spending + UHC + OOP + capacity +
  access). Health dropdown → 4 items. All verified in rendered Quarto; a full site render
  confirms nav propagation. **NEXT: Phase-2 data items** (minimum wage — needs ESDC/StatCan
  source check; CREA dwelling-type dropdown — data in hand), then Phases 3–5, then colours.
