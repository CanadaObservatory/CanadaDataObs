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
# 1683 is the population base (denominator); 1684 = all VM; 1697 = "Not a visible
# minority" — the residual category that includes white AND Indigenous people (StatCan
# has no distinct "White" group). It shares the same base, so its % is consistent.
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
    (1697, "not_vm", "Not a visible minority"),
]

# Religion: top-level 2021-Census groups (CHARACTERISTIC_ID, column, label). 1949 is
# the population base (denominator); the Christian sub-denominations 1952–1966 are
# rolled into the 1951 "Christian" total to keep the dropdown to the major groups.
# Self-reported, descriptive only — handled like the visible-minority layer (neutral,
# no scorecard, no "good/bad"). "No religion and secular perspectives" is the second
# largest group and is included.
RELIGION_BASE = 1949
RELIGION_GROUPS = [
    (1951, "christian", "Christian"),
    (1973, "no_religion", "No religion / secular"),
    (1969, "muslim", "Muslim"),
    (1967, "hindu", "Hindu"),
    (1970, "sikh", "Sikh"),
    (1950, "buddhist", "Buddhist"),
    (1968, "jewish", "Jewish"),
    (1971, "indigenous_spirituality", "Traditional Indigenous spirituality"),
    (1972, "other_religion", "Other religions & spiritual traditions"),
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


def build_cma_religion():
    """Per-city share of each major religion (2021 Census), for a dropdown choropleth.
    % = group count / 1949 population base. Same descriptive, neutral treatment as the
    visible-minority layer (self-reported; no scorecard, no evaluative direction)."""
    z = zipfile.ZipFile(io.BytesIO(requests.get(COMP_CMA_URL, timeout=300).content))
    csvn = [n for n in z.namelist() if n.endswith("_data.csv")][0]
    with z.open(csvn) as f:
        df = pd.read_csv(f, encoding="latin-1", dtype=str,
                         usecols=["ALT_GEO_CODE", "GEO_NAME", "CHARACTERISTIC_ID", "C1_COUNT_TOTAL"])
    df["CHARACTERISTIC_ID"] = pd.to_numeric(df["CHARACTERISTIC_ID"], errors="coerce")
    df["v"] = pd.to_numeric(df["C1_COUNT_TOTAL"], errors="coerce")
    names = df.drop_duplicates("ALT_GEO_CODE").set_index("ALT_GEO_CODE")["GEO_NAME"]

    def by_id(cid):
        return (df[df["CHARACTERISTIC_ID"] == cid].drop_duplicates("ALT_GEO_CODE")
                .set_index("ALT_GEO_CODE")["v"])

    denom = by_id(RELIGION_BASE)
    out = pd.DataFrame({"name": names})
    for cid, col, _ in RELIGION_GROUPS:
        out[col] = (by_id(cid) / denom * 100).round(1)
    out.index.name = "cmauid"
    out = out.dropna(subset=["christian"])
    os.makedirs(GEO_DIR, exist_ok=True)
    out.reset_index().to_csv(f"{GEO_DIR}/statcan_cma_religion.csv", index=False)
    print(f"religion: {len(out)} CMAs | sample Toronto no_religion="
          f"{out.loc[out['name']=='Toronto','no_religion'].values}")


COMP_CT_URL = ("https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/"
               "download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO=007")
DWELLING_VALUE_CHAR = "Median value of dwellings ($)"


def _download_cache(url, path, label, stream=True):
    """Download `url` to `path` once and reuse it (these census files are large and
    static). Returns the cached path."""
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"  using cached {label}: {path} ({os.path.getsize(path)/1e6:.0f} MB)")
        return path
    print(f"  downloading {label} (large, one-time) ...")
    with requests.get(url, stream=stream, timeout=1800) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print(f"  saved {label}: {os.path.getsize(path)/1e6:.0f} MB")
    return path


