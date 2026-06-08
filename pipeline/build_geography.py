"""
One-time builder for the Geography section's STATIC map assets.

Like build_census_geo.py, these are generated once and committed — they are
physical-geography facts (boundaries, ecological zones, permafrost) or 5-yearly
census measures, NOT weekly indicators. The weekly time series for this section
(wildfire area burned, sea-ice extent) live in pipeline/fetch_geography.py and run
in the normal registry pipeline.

Outputs (committed to data/geo/):
  prov_2021.geojson                 13 province/territory boundaries (simplified, id=PRUID)
  statcan_prov_geography.csv        per-province population density + % freshwater area
  nef_ecozones.geojson              15 terrestrial ecozones (25 polygons, id=fid, props.ecozone)
  statcan_landcover_ecozone.csv     per-polygon land-cover composition (% of each class)
  permafrost_zones.geojson          4 permafrost zones (dissolved, id=fid, props.zone)
  permafrost_zones.csv              fid -> zone label (drives the categorical map)

Run:  /opt/anaconda3/bin/python -m pipeline.build_geography
      (any interpreter with geopandas + pyogrio; not in the weekly pipeline)
"""

import os
import json
import zipfile
import requests
import pandas as pd
import geopandas as gpd

GEO_DIR = "data/geo"
COORD_DECIMALS = 3      # ~110 m; national-scale maps don't need finer
SIMPLIFY_TOL = 0.02     # ~2 km generalisation for whole-country polygons


def _rnd(o):
    if isinstance(o, float):
        return round(o, COORD_DECIMALS)
    if isinstance(o, list):
        return [_rnd(x) for x in o]
    return o


