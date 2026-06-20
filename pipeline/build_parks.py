"""Authoritative agency PARK BOUNDARIES — a clean, recognisable "parks people know"
layer, kept DISTINCT from the broader Canadian Protected and Conserved Areas
(CPCAD) geometry on geography/parks.qmd.

This is the *legal* boundary layer: where CPCAD maps reported/illustrative
protected ZONES (so e.g. Algonquin shows only its protected core, and Rouge can
look parcel-based), this layer maps the boundaries defined in legislation by the
administering agency. The two are shown together so the reader can compare the
reported conservation footprint with the familiar legal park.

Modular by jurisdiction so provinces/territories can be added one at a time
(Ontario next). Phase 1 = FEDERAL only, from Natural Resources Canada's Canada
Lands Survey System (CLSS).

One-time static build (NOT in the weekly registry), like build_geography.py:
fetch raw from the live CLSS REST service at build time (the authoritative,
monthly-maintained, versioned source is the archive — we don't commit raw), then
write the display-ready, validity-repaired GeoJSON to data/geo/.

GEOMETRY GOTCHA (shared with build_parks_detailed): Mapbox GL SILENTLY draws a
BLANK layer if any polygon self-intersects. So repair with buffer(0) → topology-
preserving simplify → buffer(0), assert .is_valid before writing, and do NOT round
coordinates after the repair (rounding re-introduces self-intersections).
"""
import io
import os
import json

import pandas as pd
import geopandas as gpd
import requests

GEO_DIR = "data/geo"

# --- Federal: NRCan / Canada Lands Survey System ---------------------------
# "National Parks and National Park Reserves of Canada Legislative Boundaries"
# (Open Government Licence – Canada). MapServer layer 1; legal boundaries
# (representationPurposeEng == "Legal"). Source SR is EPSG:3979 (NAD83 Canada
# Atlas Lambert); we request outSR=4326 for Plotly.
FEDERAL_URL = ("https://proxyinternet.nrcan-rncan.gc.ca/arcgis/rest/services/"
               "CLSS-SATC/CLSS_Administrative_Boundaries/MapServer/1/query")
FEDERAL_DATASET = ("National Parks and National Park Reserves of Canada "
                   "Legislative Boundaries")
FEDERAL_SOURCE_URL = "https://open.canada.ca/data/en/dataset/9e1507cd-f25c-4c64-995b-6563bf9d65bd"

# distributionTypeEng → our harmonised park_type
_FED_TYPE = {
    "National Park of Canada": "National Park",
    "National Park Reserve of Canada": "National Park Reserve",
    "Rouge National Urban Park": "National Urban Park",
    "Saguenay-St. Lawrence Marine Park": "Marine Park",
}
# source jurisdictionEng (province the park sits in) — fix the source's spelling slip
_PROV_FIX = {"Saskatwechan": "Saskatchewan"}


def _clean_name(name_caps, dtype):
    """The source names are ALL-CAPS ('BANFF NATIONAL PARK OF CANADA'). Title-case
    and drop the trailing ' of Canada' for a clean label. Rouge and Saguenay already
    have a properly-cased form in distributionTypeEng — use it verbatim."""
    if dtype in ("Rouge National Urban Park", "Saguenay-St. Lawrence Marine Park"):
        return dtype
    s = (name_caps or "").strip().title().replace(" Of Canada", "").strip()
    return s


def _write_geojson(gj, path):
    with open(path, "w") as f:
        json.dump(gj, f, separators=(",", ":"))


