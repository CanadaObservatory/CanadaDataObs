# Crime & Safety — coverage expansion: research, recommendations, prototypes

*Prepared overnight 2026-06-09/10. Working branch: `crime-safety-expansion`.
Prototype page: `wellbeing/crime-safety.qmd` (rendered, not yet in nav).*

## TL;DR

The site's current safety coverage — Crime Severity Index + homicide rate + a
CSI-by-city map — is a good **severity** summary but answers almost none of the
questions people actually ask about crime: *what kind* of crime, *is it rising or
falling*, *does anyone get caught*, and *what's it like in my city / my
neighbourhood*. The good news from the research: **most of that gap is fillable
from sources we already trust, and ~80% of it lives in a single Statistics Canada
table we can already fetch.**

I researched the landscape at all three scales (national/provincial, metro,
municipal/neighbourhood) plus the "lived-experience" survey layer, and built **six
working prototypes** spanning every scale, from two authoritative sources (StatCan
UCR + Toronto Police Service open data). They render cleanly and are on the branch
for you to open and react to.

What I'd like from you in the morning: a reaction to the six prototypes (keep /
cut / change), and a decision on **where this lives** — my recommendation is a
dedicated **Crime & Safety** page, promoted out of the Society & Well-being page.

---

## 1. Why the current coverage falls short

The Crime Severity Index is a severity-*weighted*, *indexed* number (2006 = 100). It
is excellent for "is serious crime worse than it used to be," but:

- It **hides composition** — a CSI of 80 doesn't tell you whether your city's issue
  is car theft, break-ins, or assault. People experience *specific* crimes.
- It **can't show direction by type** — the public anxiety is precisely that *some*
  crimes (auto theft, shoplifting, fraud) are climbing even as overall/violent crime
  is historically low. One index can't carry that.
- It is **silent on the everyday, sub-serious crime** the user flagged — porch/parcel
  theft, theft from vehicles, bike theft, vandalism — which is most of what people
  actually encounter and talk about.
- It says **nothing about resolution** (clearance) or **lived experience / fear**.

## 2. The data landscape

### 2a. National & provincial — StatCan UCR, table **35-10-0177-01** (the backbone)

This one table is the workhorse. "Incident-based crime statistics, by detailed
violations," **1998–2024, annual**, auto-refreshing (StatCan releases each July),
OGL. It carries **~300 violation types** (motor-vehicle theft, break & enter,
shoplifting, fraud, identity theft, robbery, mischief, theft, assault levels,
homicide…) × **Canada + every province/territory + ~41 CMAs** × statistics
including **actual incidents, rate per 100,000, year-over-year %-change, total
cleared, and persons charged**. Levels, trends, a metro map, and a clearance view
*all come from one fetch*. (It's the sibling of the 35-10-0026-01 CSI table we
already use.)

This drives prototypes 1–4 below.

### 2b. Metro (CMA) — same table, mapped

The 41 CMAs in 35-10-0177-01 carry the same `[35535]`-style codes we already parse
for the CSI map, so any violation's rate joins straight to `cma_2021.geojson`
(verified: 40/40 CMAs match). That means we can map **auto-theft rate, break-and-
enter rate, fraud rate** etc. by metro with a dropdown — extending the existing
CSI map to the *specific* crimes people care about. Prototype 4.

### 2c. Municipal / neighbourhood — Toronto Police Service (the keystone city)

Toronto is the one big-city portal worth a deep dive (and the city the user
named). TPS publishes on one ArcGIS org, OGL-Ontario. The keystone dataset is
**Neighbourhood Crime Rates**: a 158-neighbourhood polygon layer already carrying
**counts + rates per 100,000 + population** for **9 crime types** (auto theft, bike
theft, break & enter, theft-from-vehicle, robbery, assault, theft-over, shootings,
homicide) × **2014–2025**, pre-aggregated to TPS's official counting basis. One
fetch → a turnkey neighbourhood choropleth (prototype 5). Plus rich point datasets
(Bicycle Thefts with cost/recovery status, Auto Theft, Shootings, KSI traffic) —
prototype 6 uses Bicycle Thefts.

