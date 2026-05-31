"""
One-time builder for the census-tract choropleth's STATIC assets.

The census is a 5-yearly snapshot (2021; next 2026), so unlike the weekly
indicators these are generated once and committed, NOT run in the weekly pipeline.
Re-run this when a new census lands.

Outputs (committed):
  data/geo/ct_2021.geojson             simplified CT boundaries, WGS84, feature id = CTUID
  data/geo/statcan_ct_income_2021.csv  ctuid, median_income  (2021 Census, 2020 income)

Run:  python -m pipeline.build_census_geo
"""

import io
import os
import json
import zipfile
import requests
import pandas as pd
import geopandas as gpd

GEO_DIR = "data/geo"
BND_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/"
           "boundary-limites/files-fichiers/lct_000a21a_e.zip")
SIMPLIFY_TOL = 0.0005   # ~35 m; balances shape fidelity vs file size
COORD_DECIMALS = 4      # ~11 m precision


def build_income():
    """Median household total income (2020) per census tract, from 98-10-0058."""
    from pipeline.fetch_statcan import _get_table
    df = _get_table("98-10-0058-01")
    incol = [c for c in df.columns if "Median household total income (2020)" in c][0]
    hs = [c for c in df.columns if c.startswith("Household size")][0]
    ht = [c for c in df.columns if c.startswith("Household type")][0]
    tot = df[df[hs].str.startswith("Total", na=False)
             & df[ht].str.startswith("Total", na=False)].copy()
    tot = tot[tot["DGUID"].astype(str).str.contains("S0507")]      # CT-level rows
    tot["ctuid"] = tot["DGUID"].astype(str).str.replace("2021S0507", "", regex=False)
    tot["name"] = tot["GEO"].astype(str)              # e.g. "0001.00 - Abbotsford - Mission"
    tot["median_income"] = pd.to_numeric(tot[incol], errors="coerce")
    out = (tot[["ctuid", "name", "median_income"]]
           .dropna(subset=["median_income"]).drop_duplicates("ctuid"))
    os.makedirs(GEO_DIR, exist_ok=True)
    out.to_csv(f"{GEO_DIR}/statcan_ct_income_2021.csv", index=False)
    print(f"income: {len(out)} census tracts")
    return set(out["ctuid"])


def build_boundaries(income_ctuids):
    print("downloading CT boundary file...")
    z = zipfile.ZipFile(io.BytesIO(requests.get(BND_URL, timeout=300).content))
    z.extractall("/tmp/ct_bnd")
    shp = [f for f in z.namelist() if f.endswith(".shp")][0]
    gdf = gpd.read_file(f"/tmp/ct_bnd/{shp}")
    ctcol = [c for c in gdf.columns if c.upper() == "CTUID"][0]
    gdf = gdf.to_crs(epsg=4326)
    gdf["geometry"] = gdf["geometry"].simplify(SIMPLIFY_TOL, preserve_topology=True)
    gdf["ctuid"] = gdf[ctcol].astype(str)
    gdf = gdf[["ctuid", "geometry"]]
    bnd_ids = set(gdf["ctuid"])
    print(f"boundaries: {len(bnd_ids)} CTs | matched to income: {len(bnd_ids & income_ctuids)}")

    gj = json.loads(gdf.to_json())

    def rnd(o):
        if isinstance(o, float):
            return round(o, COORD_DECIMALS)
        if isinstance(o, list):
            return [rnd(x) for x in o]
        return o

    for feat in gj["features"]:
        feat["id"] = feat["properties"]["ctuid"]
        feat["geometry"]["coordinates"] = rnd(feat["geometry"]["coordinates"])
    path = f"{GEO_DIR}/ct_2021.geojson"
    with open(path, "w") as f:
        f.write(json.dumps(gj, separators=(",", ":")))
    print(f"wrote {path}: {round(os.path.getsize(path)/1e6, 2)} MB")


if __name__ == "__main__":
    ids = build_income()
    build_boundaries(ids)
