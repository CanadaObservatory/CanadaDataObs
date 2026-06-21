# Remaining-work plan — Canada Observatory site review

*Written 2026-06-21, after a full line-by-line audit of all 516 numbered review items
(`review-extract.md`) against the current code on branch `site-review-2026-06` (tip `257843f`).
This supersedes the day-by-day batch log in `site-review-action-plan.md` for planning purposes.
`§N` = the canonical item number in `review-extract.md`.*

## Status at a glance

The large majority of the review is **done**. Globals G1–G4, G8, G9 are complete; G2 (defensive
prose) and the owner-quoted rewrites are applied site-wide; the structural reorgs (Health split,
Fire & Ice split, Substance-Use reorg, Trade/Borrowing splits, gross/net-debt dropdown, per-section
overview pages) shipped; ~15 new indicators were built (commute, tax structure, redistribution,
debt-service ratio, voter turnout, minimum wage, income distribution, CO₂/GDP, world population/GDP/
land-area, provincial finances); the parks expansion and the clean-map style (incl. this session's
categorical variant on ecozones + permafrost) are in. Source-note clipping is fixed in every shared
line/bar/history/category builder.

What remains sorts into seven buckets below. **Tiers 1–2 are the high-value, low-risk batch to do
next** (lots of polish, a few shared-builder fixes that each touch many charts). Tiers 3–5 are real
builds. The Owner-decisions and Data-blocked lists are not actionable by me yet.

---

## Tier 1 — Quick wins: prose & small parameters (each ~S)

A single sweep could clear most of these. Grouped by page.

**Landing (`index.qmd`)**
- §14 Split "Where the data allows, maps…" into its own paragraph.
- §15 Add "easy-to-use format" framing to the downloads line.
- §17 Cut the early paragraph that overlaps the (kept) Principles section.
- §18 Add Instagram + X links (instagram.com/canadaobservatory, x.com/canobservatory) — footer/About.
- §19 Add an upfront "support conversations about Canada with reliable, timely data" sentence.
- §20 Rewrite "Start with these questions": drop "New here?", lead with exploring your own questions.

**Population (`population/index.qmd`)**
- §32 Remove "steadily" and "as a whole" from the intro.
- §41 Make the Non-Permanent-Residents chart a bar (folds into §42, Tier 3).
- §44 Delete the "fill in the working ages" sentence (+ note an immigration-age-data check for later).
- §58 Add `rangeslider=True` to the interprovincial-migration bar.

**Diversity / Religion (`population/diversity.qmd`, `religion.qmd`)**
- §74 Put "(census tract)" in parentheses; front-load the plain-language framing.
- §75 Split "Religion is self-reported…" into its own paragraph.
- §77 Remove the "now the second-largest group" + the "separate from Indigenous identity" sentences.

**Economy / Cost of Living (`economics/index.qmd`, `cost-of-living.qmd`)**
- §122 Lift the "pandemic quarters (off-scale)" annotation just above the plot frame.
- §136 Remove the trailing older-worker (55–64) sentence on the employment-rate text.
- §153 Remove the cost-of-living first sentence ("…the issue Canadians name as their top concern").
- §154 Remove the duplicate inline "Related cost pressures have their own pages…" line (kept as a section).
- §159 Set an explicit initial y-range on the headline/core/food inflation chart (stop spikes over-scaling).

