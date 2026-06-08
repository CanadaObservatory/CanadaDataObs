# Geography expansion — overnight build (started 2026-06-08, ~5 PM)

Branch: `geography-maps-expansion` (off `lakes-map-and-homepage-polish`). **Do NOT push
or open a PR** until the owner reviews. Commit each map separately. These are **drafts for
review** — the owner does the visual polish pass (colour scales, labels, framing), as with
every map this session. Keep new pages **i18n-ready** per the standing rule.

Order: **temperature → agriculture → watersheds → protected areas → elevation.**

## Status tracker
- [x] 1. Temperature (climate normals) — `geography/climate.qmd` ✅ DONE (658 stations)
- [ ] 2. Agriculture (type / cropland) — `geography/agriculture.qmd`
- [ ] 3. Watersheds (drainage regions) — add to `geography/water.qmd`
- [ ] 4. Protected areas (% conserved) — `geography/protected.qmd`
- [ ] 5. Elevation (distribution chart + best-effort relief) — `geography/elevation.qmd`

## 1. Temperature  [EASY]
ECCC Canadian Climate Normals — station POINT data, OGL-Canada. 1981-2010 subset has a
map-ready GeoJSON; 1991-2020 current = bulk CSV + Composite Station Inventory (coords).
MSC Datamart under https://dd.weather.gc.ca/ ; portal https://climate.weather.gc.ca/climate_normals/
Fields: station, lat/lon, elev, monthly+annual mean temp, total precip (Jan/Jul available).
Build → `data/geo/climate_normals.csv` (station, lat, lon, jan_temp, jul_temp, annual_temp,
annual_precip). Page: `bubble_map` proportional-symbol, Jan/Jul/annual dropdown, diverging
colour (cold→warm); precip a second view.

## 2. Agriculture  [EASY]
StatCan Census of Ag 2021 (OGL): farm type 32-10-0231-01; field crops 32-10-0309-01; land
use 32-10-0249-01. Geography = Census Agricultural Region (CAR, ~80); boundary file from the
2021 census boundary portal (https://www12.statcan.gc.ca/.../boundary-limites/index2021 →
"Census agricultural regions"). Build `data/geo/car_2021.geojson` (simplify like provinces)
+ tidy CSV. Page: dominant farm type → `choropleth_categorical`; cropland share →
`choropleth_map`. AVOID the AAFC 30 m raster.

## 3. Watersheds  [EASY]
StatCan "Drainage regions of Canada" — 25 regions nested under 5 ocean basins (Atlantic,
Hudson Bay, Arctic, Pacific, Gulf of Mexico). Shapefile, OGL.
https://www150.statcan.gc.ca/n1/en/pub/16-201-x/2017000/sec-1/m-c/m-c-1.1.zip
Build `data/geo/drainage_2017.geojson` (dissolve/tag ocean basin) → `choropleth_categorical`.

## 4. Protected areas  [EASY tabular]
ECCC CESI "Canada's conserved areas" CSV, by province/territory, 1990-2024 (30-by-30 /
25-by-2025). https://open.canada.ca/data/en/dataset/2dd0a57d-ebe5-4efa-a0e8-89834eb37709
terrestrial-by-prov CSV under https://www.canada.ca/content/dam/eccc/documents/csv/cesindicators/canada-conserved-areas/
Build `data/<sec>/protected_areas.csv`. Page: choropleth (% terrestrial conserved by prov,
join `prov_2021.geojson`) + national time-series toward 30%.

## 5. Elevation  [MEDIUM — wildcard]
NRCan MRDEM-30 (COG, OGL; multi-TB, stream don't download). National hillshade WMTS exists
but EPSG:3978 (Plotly needs 3857) → projection snag.
- Distribution chart (clean): coarse national DEM once (MRDEM overviews/gdalwarp ~1 km),
  numpy-histogram into bands → tiny CSV → "% of land below 500/1000/1500 m" chart.
- Relief map (TIMEBOXED): try MRDEM WMS static overlay, or reproject one coarse hillshade
  to 3857 + self-host tiles. If it fights back → ship the distribution chart + a note.

## Morning-summary notes (fill as I go)
- network/libs: gov hosts reachable; geopandas OK; **rasterio MISSING** (affects elevation only).
- **MAP 1 Temperature — DONE.** Used the **MSC GeoMet OGC API – Features** (`api.weather.gc.ca/
  collections/climate-normals`) — far cleaner than scraping ~1,500 per-station CSVs: decimal
  lat/lon, NORMAL_ID=1 mean temp / 56 precip, MONTH 1/7/13. 658 stations. New reusable builder
  `charts.point_value_map` (colour-by-value point map + variable dropdown; for diverging data,
  vs bubble_map's size-by-value). Page `geography/climate.qmd`: temp map (Jan/Jul/Annual dropdown,
  RdBu reversed, cmid=0 → blue<0<red) + precip map (Blues). Dropdown restyle verified working.
  **Owner review:** colour scales (RdBu/Blues), marker size/opacity, prose, whether to add the
  Climate page elsewhere in nav. Only 1981-2010 normals are on the Datamart (1991-2020 not there).
- per-map: data source result, aesthetic defaults chosen for owner review, blockers
- elevation outcome:
