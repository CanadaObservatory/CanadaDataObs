# Continuous temperature map — data assessment & plan (2026-06-25)

**Owner ask (offline brief, 2026-06-25):** a *continuous* (raster, not polygon) map of Canadian
temperature for the Climate Change page, showing **(1) current means and maximum temperatures**
and **(2) change over time** (warming), ideally updatable **monthly or seasonally**. Assess which
reanalysis/gridded dataset is **easiest for *this* project** *before* building. This doc is the
assessment + plan; **nothing has been built.**

---

## 1. What "continuous map" means in our stack

A continuous temperature field is a **raster**, not a polygon choropleth. We already have the
exact pattern on the **Elevation page** (`geography/elevation.qmd`): a **Leaflet** map with a live
ECCC/NRCan tile layer + vector overlays, and a fallback `build_geography.relief_map` that renders a
gridded field → coloured **WebP** (matplotlib/rasterio/Pillow) shown as an image overlay. Two
build routes follow from that:

- **(A) Live WMS overlay — minimal build.** Point a Leaflet (or mapbox image) layer at a remote
  **Web Map Service** that already renders the temperature grid as coloured map tiles. *Almost no
  pipeline code* — same risk class as the elevation page's live NRCan hillshade. Time-enabled WMS
  layers give the monthly/seasonal "slider" for free.
- **(B) Fetch the grid → render our own raster.** Pull NetCDF/GeoTIFF, render to WebP per
  month/season/decade, swap frames with a slider/dropdown (like the warming-spiral animation).
  Full styling control; needs `xarray`+`netCDF4` (new deps) on top of the existing
  matplotlib/rasterio/Pillow.

Route A is dramatically easier *if* a suitable open WMS exists — and for Canada, one does (below).

---

## 2. Candidate datasets

"Reanalysis" strictly means model-assimilated fields (ERA5, NARR). For a Canadian temperature map
the **station-interpolated gridded-observation** products (CanGRD, ANUSPLIN) are an equally valid —
arguably *more appropriate and easier* — way to meet the same goal, and are Canadian primary sources.

| Dataset | Type | Res. | Coverage / period | Cadence | Mean / **Max** | Access (key?) | Licence |
|---|---|---|---|---|---|---|---|
| **CanGRD** (ECCC) | gridded obs (from AHCCD) | 50 km | Canada; 1948– (all), 1900– (south of 60°N) | monthly / seasonal / annual | mean-temp **anomalies** (not Tmax) | **MSC GeoMet** OGC API / **WMS** / WCS + Datamart — **NO key** | OGL-Canada |
| **ANUSPLIN** (NRCan/CFS) | gridded obs | 2–10 km | Canada; **1950–2017 (frozen)** | daily/pentad/monthly | **Tmean + Tmax + Tmin** | bulk download — no key | OGL-Canada |
| **ERA5-Land** (ECMWF/C3S) | reanalysis | **9 km** | global; 1950–present (~1–2 mo lag) | hourly→monthly means | 2 m temp **+ max** | **Copernicus CDS API — needs free account + key** | Copernicus (attribution) |
| **ERA5** (ECMWF/C3S) | reanalysis | 25 km | global; 1940–present | hourly→monthly | 2 m temp **+ max** | CDS API (key); also Google Earth Engine (auth) | Copernicus (attribution) |
| **NARR** (NCEP) | reanalysis | 32 km | North America; 1979–present (~1 mo lag) | monthly + daily | Tmean **+ Tmax (daily)** | **NOAA PSL direct NetCDF / OPeNDAP — NO key** | public domain (cite PSL) |
| NCEP-NCAR R1/R2, MERRA-2, JRA-3Q | reanalysis | ≥50 km / coarse | global | monthly | mean (+max) | PSL no-key (R1/R2) / Earthdata key (MERRA-2) | open | 

*Also-rans:* R1/R2 too coarse (~2°) for a nice national map; MERRA-2 needs an Earthdata login; JRA
more involved. Not worth it here.

---

## 3. The decisive factor — we already use MSC GeoMet

