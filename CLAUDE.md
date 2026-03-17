# DataCan (Canada Observatory)

Interactive data visualization website comparing Canada to OECD peers across
population, economics, and science/innovation metrics. Built with Quarto +
Plotly, deployed to GitHub Pages via GitHub Actions.

**Repo:** `CanadaObservatory/CanadaDataObs`
**Live site:** https://canadaobservatory.github.io/CanadaDataObs/

## Architecture

Four-layer design (v2 target):

1. **Source adapters** — `pipeline/sources/` — talk to StatCan, OECD APIs
2. **Transform + validate** — `pipeline/transforms/` — clean data, check schemas
3. **Indicator registry** — `pipeline/config.py` — declarative indicator definitions
4. **Rendering** — `.qmd` files + `charts/` — Quarto pages with Plotly charts

## Project structure

```
DataCan/
├── CLAUDE.md              ← this file
├── _quarto.yml            ← site config, nav, theme
├── index.qmd              ← landing page
├── about.qmd              ← methodology
├── population/index.qmd   ← population charts
├── economics/index.qmd    ← inflation, GDP charts
├── science/index.qmd      ← R&D spending charts
├── pipeline/
│   ├── __init__.py
│   ├── config.py          ← peer groups, table IDs, styling, indicator registry
│   ├── fetch_statcan.py   ← Statistics Canada API
│   ├── fetch_oecd.py      ← OECD SDMX API
│   ├── charts.py          ← reusable Plotly chart builders
│   └── run_pipeline.py    ← orchestrator
├── data/
│   ├── population/        ← cleaned CSVs + metadata JSONs
│   ├── economics/
│   └── science/
├── .github/workflows/
│   └── update-data.yml    ← weekly cron: fetch → commit → deploy
└── requirements.txt
```

## Key commands

```bash
# Run data pipeline (fetches from StatCan + OECD, saves CSVs)
python -m pipeline.run_pipeline

# Preview site locally
quarto preview

# Render site to _site/
quarto render
```

## Data sources

- **Statistics Canada** — via `stats_can` library
  - Population quarterly (17-10-0009-01)
  - Population components (17-10-0014-01)
  - CPI monthly (18-10-0004-01)
- **OECD** — via SDMX REST API (`sdmx.oecd.org`)
  - R&D expenditure (MSTI)
  - GDP per capita (SNA_TABLE1)

## Peer group

20 OECD countries: G7 + Australia, South Korea, Netherlands, Sweden,
Switzerland, Norway, Denmark, Finland, Israel, Austria, Belgium, Ireland,
New Zealand. Canada highlighted in red, peers in grey, OECD average dashed blue.

## Chart conventions

- Canada: `#d62728` (red), width 3, lines+markers
- Peers: `#7f7f7f` (grey), width 1.5
- OECD average: `#1f77b4` (blue), dashed
- Range selector buttons: 1Y, 2Y, 5Y, 10Y, 20Y, All — top-left at `x=0, y=1.01`
- No Plotly titles (Quarto `##` headings serve as titles)
- Source annotations at bottom of each chart
- Legends below x-axis on multi-series charts
- `plot_bgcolor="white"`, grid color `#e0e0e0`

## CPI inflation chart (economics/index.qmd)

Special behavior via inline JavaScript:
- Bar chart with color coding: red (>3%), blue (<1%), grey (in target range)
- Grey band shows Bank of Canada 1-3% target range
- "2% target" label outside plot area (right margin)
- **Y-axis auto-rescaling** via JS polling (every 500ms) because Plotly 3.x
  does NOT fire `plotly_relayout` for rangeselector button clicks
- Uses `el._fullData[barIdx]` for data access (rawY is Float64Array in Plotly 3.x)
- X-axis tick spacing left to Plotly auto-tick (no dtick override)

## GitHub Actions

- **Trigger:** push to main, weekly cron (Monday 6am UTC), manual
- **Pipeline:** fetch data → commit CSVs → Quarto render → deploy to Pages
- Data fetch only runs on schedule/manual (not every push)
- Deploy runs on every push (always rebuilds site from latest code + data)

## Known issues

- Plotly CDN 403 for `plotly-3.4.0.min` (Quarto bundles its own copy, charts work)
- `plotly_relayout` event does not fire for rangeselector buttons in Plotly 3.x
- GDP per capita charts may be blank if OECD API returns empty data

## v2 plan

Priority order for next development phase:

### Phase 1: Foundation (do now)
1. Remove `sys.path.insert` hacks — use `python -m pipeline.run_pipeline`
2. Add metadata sidecar JSONs next to each CSV (source, retrieval date,
   latest observation date, units, transformations)
3. Replace `DATA_DATE = date.today()` with actual dataset freshness from metadata
4. Add column validation in fetch functions — fail loudly on schema changes
5. Separate `data/raw/` from `data/processed/` (raw downloads preserved)

### Phase 2: Indicator registry (do next)
6. Define indicators declaratively in config.py (title, source, fetch_fn,
   transform_fn, validation schema, chart recipe, peer group, unit, frequency)
7. Refactor run_pipeline.py to iterate the registry instead of manual calls
8. Polish CPI as the gold-standard indicator template

### Phase 3: Chart architecture (do later)
9. Two core chart recipes: Canada-highlighted line + ranked bar
10. Standardize visual grammar (subtitles, source notes, latest-value labels)
11. Add core inflation (CPI-trim) as dropdown option on inflation chart

### Deferred
- Full canonical schema (indicator_id, geo, date, value, unit, ...)
- Dataset versioning (hash raw files, log source URLs)
- Run reports (machine-readable pipeline summary)
- Small-multiple and indexed chart recipes
- Mobile-aware layout presets