def build_ct_from_profile():
    """Census-tract dwelling value + visible-minority shares from the comprehensive
    2021 Census Profile for census tracts (98-401-X2021007, GEONO=007 — a ~238 MB
    zip, multi-GB uncompressed). One-time/static (census is 5-yearly); NOT in the
    weekly pipeline. Reuses the existing ct_2021.geojson geometry, so this only emits
    the two value CSVs, keyed by CTUID exactly like the income map.

    The big CSV is read in chunks, keeping only census-tract rows (DGUID contains
    'S0507') and only the characteristics we need, so memory stays bounded."""
    cache = "/tmp/census_profile_ct_007.zip"
    _download_cache(COMP_CT_URL, cache, "CT census profile (GEONO=007)")
    z = zipfile.ZipFile(cache)
    csvn = [n for n in z.namelist() if n.endswith("_data.csv")][0]

    needed_ids = ({cid for cid, _, _ in VM_GROUPS} | {1683}
                  | {cid for cid, _, _ in RELIGION_GROUPS} | {RELIGION_BASE})
    cols = ["DGUID", "GEO_NAME", "CHARACTERISTIC_ID", "CHARACTERISTIC_NAME", "C1_COUNT_TOTAL"]
    keep = []
    for chunk in pd.read_csv(z.open(csvn), usecols=cols, dtype=str,
                             encoding="latin-1", chunksize=400_000):
        chunk = chunk[chunk["DGUID"].str.contains("S0507", na=False)]   # CT level only
        if chunk.empty:
            continue
        cid = pd.to_numeric(chunk["CHARACTERISTIC_ID"], errors="coerce")
        mask = cid.isin(needed_ids) | (chunk["CHARACTERISTIC_NAME"].str.strip() == DWELLING_VALUE_CHAR)
        if mask.any():
            keep.append(chunk[mask])
    df = pd.concat(keep, ignore_index=True)
    df["cid"] = pd.to_numeric(df["CHARACTERISTIC_ID"], errors="coerce")
    df["ctuid"] = df["DGUID"].astype(str).str.replace("2021S0507", "", regex=False)
    df["v"] = pd.to_numeric(df["C1_COUNT_TOTAL"], errors="coerce")
    names = df.drop_duplicates("ctuid").set_index("ctuid")["GEO_NAME"].astype(str)
    os.makedirs(GEO_DIR, exist_ok=True)

    def ct_series(cid):
        return df[df["cid"] == cid].drop_duplicates("ctuid").set_index("ctuid")["v"]

    # --- dwelling value (owner-estimated) ---
    dv = (df[df["CHARACTERISTIC_NAME"].str.strip() == DWELLING_VALUE_CHAR]
          .drop_duplicates("ctuid").set_index("ctuid")["v"])
    dval = pd.DataFrame({"name": names, "dwelling_value": dv}).dropna(subset=["dwelling_value"])
    dval.index.name = "ctuid"
    dval.reset_index().to_csv(f"{GEO_DIR}/statcan_ct_dwelling_value_2021.csv", index=False)
    print(f"CT dwelling value: {len(dval)} tracts")

    # --- visible-minority shares (% of population base 1683) ---
    base = ct_series(1683)
    eth = pd.DataFrame({"name": names})
    for cid, col, _ in VM_GROUPS:
        eth[col] = (ct_series(cid) / base * 100).round(1)
    eth.index.name = "ctuid"
    eth = eth.dropna(subset=["all_vm"])
    eth.reset_index().to_csv(f"{GEO_DIR}/statcan_ct_ethnicity_2021.csv", index=False)
    print(f"CT ethnicity: {len(eth)} tracts")

    # --- religion shares (% of population base 1949) ---
    rbase = ct_series(RELIGION_BASE)
    rel = pd.DataFrame({"name": names})
    for cid, col, _ in RELIGION_GROUPS:
        rel[col] = (ct_series(cid) / rbase * 100).round(1)
    rel.index.name = "ctuid"
    rel = rel.dropna(subset=["christian"])
    rel.reset_index().to_csv(f"{GEO_DIR}/statcan_ct_religion_2021.csv", index=False)
    print(f"CT religion: {len(rel)} tracts")


# ---- Historical visible-minority composition (by census year) -------------------
# Source: 98-10-0429-01, the one current cube with a Census-year dimension
# (2006/2011/2016/2021) crossed with Visible minority (15) and geography. Its
# universe is the population aged 15+ (no 0-14 age group), so shares here are of the
# 15+ population — labelled as such, and a touch different from the all-ages maps.
# 2011 was the voluntary National Household Survey (lower response, quality caveats):
# kept but flagged on the chart rather than dropped. 2001 is a best-effort extension
# from a legacy product (see _vm_history_2001) and is skipped if it can't be parsed.
VM_HISTORY_TABLE = "98-10-0429-01"
VM_BASE_MEMBER = "Total - Visible minority"
VM_PLOT_MEMBERS = [          # cube member name -> chart label (order = legend order)
    ("Total visible minority population", "All visible minorities"),
    ("Not a visible minority", "Not a visible minority"),
    ("South Asian", "South Asian"), ("Chinese", "Chinese"), ("Black", "Black"),
    ("Filipino", "Filipino"), ("Arab", "Arab"), ("Latin American", "Latin American"),
]
PROV_TERR = ["Newfoundland and Labrador", "Prince Edward Island", "Nova Scotia",
             "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan",
             "Alberta", "British Columbia", "Yukon", "Northwest Territories", "Nunavut"]
HISTORY_CMAS = ["Toronto", "Montr", "Vancouver", "Calgary", "Edmonton",
                "Ottawa", "Winnipeg", "Halifax"]


def _vm_geo_match(geo):
    """Map a cube GEO label to (level, clean_label) for our target tiers, else None."""
    g = str(geo)
    if g == "Canada":
        return ("national", "Canada")
    if g in PROV_TERR:
        return ("province", g)
    if "(CMA)" in g:
        for city in HISTORY_CMAS:
            if g.startswith(city):
                return ("cma", g.split(" (CMA)")[0])
    return None


