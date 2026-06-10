# Site Reorganization & Gap Roadmap

> **Internal strategy note — not published** (`_strategy/` is Quarto-ignored).
> **Date:** 2026-06-10 · **Status:** Phase 1 (reorg + front door + About suite) IMPLEMENTED
> on branch `site-reorg-six-areas`. Phases 2–4 below are the OWNER-APPROVED to-do list —
> including explicit drops; don't re-propose dropped items without new cause.

## The reorganization (Phase 1 — done)

Nav consolidated **8 thematic dropdowns → 6**. Nav grouping is decoupled from URLs:
**no directories moved, no links broken, no `data/<section>` or `Indicator.section` changes.**

| Area (new) | Pages (nav text → file) |
|---|---|
| **People & Society** | Population & Growth, Diversity, Religion (all `population/`), Crime & Safety (`wellbeing/crime-safety.qmd`) |
| **Economy & Affordability** | Growth & Jobs, Cost of Living (`economics/`), Housing (`housing/`), Income & Inequality (`income/`) |
| **Government & Public Finances** | Government Finances (`fiscal/`), Government Employment + Federal Spending (`government/`) |
| **Health & Well-being** | Health & Health Care, Substance Use (`health/`), Well-being (`wellbeing/index.qmd`, retitled) |
| **Land & Environment** | header *The Land*: Where People Live, Ecozones & Land Cover, Elevation, Water, Agriculture, Protected Areas (all `geography/`) · header *Climate & Atmosphere*: Today's Climate (`geography/climate.qmd`), Climate Change, Fire & Ice (`geography/`), Air Quality, Air Quality by City, Emissions & Energy (all `environment/`) |
| **Education, Science & Innovation** | Education, Science, Innovation |

Judgment calls settled with the owner: Health stays top-level (as Health & Well-being);
Well-being (happiness) rides with Health; Crime & Safety goes to People & Society;
Where People Live stays in Land & Environment as its landing.

**Navbar labels compacted (same day, owner-chosen):** the full area names made the navbar
~1,590px wide, and Bootstrap navbars **clip from the right with no wrap and no scrollbar**
— About + the GitHub link were literally unreachable at 1,440px (MacBook) and below.
Top-level labels are now **People / Economy / Government / Health / Environment /
Education & Science** (~955px min-viewport, under the 992px hamburger breakpoint → can
never clip on any device), and **Home was dropped** (the DataCan brand links home). The
full thematic names remain the areas' identities on the landing cards and page titles —
the navbar label is a wayfinding button, not the definition. This also pre-pays the
French-label problem ("Gouvernement et finances publiques" would never have fit).

Also in Phase 1: landing page rebuilt (6 cards mirroring the areas — fixed the
missing-Geography card and the phantom "educational attainment" promise — plus an expanded
question router); **About became a dropdown**: `about.qmd` (Mission & Method),
`about/people.qmd` (scaffold — owner to add bios), `about/data-sources.qmd` (full source
roster + licences, replacing the stale 4-source list), `about/open-data.qmd` (**the single
deliberate advocacy exception**: creation, use, and open availability of public data,
framed around transparency + informed civic engagement; uses the 2011 voluntary-NHS
data-quality episode descriptively, no partisan blame), `about/related.qmd` (Sites We
Like: OWID, USAFacts, Gapminder, CensusMapper, StatCan QoL Hub, OECD/WB explorers —
deliberately omits gated/advocacy-parent comparators).

## Phase 2 — registry adds (owner-approved, by area)

**People & Society**
- Age structure & aging: pyramid, median age, old-age dependency (StatCan 17-10-0005-01; OECD peers).
- Fertility rate vs peers (WB `SP.DYN.TFRT` — one row).
- Interprovincial migration (17-10-0022-01).
- Immigration composition: PRs by category (IRCC open data), target-vs-actual vs the levels plan.
- **NEW (owner): citizenship/nativity map + data** — Canadian-born / foreign-born citizens
  (naturalized) / non-citizens (incl. PRs). Census characteristics (citizenship + immigrant
  status) on the same CMA/tract machinery as diversity.
- **Languages map — priority** — explicitly modelled on the diversity/religion maps
  (tract map + groups dropdown + history; census mother tongue / home language).
- **NEW (owner): "largest group" option on the Diversity map** — plurality
  visible-minority group (incl. derived White & Indigenous) per tract/CMA; categorical
  layer (`choropleth_categorical`-style) alongside the existing share dropdown.
