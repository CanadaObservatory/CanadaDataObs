# DataCan (Canada Observatory)

Interactive data-visualization website on the **state of Canada** — population,
economy, cost of living, incomes, public finances, health, education, environment,
and well-being — each compared against a group of OECD peers. Built with Quarto +
Plotly, deployed to GitHub Pages via GitHub Actions.

**Repo:** `CanadaObservatory/CanadaDataObs`
**Live site:** https://canadaobservatory.github.io/CanadaDataObs/

Editorial stance: **non-partisan, descriptive, no policy advocacy.** Comprehensive,
comparable, authoritative coverage is the point — the data, peer comparisons, and
official benchmarks (e.g. the Bank of Canada inflation target) do the work; we do
not editorialize "good/bad."

## Architecture

A declarative **indicator registry** drives everything:

1. **Registry** — `pipeline/config.py` — `INDICATORS` is a list of `Indicator`
   dataclasses (the single source of truth: id, section, source, dataflow/key or
   StatCan table+filters, value column, unit, frequency, chart recipe, optional
   transform hook).
2. **Fetchers** — one generic per source. `fetch_oecd.py:fetch_oecd_indicator`
   handles every OECD SDMX series; `fetch_statcan.py:fetch_statcan_indicator`
   handles single-series StatCan tables. Irregular sources (population, CPI, OWID
   energy, WHR) stay bespoke and are referenced by `Indicator.fetch_fn` (a name
   resolved in `run_pipeline.py`).
3. **Orchestrator** — `run_pipeline.py` iterates `INDICATORS`, dispatching on
   `source`. Each indicator is isolated; an empty/failed fetch **keeps the prior
   CSV (STALE)** instead of blanking a chart. Exits non-zero only on a hard
   failure (no data and no prior CSV).
4. **Rendering** — `.qmd` pages call reusable builders in `pipeline/charts.py`.

**To add an indicator:** add one `Indicator(...)` row to `INDICATORS`, then add a
chart block to the relevant `.qmd`. No new fetch function for OECD/StatCan series.

## Project structure

```
DataCan/
├── CLAUDE.md              ← this file
├── _quarto.yml            ← site config, nav (Population, Geography, Economy, Public Finances, Education & Science are dropdowns), theme
├── index.qmd  about.qmd   ← landing + methodology
├── population/index.qmd   ← **Population & Growth** (Population-dropdown landing): total, by-province, growth rate, components, non-permanent residents
├── population/diversity.qmd ← population-group tract map (Viridis, soft 0.6 fill; dropdown incl. derived White & Indigenous) + diversity-over-time chart (census-year + geography dropdown) + per-metro DA diversity links
├── population/religion.qmd  ← religion tract map (Viridis, soft fill) + religion trends (1871–2021 long-run, 1981→2021 change, 2021 composition, 2011-vs-2021 by place) + per-metro DA religion links
├── population/neighbourhoods*.qmd ← per-metro **dissemination-area diversity** maps — Vancouver/Toronto/Montréal/Calgary/Ottawa (DA = StatCan's finest ~400–700-person geography; ~1–3 MB each, built by build_da_profile)
├── population/religion-neighbourhoods*.qmd ← per-metro **DA religion** maps, same 5 metros (religion-neighbourhoods.qmd = Vancouver)
├── geography/index.qmd    ← **Where People Live** (Geography-dropdown landing): population density (province log-scale + by-city) + "Canada in the world" framing
├── geography/land.qmd     ← 15 ecozones (categorical) + land cover by ecozone (dropdown)
├── geography/water.qmd    ← **major lakes & rivers** (40 largest, NRCan Atlas 1:1M; lakes log-shaded by area with a dark outline, rivers in flat blue; light province/territory borders for orientation)
├── geography/fire-ice.qmd ← wildfire (national 1959– bar + **2023 fire locations**: every NFDB fire point sized by area burned) + permafrost zones (categorical) + Arctic sea-ice extent
├── economics/index.qmd    ← real GDP growth, GDP/capita, productivity, business investment, unemployment (+by-city map), employment rate (unemployment + employment have an **age-bracket dropdown**: youth/prime/older/total), current account
├── housing/index.qmd      ← CPI inflation, real house prices, price-to-income, NHPI, prices-vs-incomes, home value + affordability maps (by city) + link to neighbourhood home-value page, rent, housing starts, vacancy rate, household debt
├── housing/neighbourhoods.qmd ← census-tract dwelling-value choropleth (heavy ~3MB; own page)
├── income/index.qmd       ← median income, wages, disposable income, Gini, poverty, LIM-AT, food insecurity, income map (city) + link to neighbourhood-detail page
├── income/neighbourhoods.qmd ← census-tract income choropleth (heavy ~3MB; its own page so the index stays light)
├── fiscal/index.qmd       ← **Government Finances** (Public-Finances dropdown): govt gross debt, budget balance, revenue, interest costs, defence (all vs OECD peers)
├── government/index.qmd   ← **Government Employment** (Public-Finances dropdown): employment by level of government, full public-sector composition (archived), OECD peer comparison, federal public-service headcount/by-department/demographics/executives, + sourced occupational note
├── government/spending.qmd ← **Federal Spending**: revenue & spending %GDP (1961–) + nominal, expense by economic type, by standard object, by department, by function (CCOFOG — all governments)
├── health/index.qmd       ← life expectancy, avoidable mortality, health spending (%GDP + per person), beds, physicians, nurses, MRI units
├── education/index.qmd   ← **Education** (Education-&-Science nav dropdown): university tuition — real by province, domestic vs international, by field (StatCan TLAC 37-10-0045-01 / 37-10-0003-01, bespoke fetch_tuition/_by_field)
├── science/index.qmd      ← **Science** (Education-&-Science dropdown): R&D (GERD), researchers
├── innovation/index.qmd   ← **Innovation** (Education-&-Science dropdown): business R&D (BERD) — starter page to grow
├── environment/index.qmd  ← CO2 per capita, CO2 indexed, consumption CO2, low-carbon electricity, electricity mix (by country + by province), energy mix
├── wellbeing/index.qmd    ← happiness score + factor decomposition, safety (crime severity + homicide + by-city map)
├── pipeline/
│   ├── config.py          ← Indicator dataclass + INDICATORS registry, peer group, COMPARATOR_COLORS, styling
│   ├── fetch_oecd.py      ← fetch_oecd_indicator (generic SDMX) + _fetch_oecd_csv
│   ├── fetch_statcan.py   ← fetch_statcan_indicator (generic) + bespoke population/CPI
│   ├── fetch_owid.py      ← OWID energy mix + consumption CO2 (bespoke)
│   ├── fetch_worldbank.py ← fetch_worldbank_indicator (generic WB API)
│   ├── fetch_boc.py       ← fetch_boc_indicator (generic Bank of Canada Valet API; source="boc", Indicator.boc_series = {col: valet_code})
│   ├── fetch_whr.py       ← World Happiness Report (bespoke)
│   ├── metadata.py        ← save_metadata sidecars + validate_columns
│   ├── charts.py          ← peer_comparison_line, ranked_bar, peer_comparison_line_by_age + ranked_bar_by_age (age-bracket dropdown variants), single_line, choropleth_map (+ log scale), choropleth_categorical, choropleth_groups_map, bubble_map (proportional-symbol map, e.g. wildfire points), add_city_markers + add_boundaries (orient physical-geography maps — city dots, plus province/territory & national boundary line-layer overlays), history_lines, ranking_strip, lines_over_time, stacked_area, category_bar, single_line_multi, category_bar_views. Every choropleth/bubble map carries a **hover on/off toggle** (`_hover_toggle`); ranked bars show one clearly-labelled year (no duplicate "Data as of")
│   ├── build_census_geo.py ← ONE-TIME builder for the census-tract choropleth assets (not weekly)
│   ├── build_geography.py ← ONE-TIME builder for the Geography section's static assets: province/ecozone/permafrost boundaries, province density + % freshwater, CMA density, land cover, **major lakes (build_lakes, NRCan 1:1M waterbodies) + 2023 wildfire points (build_wildfire_points, NFDB)** (not weekly)
│   ├── build_wait_times.py ← ANNUAL builder (not weekly): CIHI wait times (% meeting benchmark, national, by procedure) → data/health/cihi_wait_times.csv; bump CIHI_URL each spring
│   ├── fetch_geography.py ← registry custom fetchers: wildfire (NFDB, annual) + Arctic sea ice (NSIDC, monthly)
│   ├── fetch_environment.py ← registry custom fetchers: GHG emissions national total + by economic sector (ECCC National Inventory Report / CESI; year-stamped URL — bump GHG_RELEASE each spring)
│   ├── fetch_government.py ← Government-section custom fetchers: StatCan workforce (employment by level 36-10-0489-01; public-sector composition by industry 14-10-0027-01 LFS) + federal finance (36-10-0477-01 1961– + GDP 36-10-0222-01; expense-by-type 10-10-0016-01; CCOFOG 10-10-0005-01) + TBS federal public service (open.canada.ca CKAN) + GC InfoBase (standard objects, by-dept, executives)
│   └── run_pipeline.py    ← registry-driven orchestrator
├── data/<section>/        ← cleaned CSVs + metadata JSON sidecars
├── data/geo/              ← static 2021-census choropleth assets (CT income/dwelling-value/visible-minority/religion; CMA unemployment/dwelling-value/value-to-income/crime/visible-minority/religion; visible-minority-by-census-year history; **Geography:** province boundaries + density + %-freshwater, CMA density, ecozone boundaries + land-cover-by-ecozone, permafrost zones)
├── data/geography/        ← weekly/annual Geography series (NFDB wildfire, NSIDC sea ice)
├── data/government/       ← Government section: StatCan workforce+finance, TBS federal public service, GC InfoBase spending/headcount (12 series)
├── .claude/launch.json    ← preview servers: `quarto-preview` (live) and `site` (static _site)
├── .github/workflows/update-data.yml  ← weekly cron: fetch → commit → deploy
└── requirements.txt
```