def build_federal_parks(simplify_tol=0.0006, server_offset=0.0004):
    """Federal parks (legal boundaries) → data/geo/parks_federal.geojson.

    46 features: National Parks, National Park Reserves, Rouge National Urban Park,
    and Saguenay–St. Lawrence Marine Park (tagged marine). Harmonised, jurisdiction-
    agnostic schema so later provincial/territorial layers append cleanly."""
    print("Building federal parks (CLSS legislative boundaries) ...")
    params = {
        "where": "1=1",
        "outFields": ("adminAreaId,adminAreaNameEng,adminAreaNameFra,"
                      "distributionTypeEng,jurisdictionEng,representationPurposeEng"),
        "returnGeometry": "true", "maxAllowableOffset": str(server_offset),
        "outSR": "4326", "f": "geojson",
    }
    r = requests.get(FEDERAL_URL, params=params, timeout=300,
                     headers={"User-Agent": "CanadaObservatory/parks-build"})
    r.raise_for_status()
    g = gpd.read_file(io.BytesIO(r.content))
    g = g[~g.geometry.is_empty & g.geometry.notna()].copy()

    # Validity repair (Mapbox GL silently blanks on self-intersections): buffer(0)
    # → topology-preserving simplify → buffer(0). No coordinate rounding after.
    g["geometry"] = g.geometry.buffer(0)
    g["geometry"] = g.geometry.simplify(simplify_tol, preserve_topology=True).buffer(0)
    g = g[~g.geometry.is_empty & g.geometry.notna()].copy()

    g["park_id"] = g["adminAreaId"].astype(str)
    g["park_type"] = g["distributionTypeEng"].map(_FED_TYPE).fillna("National Park")
    g["name"] = [_clean_name(n, d) for n, d in zip(g["adminAreaNameEng"], g["distributionTypeEng"])]
    g["name_fr"] = [(_clean_name(n, d) if d not in _FED_TYPE else (n or "").strip().title())
                    for n, d in zip(g["adminAreaNameFra"], g["distributionTypeEng"])]
    g["province"] = g["jurisdictionEng"].replace(_PROV_FIX)
    g["jurisdiction"] = "Canada"
    g["admin_level"] = "federal"
    g["source_agency"] = "Natural Resources Canada / Parks Canada"
    g["source_dataset"] = FEDERAL_DATASET
    g["geometry_quality"] = "authoritative legislative boundary"
    g["display_status"] = "include"
    g = g.sort_values("name").reset_index(drop=True)

    cols = ["park_id", "name", "name_fr", "jurisdiction", "admin_level", "park_type",
            "province", "source_agency", "source_dataset", "geometry_quality",
            "display_status", "geometry"]
    gj = json.loads(g[cols].to_json())
    for ft in gj["features"]:
        ft["id"] = ft["properties"]["park_id"]   # top-level id for featureidkey

    os.makedirs(GEO_DIR, exist_ok=True)
    out = f"{GEO_DIR}/parks_federal.geojson"
    _write_geojson(gj, out)

    chk = gpd.read_file(out)
    n_invalid = int((~chk.is_valid).sum())
    from collections import Counter
    tc = Counter(f["properties"]["park_type"] for f in gj["features"])
    print(f"  wrote {out}: {len(gj['features'])} parks {dict(tc)}, "
          f"invalid={n_invalid}, {round(os.path.getsize(out) / 1e6, 2)} MB")
    _write_sources_row()
    return out


def _write_sources_row():
    """Append/refresh the federal provenance row in parks_sources.csv (one row per
    jurisdiction; grows as provinces/territories are added)."""
    path = f"{GEO_DIR}/parks_sources.csv"
    row = {
        "jurisdiction": "Canada", "admin_level": "federal",
        "source_agency": "Natural Resources Canada (Canada Lands Survey System)",
        "source_dataset": FEDERAL_DATASET,
        "source_url": FEDERAL_SOURCE_URL,
        "licence": "Open Government Licence – Canada",
        "boundary_type": "legislative (legal)",
    }
    df = pd.DataFrame([row])
    if os.path.exists(path):
        prev = pd.read_csv(path)
        prev = prev[prev["jurisdiction"] != "Canada"]
        df = pd.concat([prev, df], ignore_index=True)
    df.to_csv(path, index=False)
    print(f"  wrote {path}: {len(df)} jurisdiction(s)")


if __name__ == "__main__":
    build_federal_parks()