- DROPPED for now: charitable giving/volunteering (civic set narrowed to turnout + trust,
  and it moved to Government — below); perception-of-safety survey layer (stays deferred).

**Economy & Affordability**
- Gasoline prices (18-10-0001-01 monthly retail).
- Wealth distribution (StatCan Distributions of Household Economic Accounts 36-10-0660,
  quarterly — the official answer to the deferred WID idea).
- Labour depth: participation rate, job vacancies (14-10-0432-01), youth NEET (OECD),
  gender pay gap (OECD).
- Household stress: debt-service ratio (11-10-0065-01) and/or OSB insolvencies.
- Sector composition / resource economy: GDP by industry (36-10-0434-01), resource share
  (placement may end up shared with Land & Environment — decide at build).
- DROPPED: child-care fees. Homeownership rate still waits for the 2026 Census.

**Government & Public Finances**
- Provincial government finances — net debt/deficit by province (StatCan 10-10-0020 family).
- Tax-to-GDP over time vs peers (OECD Revenue Statistics) + tax wedge (Taxing Wages).
- **Democracy mini-set lives HERE** (owner): voter turnout (Elections Canada; historical
  constants OK to hardcode) + trust in institutions + maybe trust in government (OECD
  Trust Survey / GaaG).
- Government infrastructure investment %GDP (OECD).
- SKIPPED (owner-confirmed): public-vs-private pay premium (contested methodology).
  Budget-vs-PBO projections stay declined (no-hardcoded-values rule).

**Health & Well-being**
- % with a regular family doctor (CCHS 13-10-0484) — top priority, the public's #1 question.
- Self-rated mental health (CCHS).
- Long-term-care capacity (OECD).
- Pharmaceutical spending (OECD SHA — existing dataflow).
- Vaccination coverage (WB/WHO rows, e.g. measles/DTP).
- Life satisfaction by province (StatCan Quality of Life hub) to deepen Well-being.
- Avoidable mortality stays removed (2026-06 decision).

**Land & Environment**
- CESI water quality (the Water page is physical-only today).
- CESI species at risk / biodiversity.
- GHG by province (extends the existing ECCC NIR fetcher).
- ZEV/EV share of new registrations (20-10-0025-01).
- Natural-resource production (oil/gas/forestry/mining — CER/StatCan; placement TBD vs Economy).
- DROPPED for now: waste & diversion. SKIPPED: disaster/extreme-weather costs (no clean
  open source; IBC/CatIQ proprietary). Standing defers: pipelines map (licensing), carbon
  price (editorially delicate).

**Education, Science & Innovation**
- **PISA** — revisit as an annual-style manual builder (the CIHI/NAPS pattern fits the
  3-year cycle; 2025 results land Dec 2026). Highest value in the area.
- OECD Education at a Glance re-probe: per-student spending (cleaner) + tertiary attainment.
- Patents (triadic families — likely one more row on the already-used MSTI dataflow).
- International students (IRCC study-permit holders — bridges the Population NPR story).
- Apprenticeships/trades (RAIS 37-10-0023-01).
- DROPPED: PIAAC adult skills; broadband/connectivity. Standing: Leiden parked; UCASS out
  (COI); no publication counts.

## Phase 3 — builders (bigger lifts)

PISA (above), provincial finances, CMHC average rents by city (RMS), languages map build
(census pass), citizenship/nativity build (census pass — can share the languages
extraction), immigration-composition (IRCC).

## Phase 4 — site features

National headline scorecard on the landing page (compose from `SNAPSHOT_SPECS`);
per-page "last updated" freshness stamps (surface the metadata sidecars); a generated
data-index page; expand the question router into the full "Questions Canadians Are
Asking" layer; What's New/changelog; og:image share cards; mobile source-note layout;
French stays gated on v1 (keep new code i18n-ready); `MAINTENANCE.md` consolidating the
~10 annual builder rituals.

## Explicitly out (don't re-propose without new cause)

Child-care fees · waste/diversion · disaster costs · PIAAC · broadband · charitable
giving · perception-of-safety (deferred, researched) · public-vs-private pay ·
Budget-vs-PBO overlay · UCASS · publication counts (Leiden parked) · pipelines map ·
extra trade partners beyond US/EU/China · homeownership before the 2026 Census.