## Key commands

```bash
python -m pipeline.run_pipeline   # fetch all indicators → data/<section>/*.csv (+ .json)
quarto preview                    # local live preview
quarto render                     # render site to _site/
```

## Indicator registry (pipeline/config.py)

`Indicator` fields: `id, section, source ("oecd"|"statcan"|"custom"), title, unit,
frequency, value_col, source_table, chart_recipe`; OECD: `dataflow, key
(uses {countries} placeholder), start_period`; StatCan: `statcan_table,
statcan_filters (col→value), date_format`; custom: `fetch_fn`; shared: `transform`
(df→df hook, e.g. `_drop_future_years` for OECD Economic Outlook projection years),
`output_subpath`. `Indicator.out_path` → `data/<section>/<source>_<id>.csv`.

OECD SDMX keys are exact and finicky — validate against `sdmx.oecd.org` before
trusting one (probe the dataflow, find the all-total breakdown). Heavy interactive
probing trips a burst HTTP 429; the weekly pipeline (2s spacing, ~25 OECD calls <
60/hr) does not.

## Data sources (64 indicators / 11 sections)

- **Statistics Canada** (bulk CSV-zip by table id): population 17-10-0009-01,
  components 17-10-0008-01, CPI 18-10-0004-01 (All-items + the "Rent" group),
  New Housing Price Index 18-10-0205-01, median after-tax income 11-10-0190-01,
  low income (LIM-AT) 11-10-0135-01, electric power generation by type
  25-10-0015-01 + fuel-level generation 25-10-0084-01 (provincial electricity mix
  with the fossil slice split into coal/gas/oil; bespoke `fetch_provincial_electricity`),
  housing starts 34-10-0143-01 + rental vacancy 34-10-0127-01 (CMHC), food insecurity
  13-10-0835-01, Crime Severity Index 35-10-0026-01, homicide rate 35-10-0068-01,
  non-permanent residents 17-10-0121-01 (all generic single-series `fetch_statcan_indicator`).
  Bespoke multi-series StatCan fetchers: quarterly real GDP 36-10-0104-01 (recession
  chart), university tuition (TLAC 37-10-0045-01 by level + 37-10-0003-01 by field),
  food + CPI-trim core inflation (18-10-0004-01 / 18-10-0256-01), and merchandise
  trade with the US 12-10-0011-01 (export shares for the US, EU and China — scaling
  US dominance against the next-largest markets — + US-vs-rest-of-world balances).
- **Environment & Climate Change Canada** (`fetch_environment.py`, OGL-Canada): GHG
  emissions — national total + by economic sector — on the National Inventory Report
  basis (the series Canada's 40–45%-below-2005 2030 target is defined against; ECCC
  CESI year-stamped CSVs).
