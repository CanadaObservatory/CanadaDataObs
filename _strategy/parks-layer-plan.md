# Parks layer — feasibility assessment & Phase-1 plan (2026-06-20)

*Owner brought a GPT-developed plan to add an authoritative **agency park-boundary**
overlay, starting with federal parks. This doc = the feasibility verdict, source
inspection, reconciliation with the existing site, and the build plan. `_strategy/`
is Quarto-ignored.*

## Verdict

**Feasible and well-conceived.** The named dataset is real, authoritative,
OGL-licensed, small, and fits the site's static-geo pattern. Three refinements
needed because the plan was written without seeing the repo (below). The two-layer
*comparison* (reported CPCAD footprint vs. legal agency boundary) is genuinely
valuable — Rouge and Algonquin are exactly the cases where they diverge.

## Source inspection (confirmed)

- **Title:** National Parks and National Park Reserves of Canada Legislative Boundaries
- **Publisher / custodian:** Natural Resources Canada (Canada Lands Survey System, CLSS)
- **Licence:** Open Government Licence – Canada ✓ (publish-with-attribution, like our other geo)
- **Last modified:** 2022-07-22; **maintenance frequency: monthly**
- **Coverage (4 legislated classes):** (1) National Parks — Schedule 1, *Canada National
  Parks Act*; (2) National Park Reserves — Schedule 2; (3) **Rouge National Urban Park**
  — *Rouge National Urban Park Act*; (4) **Saguenay–St. Lawrence Marine Park** — its Act.
  Comprehensive Claims Settlement Areas removed.
- **Boundary class:** **legislative / legal** (statutory definitions) — strictly better than
  the CPCAD "illustrative, not legal" boundaries and the Parks-Canada "non-legal" boundaries.
- **Access methods:**
  - ESRI REST (EN): `https://proxyinternet.nrcan-rncan.gc.ca/arcgis/rest/services/CLSS-SATC/CLSS_Administrative_Boundaries/MapServer/1`
  - WMS (EN): `…/CLSS_Administrative_Boundaries/MapServer/WMSServer`
  - Shapefile FTP: `https://clss.nrcan-rncan.gc.ca/data-donnees/nplb_llpn/`
  - Open Canada record: `9e1507cd-f25c-4c64-995b-6563bf9d65bd`
- **To confirm at pull (REST `?f=json`; live query was transiently blocked):** exact attribute
  field names, source spatial reference, feature count (expect ~48: ~37 NP + ~10 reserves +
  Rouge + Saguenay). We pull with `outSR=4326` server-side, as the ecozones/CPCAD builds do.

## Current site architecture (what actually exists)

Two parks artefacts already exist — the plan assumed one:

1. **`geography/protected.qmd`** ("Protected & Conserved Areas") — the overview page:
   province %-conserved choropleth (CESI), a **national-parks bubble map** (centroids sized
   by area, `national_parks.csv` from Parks Canada "Places administered…"), and the 30×30
   progress line. Links out to ↓.
2. **`geography/parks.qmd`** ("Canada's Parks, Mapped") — the **heavy detail page**:
   `parks_detailed.geojson` (~2.46 MB, 743 polygons) drawn by `choropleth_categorical`,
   coloured by jurisdiction (Federal green / Provincial blue / Territorial orange).
   **Source = CPCAD**, already **filtered to *park* designations only** (national/provincial/
   territorial parks + Québec parcs nationaux; marine + non-park designations excluded).

Builders: `pipeline/build_geography.py` → `build_national_parks()` (centroids; note it
*already* fetches the Parks-Canada polygons but discards them — ~15 MB) and
`build_parks_detailed()` (the CPCAD polygons; carries the documented validity-repair recipe).

## Reconciliation — the one conceptual mismatch

The plan's **layer 1 = "broad conservation estate (parks + reserves + wildlife areas +
OECMs)."** Our existing CPCAD layer (`parks.qmd`) is **already parks-only**, not the broad
estate. So the plan's two-layer model maps onto our site as:

- **Layer 1 (have):** CPCAD **parks** — reported boundaries, the known fragmentation/zoning
  limitation (Algonquin = protected core only). *Not* the full estate.
- **Layer 2 (new, Phase 1 = federal):** CLSS **legislative** park boundaries — clean, legal,
  recognizable; includes Rouge's proper boundary.

→ **Home for the new layer = `parks.qmd`** (over the existing CPCAD fill), as a toggleable
overlay. For federal parks the comparison (CPCAD footprint vs. legal boundary) is the payoff.
Broadening layer 1 to the *full* conservation estate (all CPCAD designations) is a separate,
later step — **not Phase 1.** Flag this to the owner; don't silently broaden.

## Plan mapped to repo conventions (not the plan's data_raw/scripts tree)

- **Builder:** new `pipeline/build_parks.py` with a modular `build_federal_parks()` (one
  jurisdiction per function, so Ontario/AB/BC/QC/territories slot in later). One-time static
  build, like `build_geography.py` (NOT in the weekly registry). Fetch raw from the CLSS REST
  at build (cache to `/tmp`); **commit only the display-ready GeoJSON** — consistent with the
  repo (raw downloads aren't committed; the authoritative versioned source IS the archive).
- **Output:** `data/geo/parks_federal.geojson` (display-ready, simplified + validity-repaired)
  + `data/geo/parks_sources.csv` (provenance row per jurisdiction, grows over time).
- **Harmonized schema** (GeoJSON feature properties; pragmatic subset of the plan's 13 fields):
  `park_id` (authoritative CLSS id — keep it, don't key on name), `name`, `name_fr`,
  `jurisdiction`="Canada", `admin_level`="federal", `park_type`, `source_agency`,
  `source_dataset`, `geometry_quality`="authoritative legislative boundary",
  `display_status`="include". Designed to be jurisdiction-agnostic.
- **Inclusion (Phase 1):** National Park, National Park Reserve, National Urban Park (Rouge),
  + Saguenay–St. Lawrence Marine Park IF kept (it's a *marine* park — decide whether it belongs
  on a terrestrial-parks page; lean **exclude** for now to match the page's "terrestrial" framing,
  or include with a clear marine tag). Exclude wildlife areas / sanctuaries / ecological reserves /
  proposed / general conservation lands (the source doesn't carry most of these anyway).
- **Geometry rules:** reproject→WGS84; `buffer(0)` → topology-preserving `simplify` → `buffer(0)`;
  **validate `.is_valid` before inlining** (Mapbox GL silently blanks on self-intersections — the
  documented trap); dissolve by `park_id`; preserve genuine multipart parks (no forced contiguity);
  no coordinate rounding after repair. Expect well under 1 MB simplified (~48 features).
- **Map integration (least-disruptive):** on `parks.qmd`, keep the CPCAD categorical fill exactly
  as is; **add the federal legislative boundary as one extra Plotly trace** (a low-opacity
  Choroplethmapbox so the whole polygon is a hover target + carries the faint wash, with a darker
  `marker.line` outline) + its own legend entry. **Toggle = Plotly legend click** (native, clean,
  no new UI framework) — default ON. Its hover is park-only (no CPCAD attributes mixed in):
  `<b>{name}</b><br>Federal park boundary<br>Administered by Parks Canada<br>Source: CLSS
  Legislative Boundaries`. (If a real checkbox UI is wanted later, that's a `parks.qmd`-local
  control, deferred.)

## Styling options (owner to pick; using the brand palette)

The CPCAD fill underneath is green/blue/orange by jurisdiction, over carto-positron.

- **A — Deep Navy (recommended):** outline `#17324D` (brand primary / "authoritative reference"),
  ~1.3 px, + very faint navy wash (~0.07 opacity) or no wash. Matte, brand-aligned, clearly
  distinct from the green federal CPCAD fill; navy reads as "official/legal."
- **B — Soft charcoal:** outline `#3a3f44` (not heavy black), ~1.2 px, + ~0.06 neutral-grey wash.
  Maximally neutral reference layer; won't compete with any jurisdiction colour.
- **C — Darkened Lake Blue:** outline `#155063` (darkened brand link colour), hairline, line-only.
  Ties to the site's accent without using maroon/navy chrome.

All avoid: a second strong green fill, heavy black outlines, saturation, clutter.

## Open decisions for the owner (checkpoint before building)

1. **Home = `parks.qmd`** (overlay on the CPCAD parks) — confirm. (Alt: a new dedicated map.)
2. **Styling A / B / C** (recommend A, navy).
3. **Saguenay–St. Lawrence Marine Park:** include (tagged marine) or exclude on this
   terrestrial-parks page?
4. Acknowledge layer-1-stays-parks-only for now (full-estate broadening is a later step).

## Deliverables when greenlit (logically separated commits)

1. `pipeline/build_parks.py` + `data/geo/parks_federal.geojson` + `parks_sources.csv` (data).
2. `parks.qmd` integration (overlay trace + legend toggle + hover + copy + source note).
3. Validation pass (Rouge, Banff, Jasper, Fundy, Pacific Rim, Gros Morne, a small/coastal park)
   + provenance doc + the implementation report (records in/out, sizes pre/post, Rouge finding).

---

## Jurisdiction coverage (built 2026-06-20)

One unified "Parks — official boundary" navy overlay. Each layer = `build_<jur>_parks()` in
`pipeline/build_parks.py` → `data/geo/parks_<jur>.geojson`; all merged in `parks.qmd`. Provenance
per jurisdiction in `data/geo/parks_sources.csv`.

**Included (federal + 8 provinces + 1 territory = 1,498 parks):** Federal 46 (NRCan/CLSS, legal) ·
Ontario 347 (LIO) · Alberta 116 (AB EPA — PP/WPP/WA/WP) · BC 782 (DataBC — Provincial Park/Protected
Area/Recreation Area, excl. Ecological Reserves) · Québec 34 (MELCCFP parcs nationaux, CC-BY) ·
Manitoba 93 · Saskatchewan 36 (Parks-as-Legislated layer 0) · New Brunswick 24 (GeoNB) · Nova Scotia
16 (Protected-Areas-System, Provincial Park designation) · Yukon 4 territorial parks (Geomatics
Yukon). All open-licence, ArcGIS-REST GeoJSON, 0 invalid geometry. Page ~7 MB (heavy detail page).

**Documented GAPS (show only as CPCAD fill; page carries a generic caveat):**
- **Prince Edward Island** — provincial-parks GIS exists but under a custom licence forbidding
  redistribution; not on the open hub. (Federal PEI National Park is still shown.)
- **Newfoundland & Labrador** — shapefile exists but its licence prohibits redistribution → would
  need CREA-style written permission. ~31 provincial parks.
- **Northwest Territories** — territorial parks published only as POINTS (GNWT layer 204); no open
  polygon boundaries exist.
- **Nunavut** — no GN open GIS; only federal CPCAD carries the 9 territorial parks (already our base
  layer, so no independent comparison to overlay).
Future paths for the gaps: written permission (PEI/NL, like CREA) or point markers (NWT).

## Rouge boundary — legislative vs operational (owner Q, 2026-06-20)

Owner noted our navy Rouge boundary stops ~3 km short of Lake Ontario vs. the Parks Canada visitor
map. **Verified NOT a simplification artifact** — raw CLSS == our output (both south extent
43.8227°N). The CLSS **legislative** Rouge is **60.5 km²** vs the **~79 km² operational** park: the
southern lakefront lands (Rouge Beach / river mouth) are *managed* by Parks Canada but not yet in the
**gazetted legal boundary schedule** (Rouge is still legally assembling land). Parks Canada's
operational GIS service (`vw_Places_Public…`) does **not** include Rouge at all; no separate open
operational-boundary dataset found. NB: our **CPCAD base layer DOES reach the lake** (43.7969°N), so
the fuller Rouge is already visible as the green fill — the navy legal boundary is correctly the
smaller gazetted subset. Decision pending owner: keep legal boundary (authoritative, recommended) ±
a small note / pursue an operational source.
