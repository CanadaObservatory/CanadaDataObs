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
├── _quarto.yml            ← site config, nav (Economy is a dropdown), theme
├── index.qmd  about.qmd   ← landing + methodology
├── population/index.qmd   ← total, by-province, growth rate, components, non-permanent residents
├── economics/index.qmd    ← real GDP growth, GDP/capita, productivity, business investment, unemployment, employment rate, current account
├── housing/index.qmd      ← CPI inflation, real house prices, price-to-income, NHPI, prices-vs-incomes, rent, housing starts, vacancy rate, household debt
├── income/index.qmd       ← median income, wages, disposable income, Gini, poverty, LIM-AT, food insecurity, neighbourhood income map (choropleth)
├── fiscal/index.qmd       ← govt gross debt, budget balance, revenue, interest costs, defence
├── health/index.qmd       ← life expectancy, avoidable mortality, health spending (%GDP + per person), beds, physicians, nurses, MRI units
├── science/index.qmd      ← R&D (GERD), business R&D (BERD), researchers  (titled "Education & Innovation")
├── environment/index.qmd  ← CO2 per capita, CO2 indexed, consumption CO2, low-carbon electricity, electricity mix (by country + by province), energy mix
├── wellbeing/index.qmd    ← happiness score + factor decomposition, safety (crime severity + homicide)
├── pipeline/
│   ├── config.py          ← Indicator dataclass + INDICATORS registry, peer group, COMPARATOR_COLORS, styling
│   ├── fetch_oecd.py      ← fetch_oecd_indicator (generic SDMX) + _fetch_oecd_csv
│   ├── fetch_statcan.py   ← fetch_statcan_indicator (generic) + bespoke population/CPI
│   ├── fetch_owid.py      ← OWID energy mix + consumption CO2 (bespoke)
│   ├── fetch_worldbank.py ← fetch_worldbank_indicator (generic WB API)
│   ├── fetch_whr.py       ← World Happiness Report (bespoke)
│   ├── metadata.py        ← save_metadata sidecars + validate_columns
│   ├── charts.py          ← peer_comparison_line, ranked_bar, single_line, choropleth_map, ranking_strip
│   ├── build_census_geo.py ← ONE-TIME builder for the census-tract choropleth assets (not weekly)
│   └── run_pipeline.py    ← registry-driven orchestrator
├── data/<section>/        ← cleaned CSVs + metadata JSON sidecars
├── data/geo/              ← static 2021-census choropleth assets (CT GeoJSON + income CSV)
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

## Data sources (50 indicators / 9 sections)

- **Statistics Canada** (bulk CSV-zip by table id): population 17-10-0009-01,
  components 17-10-0008-01, CPI 18-10-0004-01 (All-items + the "Rent" group),
  New Housing Price Index 18-10-0205-01, median after-tax income 11-10-0190-01,
  low income (LIM-AT) 11-10-0135-01, electric power generation by type
  25-10-0015-01 + fuel-level generation 25-10-0084-01 (provincial electricity mix
  with the fossil slice split into coal/gas/oil; bespoke `fetch_provincial_electricity`),
  housing starts 34-10-0143-01 + rental vacancy 34-10-0127-01 (CMHC), food insecurity
  13-10-0835-01, Crime Severity Index 35-10-0026-01, homicide rate 35-10-0068-01,
  non-permanent residents 17-10-0121-01 (all generic single-series `fetch_statcan_indicator`).
- **OECD SDMX** (`fetch_oecd_indicator`): R&D/BERD/researchers (MSTI
  `DSD_MSTI@DF_MSTI`), GDP/capita (`DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_HCPC`),
  productivity (`DSD_PDB@DF_PDB_LV`), unemployment (`DSD_KEI@DF_KEI`), employment
  rate (`DSD_LFS@DF_IALFS_EMP_WAP_Q`), and from the Economic Outlook (`DSD_EO@DF_EO`,
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
- **Our World in Data** — consumption-based CO2 per capita (`fetch_consumption_co2`,
  OWID CO2 dataset / Global Carbon Project), and the energy mix CSV (Energy Institute + Ember + EIA): both
  electricity-generation shares (`*_share_elec`, `low_carbon_share_elec`) and
  primary-energy shares (`*_share_energy`). Energy is framed as **electricity** by
  default (nuclear/hydro properly sized; Canada ≈78% low-carbon) with a labelled
  total-energy secondary; the standalone OECD "renewables share" was dropped.
- **World Happiness Report** — Figure 2.1 XLSX. `WHR_URL` in `fetch_whr.py` must
  be bumped each year (~March).

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
  to free the bottom for the slider + source — no overlap. The 17-country peer
  line charts deliberately keep range buttons only (a right-side 17-name legend is
  unwieldy and their ~25-35yr span is well served by the buttons).
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

## Licensing note (what may NOT be published)

Every public source here permits republication with attribution (StatCan, OECD,
OWID CC-BY, WHR). **CREA MLS® HPI is the exception** — its terms allow downloading
for analysis but bar publishing/displaying the data without CREA's written consent,
which is incompatible with this public repo + CSV downloads. It is the only source
for absolute resale prices by city × dwelling type, so a reference figure is built
**internally only** (`internal/crea_house_prices.py` → `internal/…html`); the whole
`internal/` dir and `*MLS_HPI*` are git-ignored and must never be committed or put
on a page. The published affordability story uses open data instead — the
"Home Prices vs. Incomes" chart (OECD **real** house-price index vs. StatCan
**real** median after-tax income, both rebased to 2000 = 100; by 2025 prices ≈280
vs. income ≈126). Note: keep both lines on the same basis — the income CSV is in
2024 constant dollars (real), so pairing it with a *nominal* price index is wrong;
and NHPI tracks new-build builder prices, which understate the resale run-up, so
the OECD real resale index is used here, not NHPI.

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
- CIHI wait-times have no automated feed (beds/physicians/MRI are the proxies).
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

## Status & what's deferred

Done: registry + generic fetchers (was the v2 plan), metadata sidecars, STALE
fallback, the four new domains (Housing, Income, Health, Public Finances),
comparator highlighting, peer-group trim, health spending per capita, provincial
electricity mix. A 2026-05 reviewer-driven expansion added the scorecard magnitude
column and ~15 indicators: business investment (GFCF), current account, govt
revenue + interest, defence (with the NATO 2% benchmark), nurses, avoidable
mortality, real household disposable income, consumption-based CO2, housing starts
+ vacancy, food insecurity, Crime Severity Index + homicide, non-permanent residents.
Deferred (candidates, not committed):
**homeownership rate** (Census-only — no clean annual StatCan series; revisit when
2026 Census tenure lands), top income shares / wealth (WID — patchy/lagged),
PISA / tertiary attainment (no clean feed), CIHI wait-times (no automated feed),
nurses/CT/ICU subdetail, absolute house prices by city + dwelling type (CREA MLS HPI
— internal only), raw-vs-processed data split, dataset versioning.