**Why not a multi-city comparison?** I researched Vancouver, Montréal, Ottawa,
Calgary, Edmonton, Winnipeg, Halifax, Peel/York. The honest finding: **city portals
are not mutually comparable** — incompatible offence taxonomies, geographies, and
counting rules (Vancouver's portal *explicitly states* its data "is not comparable
to Statistics Canada"). Calgary discontinued its feed in 2024; Edmonton's public
feed was retired. So a cross-city map built from police portals would be
*misleading*. The correct pattern, which the prototypes follow: **the comparable
cross-city layer is the StatCan CMA data; individual cities (Toronto here) are a
"drill into your own city" texture layer underneath it**, each on its own scale.

### 2d. Lived experience / perception — StatCan victimization survey (caveated)

Police-reported counts miss two things people care about: crime that's never
reported, and whether people *feel* safe. Both come from the **General Social Survey
on Canadians' Safety / Survey on Canadians' Safety (SCS)**. The headline facts are
striking — in 2019 only **~29% of crime was reported to police** (violent 24%,
sexual assault 6%), and **80%** felt safe walking alone after dark. **Caveats:** it's
a voluntary survey, runs only every ~5 years (now moving to every 3; 2019 is the
current cycle, next data ~2027), and almost none of it is a clean queryable cube —
most lives in Juristat *article tables*, i.e. **not auto-refreshable**. So this is a
"manual periodic builder" layer (like CIHI wait-times / NAPS), to be added with
clear survey labelling — **not** a weekly series. Our auto-refreshable **clearance**
chart (prototype 3) already delivers a related, reproducible "the system often
doesn't resolve everyday crime" message without any hardcoding.

## 3. The six prototypes (all built, rendering on the branch)

| # | Prototype | Scale | Source | The point it makes |
|---|-----------|-------|--------|--------------------|
| 1 | **Everyday-crime rates over time** (geography dropdown: Canada / province / metro) | National·Provincial | UCR 35-10-0177-01 | Composition + trend of the crime people actually meet; theft-under-$5k is the bulk, vehicle-theft & fraud diverge |
| 2 | **What's rising, what's falling** (diverging %-change bar, 2014→2024) | National | UCR | Fraud +89%, identity theft +124%, shoplifting +66% *up*; break-ins −32%, theft-from-vehicle −43% *down*. Resolves "is crime up or down?" |
| 3 | **How often is a crime solved?** (clearance-rate bar) | National | UCR | Homicide ~73% cleared vs **auto theft ~10%, theft-from-vehicle ~3%**. The statistical face of "property crime feels unpoliced" |
| 4 | **Crime by type across metros** (CMA choropleth, offence dropdown) | Metro | UCR | Auto theft clusters in the Prairies + Toronto–Hamilton; each offence has its own geography |
| 5 | **Toronto, neighbourhood by neighbourhood** (158-hood choropleth, 9-offence dropdown) | Neighbourhood | TPS Neighbourhood Crime Rates | The local "texture" of crime in one's own area, per capita |
| 6 | **Bike theft: seasonality + recovery** | Neighbourhood/City | TPS Bicycle Thefts | Sharp summer peak; **1.0%** of stolen bikes recovered — a concrete "small crime" case study |

Each carries its source note and the required OGL-Ontario attribution; maps have the
existing hover on/off toggle; the descriptive, non-partisan framing is preserved
throughout (no "good/bad", no scorecard valence on crime).

## 4. Recommended build order (if we proceed)

1. **Ship prototypes 1–4 (StatCan UCR).** Highest value, fully auto-refreshing, one
   new fetcher (`fetch_crime.py`), reuses existing builders + one small additive
   change to `choropleth_groups_map` (see §6). This alone transforms the coverage.
2. **Ship prototype 5 (Toronto neighbourhood map)** and **6 (bike theft).** The local
   scale the user emphasized; `fetch_toronto_police.py`, monthly-ish refresh.
3. **Add the perception/“fear gap” layer** (GSS reporting-rate + feel-safe-after-
   dark) as a clearly-labelled survey section / manual builder. High narrative value,
   but slower and partly non-refreshable — do it deliberately, not first.
4. **Optional later:** Toronto cyclist/pedestrian **KSI** traffic-safety map (the
   "vulnerable road user" angle — note e-scooters are not tracked, see §5);
   cybercrime (35-10-0002-01) and hate-crime (35-10-0191-01) by-CMA maps (clean
   standalone annual tables); police-strength-per-100k long series (35-10-0076-01).

## 5. Honest gaps (stated on the prototype page too)

- **No "porch/parcel theft" statistic exists** anywhere official; closest is "theft
  under $5,000." We say so rather than implying coverage.
- **No e-scooter collision data** — kick e-scooters aren't street-legal in Toronto,
  so police don't track them; the micromobility-injury question is *not answerable*
  from police data. (City of Toronto cordon counts are the only adjacent source.)
- **Perception/victimization is survey-based and ~5-yearly** (2019 current) — label
  it as such; don't put it on the same footing as the annual UCR series.
- **Cross-city comparison is StatCan-only** by necessity (city taxonomies aren't
  comparable). Toronto is a depth example, not a ranking.
- **Firearms/shootings nationally** has no clean self-refreshing CODR table (it lives
  in Juristat); if built, derive from UCR firearm-violation codes so it stays
  reproducible, per the no-hardcode rule.

## 6. Technical notes

- **New fetchers:**
  - `pipeline/fetch_crime.py` → `fetch_crime_by_type()` chunk-reads the 1.5 GB UCR
    CSV (streamed/cached zip; can't load whole), keeps curated violations across
    Canada/provinces/CMAs, pivots rate/incidents/cleared/%-change → tidy
    `data/wellbeing/statcan_crime_by_type.csv` (16.7k rows, 1.6 MB).
  - `pipeline/fetch_toronto_police.py` → `fetch_toronto_neighbourhood_crime()`
    (boundary GeoJSON `id=HOOD_158`, simplified to ~30 m, **144 KB** + latest-year
    rate CSV) and `fetch_toronto_bike_thefts()` (server-side aggregation → month /
    status / year, no point paging).
  - Both are registry-ready (`source="custom"`, add to `CUSTOM_FETCHERS`); UCR data
    is annual so weekly re-fetch just re-confirms, with the STALE fallback for a
    transient outage. (The 95 MB UCR download is the one heaviness; if undesirable
    weekly, make it an annual manual builder like `build_naps_cities`.)
- **One additive, backwards-compatible builder change:** `choropleth_groups_map`
  gained `value_fmt` / `value_suffix` / `cbar_title` / `cbar_ticksuffix` (defaults
  reproduce the old percentage behaviour exactly — every existing caller is
  unaffected) so it can map a **rate per 100k** instead of only a share. Verified
  live: the dropdown rescales and the hover reads "… per 100k", not "%".
- **One bespoke chart** is currently inline in the page: the multi-line-over-time
  *with a geography dropdown* (prototype 1). `history_lines` is hardwired for sparse
  census years ("Census year" axis, marker-per-point), so it doesn't fit 27 annual
  points. If we keep prototype 1, promote this to a small `charts.py` builder
  (`lines_over_time` + an optional geography dropdown).
- **Automatability tiers:** UCR (1–4) = fully auto, annual. Toronto (5–6) = auto,
  monthly-ish. Perception = manual periodic. Multi-city = deliberately not built.

## 7. Proposed site structure

Crime now warrants more than a sub-section. Options, in order of preference:

1. **A dedicated `wellbeing/crime-safety.qmd` page** (what the prototype is),
   linked from the Society & Well-being page and the navbar. Keeps the happiness/
   safety landing page light; gives crime room to breathe. *Recommended.*
2. Expand the existing **Safety** section in `wellbeing/index.qmd` in place (simpler,
   but crowds the page).
3. A small **"Crime & Safety" nav dropdown** if we later add the perception layer and
   a traffic-safety page (probably premature now).

## 8. Key sources

- StatCan UCR detailed violations **35-10-0177-01**; CSI **35-10-0026-01** (existing);
  cybercrime **35-10-0002-01**; hate crime **35-10-0191-01**; police personnel
  **35-10-0076-01**; victimization reporting **35-10-0164-01**; perception-of-police
  cluster **35-10-0158…0163** (frozen 2014).
- Toronto Police Service Public Safety Data Portal (`data.tps.ca`, ArcGIS org
  `S9th0jAJ7bqgIRjw`): Neighbourhood Crime Rates, Bicycle Thefts, Auto Theft,
  Shootings, KSI. OGL-Ontario.
- Other cities (for the record, *not* used for comparison): VPD GeoDASH, SPVM Actes
  criminels, OPS Community Safety portal (the cleanest three, but incompatible).
- GSS/SCS on Canadians' Safety (SDDS 4504); Juristat 85-002-X articles for
  victimization/perception detail.