def _detect(cols, *needles):
    for c in cols:
        cl = c.lower()
        if all(n in cl for n in needles):
            return c
    return None


def build_vm_history():
    """Visible-minority composition by census year x geography -> a tidy long CSV
    (geography, geo_level, year, group, count, share) for the historical trend chart.
    Robust core = 2006/2011/2016/2021 from one cube; 2001 added best-effort."""
    parts = VM_HISTORY_TABLE.split("-")
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{''.join(parts[:3])}-eng.zip"
    cache = "/tmp/statcan_98100429.zip"
    try:
        _download_cache(url, cache, f"StatCan {VM_HISTORY_TABLE}")
        z = zipfile.ZipFile(cache)
        member = [n for n in z.namelist()
                  if n.endswith(".csv") and "metadata" not in n.lower()][0]
    except Exception as e:
        print(f"  vm_history: cube fetch failed ({e}) — skipping")
        return

    import re
    wanted_members = {VM_BASE_MEMBER} | {m for m, _ in VM_PLOT_MEMBERS}
    rows, colmap, year_cols = [], {}, []
    for chunk in pd.read_csv(z.open(member), dtype=str, low_memory=False, chunksize=200_000):
        if not colmap:
            cols = list(chunk.columns)
            colmap = dict(
                gen=_detect(cols, "generation"), age=_detect(cols, "age"),
                gender=_detect(cols, "gender"), cert=_detect(cols, "certificate"),
                stat=_detect(cols, "statistic"), vm=_detect(cols, "visible minor"))
            # This cube is WIDE in census year: one value column per year, named
            # like "Census year (4):2016[2]" — there is no single VALUE column.
            year_cols = [(c, int(re.search(r":(\d{4})", c).group(1)))
                         for c in cols
                         if c.startswith("Census year") and re.search(r":(\d{4})", c)]
        c = chunk
        for k in ("gen", "age", "gender", "cert"):
            if colmap.get(k):
                c = c[c[colmap[k]].str.startswith("Total", na=False)]
        if colmap.get("stat"):
            c = c[c[colmap["stat"]].str.strip().str.lower() == "count"]
        c = c[c[colmap["vm"]].str.strip().isin(wanted_members)]
        if c.empty:
            continue
        for _, r in c.iterrows():
            m = _vm_geo_match(r["GEO"])
            if not m:
                continue
            mem = r[colmap["vm"]].strip()
            for col, yr in year_cols:
                rows.append((m[1], m[0], yr, mem, r[col]))

    long = pd.DataFrame(rows, columns=["geography", "geo_level", "year", "member", "value"])
    long["year"] = pd.to_numeric(long["year"], errors="coerce").astype("Int64")
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    long = long.dropna(subset=["year", "value"])

    # best-effort 2001 extension (legacy product); never breaks the build
    try:
        extra = _vm_history_2001()
        if extra is not None and not extra.empty:
            long = pd.concat([long, extra], ignore_index=True)
            print(f"  vm_history: added 2001 ({len(extra)} rows)")
    except Exception as e:
        print(f"  vm_history: 2001 extension skipped ({e})")

    # base (15+ population) per geography x year, then shares
    base = (long[long["member"] == VM_BASE_MEMBER]
            .set_index(["geography", "year"])["value"])
    label = dict(VM_PLOT_MEMBERS)
    plot = long[long["member"].isin(label)].copy()
    plot["base"] = plot.set_index(["geography", "year"]).index.map(base)
    plot["share"] = (plot["value"] / plot["base"] * 100).round(2)
    plot["group"] = plot["member"].map(label)
    out = (plot[["geography", "geo_level", "year", "group", "value", "share"]]
           .rename(columns={"value": "count"})
           .dropna(subset=["share"]).sort_values(["geo_level", "geography", "group", "year"]))
    os.makedirs(GEO_DIR, exist_ok=True)
    out.to_csv(f"{GEO_DIR}/statcan_vm_history.csv", index=False)
    yrs = sorted(out["year"].unique().tolist())
    print(f"vm_history: {len(out)} rows | years {yrs} | geos {out['geography'].nunique()}")


def _vm_history_2001():
    """Best-effort 2001 visible-minority counts (Canada/provinces/CMAs) to extend the
    series back. Legacy census products are XML/IVT-only and format-fragile, so this
    is intentionally isolated: it returns a tidy frame matching build_vm_history's
    schema on success, or None to be skipped. Left as a documented hook for now —
    the robust 2006-2021 series ships regardless."""
    return None


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
    build_cma_religion()
    build_ct_income_geojson()
    build_vm_history()         # historical visible-minority composition (cube)
    build_ct_from_profile()    # CT dwelling value + diversity + religion (~238 MB profile)