- **OECD SDMX** (`fetch_oecd_indicator`): R&D/BERD/researchers (MSTI
  `DSD_MSTI@DF_MSTI`), GDP/capita (`DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_HCPC`),
  productivity (`DSD_PDB@DF_PDB_LV`), unemployment (`DSD_KEI@DF_KEI`), employment
  rate (`DSD_LFS@DF_IALFS_EMP_WAP_Q`) — note the **single-total** KEI/EMP_WAP series
  drive only the scorecard + are kept for the headline; the **age-bracket** trend +
  ranked-bar charts (youth 15–24 / prime 25–54 / older 55–64 / total 15–64, dropdown)
  come from the unified LFS indicators flow `DSD_LFS@DF_IALFS_INDIC` (bespoke
  `fetch_oecd.fetch_labour_by_age` → `oecd_unemployment_by_age.csv` +
  `oecd_employment_by_age.csv`; UNE_LF total ≈ KEI within 0.3 pp). And from the
  Economic Outlook (`DSD_EO@DF_EO`,
  key `{countries}.MEASURE.A`, all `transform=_drop_future_years`): real GDP growth
  GDPV_ANNPCT, gross debt GGFLQ, budget balance NLGQ, current account CBGDPR,
  govt revenue YRGTQ, net interest GNINTQ (the `Q`/PT_B1GQ variants are %GDP), house
  prices + price-to-income (`DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES`), household debt +
  real household disposable income per capita (`DSD_HHDASH@DF_HHDASH_CTRY`; debt
  MEASURE=LES1M_FD4, disposable income MEASURE=B6GS1M_R_POP unit IX, index 2007=100,
  13 countries), Gini + poverty (`DSD_WISE_IDD@DF_IDD`), average
  wages (`DSD_EARNINGS@AV_AN_WAGE`), life expectancy (`DSD_HEALTH_STAT@DF_LE`),
  health spending (`DSD_SHA@DF_SHA` — both % of GDP via `PT_B1GQ`/`PRICE_BASE=_Z`
  and USD PPP per capita via `USD_PPP_PS`/`PRICE_BASE=V`; per-capita needs the
  current-prices `V`, not `_Z`), hospital beds (`DSD_HEALTH_REAC_HOSP@DF_BEDS_FUNC`),
  physicians (`DSD_HEALTH_EMP_REAC@DF_PHYS`), nurses (`DSD_HEALTH_REAC_EMP@DF_NURSE`
  — note the reversed DSD name; HEALTH_PROF=MINU, activity P), MRI units
  (`DSD_HEALTH_REAC_HOSP@DF_MED_TECH`), avoidable mortality (`DSD_HEALTH_STAT@DF_AM`,
  MEASURE=AVM, deaths/100k), CO2 per capita + indexed (Green Growth `DSD_GG@DF_GREEN_GROWTH`).
- **World Bank API** (`fetch_worldbank_indicator`, source="worldbank", `wb_indicator`
  code; JSON, ISO-3 codes match PEER_CODES, CC-BY): business investment / gross fixed
  capital formation %GDP (`NE.GDI.FTOT.ZS`) and defence spending %GDP
  (`MS.MIL.XPND.GD.ZS`, WB-sourced from SIPRI so all 17 peers are covered, not just
  NATO; the defence chart draws the NATO 2%-of-GDP guideline as a benchmark line).
- **Bank of Canada Valet API** (`fetch_boc_indicator`, source="boc", `boc_series`
  = {output_col: Valet series code}; JSON, reproduction permitted with attribution —
  every chart carries "Source: Bank of Canada"). One generic fetcher pulls all of an
  indicator's codes in one request → a wide `[date, cols…]` CSV. Four series (Canada-only,
  auto-updating weekly): **policy rate** (Bank Rate `V122530`, 1935– — the consistent
  long-run policy series, charted vs CPI inflation on cost-of-living.qmd; the early-80s
  ~21% peak); **CAD/US$ exchange rate** (`FXUSDCAD`, 2017–, *CAD per USD* as published →
  higher = weaker loonie; economics page, pairs with US-trade); **prime + conventional
  5-year mortgage rate** (`V80691311` + `V80691335`, 1980–; housing page); and **GoC
  benchmark bond yields by term** (`BD.CDN.{2,3,5,7,10,LONG}YR.DQ.YLD`, 2001–; housing
  page via `single_line_multi` term dropdown — 5-year default, maps to fixed-mortgage
  terms). Note: the daily overnight-target `V39079` starts only 2009, so the long-run
  chart uses the Bank Rate; FX daily series has a 2017 methodology break.
- **Our World in Data** — consumption-based CO2 per capita (`fetch_consumption_co2`,
  OWID CO2 dataset / Global Carbon Project), and the energy mix CSV (Energy Institute + Ember + EIA): both
  electricity-generation shares (`*_share_elec`, `low_carbon_share_elec`) and
  primary-energy shares (`*_share_energy`). Energy is framed as **electricity** by
  default (nuclear/hydro properly sized; Canada ≈78% low-carbon) with a labelled
  total-energy secondary; the standalone OECD "renewables share" was dropped.
- **World Happiness Report** — Figure 2.1 XLSX. `WHR_URL` in `fetch_whr.py` must
  be bumped each year (~March).
- **Geography** (the Geography section) — two registry custom series plus a one-time
  static builder. Registry (`fetch_geography.py`, weekly): **wildfire** area burned
  (NRCan Canadian National Fire Database `NFDB_point_stats.xlsx` — national from the
  summary sheet + by-province from the wide "by agency" sheet, 1959–; `fetch_wildfire`,
  annual) and **Arctic sea-ice extent** (NSIDC Sea Ice Index G02135 monthly NH-extent
  CSVs; `fetch_sea_ice`, monthly). Static (`build_geography.py`, like `build_census_geo`
  — **not weekly**): province/territory boundaries (`lpr_000a21a_e.zip`) + population
  density (Census Profile GEONO=001 char 6, recomputed from pop÷land so the territories
  aren't rounded to 0) + **% freshwater area** (hardcoded NRCan/StatCan land-&-freshwater
  table — stable geographic facts, no clean CSV exists), CMA density (GEONO=002 char 6),
  the 15 terrestrial **ecozones** (AAFC National Ecological Framework via its ArcGIS
  FeatureServer as WGS84 GeoJSON with server-side `maxAllowableOffset` — no reprojection
  needed), **land cover by ecozone** (StatCan 38-10-0177-01, 2020; NRCan's 2.1 GB raster
  is unusable so this pre-summarised table is the path), and **permafrost** zones (NRCan
  Atlas of Canada 5th ed. shapefile, ~1995). See "Geography section maps" below.
- **Government / Public Sector** (the Public-Finances "Government" pages; bespoke
  `fetch_government.py`, all Open Government Licence – Canada). **Workforce:**
  employment by level of government (StatCan **36-10-0489-01** SNA jobs, 1997– —
  NAICS "public administration" = the civil-service bureaucracy only, and federal
  [911] **includes the military**); the whole public-sector workforce by industry —
  public administration vs. public education / health care / Crown corporations
  (**14-10-0027-01**, Labour Force Survey "class of worker", *current*: education ≈
  health > public administration, ~4.55M total); the federal public-service headcount + by-department / age / tenure /
  region / language / sex (**Treasury Board "Federal public service statistics"**,
  open.canada.ca CKAN `f0d12b41…`, 2010–, a March-31 snapshot of core public
  administration + separate agencies, **excl. military/RCMP**); executives vs
  non-executives (**GC InfoBase** `org_employee_ex_lvl`); and the OECD peer anchor —
  general-government employment as a % of total employment (Government at a Glance
  **`DSD_GOV@DF_GOV_EMPPS_REP_2025`**, key `A.{countries}.EMPG.PT_EMP.S13.2025.EMPPS_REP`).
  **Spending:** federal revenue/expenditure/interest 1961– + % of GDP
  (**36-10-0477-01** quarterly→annual flows + **36-10-0222-01** current-prices GDP),
  federal expense by economic type incl. **compensation of employees** (**10-10-0016-01**,
  2008–), spending by **standard object** + by **department** (**GC InfoBase**
  `org_sobjs` + `igoc_en`, latest Public Accounts year), and spending by **function**
  (**10-10-0005-01** CCOFOG — *all governments consolidated, not federal-only*).

