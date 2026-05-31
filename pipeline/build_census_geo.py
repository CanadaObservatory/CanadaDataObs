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


CMA_BND_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/"
               "boundary-limites/files-fichiers/lcma000a21a_e.zip")
COMP_CMA_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/"
                "download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=002")


def build_cma():
    """City-level (CMA/CA) choropleth assets: unemployment, median dwelling value,
    value-to-income (dwelling value / household income — an affordability proxy),
    and Crime Severity Index. Crime is only published at this geography, so the
    whole batch is built at CMA for consistency. Dwelling value is owner-estimated
    (2021 Census), not sale prices."""
    from pipeline.fetch_statcan import _get_table

    # --- census indicators from the comprehensive CMA profile (GEONO=002) ---
    z = zipfile.ZipFile(io.BytesIO(requests.get(COMP_CMA_URL, timeout=300).content))
    csvn = [n for n in z.namelist() if n.endswith("_data.csv")][0]
    with z.open(csvn) as f:
        prof = pd.read_csv(f, encoding="latin-1", dtype=str,
                           usecols=["ALT_GEO_CODE", "GEO_NAME", "CHARACTERISTIC_NAME", "C1_COUNT_TOTAL"])
    prof["CHARACTERISTIC_NAME"] = prof["CHARACTERISTIC_NAME"].str.strip()
    prof["v"] = pd.to_numeric(prof["C1_COUNT_TOTAL"], errors="coerce")

    def ser(pred):
        s = prof[prof["CHARACTERISTIC_NAME"].apply(pred)].drop_duplicates("ALT_GEO_CODE")
        return s.set_index("ALT_GEO_CODE")["v"]

    une = ser(lambda c: c == "Unemployment rate")
    dv = ser(lambda c: c == "Median value of dwellings ($)")
    inc = ser(lambda c: "edian total income of household" in c.lower() and "2020" in c)
    names = prof.drop_duplicates("ALT_GEO_CODE").set_index("ALT_GEO_CODE")["GEO_NAME"]
    ind = pd.DataFrame({"name": names, "unemployment": une, "dwelling_value": dv, "median_income": inc})
    ind["value_to_income"] = (ind["dwelling_value"] / ind["median_income"]).round(2)
    ind.index.name = "cmauid"
    print(f"CMA indicators: {len(ind)} | unemp {ind.unemployment.notna().sum()} | "
          f"dwelling_val {ind.dwelling_value.notna().sum()} | income {ind.median_income.notna().sum()}")

    # --- Crime Severity Index by CMA (latest year) ---
    crime = _get_table("35-10-0026-01")
    csi = crime[crime["Statistics"] == "Crime severity index"].copy()
    yr = csi["REF_DATE"].max()
    csi = csi[csi["REF_DATE"] == yr]
    csi["cmauid"] = csi["GEO"].astype(str).str.extract(r"(\d{5})")[0].str[-3:]  # prov(2)+cma(3) -> cma
    csi["csi"] = pd.to_numeric(csi["VALUE"], errors="coerce")
    # split CMAs (Ottawa-Gatineau etc.) appear as province "parts" + a combined row;
    # prefer the combined whole-CMA figure over a single part
    csi["_ispart"] = csi["GEO"].str.contains("part", case=False, na=False).astype(int)
    csi = csi.dropna(subset=["cmauid", "csi"]).sort_values("_ispart")
    csi_s = csi.drop_duplicates("cmauid", keep="first").set_index("cmauid")["csi"]
    ind["crime_severity"] = csi_s
    print(f"crime: matched {ind.crime_severity.notna().sum()} CMAs (year {yr})")

    os.makedirs(GEO_DIR, exist_ok=True)
    ind.reset_index().to_csv(f"{GEO_DIR}/statcan_cma_indicators.csv", index=False)

    # --- CMA boundaries ---
    bz = zipfile.ZipFile(io.BytesIO(requests.get(CMA_BND_URL, timeout=300).content))
    bz.extractall("/tmp/cma_bnd")
    shp = [f for f in bz.namelist() if f.endswith(".shp")][0]
    gdf = gpd.read_file(f"/tmp/cma_bnd/{shp}")
    uid = [c for c in gdf.columns if c.upper() == "CMAUID"][0]
    gdf = gdf.to_crs(epsg=4326)
    gdf["cmauid"] = gdf[uid].astype(str)
    # merge cross-province CMAs (Ottawa-Gatineau, Lloydminster, …) that the file
    # splits into same-CMAUID province parts — otherwise duplicate feature ids
    # leave half the CMA uncoloured.
    gdf = gdf.dissolve(by="cmauid", as_index=False)[["cmauid", "geometry"]]
    gdf["geometry"] = gdf["geometry"].simplify(0.004, preserve_topology=True)
    print(f"CMA boundaries: {len(gdf)} | match indicators: {len(set(gdf.cmauid) & set(ind.index))}")
    gj = json.loads(gdf.to_json())

    def rnd(o):
        if isinstance(o, float):
            return round(o, COORD_DECIMALS)
        if isinstance(o, list):
            return [rnd(x) for x in o]
        return o

    for ft in gj["features"]:
        ft["id"] = ft["properties"]["cmauid"]
        ft["geometry"]["coordinates"] = rnd(ft["geometry"]["coordinates"])
    path = f"{GEO_DIR}/cma_2021.geojson"
    with open(path, "w") as f:
        f.write(json.dumps(gj, separators=(",", ":")))
    print(f"wrote {path}: {round(os.path.getsize(path)/1e6, 2)} MB")


