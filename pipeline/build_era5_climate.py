#!/usr/bin/env python3
"""ANNUAL/periodic manual builder (NOT in the weekly registry): ERA5-Land temperature maps.

Pulls ERA5-Land monthly-mean 2 m temperature for Canada from the Copernicus Climate Data
Store (needs ~/.cdsapirc), then builds, for the Climate Change page (environment/climate-change.qmd):

  * **Current mean temperature** — the 1991–2020 climate normal (annual + the 4 seasons,
    kept in the manifest for a season toggle).
  * **Warming** — the change in annual-mean temperature, recent (2016–2025, the latest ten
    full years) minus the mid-century baseline (1951–1980).

Each field is reprojected to **Web-Mercator (EPSG:3857)** and rendered to a transparent WebP
positioned by WGS84 corner coordinates, for the `charts.relief_map` mapbox overlay. A small
PNG preview (lat-lon + province outlines + colourbar) is written alongside for review.

ERA5-Land monthly means lag only ~1 month. Re-run after each refresh and **bump
LATEST_YEAR/LATEST_MONTH** to the newest available month:
    python -m pipeline.build_era5_climate
Heavy CDS pull (75 yr × 12 mo) → not weekly. Deps: cdsapi, xarray, rasterio, matplotlib, Pillow.
Attribution required on every map: "Generated using Copernicus Climate Change Service information".
"""
import json
import logging
from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from PIL import Image
import rasterio
from rasterio.transform import from_origin, array_bounds
from rasterio.warp import reproject, Resampling, transform_bounds, calculate_default_transform

from pipeline.config import DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NC = "/tmp/era5land_monthly_canada.nc"           # cached raw pull (gitignored /tmp)
OUT = DATA_DIR / "geo"                            # committed assets live here
AREA = [84, -141, 41, -52]                        # Canada bbox N,W,S,E
LATEST_YEAR, LATEST_MONTH = 2026, 5               # newest available ERA5-Land month — BUMP each refresh
NORMAL = range(1991, 2021)                        # WMO current normal (fixed)
RECENT, BASE = range(2016, 2026), range(1961, 1991)   # warming: latest 10 full years vs the 1961–1990 reference (matches the page baseline)
SEASONS = {"annual": None, "winter": [12, 1, 2], "spring": [3, 4, 5],
           "summer": [6, 7, 8], "autumn": [9, 10, 11]}


def pull():
    """Download the monthly-means netCDF (idempotent; skip if cached).

    Two requests because the current year is partial: full years 1950..LATEST_YEAR-1 (all
    months) + LATEST_YEAR months 1..LATEST_MONTH."""
    if Path(NC).exists():
        logger.info(f"using cached {NC}")
        return
    import cdsapi
    c = cdsapi.Client()
    base = {"product_type": ["monthly_averaged_reanalysis"], "variable": ["2m_temperature"],
            "time": ["00:00"], "area": AREA, "data_format": "netcdf", "download_format": "unarchived"}
    logger.info(f"pulling ERA5-Land monthly means 1950–{LATEST_YEAR}-{LATEST_MONTH:02d}…")
    c.retrieve("reanalysis-era5-land-monthly-means", {**base,
        "year": [str(y) for y in range(1950, LATEST_YEAR)],
        "month": [f"{m:02d}" for m in range(1, 13)]}, "/tmp/_era5_full.nc")
    c.retrieve("reanalysis-era5-land-monthly-means", {**base,
        "year": [str(LATEST_YEAR)],
        "month": [f"{m:02d}" for m in range(1, LATEST_MONTH + 1)]}, "/tmp/_era5_cur.nc")
    xr.concat([xr.open_dataset("/tmp/_era5_full.nc").load(),
               xr.open_dataset("/tmp/_era5_cur.nc").load()], dim="valid_time").to_netcdf(NC)


def _mean_c(ds, years, months=None):
    """Mean 2 m temperature (°C) over the given years (and months), as a (lat, lon) array."""
    yr, mo = ds.valid_time.dt.year, ds.valid_time.dt.month
    mask = yr.isin(list(years))
    if months:
        mask = mask & mo.isin(months)
    sub = ds.sel(valid_time=ds.valid_time[mask])
    return sub["t2m"].mean("valid_time").values.astype("float32") - 273.15


def _reproject_3857(field, lon, lat):
    """4326 (lat desc, lon asc) → 3857; returns (array, (W, S, E, N) WGS84 corners)."""
    dx, dy = abs(lon[1] - lon[0]), abs(lat[1] - lat[0])
    west, north, south, east = lon.min() - dx/2, lat.max() + dy/2, lat.min() - dy/2, lon.max() + dx/2
    src_t = from_origin(west, north, dx, dy)
    h, w = field.shape
    dst_t, dw, dh = calculate_default_transform("EPSG:4326", "EPSG:3857", w, h, west, south, east, north)
    dst = np.full((dh, dw), np.nan, "float32")
    reproject(field, dst, src_transform=src_t, src_crs="EPSG:4326", dst_transform=dst_t,
              dst_crs="EPSG:3857", resampling=Resampling.bilinear, src_nodata=np.nan, dst_nodata=np.nan)
    W, S, E, N = transform_bounds("EPSG:3857", "EPSG:4326", *array_bounds(dh, dw, dst_t))
    return dst, (W, S, E, N)