## Peer group & comparator colours

**17 OECD countries** (`PEER_COUNTRIES` in config.py): G7 + Australia, South Korea,
Netherlands, Sweden, Switzerland, Norway, Denmark, Finland, Israel, New Zealand.
(Dropped 2026-05: Belgium & Austria as redundant; Ireland because multinational
accounting distorts its GDP/productivity figures.)

Canada is always red. A named **comparator set** gets distinct colours
(`COMPARATOR_COLORS`): US blue, Australia orange, Germany green, UK purple, Sweden
brown. Everyone else is light grey; the peer average is dark-grey dashed. Changing
the highlighted set or peer list is a one-line edit in config.py.

## Chart conventions (pipeline/charts.py)

- `peer_comparison_line(df, x, y, ..., show_average=)` — the standard line chart.
  Canada red+markers on top; comparators coloured; others light grey; optional
  dark-grey-dashed peer average drawn only for years where ≥half the peers report
  (composition-bias guard). Legend: Canada first, then comparators, then other
  peers — each group **alphabetical by name** (via `legendrank`).
- `ranked_bar(df, value_col, xaxis_title, source_note, ...)` — latest-year
  horizontal bar, bars coloured by comparator. Picks the latest year that has
  ≥`min_countries` **and** includes the highlighted country, so Canada is never
  dropped from its own ranked bar when it reports a year behind peers.
- `single_line(..., rangeslider=True, source_note=, hovertemplate=, customdata=)` —
  Canada-only series (NHPI, rent, median/low income, population total/growth).
  `rangeslider=True` adds a draggable **time slider** below the chart for long
  series and owns the source-note placement so it sits below the slider with no
  overlap (these charts have no legend, which is why the slider is clean here).
  It opens on the most recent ~25 years (window starts at 1999 so the 2000 tick
  anchors it); the slider still spans all history and "All" resets the view.
- Multi-line charts that get a slider (population by province & components, Canada
  energy mix over time) move the legend to the **right** (`orientation="v", x=1.02`)
  to free the bottom for the slider + source — no overlap. **The 17-country peer
  line charts now follow the same idiom** (2026-06 review): `peer_comparison_line`
  /`_by_age` plot the year axis as real dates so they carry a draggable **range
  slider** + range-selector buttons, move the legend to the **right**, drop the
  "Year" x-title, **own the source note** (`source_note=` param, placed below the
  slider), and by default (`hide_peers=True`) show only Canada + the colour
  comparators + the peer average at load — the grey peers start `legendonly` and the
  reader adds them via the legend, which de-clutters the busy 17-line charts. Pass
  `initial_start=<year>` to open on a recent window (e.g. 2015 for the GDP charts).
- `page_snapshot(section)` (wraps `ranking_strip`) — the "Where Canada Stands"
  scorecard at the top of each peer-comparison page: one row per indicator, every
  peer a dot ordered **by rank** so further right = more favourable (lower-is-better
  measures are flipped; rank 1 = best), Canada red. Spec per section lives in
  `SNAPSHOT_SPECS` (config.py): `(label, csv path, value col, fmt, good)` where
  `good` is "high"/"low". Rank-based positioning (not value) keeps it outlier-immune,
  but because rank hides magnitude, each row also shows an always-on right-hand label
  with Canada's **value · rank · peer median** (so a tight cluster reads differently
  from a real gap), and a row whose latest year lags the newest row is flagged with
  that year in its label. Only assign a `good` direction where "favourable" is
  uncontroversial — current account and govt revenue are charted but kept off the
  scorecard because higher/lower isn't clearly better.
- `lines_over_time`, `stacked_area`, `category_bar` — generic Government-section
  builders (integer-year safe, neutral `SERIES_PALETTE`, Canada-red reserved for a
  single highlighted series). `lines_over_time`: plain multi-line (no date
  range-buttons) — employment by level, revenue-vs-spending. `stacked_area`:
  composition of a total over time — public-sector sectors, federal expense by type.
  `category_bar`: horizontal ranked bar for non-country categories (departments,
  spending objects, sectors) with an optional `highlight` set.
- Styling: Canada `#d62728`/width 3, peers `#bdbdbd`/width 1.5, average `#555`
  dashed; range buttons 1Y/2Y/5Y/10Y/20Y/All at `x=0,y=1.01`; no Plotly titles
  (Quarto `##` headings are the titles); source note at the bottom;
  `plot_bgcolor="white"`, grid `#e0e0e0`.
- Indexed series (real house prices, price-to-income, CO2-indexed) must NOT be
  ranked as if they were levels — a rebased index shows change from a base year,
  not cross-country levels. House-price ranked bars are labelled "…since 2015".

## Choropleth maps (census-tract income)

`charts.choropleth_map(geojson, df, location_col, value_col, ...)` — a zoomable
Plotly `Choroplethmapbox` with the free `carto-positron` basemap (**no Mapbox
token**); GeoJSON features must carry top-level `id == df[location_col]`. First
use: **median household income by census tract** on the income page (the
"put yourself on the map" view). Key facts:
- **Static census assets, not weekly.** Census is a 5-yearly snapshot, so the CT
  boundaries + income are built **once** by `pipeline/build_census_geo.py` →
  `data/geo/ct_2021.geojson` (simplified to ~2.9 MB, feature id = CTUID) +
  `data/geo/statcan_ct_income_2021.csv` (ctuid, name, median_income from the 2021
  Census table 98-10-0058-01, 2020 income). Re-run on the next census (2026). The
  weekly pipeline does NOT touch these.
- **Page weight** ≈ 3.2 MB for the income page (the GeoJSON is inlined). Acceptable;
  achieved via `geometry.simplify(0.0005)` + 4-decimal coordinate rounding + minified
  JSON. CTs are CMA/urban-only — rural areas are blank (stated on the page).
- **Colour scale is percentile-capped** (5th–95th) so a few ultra-rich tracts don't
  flatten the contrast for typical neighbourhoods.
- **Driving the map from JS** (e.g. preview tests): `window.Plotly` is undefined under
  Quarto's AMD bundle — use `window.requirejs('plotly')` to get the handle for
  `relayout`. (Same gotcha as the CPI rescale JS.)

