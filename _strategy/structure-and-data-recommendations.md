# Structure/reorg + new-data recommendations

**Research deliverable (2026-06-18, overnight). For the owner to review and prioritise.**
Covers the two big task lists from the site review that need research before building: **page
structure/reorganisation** and **new data/charts**. Each item gets feasibility, a source (where
known), rough effort, and a recommendation. Nothing here is built yet — this is for your steer.

Effort key: **S** = an afternoon · **M** = a day or two · **L** = multi-day / heavy data or geometry.

---

## Part 1 — Structure & reorganisation

The site has grown long pages. The review's instinct — break big pages into focused sub-pages and
lead with the most broadly useful chart — is sound. Recommended moves, lowest-risk first:

| # | Move | Effort | Recommendation |
|---|---|---|---|
| 1 | **Move quarterly GDP above** the international GDP comparison (economics) | S | **Do.** Pure reorder; puts the two GDP views together, leads with the Canada-time-series most readers want. |
| 2 | **Mental health → Well-being** (from Health) | S | **Do** as part of giving Well-being more substance (it's thin now). The CCHS chart just moves. |
| 3 | **Combine Gross/Net govt-debt ranked bars** into one dropdown | S | **Do.** Shortens the fiscal page; the dropdown pattern already exists. |
| 4 | **Defence → its own sub-section** within fiscal (heading + the curated chart) | S | **Do** — pairs with the comparator report's "global context" defence idea and the Israel fix already shipped. |
| 5 | **Substance Use reorg**: opioids become a sub-section under a heading; lead the page with the more general tobacco/alcohol/cannabis; bring Health's peer tobacco/alcohol chart onto this page | M | **Do**, but it's the one structural move that also touches narrative — worth a careful pass. The by-age opener is already reworded for this. |
| 6 | **Economy → Trade + Currency sub-sections**; **Borrowing Costs → its own page** | M | **Do.** Trade-exposure and the CAD chart are buried in a very long page and are among the most recognisable to a general reader. Sub-section headers (or a split) surface them. |
| 7 | **Housing → split + a "dashboard" lead**: a short lead page telling the main story (prices, price-to-income, rent) with the long tail of supporting charts on a second page; reorder so actual-dollar/most-useful charts lead | L | **Do, phased.** Biggest payoff, biggest effort. Start with the *reorder* (S) — lead with New Housing Prices, detached-by-city, prices-vs-income, years-of-income — then split later. The "single map, selectable layer" dashboard idea is a separate build (see Part 2). |
| 8 | **Health → split "Health of Canadians" vs "Health-Care System"** | M | **Do.** The page is the site's longest; the split is natural (population health vs. system capacity) and aids navigation. |
| 9 | **Land & Environment tidy-up**: Fire & Ice → **Wildfire** + **Ice** (thematically different); consider Permafrost/Sea-ice → Climate-Change; **Protected areas** merge with Ecozones | M | **Do the Fire/Ice split** (clean). Hold the Protected↔Ecozones merge until the "map the actual parks" build (Part 2) decides that page's shape. |
| 10 | **Per-section landing pages** for the six areas (overview + what's inside + section identity) | M–L | **Worth doing**, and it dovetails with the brand work (each area already has a colour + wave band). Recommend after the within-section splits settle, so each landing can link to a stable structure. |
| 11 | **Blog / "updates" + civics-education** under About | L | **Later** (owner already marked "eventually"). The civics/"how to read a chart / spurious correlations" idea is a strong differentiator but a content project, not a data one. |

**Cross-cutting:** the review's repeated "put the most broadly useful chart at the top, indices and
abstractions lower" is the single highest-value editorial rule — apply it during every split.

---

## Part 2 — New data & charts

Grouped by readiness. The deciding question for this site is always **"is there an authoritative,
auto-refreshable source?"** (per the no-hardcoded-values rule).

### A. Build-ready now — sourced, easy, high value
| Item | Source | Effort | Note |
|---|---|---|---|
| **CO₂ per GDP** (emissions intensity) | OWID `co2_per_gdp` (already pulling OWID) | S | Owner asked; trivial add. Add the prose point that a cold climate + long distances raise our intensity. |
| **Per-capita government employment** | existing employment-by-level ÷ existing population | S | Owner asked; just a derived series + a toggle alongside the absolute chart. |
| **Other inflation components** | StatCan 18-10-0004 sub-indices (shelter, transport, food already in) | S | Owner asked; a components breakdown / small-multiples off a table we already fetch. |
| **Minimum wage over time (nominal + real)** | ESDC minimum-wage database / StatCan; deflate with the CPI we already have | S–M | Strong cost-of-living companion; nominal/real dropdown. |
| **"Canada isn't a small country"** — population vs the peer set (+ maybe world rank) | WB `SP.POP.TOTL` (all countries) | S | Directly answers the owner's People-section point; a simple ranked bar. |
| **Warming-by-season — maximum temperatures** | AHCCD max-temp series (same GeoMet feed already used) | S–M | Data already accessed for the mean; add the max as the owner asked. |

### B. Build after a short source check — feasible, needs a clean feed confirmed
| Item | Likely source | Effort | Note |
|---|---|---|---|
| **Voter turnout** (federal, then provincial) | Elections Canada (federal, official, clean); provincial = per-agency | M (fed) / L (prov) | High civic value (owner keen). Federal is easy + authoritative; provincial is a multi-source fetch — do federal first, provincial as a follow-up with a province dropdown. |
| **Income distribution over time** (year-slider, like the age pyramid) | StatCan income shares by decile/quintile (e.g. 11-10-0193) | M | High value, reuses the pyramid/slider pattern. Confirm the cube has a clean decile series. |
| **Rent in actual $ by city** + **vacancy by city** | CMHC Rental Market Survey by CMA (OGL) | M | Owner asked for both; same source. Addresses "the vacancy chart is misleading as all-Canada." |
| **CREA dwelling-type dropdown** on the detached-price chart | CREA HPI (already used; charts-only) | S | Data already in hand (benchmark-by-type exists); add a type selector. |
| **Government science funding** (NSERC/SSHRC/CIHR) | tri-agency financial reports / federal Estimates; or StatCan GERD-by-funder | M | Owner flagged as "high value." Needs a clean, auto-refreshable cut — most likely GERD-by-funding-sector rather than per-council budgets. Worth the research. |
| **Tertiary attainment over time — Canada only** | StatCan attainment tables | M | Feasible Canada-only. **Peer comparison stays deferred** — the OECD attainment dataflow mixes national methodologies (the documented blocker). |
| **Family-formation age** | StatCan vital stats (mean age of mother at birth; age at first marriage) | M | Feasible for the "Millennial-stress" theme. **First-time-home-buyer age has no clean annual feed** → defer that half. |
| **Households vs individuals / nominal vs real toggles** on income | StatCan 11-10-0190 (has both household & individual; values are real) | S–M | Feasible if both series are in the cube; nominal would need a parallel nominal series. Confirm before promising the toggle. |
| **Provincial fiscal data** (spending/balance/debt by province) | StatCan Canadian Govt Finance Statistics, provincial | L | Valuable and frequently asked, but needs care: provincial vs federal comparability + the consolidation caveats already noted for COFOG. A deliberate build, not a quick add. |

### C. Bigger builds / global maps — feasible but heavy
| Item | Source | Effort | Note |
|---|---|---|---|
| **Map all federal/provincial parks** | CPCAD (Canadian Protected & Conserved Areas Database) | L | The owner's "that would be great." Geometry exists but is heavy (same tract-map weight tradeoffs). Decides the Protected-areas page shape (item 9 above). |
| **Global choropleths** (military spending; population/area "Canada in the world") | WB/SIPRI (defence, all countries); WB population; area is static | M–L | Feasible — the defence series already covers all countries. Start with **one** test global map (the owner's "could a world map even make sense?") before committing to a pattern. |
| **House-price "dashboard"** (one place: real / nominal / rate-of-increase / price-to-income; or one map with a selectable variable) | existing CREA + OECD + census data | L | The owner's recurring "consolidated view" idea, across housing *and* the census maps. High value, genuinely new UI work — prototype on housing once that page is split. |
| **Reanalysis temperature/precip maps with a seasonal slider** | ERA5 (Copernicus) reanalysis | L | The owner's "continuous representation… slider through the year." Powerful but a substantial new data pipeline (gridded reanalysis). Defer behind the lighter wins; the AHCCD station data already carries the warming story. |

### D. The four confirmed topic adds (already greenlit; slot into the above)
Tax structure & redistribution · household financial stress · commute · productivity decomposition.
Quick source read: **commute** (Census journey-to-work — clean), **productivity decomposition**
(OECD/StatCan, builds on the productivity series we have), **tax structure & redistribution**
(OECD Revenue Statistics + StatCan; the redistribution/Gini-before-vs-after-tax angle is strong and
non-partisan-safe if framed descriptively), **household financial stress** (debt-service ratio,
arrears — StatCan/BoC). All four are feasible; **commute** and **productivity decomposition** are the
quickest.

### E. Defer — no clean auto-refreshable source (don't re-propose without one)
- **First-time-home-buyer age** (no clean annual feed).
- **Representative-institution tuition** (e.g. UofT) — per-institution fees aren't a clean feed; the
  aggregated StatCan TLAC series is the reproducible one.
- **Doctor-availability deep-dive (Ontario unattached patients)** — survey-based, Ontario-specific;
  research a source before committing.
- **Homeownership rate** — Census-only; revisit at the 2026 Census (already on the census-refresh list).

---

## Suggested sequencing
1. **Quick structural wins** (items 1–4, 9-Fire/Ice) + **Group-A data adds** (CO₂/GDP, per-capita
   gov't, inflation components, population-vs-peers) — all S, high visible payoff, no new sources.
2. **The two narrative-heavy splits** (Substance Use, Health) + **minimum wage** + **CREA type
   dropdown**.
3. **Economy Trade/Currency/Borrowing split** + **rent/vacancy by city** + **voter turnout (federal)**
   + **income distribution slider**.
4. **The four confirmed topic adds** (commute + productivity-decomposition first).
5. **Per-section landing pages**, **provincial fiscal**, **parks map / global test map**, **housing
   dashboard** — the larger builds, once the page structure has settled.
6. **Defer**: reanalysis maps, blog/civics, the Part-2-E no-source items.

Everything in steps 1–2 could be built without further owner input beyond "go"; steps 3+ benefit from
a quick source-confirmation pass first (flagged "confirm" above).