def _download_cache(url, path, label):
    """Download once to /tmp and reuse (these source files are large/static)."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  using cached {label}: {path}")
        return path
    print(f"  downloading {label} ...")
    r = requests.get(url, timeout=600)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    return path


def _write_geojson(gj, path):
    with open(path, "w") as f:
        f.write(json.dumps(gj, separators=(",", ":")))
    print(f"  wrote {path}: {round(os.path.getsize(path) / 1e6, 2)} MB")


# ---------------------------------------------------------------------------
# A. Provinces: boundaries + population density + % freshwater area
# ---------------------------------------------------------------------------
PROV_BND_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/"
                "boundary-limites/files-fichiers/lpr_000a21a_e.zip")
CENSUS001_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/"
                 "download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=001")

# Land and freshwater area by province/territory (km²) — the canonical
# NRCan / Statistics Canada figures (Canada Year Book; stable geographic facts,
# not a weekly series, so kept here with the source cited rather than fetched).
# (total_area, land_area, freshwater_area) in km².
PROV_AREA = {
    "Newfoundland and Labrador": (405212, 373872, 31340),
    "Prince Edward Island":      (5660, 5660, 0),
    "Nova Scotia":               (55284, 53338, 1946),
    "New Brunswick":             (72908, 71450, 1458),
    "Quebec":                    (1542056, 1365128, 176928),
    "Ontario":                   (1076395, 917741, 158654),
    "Manitoba":                  (647797, 553556, 94241),
    "Saskatchewan":              (651036, 591670, 59366),
    "Alberta":                   (661848, 642317, 19531),
    "British Columbia":          (944735, 925186, 19549),
    "Yukon":                     (482443, 474391, 8052),
    "Northwest Territories":     (1346106, 1183085, 163021),
    "Nunavut":                   (2093190, 1936113, 157077),
}
PROV_AREA_SRC = "Natural Resources Canada / Statistics Canada (Canada Year Book), land & freshwater area"


def build_provinces():
    """Province/territory choropleth assets: boundaries + a small indicators CSV
    (population, population density per km², and % freshwater area). Density comes
    from the 2021 Census Profile (GEONO=001, characteristic 6); % freshwater from
    the canonical NRCan/StatCan area table above."""
    z = zipfile.ZipFile(_download_cache(CENSUS001_URL, "/tmp/geo_census001.zip",
                                        "Census Profile GEONO=001"))
    csvn = [n for n in z.namelist() if n.endswith("_data.csv")][0]
    d = pd.read_csv(z.open(csvn), dtype=str, encoding="latin-1",
                    usecols=["ALT_GEO_CODE", "GEO_NAME", "CHARACTERISTIC_ID", "C1_COUNT_TOTAL"])
    d["cid"] = pd.to_numeric(d["CHARACTERISTIC_ID"], errors="coerce")
    d["v"] = pd.to_numeric(d["C1_COUNT_TOTAL"], errors="coerce")

    def by(cid):  # ALT_GEO_CODE -> value for a characteristic id
        return (d[d["cid"] == cid].drop_duplicates("ALT_GEO_CODE")
                .set_index("ALT_GEO_CODE"))

    dens, pop, land7 = by(6), by(1), by(7)
    names = dens["GEO_NAME"]
    rows = []
    for code in dens.index:
        if str(code) == "01":            # skip the Canada total — this is the province map
            continue
        name = names.loc[code]
        total, land, fresh = PROV_AREA.get(name, (None, None, None))
        popv = pop.loc[code, "v"] if code in pop.index else None
        landv = land7.loc[code, "v"] if code in land7.index else None
        # The published density (characteristic 6) rounds the territories to 0.0;
        # recompute it unrounded from population / census land area so the
        # log-scaled choropleth can still place them.
        density = round(popv / landv, 4) if (popv and landv) else dens.loc[code, "v"]
        rows.append(dict(
            pruid=str(code), name=name, population=popv, density=density,
            land_area_km2=land, total_area_km2=total, freshwater_km2=fresh,
            pct_freshwater=round(fresh / total * 100, 2) if total else None,
        ))
    out = pd.DataFrame(rows)
    os.makedirs(GEO_DIR, exist_ok=True)
    out.to_csv(f"{GEO_DIR}/statcan_prov_geography.csv", index=False)
    print(f"provinces: {len(out)} rows | density range "
          f"{out.density.min()}–{out.density.max()} | freshwater {out.pct_freshwater.min()}–{out.pct_freshwater.max()}%")

    # boundaries
    bz = zipfile.ZipFile(_download_cache(PROV_BND_URL, "/tmp/lpr_000a21a_e.zip",
                                         "province boundaries"))
    bz.extractall("/tmp/prov_bnd")
    shp = [f for f in bz.namelist() if f.endswith(".shp")][0]
    g = gpd.read_file(f"/tmp/prov_bnd/{shp}").to_crs(epsg=4326)
    uid = [c for c in g.columns if c.upper() == "PRUID"][0]
    g["pruid"] = g[uid].astype(str)
    g["geometry"] = g["geometry"].simplify(SIMPLIFY_TOL, preserve_topology=True)
    g = g[["pruid", "geometry"]]
    gj = json.loads(g.to_json())
    for ft in gj["features"]:
        ft["id"] = ft["properties"]["pruid"]
        ft["geometry"]["coordinates"] = _rnd(ft["geometry"]["coordinates"])
    _write_geojson(gj, f"{GEO_DIR}/prov_2021.geojson")


COMP_CMA_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/"
                "download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=002")


def build_cma_density():
    """Population density per km² by metro area (CMA/CA), 2021 Census profile
    (GEONO=002, characteristic 6). Reuses the existing cma_2021.geojson geometry,
    so this only emits a small value CSV keyed by CMAUID like the other CMA maps."""
    z = zipfile.ZipFile(_download_cache(COMP_CMA_URL, "/tmp/geo_cma002.zip",
                                        "CMA profile GEONO=002"))
    csvn = [n for n in z.namelist() if n.endswith("_data.csv")][0]
    df = pd.read_csv(z.open(csvn), dtype=str, encoding="latin-1",
                     usecols=["ALT_GEO_CODE", "GEO_NAME", "CHARACTERISTIC_ID", "C1_COUNT_TOTAL"])
    df["cid"] = pd.to_numeric(df["CHARACTERISTIC_ID"], errors="coerce")
    df["v"] = pd.to_numeric(df["C1_COUNT_TOTAL"], errors="coerce")
    names = df.drop_duplicates("ALT_GEO_CODE").set_index("ALT_GEO_CODE")["GEO_NAME"]
    dens = df[df["cid"] == 6].drop_duplicates("ALT_GEO_CODE").set_index("ALT_GEO_CODE")["v"]
    out = pd.DataFrame({"name": names, "density": dens}).dropna(subset=["density"])
    out.index.name = "cmauid"
    os.makedirs(GEO_DIR, exist_ok=True)
    out.reset_index().to_csv(f"{GEO_DIR}/statcan_cma_density.csv", index=False)
    print(f"CMA density: {len(out)} metros | density max {out.density.max()}/km²")


# ---------------------------------------------------------------------------
# B. Ecozones (categorical) + land cover by ecozone (% composition)
# ---------------------------------------------------------------------------
# AAFC National Ecological Framework for Canada — terrestrial ecozones, served as
# GeoJSON in WGS84 with server-side generalisation (maxAllowableOffset), so no
# reprojection/simplification step is needed locally. 15 zones across 25 polygons.
ECOZONE_URL = ("https://services.arcgis.com/lGOekm0RsNxYnT3j/arcgis/rest/services/"
               "National_ecological_framework_of_Canada_ecozones/FeatureServer/0/query"
               "?where=1%3D1&outFields=ECOZONE_ID,ECOZONE_NAME_EN&outSR=4326"
               "&maxAllowableOffset=0.02&f=geojson")
LANDCOVER_TABLE = "38-10-0177-01"        # StatCan: land cover by class, by ecozone (2020)

# (raw "Land cover class" value -> (slug, display label)); order = dropdown order.
# "Total area" is the denominator (excluded from the mapped classes).
LC_CLASSES = [
    ("Treed (including treed wetlands)", "treed", "Forest / treed"),
    ("Cropland", "cropland", "Cropland"),
    ("Inland water bodies", "water", "Inland water"),
    ("Wetland (non-treed)", "wetland", "Wetland (non-treed)"),
    ("Grassland and shrubland", "grass_shrub", "Grassland & shrubland"),
    ("Barren land", "barren", "Barren land"),
    ("Sparsely vegetated land", "sparse_veg", "Sparsely vegetated"),
    ("Permanent snow and ice", "snow_ice", "Snow & ice"),
    ("Built-up and artificial surfaces", "built_up", "Built-up"),
    ("Treed area disturbance", "treed_disturb", "Recent treed disturbance"),
]


def build_ecozones():
    """Ecozone boundaries (categorical map) + a per-polygon land-cover composition
    CSV (% of each land-cover class within the polygon's ecozone) that drives the
    land-cover dropdown choropleth. Each polygon gets a unique feature id (`fid`)
    so non-contiguous zones don't collide on a shared id."""
    gj = requests.get(ECOZONE_URL, timeout=180).json()
    feats = [f for f in gj.get("features", []) if f.get("geometry")]
    gj["features"] = feats
    rows = []
    for i, ft in enumerate(feats):
        fid = str(i)
        p = ft.get("properties", {})
        rows.append(dict(fid=fid, ecozone_id=p.get("ECOZONE_ID"),
                         ecozone=p.get("ECOZONE_NAME_EN")))
        ft["id"] = fid
        ft["properties"] = {"ecozone": p.get("ECOZONE_NAME_EN")}
        ft["geometry"]["coordinates"] = _rnd(ft["geometry"]["coordinates"])
    os.makedirs(GEO_DIR, exist_ok=True)
    _write_geojson(gj, f"{GEO_DIR}/nef_ecozones.geojson")
    feat_df = pd.DataFrame(rows)
    print(f"ecozones: {len(feat_df)} polygons across {feat_df.ecozone.nunique()} zones")

    # land cover by ecozone (38-10-0177-01) -> % of each class within the ecozone
    from pipeline.fetch_statcan import _get_table
    lc = _get_table(LANDCOVER_TABLE)
    lc = lc[lc["GEO"].str.endswith("(ecozone)", na=False)].copy()
    lc["ecozone"] = lc["GEO"].str.replace(r"\s*\(ecozone\)$", "", regex=True)
    lc["VALUE"] = pd.to_numeric(lc["VALUE"], errors="coerce")
    piv = lc.pivot_table(index="ecozone", columns="Land cover class",
                         values="VALUE", aggfunc="first")
    total = piv["Total area"]
    shares = pd.DataFrame(index=piv.index)
    for raw, slug, _ in LC_CLASSES:
        if raw in piv.columns:
            shares[slug] = (piv[raw] / total * 100).round(2)
    wide = feat_df.merge(shares.reset_index(), on="ecozone", how="left")
    wide.to_csv(f"{GEO_DIR}/statcan_landcover_ecozone.csv", index=False)
    missing = set(feat_df["ecozone"]) - set(shares.index)
    print(f"land cover: {wide.shape[0]} polygons x {len(shares.columns)} classes | "
          f"ecozones unmatched: {missing or 'none'}")


# ---------------------------------------------------------------------------
# C. Permafrost zones (categorical)
# ---------------------------------------------------------------------------
# NRCan Atlas of Canada, 5th edition permafrost map (Heginbottom et al., ~1995).
# Categorical: continuous / extensive discontinuous / sporadic discontinuous /
# isolated patches. The "No permafrost (O)" and "Subsea (U)" classes are dropped
# so the coloured polygons ARE the permafrost (the uncoloured south reads as none).
PERMAFROST_URL = ("https://ftp.cartes.canada.ca/pub/nrcan_rncan/"
                  "Surficial-geology_Geologie-des-depots-meubles/permafrost-pergelisol/"
                  "permafrost_atlas_of_canada_en.shp.zip")
PMF_LABELS = {   # PMF_CLASS -> clean label (source label spacing is inconsistent)
    "C": "Continuous (90–100%)",
    "E": "Extensive discontinuous (50–90%)",
    "S": "Sporadic discontinuous (10–50%)",
    "I": "Isolated patches (0–10%)",
}


def build_permafrost():
    """Permafrost-zone boundaries for the categorical map. Polygons are dissolved
    by zone (4 features) then simplified, keeping the file small."""
    zf = zipfile.ZipFile(_download_cache(PERMAFROST_URL, "/tmp/permafrost.shp.zip",
                                         "permafrost (NRCan Atlas 5th ed.)"))
    zf.extractall("/tmp/pf")
    shp = [f for f in zf.namelist() if f.endswith(".shp")][0]
    g = gpd.read_file(f"/tmp/pf/{shp}").to_crs(epsg=4326)
    g = g[g["PMF_CLASS"].isin(PMF_LABELS)].copy()       # drop No-permafrost (O) + Subsea (U)
    g["zone"] = g["PMF_CLASS"].map(PMF_LABELS)
    g = g.dissolve(by="zone", as_index=False)[["zone", "geometry"]]
    g["geometry"] = g["geometry"].simplify(SIMPLIFY_TOL, preserve_topology=True).buffer(0)
    gj = json.loads(g.to_json())
    rows = []
    for i, ft in enumerate(gj["features"]):
        fid = str(i)
        zone = ft["properties"]["zone"]
        rows.append(dict(fid=fid, zone=zone))
        ft["id"] = fid
        ft["properties"] = {"zone": zone}
        ft["geometry"]["coordinates"] = _rnd(ft["geometry"]["coordinates"])
    os.makedirs(GEO_DIR, exist_ok=True)
    _write_geojson(gj, f"{GEO_DIR}/permafrost_zones.geojson")
    pd.DataFrame(rows).to_csv(f"{GEO_DIR}/permafrost_zones.csv", index=False)
    print(f"permafrost: {len(rows)} zones")


# ---------------------------------------------------------------------------
# D. Wildfire ignition POINTS for one record year (2023) — NRCan NFDB
#    The "where the fires actually were" map that replaces the coarse by-province
#    % view: every recorded wildfire that year as a point sized by area burned.
# ---------------------------------------------------------------------------
NFDB_PNT_URL = ("https://cwfis.cfs.nrcan.gc.ca/downloads/nfdb/fire_pnt/"
                "current_version/NFDB_point.zip")
WILDFIRE_YEAR = 2023        # the record 17.6-million-hectare season
_FIRE_AGENCY = {
    "AB": "Alberta", "BC": "British Columbia", "MB": "Manitoba", "NB": "New Brunswick",
    "NL": "Newfoundland and Labrador", "NS": "Nova Scotia", "NT": "Northwest Territories",
    "NU": "Nunavut", "ON": "Ontario", "PC": "Parks Canada", "PE": "Prince Edward Island",
    "QC": "Quebec", "SK": "Saskatchewan", "YT": "Yukon"}


def build_wildfire_points(year=WILDFIRE_YEAR):
    """Individual wildfire points for one year (default 2023, the record season) from
    NRCan's National Fire Database point archive — same authoritative NFDB source
    (OGL-Canada) as the weekly area-burned series, just the per-fire locations rather
    than provincial totals. Writes a light CSV (lat, lon, size_ha, province, cause);
    the page plots them as a Scattermapbox sized by area burned, so the few enormous
    boreal fires that drove the 17.6 Mha total stand out from the thousands of small
    ones. Point geometry is reprojected from the Atlas-Lambert source to WGS84."""
    print(f"Building {year} wildfire points (NRCan NFDB) ...")
    z = zipfile.ZipFile(_download_cache(NFDB_PNT_URL, "/tmp/nfdb_point.zip", "NFDB point archive"))
    z.extractall("/tmp/nfdb_point")
    shp = [n for n in z.namelist() if n.lower().endswith(".shp")][0]
    g = gpd.read_file(f"/tmp/nfdb_point/{shp}")
    g = g[(g["YEAR"] == year) & g["SIZE_HA"].notna() & (g["SIZE_HA"] > 0)].to_crs(epsg=4326)
    cause = {"L": "Lightning", "H": "Human", "H-PB": "Prescribed burn", "U": "Unknown"}
    out = pd.DataFrame({
        "lat": g.geometry.y.round(4), "lon": g.geometry.x.round(4),
        "size_ha": g["SIZE_HA"].round(1),
        "province": g["SRC_AGENCY"].map(_FIRE_AGENCY).fillna(g["SRC_AGENCY"]),
        "cause": g["CAUSE"].map(cause).fillna("Other / unknown") if "CAUSE" in g else "Unknown",
        "year": int(year),
    })
    out = out[out["lat"].between(40, 84) & out["lon"].between(-141, -52)]   # sane CA bounds
    out = out.sort_values("size_ha")          # big fires drawn last → on top
    path = f"{GEO_DIR}/nfdb_fire_points_{year}.csv"
    out.to_csv(path, index=False)
    print(f"  wrote {path}: {len(out)} fires, {round(os.path.getsize(path) / 1e6, 2)} MB; "
          f"total area {out['size_ha'].sum() / 1e6:.1f} Mha")


# ---------------------------------------------------------------------------
# E. Major lakes — NRCan Atlas of Canada 1:1,000,000 waterbodies (OGL-Canada)
#    Canada has more lake area than any country; this highlights the largest named
#    lakes with their surface area (computed from the official outlines).
# ---------------------------------------------------------------------------
LAKES_URL = ("https://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/framework_cadre/"
             "Atlas_of_Canada_1M/hydrology/AC_1M_Waterbodies.shp.zip")


def build_lakes(top_n=40):
    """The largest lakes of Canada as highlighted polygons with surface-area stats,
    from NRCan's Atlas of Canada 1:1,000,000 waterbodies (OGL-Canada). Keeps the
    `top_n` largest **named, natural** lakes (reservoirs excluded) that touch Canada —
    so the shared Great Lakes are kept but wholly-US Lake Michigan is dropped — and
    computes each one's surface area in an equal-area projection. Writes a GeoJSON
    (id=lakeid, props.name/area_km2) the Water page maps as a blue choropleth shaded
    by area, plus a CSV. Areas are approximate (1:1M-scale outlines)."""
    print("Building major lakes (NRCan Atlas 1:1M waterbodies) ...")
    z = zipfile.ZipFile(_download_cache(LAKES_URL, "/tmp/ac1m_water.shp.zip", "1:1M waterbodies"))
    z.extractall("/tmp/ac1m_water")
    shp = [n for n in z.namelist() if n.lower().endswith(".shp") and "Waterbodies" in n][0]
    g = gpd.read_file(f"/tmp/ac1m_water/{shp}")
    g = g[g["NAME"].notna() & (g["RESERVOIR"].astype(str).str.lower() != "yes")].copy()

    def _fix(s):     # the dbf carries UTF-8 bytes tagged latin-1 → "RÃ©servoir" etc.
        try:
            return s.encode("latin-1").decode("utf-8")
        except Exception:
            return s
    g["NAME"] = g["NAME"].map(_fix)
    g = g.dissolve(by="NAME", as_index=False)                     # merge multi-part lakes
    g["area_km2"] = g.to_crs("ESRI:102001").area / 1e6            # Canada Albers equal-area
    cand = g.sort_values("area_km2", ascending=False).head(top_n + 15).to_crs(epsg=4326)
    canada = gpd.read_file(f"{GEO_DIR}/prov_2021.geojson").to_crs(epsg=4326).union_all()
    cand = cand[cand.intersects(canada)].head(top_n).reset_index(drop=True)
    cand["geometry"] = cand["geometry"].simplify(0.01, preserve_topology=True).buffer(0)
    cand["lakeid"] = cand.index.astype(str)
    cand["area_km2"] = cand["area_km2"].round(0)
    keep = cand[["lakeid", "NAME", "area_km2", "geometry"]].rename(columns={"NAME": "name"})
    gj = json.loads(keep.to_json())
    for ft in gj["features"]:
        ft["id"] = ft["properties"]["lakeid"]
        ft["geometry"]["coordinates"] = _rnd(ft["geometry"]["coordinates"])
    _write_geojson(gj, f"{GEO_DIR}/lakes_major.geojson")
    keep.drop(columns="geometry").to_csv(f"{GEO_DIR}/lakes_major.csv", index=False)
    print(f"  {len(keep)} lakes; largest {keep.iloc[0]['name']} {keep.iloc[0]['area_km2']:,.0f} km²")


CLIMATE_NORMALS_API = "https://api.weather.gc.ca/collections/climate-normals/items"


def build_climate_normals():
    """ECCC Canadian Climate Normals 1981-2010 — station POINT data (OGL-Canada), pulled
    from the MSC GeoMet **OGC API – Features** endpoint (decimal lat/lon, no DMS parsing).
    Mean daily temperature is NORMAL_ID=1 and total precipitation NORMAL_ID=56; MONTH 1=Jan,
    7=Jul, 13=annual. Writes a tidy point CSV (climate_id, station, province, lat, lon,
    jan_temp, jul_temp, annual_temp, annual_precip) for the proportional/coloured-point
    climate map. ~660 stations carry a temperature normal. Decennial — NOT weekly."""
    print("Building climate normals (ECCC 1981-2010, GeoMet OGC API) ...")

    def fetch(normal_id, month):
        url = f"{CLIMATE_NORMALS_API}?NORMAL_ID={normal_id}&MONTH={month}&limit=10000&f=json"
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        return r.json()["features"]

    rows = {}
    for f in fetch(1, 1):                     # Jan mean temp = base (geometry + name)
        p = f["properties"]
        cid = p["CLIMATE_IDENTIFIER"]
        lon, lat = f["geometry"]["coordinates"]
        rows[cid] = dict(climate_id=cid, station=str(p["STATION_NAME"]).title(),
                         province=p["PROVINCE_CODE"], lat=round(lat, 4), lon=round(lon, 4),
                         jan_temp=p["VALUE"])

    def add(normal_id, month, col):
        for f in fetch(normal_id, month):
            p = f["properties"]
            cid = p["CLIMATE_IDENTIFIER"]
            if cid in rows:
                rows[cid][col] = p["VALUE"]

    add(1, 7, "jul_temp")
    add(1, 13, "annual_temp")
    add(56, 13, "annual_precip")
    df = pd.DataFrame(rows.values()).dropna(subset=["jan_temp", "jul_temp"])
    os.makedirs(GEO_DIR, exist_ok=True)
    df.to_csv(f"{GEO_DIR}/climate_normals.csv", index=False)
    print(f"  {len(df)} stations | Jan {df.jan_temp.min():.1f}..{df.jan_temp.max():.1f}°C "
          f"| Jul {df.jul_temp.min():.1f}..{df.jul_temp.max():.1f}°C")


if __name__ == "__main__":
    build_provinces()
    build_cma_density()
    build_ecozones()
    build_permafrost()
    build_wildfire_points()
    build_lakes()
    build_climate_normals()
    print("build_geography complete.")