**City-level (CMA) maps** — `build_census_geo.build_cma()` builds a second, lighter tier:
`data/geo/cma_2021.geojson` (156 metro areas, **0.18 MB**) + `data/geo/statcan_cma_indicators.csv`
(unemployment, median dwelling value, value-to-income, Crime Severity Index per CMA). Sources:
the comprehensive **CMA census profile** (GEONO=002, has Unemployment rate + "Median value of
dwellings ($)" + household income) and crime from 35-10-0026-01 (CSI joined on the 3-digit CMA
code parsed from the `[35535]`-style GEO labels — ~40 CMAs report CSI). Maps drawn from it:
Crime Severity (Society & Well-being) and **median dwelling value + value-to-income** (Housing).
**The by-city unemployment map no longer uses this census snapshot** — switched 2026-06 to the
**live LFS series 14-10-0459-01** (3-month moving average, SA; bespoke
`fetch_statcan.fetch_cma_unemployment` → `data/economics/statcan_cma_unemployment.csv`, **weekly**),
covering the ~41 largest CMAs, joined to `cma_2021.geojson` via the CMA code in the DGUID
(`2021S0503<cmauid>`). The `unemployment` column in `statcan_cma_indicators.csv` is now vestigial. The housing two answer "can we map house prices?" — **yes**, via
the census's *owner-estimated* dwelling value (not sale prices; CREA sale prices stay
internal-only), and value÷income is the affordability map (Vancouver ~11.7×, Toronto ~10× vs
Calgary ~4.6×). Crime/unemployment/housing aren't available at census-tract level cheaply
(labour/housing CT tables are 300–600 MB), so these are CMA-level; CT versions are a future
heavy-extraction option. **Split-province CMA gotcha:** Ottawa-Gatineau (505), Lloydminster
(840) + two others span two provinces and appear as two boundary features sharing one CMAUID —
`build_cma()` **dissolves by CMAUID** (one polygon per CMA), else duplicate feature ids leave
half the CMA uncoloured (this was a real bug — Ottawa showed only the Gatineau side). The crime
join also prefers the **combined** whole-CMA row over a single province "part".

**Dropdown maps** — `charts.choropleth_groups_map(geojson, df, location_col, groups, ...)` adds a
Plotly `updatemenus` dropdown that `restyle`s the mapped variable across `groups`
(each option rescales its own colour range + colorbar/hover to each group's **true min–max** — city *and*
tract maps — so high-share areas never clamp and the colourbar always matches hovered values: Toronto's 57%
reads differently from a 30% city, and a 98.5% census tract reaches the top instead of being pinned under a
90% ceiling. A `cap_quantiles` param exists to clip a long tail if a specific layer ever needs it.) First use: **visible-minority
groups by city** on the Population page (`build_cma_ethnicity()` → `data/geo/statcan_cma_ethnicity.csv`,
CHARACTERISTIC_IDs 1684–1694 from the CMA census profile: All VM / South Asian / Chinese / Black /
Filipino / Arab / Latin American / SE Asian / W Asian / Korean / Japanese, **plus two derived groups, White &
Indigenous** — see below). All shares use the population base id **1683** as denominator. **Most sensitive layer —
deliberately descriptive:** neutral perceptually-uniform **Viridis** scale (colourblind-safe, no red/green valence), no scorecard, no
"good/bad" direction, StatCan's own "visible minority" term, and a note that it's separate from
Indigenous identity and shows only residential geography. **White & Indigenous are *derived*** (added 2026-06):
StatCan's visible-minority variable has no distinct White group and folds Indigenous people into a single "Not a
visible minority" residual (id **1697**). We split that residual with the single-response **Indigenous identity**
variable (id **1403**) on the same base (1683 ≡ Indigenous base 1402, verified identical): `indigenous =
1403/base`, `white = (1697 − 1403)/base` (clamped ≥0 for small-area rounding). So **White is a derived residual**
(the non-Indigenous, non-VM population — what Employment Equity treats as "white") and the three top-level groups
— All visible minorities / White / Indigenous — tile to **exactly 100%** (`_derived_population_groups` in
build_census_geo; dropdown order = `charts.DIVERSITY_MAP_GROUPS`; the derivation method is stated in the page
prose + source notes). Do **NOT** substitute the ethnic-origin "Caucasian (White)" value (id 1715, ≈1%) — it's a
multiple-response write-in, not a population share. This same group list drives the **tract-level** diversity map —
now the **main** Population-page map (Viridis + 0.6 fill, true-range colour) — plus per-metro
**dissemination-area** pages (`population/neighbourhoods-*.qmd` — five metros — each linked from the main page). DAs are StatCan's finest standard
geography (~400–700 people, ~57k nationally), built one CMA at a time by
`build_census_geo.build_da_profile(cmauid, pruid, geono, slug)` — one pass writes both the visible-minority and religion CSVs: boundary `lda_000a21a_e.zip` (~98 MB, no
per-CMA download → spatial-filter to the CMA polygon from `cma_2021.geojson`); data from the DA Census Profile
**GEONO=006** *regional* splits (the data CSV is named `*_CSV_data_<Province>.csv`, ~3.6 GB uncompressed →
chunk-read, filter DGUID `2021S0512`); VM characteristic IDs are identical to the CT profile. **GEONO gotcha:
the GEONO=006 download groups provinces into 6 regional files, NOT one per province** — single-province names
(`006_Alberta`, `006_Manitoba`) 404. The valid tokens (from the download page) are `006_Ontario`, `006_Quebec`,
`006_BC_CB` (=Colombie-Britannique, ~307 MB), `006_Prairies` (MB+SK+**AB**, ~447 MB), `006_Atlantic_Atlantique`,
`006_Territories_Territoires`; `build_da_profile` then filters to the target CMA by `pruid` + the CMA polygon, so
a regional file is fine. **Five metros are built** — Vancouver (`933`/`59`/`006_BC_CB`), Toronto
(`535`/`35`/`006_Ontario`), Montréal (`462`/`24`/`006_Quebec`), Calgary (`825`/`48`/`006_Prairies`),
Ottawa–Gatineau (~1–3 MB each). Ottawa is split-province, so `pruid`/`geono` are passed as lists (`["35","24"]` /
`["006_Ontario","006_Quebec"]`) and the CMA polygon is the dissolved 505; add another metro by calling with its
CMA/PR/GEONO. The 5 canonical calls live in `build_census_geo.build_all_da()`. One page per metro
per topic; a single-page city *selector* (a metro-dropdown swapping geojson+centre alongside the group dropdown)
is deferred. Structure rationale: the coarse city (CMA) map was dropped from the main page in favour of the tract
map, with DA as the finer linked tier. **Religion now mirrors diversity exactly** — tract map on the main page
(`statcan_ct_religion_2021.csv`) + the same five DA pages (`religion-neighbourhoods*.qmd`), all from the same
`build_da_profile` pass (religion population base **1949**, groups `RELIGION_GROUPS`).

