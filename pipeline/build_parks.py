"""Authoritative agency PARK BOUNDARIES — a clean, recognisable "parks people know"
layer, kept DISTINCT from the broader Canadian Protected and Conserved Areas
(CPCAD) geometry on geography/parks.qmd.

This is the *official* boundary layer: where CPCAD maps reported/illustrative
protected ZONES (so e.g. Algonquin shows only its protected core, and Rouge can
look parcel-based), this layer maps the boundaries defined by the administering
agency — legislative for the federal parks, regulated/official for the provinces.
The two are shown together so the reader can compare the reported conservation
footprint with the familiar park.

Modular by jurisdiction so provinces/territories are added one at a time. Each
build writes its own data/geo/parks_<jur>.geojson with a SHARED harmonised schema;
geography/parks.qmd merges whatever files exist into one "Parks — official boundary"
overlay. Built so far: federal, Ontario, Alberta, British Columbia.

One-time static build (NOT in the weekly registry), like build_geography.py: fetch
raw from the live agency REST service at build time (the authoritative, versioned
source is the archive — we don't commit raw), then write the display-ready,
validity-repaired GeoJSON to data/geo/.

GEOMETRY GOTCHA (shared with build_parks_detailed): Mapbox GL SILENTLY draws a
BLANK layer if any polygon self-intersects. So repair with buffer(0) → topology-
preserving simplify → buffer(0), assert .is_valid before writing, and do NOT round
coordinates after the repair.
"""
import io
import os
import json
from collections import Counter

import pandas as pd
import geopandas as gpd
import requests

GEO_DIR = "data/geo"
_UA = {"User-Agent": "CanadaObservatory/parks-build"}

# Harmonised, jurisdiction-agnostic schema. `park_id` keeps each source's
# authoritative identifier (never key on name); the map merges files and
# re-indexes, so cross-file id collisions don't matter.
HARMONISED_COLS = [
    "park_id", "name", "name_fr", "jurisdiction", "admin_level", "park_type",
    "province", "admin_agency", "boundary_kind", "source_agency", "source_dataset",
    "geometry_quality", "display_status", "geometry",
]


# --- shared fetch / repair / write ----------------------------------------
def _fetch_arcgis_geojson(query_url, where, out_fields, server_offset, page=1000):
    """Page through an ArcGIS REST query as GeoJSON (WGS84). `server_offset` is
    maxAllowableOffset in degrees (coarse server-side simplification to bound the
    payload); pagination handles layers above the server's maxRecordCount."""
    feats, offset = [], 0
    while True:
        params = {"where": where, "outFields": out_fields, "returnGeometry": "true",
                  "maxAllowableOffset": str(server_offset), "outSR": "4326",
                  "resultOffset": offset, "resultRecordCount": page, "f": "geojson"}
        r = requests.get(query_url, params=params, timeout=300, headers=_UA)
        r.raise_for_status()
        gj = r.json()
        fs = gj.get("features", [])
        feats += fs
        # Stop when the server returns a short page and isn't flagging more.
        if not fs or (len(fs) < page and not gj.get("exceededTransferLimit", False)):
            break
        offset += len(fs)
        if offset > 50000:   # safety stop
            break
    return gpd.GeoDataFrame.from_features(feats, crs="EPSG:4326")


def _repair(g, simplify_tol):
    """buffer(0) → topology-preserving simplify → buffer(0). Never round coords."""
    g = g[~g.geometry.is_empty & g.geometry.notna()].copy()
    g["geometry"] = g.geometry.buffer(0)
    g["geometry"] = g.geometry.simplify(simplify_tol, preserve_topology=True).buffer(0)
    return g[~g.geometry.is_empty & g.geometry.notna()].copy()


def _write_layer(g, out_path):
    """Validate + write the harmonised display GeoJSON, with a report line."""
    g = g.sort_values("name").reset_index(drop=True)
    gj = json.loads(g[HARMONISED_COLS].to_json())
    for ft in gj["features"]:
        ft["id"] = ft["properties"]["park_id"]   # top-level id for featureidkey
    os.makedirs(GEO_DIR, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(gj, f, separators=(",", ":"))
    chk = gpd.read_file(out_path)
    tc = Counter(f["properties"]["park_type"] for f in gj["features"])
    print(f"  wrote {out_path}: {len(gj['features'])} parks {dict(tc)}, "
          f"invalid={int((~chk.is_valid).sum())}, "
          f"{round(os.path.getsize(out_path) / 1e6, 2)} MB")


_MINOR = {"and", "or", "of", "the", "de", "du", "des", "la", "le", "les", "aux"}


def _title(s):
    """Title-case, but keep minor words (and, of, de…) lower unless first."""
    words = (s or "").strip().split()
    return " ".join(w.lower() if i and w.lower() in _MINOR else w.title()
                    for i, w in enumerate(words))


# --- Federal: NRCan / Canada Lands Survey System --------------------------
FEDERAL_URL = ("https://proxyinternet.nrcan-rncan.gc.ca/arcgis/rest/services/"
               "CLSS-SATC/CLSS_Administrative_Boundaries/MapServer/1/query")
FEDERAL_DATASET = ("National Parks and National Park Reserves of Canada "
                   "Legislative Boundaries")
_FED_TYPE = {
    "National Park of Canada": "National Park",
    "National Park Reserve of Canada": "National Park Reserve",
    "Rouge National Urban Park": "National Urban Park",
    "Saguenay-St. Lawrence Marine Park": "Marine Park",
}
_PROV_FIX = {"Saskatwechan": "Saskatchewan"}


def build_federal_parks(simplify_tol=0.0006, server_offset=0.0004):
    """Federal parks (legal boundaries) → data/geo/parks_federal.geojson (46)."""
    print("Building federal parks (CLSS legislative boundaries) ...")
    g = _fetch_arcgis_geojson(
        FEDERAL_URL, "1=1",
        ("adminAreaId,adminAreaNameEng,adminAreaNameFra,distributionTypeEng,"
         "jurisdictionEng"), server_offset)
    g = _repair(g, simplify_tol)
    dtype = g["distributionTypeEng"]
    g["park_id"] = g["adminAreaId"].astype(str)
    g["park_type"] = dtype.map(_FED_TYPE).fillna("National Park")
    fancy = dtype.isin(["Rouge National Urban Park", "Saguenay-St. Lawrence Marine Park"])
    g["name"] = [d if f else _title(n).replace(" Of Canada", "")
                 for n, d, f in zip(g["adminAreaNameEng"], dtype, fancy)]
    g["name_fr"] = [(_title(n).replace(" Du Canada", "")) for n in g["adminAreaNameFra"]]
    g["province"] = g["jurisdictionEng"].replace(_PROV_FIX)
    g["jurisdiction"] = "Canada"
    g["admin_level"] = "federal"
    g["admin_agency"] = "Parks Canada"
    g["boundary_kind"] = "legal boundary"
    g["source_agency"] = "Natural Resources Canada / Parks Canada"
    g["source_dataset"] = FEDERAL_DATASET
    g["geometry_quality"] = "authoritative legislative boundary"
    g["display_status"] = "include"
    _write_layer(g, f"{GEO_DIR}/parks_federal.geojson")


# --- Ontario: Land Information Ontario ------------------------------------
ONTARIO_URL = ("https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/"
               "LIO_OPEN_DATA/LIO_Open03/MapServer/4/query")
ONTARIO_DATASET = "Provincial Park Regulated (Land Information Ontario)"


def build_ontario_parks(simplify_tol=0.0009, server_offset=0.0006):
    """Ontario regulated provincial parks → data/geo/parks_on.geojson (~347). The
    regulated boundary is the FULL legal park, so it shows e.g. all of Algonquin —
    unlike CPCAD, which records only the protected core of zoned parks."""
    print("Building Ontario parks (LIO Provincial Park Regulated) ...")
    import re
    g = _fetch_arcgis_geojson(
        ONTARIO_URL, "1=1",
        "OGF_ID,PROTECTED_AREA_NAME_ENG,PROTECTED_AREA_NAME_FR,PROVINCIAL_PARK_CLASS_ENG",
        server_offset)
    g = _repair(g, simplify_tol)
    g["park_id"] = "ON-" + g["OGF_ID"].astype(str)
    g["name"] = [_title(re.sub(r"\s*\([^)]*\)\s*$", "", n or "")) for n in g["PROTECTED_AREA_NAME_ENG"]]
    g["name_fr"] = [_title(re.sub(r"\s*\([^)]*\)\s*$", "", n or "")) for n in g["PROTECTED_AREA_NAME_FR"]]
    g["park_type"] = "Provincial Park"
    g["province"] = "Ontario"
    g["jurisdiction"] = "Ontario"
    g["admin_level"] = "provincial"
    g["admin_agency"] = "Ontario Parks"
    g["boundary_kind"] = "official boundary"
    g["source_agency"] = "Ontario Parks / Land Information Ontario"
    g["source_dataset"] = ONTARIO_DATASET
    g["geometry_quality"] = "regulated boundary"
    g["display_status"] = "include"
    _write_layer(g, f"{GEO_DIR}/parks_on.geojson")


# --- Alberta: Environment and Protected Areas -----------------------------
ALBERTA_URL = ("https://geospatial.alberta.ca/titan/rest/services/boundary/"
               "parks_protected_areas_alberta/FeatureServer/0/query")
ALBERTA_DATASET = "Parks and Protected Areas of Alberta"
# The recognisable PARK designations only. Excludes Provincial Recreation Areas
# (193 mostly-tiny day-use sites), Natural Areas, Ecological Reserves, Heritage
# Rangelands, and the 5 National Parks (already in the federal layer).
_AB_TYPE = {"PP": "Provincial Park", "WPP": "Wildland Provincial Park",
            "WA": "Wilderness Area", "WP": "Wilderness Park"}


def build_alberta_parks(simplify_tol=0.0009, server_offset=0.0006):
    """Alberta provincial parks → data/geo/parks_ab.geojson (~116). Boundaries
    interpreted from the legal descriptions in Orders-in-Council."""
    print("Building Alberta parks (AB Parks & Protected Areas) ...")
    where = "TYPE IN ('PP','WPP','WA','WP')"
    g = _fetch_arcgis_geojson(ALBERTA_URL, where, "PASITES_ID,NAME,OC_NAME,TYPE", server_offset)
    g = _repair(g, simplify_tol)
    g["park_id"] = ["AB-" + (str(int(i)) if pd.notna(i) else n)
                    for i, n in zip(g["PASITES_ID"], g["NAME"].astype(str))]
    g["name"] = [(_title(s) if (s or "").isupper() else (s or "").strip()) or _title(nm)
                 for s, nm in zip(g["OC_NAME"], g["NAME"].astype(str))]
    g["name_fr"] = ""
    g["park_type"] = g["TYPE"].map(_AB_TYPE).fillna("Provincial Park")
    g["province"] = "Alberta"
    g["jurisdiction"] = "Alberta"
    g["admin_level"] = "provincial"
    g["admin_agency"] = "Alberta Parks"
    g["boundary_kind"] = "official boundary"
    g["source_agency"] = "Alberta Environment and Protected Areas"
    g["source_dataset"] = ALBERTA_DATASET
    g["geometry_quality"] = "official boundary (Order-in-Council)"
    g["display_status"] = "include"
    _write_layer(g, f"{GEO_DIR}/parks_ab.geojson")


# --- British Columbia: BC Parks / DataBC ----------------------------------
BC_URL = ("https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/"
          "MapServer/512/query")
BC_DATASET = "BC Parks, Ecological Reserves, and Protected Areas"
_BC_TYPE = {"PROVINCIAL PARK": "Provincial Park", "PROTECTED AREA": "Protected Area",
            "RECREATION AREA": "Recreation Area"}


def build_bc_parks(simplify_tol=0.0015, server_offset=0.001):
    """BC provincial parks → data/geo/parks_bc.geojson (~782). The biggest layer
    (huge coastal parks), so simplified more aggressively. Excludes the 148
    Ecological Reserves (research-only, not visited parks)."""
    print("Building BC parks (DataBC BC Parks/Protected Areas) ...")
    where = "PROTECTED_LANDS_DESIGNATION IN ('PROVINCIAL PARK','PROTECTED AREA','RECREATION AREA')"
    g = _fetch_arcgis_geojson(
        BC_URL, where, "ADMIN_AREA_SID,PROTECTED_LANDS_NAME,PROTECTED_LANDS_DESIGNATION",
        server_offset)
    g = _repair(g, simplify_tol)
    g["park_id"] = "BC-" + g["ADMIN_AREA_SID"].astype("Int64").astype(str)
    g["name"] = [_title(n) for n in g["PROTECTED_LANDS_NAME"]]
    g["name_fr"] = ""
    g["park_type"] = g["PROTECTED_LANDS_DESIGNATION"].map(_BC_TYPE).fillna("Provincial Park")
    g["province"] = "British Columbia"
    g["jurisdiction"] = "British Columbia"
    g["admin_level"] = "provincial"
    g["admin_agency"] = "BC Parks"
    g["boundary_kind"] = "official boundary"
    g["source_agency"] = "BC Parks / DataBC"
    g["source_dataset"] = BC_DATASET
    g["geometry_quality"] = "official boundary"
    g["display_status"] = "include"
    _write_layer(g, f"{GEO_DIR}/parks_bc.geojson")


# --- Québec: MELCCFP Registre des aires protégées -------------------------
QUEBEC_URL = ("https://geo.environnement.gouv.qc.ca/donnees/rest/services/"
              "Biodiversite/Aires_protegees/MapServer/4/query")
QUEBEC_DATASET = "Registre des aires protégées et des AMCE au Québec"
# Layer 4 is pre-isolated to the parcs nationaux (no réserves écologiques/fauniques).
_QC_TYPE = {"Parc national": "Provincial park (Québec)",
            "Réserve de parc national du Québec": "Provincial park reserve (Québec)"}


def build_quebec_parks(simplify_tol=0.0009, server_offset=0.0006):
    """Québec parcs nationaux → data/geo/parks_qc.geojson (~34). Québec calls its
    PROVINCIAL parks "parcs nationaux"; layer 4 of the MELCCFP registry already
    isolates them (no réserves écologiques/fauniques). French toponyms."""
    print("Building Québec parks (MELCCFP parcs nationaux) ...")
    g = _fetch_arcgis_geojson(QUEBEC_URL, "1=1", "MACODE,TOPONYME,DESIGNOM", server_offset)
    g = _repair(g, simplify_tol)
    g["park_id"] = "QC-" + g["MACODE"].astype("Int64").astype(str)
    g["name"] = g["TOPONYME"].astype(str).str.strip()
    g["name_fr"] = g["name"]
    g["park_type"] = g["DESIGNOM"].map(_QC_TYPE).fillna("Provincial park (Québec)")
    g["province"] = "Québec"
    g["jurisdiction"] = "Québec"
    g["admin_level"] = "provincial"
    g["admin_agency"] = "Québec / SÉPAQ"
    g["boundary_kind"] = "official boundary"
    g["source_agency"] = "MELCCFP (Registre des aires protégées)"
    g["source_dataset"] = QUEBEC_DATASET
    g["geometry_quality"] = "official boundary"
    g["display_status"] = "include"
    _write_layer(g, f"{GEO_DIR}/parks_qc.geojson")


# --- provenance -----------------------------------------------------------
_SOURCES = {
    "Canada": dict(admin_level="federal",
        source_agency="Natural Resources Canada (Canada Lands Survey System)",
        source_dataset=FEDERAL_DATASET,
        source_url="https://open.canada.ca/data/en/dataset/9e1507cd-f25c-4c64-995b-6563bf9d65bd",
        licence="Open Government Licence – Canada", boundary_type="legislative (legal)"),
    "Ontario": dict(admin_level="provincial",
        source_agency="Ontario Parks / Land Information Ontario",
        source_dataset=ONTARIO_DATASET,
        source_url="https://geohub.lio.gov.on.ca/datasets/lio::provincial-park-regulated",
        licence="Open Government Licence – Ontario", boundary_type="regulated (official)"),
    "Alberta": dict(admin_level="provincial",
        source_agency="Alberta Environment and Protected Areas",
        source_dataset=ALBERTA_DATASET,
        source_url="https://open.alberta.ca/opendata/gda-6b96341f-2e19-4885-98af-66d12ed4f8dd",
        licence="Open Government Licence – Alberta", boundary_type="official (Order-in-Council)"),
    "British Columbia": dict(admin_level="provincial",
        source_agency="BC Parks / DataBC",
        source_dataset=BC_DATASET,
        source_url="https://catalogue.data.gov.bc.ca/dataset/1130248f-f1a3-4956-8b2e-38d29d3e4af7",
        licence="Open Government Licence – British Columbia", boundary_type="official"),
    "Québec": dict(admin_level="provincial",
        source_agency="Ministère de l'Environnement, de la Lutte contre les changements climatiques, de la Faune et des Parcs (MELCCFP)",
        source_dataset=QUEBEC_DATASET,
        source_url="https://www.donneesquebec.ca/recherche/dataset/aires-protegees-au-quebec",
        licence="Creative Commons Attribution 4.0 (CC-BY) – Québec", boundary_type="official"),
}


def write_sources():
    path = f"{GEO_DIR}/parks_sources.csv"
    rows = [dict(jurisdiction=j, **v) for j, v in _SOURCES.items()]
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"  wrote {path}: {len(rows)} jurisdiction(s)")


if __name__ == "__main__":
    build_federal_parks()
    build_ontario_parks()
    build_alberta_parks()
    build_bc_parks()
    write_sources()