`fetch_climate.py` already pulls the **AHCCD** city temperatures from the **MSC GeoMet OGC API**
(`api.weather.gc.ca`), and **CanGRD is published on the same GeoMet service** (OGC API – Coverages,
**WMS**, WCS) — no key, OGL-Canada, NetCDF/GeoTIFF, on-demand clipping/reprojection. CanGRD is also
interpolated **from the very AHCCD network the Climate page already charts**, so it's the most
*consistent* choice. And GeoMet's **WMS** means Route A (live overlay, near-zero pipeline code, the
elevation-page pattern) is available.

---

## 4. Recommendation

**Lead: CanGRD via MSC GeoMet — easiest, most on-brand, no key, monthly/seasonal, already a project
dependency.** It directly answers the **change-over-time** view (gridded temperature *anomalies* at
monthly/seasonal/annual steps; warming since 1948/1900). Build it as a **live GeoMet WMS overlay in
Leaflet** (Route A) for minimal code and a near-zero-maintenance refresh, with the WCS/grid route as
the fallback if we want custom styling.

**The one caveat — "current means and *maximum* temperatures":** CanGRD is *anomalies* of *mean*
temperature, so it does **not** cleanly give absolute current means or **Tmax**. Options, in order
of ease:
1. Pair CanGRD (change-over-time) with the **Climate Normals** baseline (also on GeoMet) to show
   absolute means; accept that **maximum-temperature** maps need a different source.
2. For a true **Tmax** continuous map: **ANUSPLIN** has Tmax at 2–10 km but is **frozen at 2017**
   (fine for a "normals/period" map, not "current"); a true *current* Tmax field needs a reanalysis.
3. If a current, model-based field (mean **and** max, 9 km) is wanted: **ERA5-Land** is best-in-class
   — but it adds the **CDS API-key** dependency (store as a CI secret; monthly/seasonal builder, not
   weekly). **NARR** (NOAA PSL, no key, 32 km, monthly, has daily Tmax) is the easiest *reanalysis*
   if avoiding the key matters more than resolution.

**Net:** start with **CanGRD/GeoMet** for the warming map (cheap, on-brand, no key). Decide the
"maximum temperature" view separately: easiest = Normals/ANUSPLIN for a period map; best = ERA5-Land
(accept the key) for a current mean+max field; middle = NARR (no key, coarser).

---

## 5. Build sketch (only if greenlit)

- **Home:** `environment/climate-change.qmd` (joins the existing CESI anomaly + AHCCD city temps +
  warming spirals). Possibly a second Leaflet page like Elevation if it's heavy.
- **View 1 — warming (change over time):** CanGRD anomaly layer via GeoMet **WMS** in Leaflet, with a
  **time control** (GeoMet layers are time-enabled → monthly/seasonal/annual frames "for free"), a
  diverging blue–red ramp, AHCCD station dots reused from `fetch_climate.py`.
- **View 2 — current means/max:** Normals (means) and, if pursued, ERA5-Land/NARR (max) — decide per §4.
- **Refresh:** GeoMet is a *live* service → Route A needs ~no scheduled fetch (the layer updates at
  source). Route B (own raster) would be a monthly/seasonal manual builder (`build_*` pattern), never
  weekly. CI health-check ping like the elevation NRCan endpoint.
- **Reuse:** the AMD/RequireJS Leaflet-in-Quarto gotcha + Lambert framing from the elevation page
  ([[project_geography_expansion_2026-06]]); `file://`-safe inline vector overlays.

---

## 6. Verify at build time (don't re-derive)
- Exact CanGRD **layer name(s)** on GeoMet (OGC API – Coverages / WMS `GetCapabilities`) + whether a
  **time dimension** is exposed for the slider; confirm CanGRD's current update cadence/version.
- Whether GeoMet serves an absolute **Tmax** grid (vs only CanGRD mean anomalies + Normals).
- WMS legend/colour-ramp control vs rendering our own from WCS NetCDF.
- If ERA5-Land is chosen: CDS-Beta `cdsapi`, the `2m_temperature` + max variable names, and a CI
  secret for the key.
- New deps only if Route B: `xarray`, `netCDF4` (matplotlib/rasterio/Pillow already present).

**Bottom line for the owner:** the easiest, most on-brand path is **CanGRD via MSC GeoMet (WMS
overlay)** — no key, OGL, monthly/seasonal, and we already talk to GeoMet. It nails the *change-over-
time* map immediately. The only real decision is the **maximum-temperature** view: keep it easy
(Normals/ANUSPLIN period map) or go best-in-class current (ERA5-Land, accepting a CDS key).