**Diversity over time** — `charts.history_lines()` (a generic builder — pass `group_colors` +
`hidden_groups`/`thick_group`; also drives the religion trend below) is a multi-line census-year trend with a Plotly
`updatemenus` **geography dropdown** (Canada / each province·territory / 8 big CMAs); like
`choropleth_groups_map` it `restyle`s only the traces' `y` per geography (x = census years, shared). Data
from `build_vm_history()` → `data/geo/statcan_vm_history.csv` (tidy: geography, geo_level, year, group,
count, share), sourced from the one current cube with a **Census-year dimension**, **98-10-0429-01**
(2006/2011/2016/2021 × Visible minority (15) × geography). **Gotcha: that cube CSV is WIDE in census year** —
values sit in four columns `Census year (4):YYYY[n]`, with no single `VALUE` column. Caveats baked into the
page + chart: its universe is the **population aged 15+** (no 0–14 group → shares run a touch below the
all-ages maps; labelled as such); **2011** was the voluntary NHS (flagged, not hidden); sub-group definitions
drift across decades so the **All-VM total** is the comparable line. "Not a visible minority" defaults to
legend-hidden so the smaller groups are legible. (2001 is a documented best-effort hook, `_vm_history_2001`,
currently a no-op — legacy 2001/2006 census VM products are XML/IVT-only and format-fragile.)

**Religion by city + neighbourhood** — the same `choropleth_groups_map` treatment as the visible-minority
layer. `build_cma_religion()` → `data/geo/statcan_cma_religion.csv` and the same `build_ct_from_profile()`
parse → `data/geo/statcan_ct_religion_2021.csv` (one extra characteristic set in the existing CT pass — no
extra download). Top-level 2021-Census groups (`RELIGION_GROUPS`, base id **1949**): Christian / No
religion-secular / Muslim / Hindu / Sikh / Buddhist / Jewish / Traditional Indigenous spirituality / Other —
the Christian sub-denominations (1952–1966) are rolled into the Christian total (1951). Same deliberately
neutral framing (self-reported, asked only **decennially**, no scorecard/valence); shares the same neutral
perceptually-uniform **Viridis** scale as the diversity map (colourblind-safe, no red/green valence). Drives the city map on
`population/index.qmd` + the CT map on `population/religion-neighbourhoods.qmd`. Toronto sanity: Christian
46.4% / No religion 26.6% / Muslim 10.2%.

**Religion over time** — `build_religion_history()` → `data/geo/statcan_religion_history.csv`, charted with
`history_lines()` on the Population page. There is **no religion-by-census-year cube**, and religion is
**decennial**, so this is a **2-point** trend stitched from two clean censuses on a total-population basis:
2021 from the **wide cube 98-10-0353** (religion in columns; filter Age/Gender = Total, Statistics = "2021
Counts") + 2011 from the **NHS Profile** CSVs (Canada/prov = FMT `CSV101`, CMA = `CSV201`; skiprows=1, name
col is `Prov_Name` vs **`CMA_CA_Name`** respectively, filter Topic="Religion"). Counts (incl. a `_base_` row)
are summed per geography·year before dividing, so **split-province CMA parts (Ottawa–Gatineau) and dup rows
are handled**; the 2021 cube excludes "part" geographies to avoid double-counting. Canada Christian 67%→53%,
No religion 24%→35% (2011→2021). 2011 = voluntary NHS (flagged). This `statcan_religion_history.csv` drives the
**"By province and city, 2011 vs 2021"** dropdown chart (the geographic comparison).