**Housing (`housing/index.qmd`, `pipeline/crea.py`)**
- §168 / §172 / §198 Open real-house-prices, price-to-income, and rent on a recent window (≈2014).
- §176 Add a one-line NHPI caveat (it's a builder total; condos move differently).
- §178 Add a prominent "data current to …" line above the CREA by-type chart.
- §180 Un-bold the CREA-permission sentence and move it into the source line.
- §184 Shorten CREA city names / standardise "Greater … / … CMA".
- §189 Replace "— a usable proxy" with plainer phrasing.
- §206 Note that household debt is mostly mortgage + other types.

**Borrowing costs (`economics/borrowing-costs.qmd`)**
- §213 Clarify "conventional 5-year mortgage rate" (posted/benchmark vs discounted).
- §217 Add the "Use the dropdown to switch term" sentence.
- §218 Remove "especially" / the "while…" parenthetical.
- §219 Add a small right margin so the term dropdown/plot don't clip (`single_line_multi`).

**Income (`income/index.qmd`)**
- §230 Put "Latest year…" on its own line in the median-income source note.
- §238 State the OECD average-wage real base year in prose.

**Government (`government/index.qmd`, `government/spending.qmd`)**
- §269 Add a one-line note that net interest can be negative (interest income > payments).
- §273 Cap the defence ranked-bar x-axis at 5% (Israel already omitted).
- §277 Move the companion-page line below the two-definition block.
- §284 Rename "The bureaucracy vs. the whole public sector" → "The public sector".
- §289 Add units ("thousand") to the public-sector composition hover.
- §292/§293/§294 Bridge "general government" vs "public sector"; add a coverage caveat; add a sub-heading above the peer ranked bar.
- §304 Use a 2015 baseline for the "which departments grew" diff.
- §318 Rename "Who the public service is".
- §331 Trim the revenue/spending intro further (keep "The gap…").
- §340 Relabel "Compensation of employees" → "Salaries" (width).
- §347 Add a "Top 10" department option and make it the default.

**Geography (`geography/agriculture.qmd`, `climate.qmd`, `environment/climate-change.qmd`)**
- §428 Move the cropland map above the farm-type map.
- §429 Delete the "The type of farming… is another" sentence.
- §470 Convert the precipitation colourbar from mm to cm.
- §478 **Remove the linear-trend lines** on the long-run city-temperature chart (+ seasonal slope labels) — owner felt strongly (base-year cherry-pick risk).

**Air Quality (`environment/air-quality.qmd`)**
- §500 Widen the emissions chart (unused right-side space).
- §504 Add a one-line data-currency note (national NAPS/CESI lag).
- §507 Add a sentence explaining the OECD PM2.5 series' sparse/flat pre-2000 (modelled satellite years).

**Health (`health/index.qmd`, `health-care-system.qmd`, `substance-use.qmd`)**
- §356 Tighten the gap between the scorecard and its legend (`page_snapshot`/`ranking_strip`).
- §358 Add `initial_visible=["USA","AUS","DEU"]` to life expectancy (currently loads Sweden/UK too).
- §373 Add a lead sentence framing diabetes as a major risk factor.
- §390 Break the opioid "Scale of the crisis" source note after "Data as of …".
- §399 Retitle "Hospitalizations" → "Hospitalizations due to opioids".

**Education / Science (`education/index.qmd`, `science/index.qmd`)**
- §528 / §531 Pad the tuition charts' lower y-range so $0 clears the first x-tick.
- §530 Two-line the international-tuition legend entries.
- §542 State the explicit data-currency split (Canada 2025 / most peers 2024) on the R&D note.
- §543 Add a one-line caveat that researchers-per-1,000 is *intensity*, not output (the favourable-vs-US number is real but easily misread).

---

## Tier 2 — Shared-builder fixes (one change → many charts; high leverage)

- **B1. Range slider on `lines_over_time` + `stacked_area`.** Most-repeated request. Adds a slider to
  ~6 government charts at once: §279 employment-by-level, §285 composition, §321 demographics,
  §332 revenue/spending, §341 expense-by-type (+ §337 budget-by-era, a bespoke `go.Bar`). Effort M.
- **B2. Ranked-bar "x-label to top".** Owner wants the x-axis title promoted to a top title to close the
  blank gap on the aging (§51) and fertility (§54) ranked bars. `ranked_bar` change; site-wide reach. M.
- **B3. `lines_over_time` polish.** y-axis lower-pad option (fixes §528/§531 tuition $0 overlap) +
  a legend-only/muted-series mechanism (needed for §527 muted Alberta/NS/NL and any "load few" case).
  Optionally an `initial_start` like `single_line` (tuition slider §526, rent §198). M.
- **B4. `category_bar_views` parity.** Give it `category_bar`'s self-sizing source note + wrap long
  y-labels — fixes the departments chart (§345 source overlap/left-clip, §346 long names). S–M.
- **B5. Map source-note spacing pass.** Verify `choropleth_groups_map` / `choropleth_map` notes clear
  the map bottom on the city/affordability/crime maps (§107, §133, §191, §196, §234). Mostly verify; S.
- **B6. "Canada is red" de-dup (G11).** Replace the repeated per-chart "Canada is shown in red" with one
  top-of-page note site-wide (§166); part of the broader "pages stand alone" pass. M.

---

## Tier 3 — Feature additions on existing data (each ~M)

- §42 **NPR rebuild** — fix the range-button/data mismatch and add a stacked breakdown by permit type
  (work / study / asylum) from 17-10-0121-01. (Absorbs §41.)
- §83 **Religion "scale of shift"** — add a baseline-year dropdown to `change_bars` (data spans 1871–2021).
- §103 **Crime "what's rising/falling"** — add a national / provinces / top-10-CMA geography selector
  (data already in `statcan_crime_by_type.csv`).
- §99 **Provincial voter turnout** — add provincial elections with a province dropdown (federal is done).
- §148 **Currency** — make it a sub-section and add EUR (BoC `FXEURCAD`), maybe JPY. (§140 likewise:
  give business-investment its own sub-section.)
- §228 / §229 **Income toggles** — household-vs-individual and nominal-vs-real on median income.
- §246 / §249 **Gini & poverty** — drop sparse-coverage countries on load (not just grey them).
- §286 **Public-sector composition** — add a per-capita view. §306 dept change as a stacked-over-time
  view. §314 surface actual executive numbers.
- §160 **Inflation** — add a food sub-components chart. §186 years-of-income — add a dwelling-type selector.
- §437 **Elevation** — add a labelled feature layer (e.g. the Niagara Escarpment ridge).
- §484 **Warming spirals** — add a semi-opaque wedge behind the radial °C ticks so they read over the lines.

---

## Tier 4 — Bigger / structural builds (each ~L)

- §173 / §175 / §192 **Housing page reorder** — lead with the most useful charts and actual dollar
  figures, demote the rebased indices, consider a dashboard-style landing + a consolidated
  "choose-what-to-map" map. (Design call; see Owner decisions.)
- §552 **Innovation page content** — genuinely thin (BERD only). Candidates: patents, VC, BERD-by-industry,
  the productivity/innovation gap.
- §151 **Cost of Living** — broaden so the page better answers "why people feel cost pressure".

---

## Tier 5 — New data / research (needs sourcing first)

- §547 **Government science funding over time** — NSERC/SSHRC/CIHR (tri-council; owner: high value).
- §535 **Tertiary attainment vs peers** — OECD EAG mixes methodologies (Canada excluded from the clean key);
  needs harmonisation. §546 — explore a Canada-only literacy/numeracy series (PIAAC) as the PISA replacement.
- §536 **Representative-institution tuition** (e.g. UofT) — StatCan doesn't publish by institution; needs a
  non-StatCan source.
- §95 **Languages trend over time** — needs a new home-language-by-census-year dataset (à la religion/VM).
- §67 / §68 **Diversity over time** — split White/Indigenous out of "Not a visible minority" (as the map
  does) and pursue 2001 (legacy products are XML/IVT-only).
- §383 **Doctor availability** — provincial / Ontario / by-age cut of the regular-provider series
  (13-10-0096 has the dimensions). §364 — suicide by age/sex (needs a Canada source; WB is total only).
- §200 **Actual rent $ by city** — CMHC average-rent table (34-10-0133).
- §326 **International aid** spending breakdown.
- §468 / §471 **Reanalysis climate maps** — continuous temp/precip with a through-the-year slider (ERA5-class).
- §9 / §10 First-time-home-buyer age + family-formation age. §8 a "missing-middle / millennial stress" topic.
- §193 Map condo vs detached values (data-gated at CT/CMA).

---

## Owner decisions (no build until you choose)

- §4 **Country + province colour-system report** — the big one; explicitly "a report before implementation".
- §11 **Comparator stress-test** — are the 17 right; topical add-ins. (CO₂ China/India context already shipped.)
- §6 / §7 / §112 **Global choropleths** — military spending? other topics? a population-vs-peers map?
- §458 / §432 Merge Protected ↔ Ecozones? §494 Where do permafrost + sea ice belong?
- §460 %-conserved as a bar instead of a map? §31 population as a bar? §47 fold median age into the pyramid?
- §408 Call the section "Well-being" or "happiness"? §323 "Sex" → "gender"? §380 capacity as its own page?
- §169 / §192 Housing dashboard design (gates Tier 4 housing work).
- §22 Blog/updates and §23 civics-education under About — flagged "eventually".
- §144 Oil/US current-account narrative (owner musing).

---

## Data-blocked (upstream releases — not fixable in code; verify on refresh)

- §123 / §283 **Productivity decomposition** — OECD `DSD_PDB` is HTTP-500; the "What drives GDP per
  capita" chart shows its fallback until OECD recovers (no CSV present). Finish when data lands.
- §128 / §130 / §138 US labour 2025 not yet in the OECD feed; §359 life expectancy (2023), §363 suicide
  (2021), §372 alcohol (2020), §381 capacity, §247 Gini (2022), §253 food insecurity (2018-start),
  §526 tuition (starts 2006), §298 federal HR (starts 2010), §316 TBS 2017 snapshot — all source-limited.
- §490 Verify NFDB wildfire 2025 isn't yet published (data-freshness check).

---

## Cross-cutting global rules still open

- **G5 — y-axis scale navigation** (§37, §156, §159, §212, §377): consistent default range + period-aware
  rescale. Needs a strategy decision, then implementation. (Inflation/borrowing/vaccination are the cases.)
- **G7 — "data current to" prominence**: pattern exists but isn't applied site-wide (§134, §178 are instances).
- **G10 — bar-vs-line guideline**: per-chart judgement; open instances at §31, §41, §251, §297, §315, §333.
- **G11 — pages stand alone**: remove cross-page "linking" sentences + the "Canada is red" repetition (§166).
- **G12 — data-currency audit**: one pass to add brief "why this ends in YYYY" notes where useful (most are
  the Data-blocked items above, confirmed source-limited).

---

## Suggested sequencing

1. **Tier 1 sweep** (one or two commits per page-cluster) — clears the bulk of the visible review.
2. **Tier 2 builder fixes** B1–B6 — each lands many charts; do B1 (sliders) and B3 (lines_over_time
   polish) first since they unblock several Tier-1/Tier-3 items.
3. **Tier 3 features** in priority order (NPR rebuild, crime/religion/turnout dropdowns, currency EUR).
4. Pause for **Owner decisions** — especially the colour report (§4) and the housing-dashboard design
   (§169/§192), which gate Tier-4 and the colour pass.
5. **Tier 4–5** builds as sourcing/decisions allow.
