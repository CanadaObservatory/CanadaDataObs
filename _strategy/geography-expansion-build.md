# Geography expansion — overnight build (started 2026-06-08, ~5 PM)

Branch: `geography-maps-expansion` (off `lakes-map-and-homepage-polish`). **Do NOT push
or open a PR** until the owner reviews. Commit each map separately. These are **drafts for
review** — the owner does the visual polish pass (colour scales, labels, framing), as with
every map this session. Keep new pages **i18n-ready** per the standing rule.

Order: **temperature → agriculture → watersheds → protected areas → elevation.**

## Status tracker
- [x] 1. Temperature (climate normals) — `geography/climate.qmd` ✅ DONE (658 stations)
- [x] 2. Agriculture (type / cropland) — `geography/agriculture.qmd` ✅ DONE (72 CARs)
- [x] 3. Watersheds (drainage regions) — added to `geography/water.qmd` ✅ DONE
- [x] 4. Protected areas (% conserved) — `geography/protected.qmd` ✅ DONE
- [x] 5. Elevation — `geography/elevation.qmd` ✅ DONE (chart + province map; relief deferred)

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
- **MAP 2 Agriculture — DONE.** Census of Ag 2021 by Census Agricultural Region (72 CARs):
  dominant farm type (32-10-0231-01) + cropland share (32-10-0249-01 ÷ CAR land area). Boundary
  `lcar000a21a_e.zip` → `car_2021.geojson` (0.14 MB). Split NAICS [1121] into beef (112110) vs
  dairy (112120). **#1 REVIEW ITEM — the farm-type METRIC:** it's "dominant **by number of
  farms**", which has two quirks: (a) **dairy never tops a region** by farm count (Quebec leads
  with the broad **"Other crop"** catch-all), and (b) small specialty operations can outvote a
  few large farms. Alternatives to consider: by **area**, or a **specialization / location-quotient**
  index (would surface dairy in QC/ON, fruit in Niagara, etc.). I did NOT pick one — owner's call.
  Cropland-share map (YlGn) is clean and intuitive. Page prose states both caveats.
- **MAP 3 Watersheds — DONE.** StatCan Drainage regions (16-201-X): 25 regions × 5 ocean
  basins → categorical map ("Where the water goes" section on `water.qmd`), Hudson Bay basin
  dominates. `build_drainage()` → `drainage_2017.geojson`. **Size fix:** raw file was 3.1 MB
  (thousands of tiny Arctic islands by *count*); explode→drop parts <50 km²→dissolve got it to
  **0.30 MB**. **Owner review:** region names from the source DBF have a dropped-separator glitch
  (e.g. "FraserLower Mainland" should be "Fraser–Lower Mainland") — only in hover; left as-is.
- **MAP 4 Protected areas — DONE.** ECCC CESI conserved areas: by-province choropleth (Greens,
  2024, PEI 5% → Yukon 21%) + national "30 by 30" trend (Land + Ocean, 1990–2024, with the 30%
  target line). `build_protected_areas()` → 2 small CSVs. **Owner review:** CESI URL is
  **year-stamped** (`.../2025/...`) → bump `CESI_CONS_BASE` each release (like the GHG fetch);
  could move to the weekly registry (fetch_geography.py) for auto-refresh instead of build_geography.
- **MAP 5 Elevation — DONE (the achievable parts; relief map DEFERRED).** `pip install rasterio`
  succeeded. Read NRCan **MRDEM-30** national DTM mosaic VRT (`/vsicurl/…mrdem-30-dtm.vrt`, EPSG:3979)
  at a COARSE overview (no multi-TB download) → `build_elevation()`. Shipped: **distribution chart**
  (% of land by elevation band — 41% 0-200 m, 76% below 500 m, 0.5% above 2 km) + **median elevation
  by province** choropleth (BC 1056 m → PEI 13 m). Both Canadian-primary (MRDEM), clearly labelled
  "coarse/approximate". **DEFERRED — the photographic hillshade/relief map:** genuinely blocked — the
  only NRCan hillshade tile service is **EPSG:3978** and Plotly needs Web-Mercator 3857 (no 3857
  hillshade exists). The viable path is to reproject the coarse MRDEM array 3979→3857, colour-map to a
  PNG, and drop it in as a Plotly mapbox **image layer** — but the geographic-corner alignment needs a
  visual check, so I left it for a collaborative pass rather than spinning on it unattended.

## ✅ ALL 5 MAPS DONE — overnight build complete
Branch `geography-maps-expansion` (off `lakes-map-and-homepage-polish`), **NOT pushed**. 5 commits,
one per map. New nav under Geography: Climate, Agriculture, Elevation, Protected Areas; Watersheds
added to Water. New `charts.point_value_map` builder. **Top review items:** (1) Agriculture farm-type
metric (by-count vs area/specialization); (2) elevation relief image-overlay (deferred); (3) colour
scales + prose throughout; (4) Protected-areas could move to the weekly registry. See per-map notes above.