**Religion over time — Canada long-run (1871–2021).** `build_religion_canada_longrun()` →
`data/geo/statcan_religion_canada_longrun.csv`, charted with `history_lines(dropdown=False)` (single-geography,
no selector — added a `dropdown` flag) as the **lead** chart in that section. **16 decennial census points,
Canada only**, on a total-population basis, stitched from primary StatCan products: **1871–1971** = CANSIM
**17-10-0073-01** ("Historical statistics, principal religious denominations"; the ~16 Christian denominations
roll into "Christian", Jewish/No-religion/Other map direct, "denominations unknown" stays in the base);
**1981** = **95F0303X Table 15** total-pop column (the only primary source covering 1981; Christian summed from
its detailed denominations — page IDs are year-paginated: 2001=4068393, 1991=4068394, 1981=**4153162**);
**1991/2001** = the **"Major religious denominations, Canada, 1991 and 2001"** companion table (its Christian
total **includes "Christian n.i.e."**, matching how 2011/2021 roll up — the 95F0303X product lumps n.i.e. into
"Other" and understates Christian, so it is NOT used for 1991/2001); **2011/2021** reused from the history CSV
above. Each gap-year set is verified to sum to its census total. Muslim/Hindu/Sikh/Buddhist begin **1981**
(negligible & inside "Other" before, so those lines start there; **"Other religions" is truncated at 1971** in
the long-run line chart — its broad-catch-all era — so it doesn't appear to still contain them post-1981, and to
avoid a misleading 1971→1981 drop). Christian/No-religion/Jewish span the full series. The long-run chart also
carries a **%/absolute "Show:" toggle** (`history_lines(measures=[...])` — method="update" restyles every
trace's y + the y-axis title; counts show that even Christianity grew in raw numbers as its share fell). Canada
Christian **95%→53%**, No religion **0.2%→35%** (1871→2021). **Use only authoritative primary sources for this site — never Wikipedia or
third-party compilations**, even as a convenient cross-check. 2001 is no longer "omitted" (the prior note); it
and 1981/1991 are now sourced from the published census tabulations above. Two **companion charts** sit in the
same section: `charts.change_bars()` — a diverging horizontal bar of each group's **1981→2021 percentage-point
change** (the "scale of change"; Christian −36 pp vs No religion +27 pp, world religions each >4×), coloured by
the same group palette, labels inside the long bars (`textposition="auto"`); and `charts.composition_bars()` —
a **100%-stacked** 2021 composition across Canada + the 8 big CMAs (from `statcan_religion_history.csv`, ordered
by Christian share), showing Toronto/Vancouver's diversity vs Montréal's Christian majority. Both derive from
existing CSVs (no new data file).

**Geography section maps** (`geography/index.qmd`, static assets from `build_geography.py` + the two
`fetch_geography.py` series). Reuses the choropleth builders and adds one primitive:
`charts.choropleth_categorical(geojson, df, location_col, cat_col, …)` — a discrete-colour map for
*categories* (Plotly's Choroplethmapbox is value-based, so each category maps to an integer over a
hard-stepped colourscale, the colourbar is hidden, and the legend is drawn with zero-point
`Scattermapbox` proxies — verified to render). Also added a `log=True` option to `choropleth_map`
(base-10 colour scale, colourbar ticks relabelled to real values; hover always shows the true value
via customdata). Seven maps + two time charts, no scorecard (descriptive, like the diversity/religion
maps); page ≈ 1.1 MB (province/ecozone/permafrost/CMA GeoJSON each < 0.2 MB, inlined):
- **Population density** — province choropleth on a **log** scale (PEI ~27 vs Nunavut ~0.02/km²).
  Density is recomputed **pop ÷ census land area**, NOT the published characteristic 6, which rounds
  the territories to `0.0` (log of 0 → blank). Plus a by-CMA density map (same log treatment).
- **Ecozones** (categorical) + **land cover by ecozone** (`choropleth_groups_map` dropdown, YlGn).
  Both key on a per-polygon **unique `fid`** (25 polygons / 15 zones) so non-contiguous zones don't
  collide on a shared id (same dup-id trap as Ottawa–Gatineau). Land cover is **by ecozone, not
  province** — table 38-10-0177-01 has no province dimension.
- **Major lakes & rivers** (`geography/water.qmd`) — the 40 largest waterbodies (NRCan Atlas 1:1M); lakes
  log-shaded by surface area with a dark outline, and the three river features (Mackenzie/Yukon/Peace) split into a
  separate **flat-blue** trace so they read as water, not borders. Light province/territory boundaries
  (`add_boundaries` line-layer from `prov_2021.geojson`, below the fills) orient the map — their southern edges
  trace the Canada–US line, so no standalone national outline is drawn (an earlier dissolved-provinces national
  outline was tried but dropped as too heavy/distracting). The earlier **% freshwater-area-by-province** map was
  dropped as uninformative; its `pct_freshwater` column is still built (still in `statcan_prov_geography.csv`),
  just no longer mapped. Unlike the other Geography maps it carries **no explicit `add_city_markers` overlay** —
  the carto basemap's own labels reveal place names as you zoom in, which keeps the default national view
  uncluttered. Surface **area** is the only physical attribute: the 1:1M waterbodies layer is outline-only (**no
  depth/volume**), and there is no authoritative all-Canada lake-volume dataset, so volume is deliberately omitted
  rather than hardcoded from mixed third-party sources (don't re-propose without a primary source).
- **Wildfire** — national annual area-burned bar (1959–; 2023 = 17.6 M ha record) + a **2023
  by-province choropleth normalised to % of each province's land area** (raw hectares would just
  track province size: pct = ha ÷ land-km²). NFDB "by agency" sheet is wide & irregular (Nunavut
  block has no `TOTAL_HA`; Parks Canada "PC" is federal → in the national total only) → parsed by
  forward-filling the agency code across each block and taking that block's exact `TOTAL_HA` column.
- **Permafrost** (categorical, ordinal blues) — NRCan Atlas 5th ed.; dissolved to 4 zones, subsea
  (`U`) + no-permafrost (`O`) dropped; labelled **~1995 vintage (extent has since retreated)**.
- **Arctic sea-ice extent** — September minimum + March maximum lines (NSIDC G02135); no clean
  Canadian-only series (CIS has no flat-file API), so Arctic-wide is used and cited.

**City → neighbourhood level-of-detail (separate page, not JS lazy-load).** The income map shows
the light **CMA** layer on `income/index.qmd` (page **365 KB**) with a link to a dedicated
`income/neighbourhoods.qmd` that **embeds** the full ~6,000-tract choropleth (that page ≈3 MB). The
heavy tract layer therefore loads only when the user navigates to it, the index stays fast, and —
crucially — it **works from `file://` too** (everything is embedded; nothing is fetched). We first
tried JS `fetch()` lazy-loading on one page, but browsers block `fetch()` of local files on
`file://` (the reviewer opens rendered files directly), so the separate-page approach is the robust
pattern and the one to reuse for future tract maps. (`build_ct_income_geojson()` still emits a
combined `data/geo/ct_income_2021.geojson` as a data download.)

**Now extended to home value + diversity** (`build_ct_from_profile()`): both the CT **dwelling value**
(`statcan_ct_dwelling_value_2021.csv`, 6,054 tracts) and the CT **visible-minority shares**
(`statcan_ct_ethnicity_2021.csv`, 6,158 tracts) come from the **same** one-time download — the comprehensive
Census Profile *for census tracts*, **98-401-X2021007** (`GetFile.cfm?…&GEONO=007`, ~238 MB zip, multi-GB
uncompressed). It's read in **chunks** (keep only `DGUID` contains `S0507` = CT rows + the needed
characteristics: dwelling-value id 1488 resolved by name, VM ids 1683–1697 + Indigenous-identity id 1403 for the
derived White/Indigenous split) so memory stays bounded, and the
zip is cached to `/tmp` so re-runs are cheap. CTUIDs are derived `DGUID.replace("2021S0507","")` — identical to
`build_income()`, so they match the existing `ct_2021.geojson` geometry (which is **reused**, no new boundary
download; both new CSVs join 100%). Pages: `housing/neighbourhoods.qmd` (dwelling value, `choropleth_map`) and
`population/neighbourhoods.qmd` (diversity dropdown, `choropleth_groups_map`), each linked from its index page
like the income one. Crime still has no tract data; unemployment/value-to-income would each need their own CT
extraction. **None of this is weekly** — it's a one-time census build in `build_census_geo.py`.

## CPI inflation chart (housing/index.qmd — moved from economics)

Bar chart with red(>3%)/blue(<1%)/grey(in-range) bars, the BoC 1–3% target band,
and a 2% dashed line. **Y-axis auto-rescale** via 500 ms JS polling because Plotly
does not fire `plotly_relayout` for rangeselector clicks; it targets the page's
first plot (`plots[0]`), so the CPI chart must stay first on its page. Caveat:
the JS needs `window.Plotly`, which Quarto's AMD-loaded bundle does not always
expose (the chart still renders correctly; only the rescale-on-button is affected).

## GitHub Actions (update-data.yml)

Push to main, weekly cron (Mon 6am UTC), or manual. Data fetch runs on
schedule/manual only; deploy runs on every push (renders from latest code + data).
`continue-on-error` + the STALE fallback mean a transient source outage won't
fail the build or blank a chart.

## Licensing note (CREA — published as charts only, with permission)

Every source here permits republication with attribution (StatCan, OECD, OWID CC-BY,
WHR). **CREA MLS® HPI** was previously internal-only; **as of 2026-06 we have CREA's
written permission for educational public use on this site**, so it is now published —
but **as charts only, not as a redistributable dataset**. Rules that preserve that:
- **Never commit or write CREA data to `data/`, and never offer it as a CSV download.**
  A committed CSV = redistribution; only the rendered *charts* are published (display,
  which the permission covers).
- `pipeline/crea.py` loads the monthly HPI workbook (`Seasonally Adjusted (M).xlsx` in
  `MLS_HPI_<Month>_<Year>.zip`) at **render time** — cached in the git-ignored
  `internal/` dir; a fresh CI checkout downloads the latest month — and builds the
  figures. Page blocks wrap it in try/except → "temporarily unavailable" if the fetch
  fails (no STALE CSV fallback, by design; needs `openpyxl`, already in requirements).
- **Every CREA figure carries `crea.ATTRIB`**: "Source: CREA MLS® Home Price Index,
  © The Canadian Real Estate Association. Used with permission for educational purposes."