def _webp(field3857, cmap, vmin, vmax, path):
    rgba = matplotlib.colormaps[cmap](mcolors.Normalize(vmin, vmax)(np.ma.masked_invalid(field3857)))
    rgba[..., 3] = np.where(np.isfinite(field3857), 1.0, 0.0)        # transparent where no land
    Image.fromarray((rgba * 255).astype("uint8")).save(path, "WEBP", quality=88, method=6)


def _draw_prov(ax, gj):
    for feat in gj.get("features", []):
        g = feat["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            for ring in poly:
                a = np.array(ring)
                ax.plot(a[:, 0], a[:, 1], color="#666", lw=0.4)


def _preview(field, lon, lat, cmap, vmin, vmax, title, path, prov=None, ticksuffix="°C"):
    fig, ax = plt.subplots(figsize=(8, 6.4), dpi=120)
    m = ax.pcolormesh(lon, lat, field, cmap=cmap, vmin=vmin, vmax=vmax, shading="auto")
    if prov:
        _draw_prov(ax, prov)
    ax.set_title(title, fontsize=12)
    ax.set_aspect(1 / np.cos(np.deg2rad(60)))
    ax.set_xlim(lon.min(), lon.max()); ax.set_ylim(lat.min(), lat.max())
    ax.set_xticks([]); ax.set_yticks([])
    fig.colorbar(m, ax=ax, shrink=0.8, label=ticksuffix)
    fig.tight_layout(); fig.savefig(path, bbox_inches="tight"); plt.close(fig)


def _nice(v, step, fn):
    return fn(v / step) * step


def _corners(c):
    W, S, E, N = c
    return [[W, N], [E, N], [E, S], [W, S]]          # TL, TR, BR, BL (lon, lat)


def build():
    pull()
    OUT.mkdir(parents=True, exist_ok=True)
    ds = xr.open_dataset(NC).squeeze()
    lon = np.where(ds.longitude.values > 180, ds.longitude.values - 360, ds.longitude.values)
    lat = ds.latitude.values
    latest = str(ds.valid_time.values.max())[:7]
    prov_path = OUT / "prov_2021.geojson"
    prov = json.load(open(prov_path)) if prov_path.exists() else None
    manifest = {"layers": [], "latest_month": latest,
                "source": "ECMWF Copernicus Climate Change Service — ERA5-Land",
                "attribution": "Generated using Copernicus Climate Change Service information"}

    # ---- current mean (1991–2020 normal); annual + seasons share one scale ----
    means = {k: _mean_c(ds, NORMAL, mo) for k, mo in SEASONS.items()}
    allvals = np.concatenate([f.ravel() for f in means.values()])
    lo = _nice(np.nanpercentile(allvals, 1), 5, np.floor)
    hi = _nice(np.nanpercentile(allvals, 99), 5, np.ceil)
    logger.info(f"mean-temp scale: {lo}..{hi} °C")
    for key, f in means.items():
        f3857, corners = _reproject_3857(f, lon, lat)
        _webp(f3857, "RdYlBu_r", lo, hi, OUT / f"era5_mean_{key}.webp")
        manifest["layers"].append(dict(key=f"mean_{key}", kind="mean", season=key,
            label=f"Mean temperature — {key} (1991–2020 normal)", webp=f"era5_mean_{key}.webp",
            corners=_corners(corners), vmin=lo, vmax=hi, cmap="RdYlBu_r", units="°C"))
        if key in ("annual", "summer", "winter"):
            _preview(f, lon, lat, "RdYlBu_r", lo, hi,
                     f"Mean 2 m temperature — {key} (ERA5-Land, 1991–2020)", OUT / f"_preview_mean_{key}.png", prov)

    # ---- warming: latest 10 full years minus mid-century, annual ----
    anom = _mean_c(ds, RECENT) - _mean_c(ds, BASE)
    amax = max(1.0, _nice(np.nanpercentile(np.abs(anom), 98), 0.5, np.ceil))
    logger.info(f"warming anomaly scale: ±{amax} °C; Canada-land mean Δ = {np.nanmean(anom):.2f} °C")
    a3857, corners = _reproject_3857(anom, lon, lat)
    _webp(a3857, "RdBu_r", -amax, amax, OUT / "era5_warming_annual.webp")
    manifest["layers"].append(dict(key="warming_annual", kind="anomaly", season="annual",
        label="Warming — annual mean, 2016–2025 vs 1961–1990", webp="era5_warming_annual.webp",
        corners=_corners(corners), vmin=-amax, vmax=amax, cmap="RdBu_r", units="°C"))
    _preview(anom, lon, lat, "RdBu_r", -amax, amax,
             "Warming — annual mean, 2016–2025 vs 1961–1990 (ERA5-Land)", OUT / "_preview_warming.png", prov)

    json.dump(manifest, open(OUT / "era5_climate_manifest.json", "w"), indent=0)
    logger.info(f"wrote {len(manifest['layers'])} layers + manifest (data through {latest}) -> {OUT}")


if __name__ == "__main__":
    build()