# Visible-minority groups: (census CHARACTERISTIC_ID in the 2021 profile, column, label).
# Descriptive only — no evaluative direction. "Visible minority" is StatCan's term.
VM_GROUPS = [
    (1684, "all_vm", "All visible minorities"),
    (1685, "south_asian", "South Asian"),
    (1686, "chinese", "Chinese"),
    (1687, "black", "Black"),
    (1688, "filipino", "Filipino"),
    (1689, "arab", "Arab"),
    (1690, "latin_american", "Latin American"),
    (1691, "southeast_asian", "Southeast Asian"),
    (1692, "west_asian", "West Asian"),
    (1693, "korean", "Korean"),
    (1694, "japanese", "Japanese"),
]


def build_cma_ethnicity():
    """Per-city share of each visible-minority group (2021 Census), for a
    dropdown choropleth. % = group count / population on the visible-minority
    base. Strictly descriptive (where people live); no scorecard, neutral colours."""
    z = zipfile.ZipFile(io.BytesIO(requests.get(COMP_CMA_URL, timeout=300).content))
    csvn = [n for n in z.namelist() if n.endswith("_data.csv")][0]
    with z.open(csvn) as f:
        df = pd.read_csv(f, encoding="latin-1", dtype=str,
                         usecols=["ALT_GEO_CODE", "GEO_NAME", "CHARACTERISTIC_ID",
                                  "CHARACTERISTIC_NAME", "C1_COUNT_TOTAL"])
    df["CHARACTERISTIC_ID"] = pd.to_numeric(df["CHARACTERISTIC_ID"], errors="coerce")
    df["v"] = pd.to_numeric(df["C1_COUNT_TOTAL"], errors="coerce")
    names = df.drop_duplicates("ALT_GEO_CODE").set_index("ALT_GEO_CODE")["GEO_NAME"]
    denom = (df[df["CHARACTERISTIC_NAME"].str.strip().str.startswith(
                 "Total - Visible minority for the population", na=False)]
             .drop_duplicates("ALT_GEO_CODE").set_index("ALT_GEO_CODE")["v"])

    def by_id(cid):
        return (df[df["CHARACTERISTIC_ID"] == cid].drop_duplicates("ALT_GEO_CODE")
                .set_index("ALT_GEO_CODE")["v"])

    out = pd.DataFrame({"name": names})
    for cid, col, _ in VM_GROUPS:
        out[col] = (by_id(cid) / denom * 100).round(1)
    out.index.name = "cmauid"
    out = out.dropna(subset=["all_vm"])
    os.makedirs(GEO_DIR, exist_ok=True)
    out.reset_index().to_csv(f"{GEO_DIR}/statcan_cma_ethnicity.csv", index=False)
    print(f"ethnicity: {len(out)} CMAs | sample Toronto all_vm={out.loc[out['name']=='Toronto','all_vm'].values}")


def build_ct_income_geojson():
    """Combined census-tract income GeoJSON (geometry + income baked into
    feature properties + id=CTUID), served as a static file and fetched
    client-side when the user opts into neighbourhood detail on the income map."""
    gj = json.load(open(f"{GEO_DIR}/ct_2021.geojson"))
    inc = pd.read_csv(f"{GEO_DIR}/statcan_ct_income_2021.csv", dtype={"ctuid": str})
    vmap = inc.set_index("ctuid")["median_income"].to_dict()
    nmap = inc.set_index("ctuid")["name"].to_dict()
    feats = []
    for f in gj["features"]:
        cid = f.get("id") or f.get("properties", {}).get("ctuid")
        if cid in vmap:
            f["id"] = cid
            f["properties"] = {"v": vmap[cid], "name": nmap.get(cid)}
            feats.append(f)
    gj["features"] = feats
    path = f"{GEO_DIR}/ct_income_2021.geojson"
    with open(path, "w") as fh:
        fh.write(json.dumps(gj, separators=(",", ":")))
    print(f"wrote {path}: {round(os.path.getsize(path)/1e6, 2)} MB, {len(feats)} tracts")


if __name__ == "__main__":
    ids = build_income()
    build_boundaries(ids)
    build_cma()
    build_cma_ethnicity()
    build_ct_income_geojson()