- Housing page CREA charts: benchmark price by city × dwelling type; detached price
  over time by city; national price-to-income over time (≈5.7×→9.3×, 2005→2024 — CREA
  composite deflated to 2024 $ via CPI ÷ real median income). `internal/crea_house_prices.py`
  stays as the original reference builder; `*MLS_HPI*` zips stay git-ignored.

The open-data **"Home Prices vs. Incomes"** chart (OECD **real** house-price index vs.
StatCan **real** median after-tax income, both rebased to 2000 = 100) is kept as a
complementary, fully-open cross-check. Keep both lines on the same basis — the income
CSV is 2024 constant dollars (real), so pairing it with a *nominal* price index is wrong;
and NHPI tracks new-build builder prices, which understate the resale run-up.

## Known issues / gotchas

- `window.Plotly` undefined under Quarto's bundled Plotly → CPI rescale JS may not
  fire (pre-existing; chart renders fine).
- OECD Economic Outlook `DSD_EO` returns ~2 forecast years; capped by
  `_drop_future_years`, charts note "recent years are projections".
- `labour_productivity` (PDB_LV) intermittently returns HTTP 500 server-side →
  rides the STALE fallback.
- PISA / tertiary attainment deferred: the OECD education attainment dataflow mixes
  national survey methodologies (excluded Canada from a fixed-methodology key);
  needs harmonisation. PISA has no clean SDMX feed.
- CIHI wait-times have no automated feed, so they are NOT in the weekly pipeline;
  the Health page charts the % meeting the pan-Canadian benchmark via
  `build_wait_times.py` — an **annual manual builder** (downloads CIHI's XLSX data
  tables; bump `CIHI_URL` each spring). Beds/physicians/MRI remain the
  internationally comparable proxies.
- Energy: nuclear in *primary energy* (~6% for Canada) looks low because primary
  energy is dominated by transport/heating fuels — that's the denominator, not a
  bug. The page leads with *electricity* shares where nuclear is ~13% (Ontario
  ~50%) and Canada's grid is ~78% low-carbon. "Low-carbon" = renewables + nuclear;
  prefer it over "renewables" (which omits nuclear) for the decarbonisation lens.
- Provincial electricity (25-10-0015-01) is **generation** (actual output, latest
  12 months), not installed capacity — gas shows at its real ~17% national share,
  not its larger peaking capacity. Turbine types are bucketed Hydro/Nuclear/Wind/
  Solar/Biomass + a fossil total; since that table only knows *turbine* type (steam/
  combustion), not fuel, the fossil slice is split into **Coal/Natural gas/Oil** by
  the fuel-level generation shares in **25-10-0084-01** (latest annual) — coal is
  worth separating (≈2× the CO2/kWh of gas; Nova Scotia ~42% coal, Saskatchewan ~28%,
  Alberta now ~2% after its coal→gas switch, Ontario 0%). Shares computed off the
  bucket sum (≈100%; tidal & misc omitted). On its stacked bar the long province names force a wide left
  margin, so the legend sits **on top** (a bottom legend wraps and collides with
  the source note); like every chart here the bottom source note still clips at
  mobile widths (deferred mobile-layout work), but fits the ~800px desktop column.
- **Federal workforce by occupation is NOT published as a reproducible series.**
  GC InfoBase's People module has only tenure/age/EX-level/language/sex/region; TBS
  open data and the PSC PSEA-population dataset have no occupational-group population;
  and the classification itself broke (1993 categories repealed, 1999 Universal
  Classification Standard 72→29 groups, CS→IT). The workforce page therefore uses the
  **executive vs non-executive** split (the one clean role axis) plus a sourced note
  (TBS Demographic Snapshot 2017: knowledge groups AS/PM/CS/EC/EX rose 31.8%→42.6% of
  the core public administration, 2000→2017; executives +56%). Don't re-attempt an
  occupation time series without a new authoritative source.
- **No federal-only COFOG split** — 10-10-0005-01 only offers "consolidated Canadian
  general government" (all levels) or P/T-local; the federal residual is contaminated
  by the netting of transfers to provinces (it badly understates federal health), so
  the by-function chart is labelled **all governments**.
- **36-10-0477-01 is quarterly only** (unadjusted flows summed to annual) and has **no
  compensation line** — use 10-10-0016-01 for federal compensation (2008–). GDP for the
  %-of-GDP view is 36-10-0222-01 (1981–), so %-of-GDP starts 1981 while the dollar
  series runs from 1961.
- **GC InfoBase** spending is a **5-year rolling Public Accounts window** with no
  in-file year labels (charts say "latest Public Accounts"); files are committed CSVs at
  `github TBS-EACPD/infobase /data` (`master` moves ~weekly). Standard objects 1–12 are
  budgetary (1=Personnel, 10=Transfers, 11=Public debt charges); 21/22 are
  revenue-netting (excluded). `igoc_en.csv` is UTF-8, the People CSVs are latin-1/ASCII
  (the fetcher tries utf-8-sig then latin-1); the SOBJ9 source label typo "equipement"
  is corrected in the fetcher.
- The "whole public sector" composition uses the **LFS class-of-worker** cube
  **14-10-0027-01** ("Public sector employees" × NAICS industry, current to 2025) —
  public administration (all levels) vs. public education / health care / Crown
  corporations. It replaced the institutional-sector table 10-10-0025-01, which
  StatCan discontinued in 2011 (that table is no longer used).

## Status & what's deferred

Done: registry + generic fetchers (was the v2 plan), metadata sidecars, STALE
fallback, the four new domains (Housing, Income, Health, Public Finances),
comparator highlighting, peer-group trim, health spending per capita, provincial
electricity mix. A 2026-05 reviewer-driven expansion added the scorecard magnitude
column and ~15 indicators: business investment (GFCF), current account, govt
revenue + interest, defence (with the NATO 2% benchmark), nurses, avoidable
mortality, real household disposable income, consumption-based CO2, housing starts
+ vacancy, food insecurity, Crime Severity Index + homicide, non-permanent residents.
A **2026-06 addition built the Government section** (the "Public Finances" nav item is
now a dropdown): a **public-service workforce** page (employment by level of government,
the full public-sector composition, federal headcount + by-department + demographics +
executives, and the OECD peer employment share) and a **federal spending** page
(revenue/spending % of GDP since 1961 + nominal, expense by economic type, by standard
object, by department, by function) — **12 new indicators** via `fetch_government.py`
(StatCan + Treasury Board open data + GC InfoBase) plus 3 reusable chart builders.
Deferred (candidates, not committed):
**homeownership rate** (Census-only — no clean annual StatCan series; revisit when
2026 Census tenure lands), top income shares / wealth (WID — patchy/lagged),
PISA / tertiary attainment (no clean feed),
nurses/CT/ICU subdetail, absolute house prices by city + dwelling type (CREA MLS HPI
— internal only), raw-vs-processed data split, dataset versioning, **federal public
service by occupational group over time** (no reproducible authoritative series — TBS
Demographic Snapshots only; see the gotcha above).
