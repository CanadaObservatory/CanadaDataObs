# DataCan / Canada Observatory — Project Overview

*A review document for collaborators. Reflects the live state of the site: 35
registry indicators across 9 sections, plus derived charts and per-page
scorecards. Last updated 2026-05-30.*

**Live site:** https://canadaobservatory.github.io/CanadaDataObs/
**Repo:** `CanadaObservatory/CanadaDataObs`

---

## 1. What this is

An interactive, data-driven website on **the state of Canada** — population,
economy, cost of living, incomes, public finances, health, education & innovation,
environment, and well-being — with **every domestic indicator set against a fixed
group of 17 OECD peer countries** and, where one exists, an **official benchmark**
(e.g. the Bank of Canada's inflation target). Built with **Quarto + Plotly
(Python)**, data refreshed weekly by an automated pipeline, deployed to GitHub
Pages.

**Editorial stance — deliberate and load-bearing: non-partisan, descriptive, no
policy advocacy.** The site never labels a number "good" or "bad." Its job is to
assemble comprehensive, comparable, authoritative evidence and let the peer
comparisons and official benchmarks do the interpretive work. The conviction is
that a shared, trustworthy factual baseline is the thing most missing from Canadian
civic debate — so we build that, and leave the arguing to readers.

## 2. The design grammar (read this once; it explains every page)

Three recurring structures carry the whole site:

- **The peer-comparison line chart.** Canada in **red** (bold, with markers)
  against the 17 peers over ~25–35 years. Five named comparators get distinct
  colours — **US blue, Australia orange, Germany green, UK purple, Sweden brown** —
  so the eye has anchors; all other peers are light grey; an optional dark-grey
  dashed **peer average** is drawn only for years where ≥half the peers report (a
  composition-bias guard).
- **The ranked bar.** The same metric as a latest-year horizontal bar, so you can
  read Canada's *current standing* at a glance. Most international metrics appear in
  **both** forms (trend + ranking).
- **The "Where Canada Stands" scorecard** at the top of each comparison page: one
  row per indicator, every peer a dot ordered **by rank** so **further right = more
  favourable for Canada** (lower-is-better measures are flipped; rank-based, not
  value-based, so a single outlier like Japan's debt can't distort it). A 10-second
  read of the whole page.

Canada-only series (incomes, rents, the new-housing index, population) instead use
a **single line with a draggable time slider**, opening on the most recent ~25
years.

**Why peer comparison at all?** "Is 80 years' life expectancy good?" is unanswerable
in isolation and immediately answerable against comparable rich democracies. The
peer frame converts raw numbers into judgments readers can actually form — without
us imposing the judgment.

## 3. The peer group

**17 OECD countries:** the G7 (US, UK, Germany, France, Italy, Japan + Canada) plus
Australia, South Korea, Netherlands, Sweden, Switzerland, Norway, Denmark, Finland,
Israel, New Zealand. These are the advanced democracies Canadians actually measure
themselves against. We dropped Belgium and Austria (redundant small EU economies)
and **Ireland** (its GDP and productivity are inflated ~2× by multinational tax
accounting and were distorting those charts). The list and the highlighted
comparator set are each a one-line change in `config.py`.

## 4. Page-by-page: every plot, and why it's there

> Pages marked ★ open with the "Where Canada Stands" scorecard. Unless noted, each
> international metric is shown as **both** a trend line and a latest-year ranked bar.

### Population (domestic; slider charts)
| Metric | Why chosen |
|---|---|
| Population over time (total) | The country's basic scale and growth trajectory — the denominator behind every per-capita figure and much of the housing/services strain. |
| Population by province & territory | Shows how unevenly Canadians are distributed and which regions are growing. |
| Population growth rate | Canada's growth is among the fastest in the G7 — a live debate about housing and capacity. |
| Components of change (births, deaths, immigration, emigration) | Decomposes growth to make immigration's dominant role explicit — directly informs the immigration conversation. |

### Economy & Jobs ★
| Metric | Why chosen |
|---|---|
| Real GDP growth | Headline "is the economy expanding?" measure. |
| GDP per capita (PPP) | Living standards *per person* — a fairer prosperity comparison than total GDP, and the heart of the "Canada is falling behind per-capita" debate. |
| Labour productivity (GDP per hour) | The root driver of long-run wages and living standards; Canada's productivity gap vs. the US/peers is arguably its central economic problem. |
| Unemployment rate | The most familiar gauge of labour-market health. |
| Employment rate (15–64) | Complements unemployment by capturing *participation* (discouraged non-seekers aren't "unemployed") — a fuller read of labour utilisation. |

### Public Finances ★
| Metric | Why chosen |
|---|---|
| Government gross debt (% GDP) | Sustainability and the intergenerational burden of public finances. |
| Budget balance (% GDP) | The surplus/deficit flow that drives the debt stock. |

*(Both from the OECD Economic Outlook; the most recent year or two are projections
and are labelled as such.)*

### Housing & Cost of Living ★
| Metric | Why chosen |
|---|---|
| CPI inflation (YoY) | The cost-of-living headline. **The one explicitly benchmarked chart** — drawn against the Bank of Canada's official 1–3% target band (an official target, not our judgment). |
| Real house prices (indexed) | The housing boom in real terms; Canada's run-up is among the steepest of the peers. |
| House-price-to-income ratio | Affordability — prices relative to earnings. |
| New Housing Price Index (domestic) | A Canada-specific builder-price series over the long run. |
| **Home Prices vs. Incomes** (real, both rebased to 2000) | The most relatable affordability visual: real resale prices (≈ index 280 by 2025) drawn against real median income (≈ 126) — you *see* the gap open. |
| Rent (CPI) | Renters are ~⅓ of households; rent is the cost-of-living piece owner-focused indices miss. |
| Household debt (% disposable income) | How leveraged households are — affordability and financial-risk lens. |

### Income & Inequality ★
| Metric | Why chosen |
|---|---|
| Median after-tax income (domestic, real) | The typical household's take-home pay over time — the most relatable income measure. |
| Average annual wage (real, peer) | Comparable wage *levels* across countries. |
| Gini coefficient | The standard one-number summary of income inequality. |
| Relative poverty (<50% of median, OECD) | Internationally comparable poverty. |
| Low-income rate (LIM-AT, StatCan) | Canada's *domestic* relative-poverty measure — intentionally kept alongside the OECD one so readers see both the international and the official-domestic lens. |

### Health ★
| Metric | Why chosen |
|---|---|
| Life expectancy at birth | The headline population-health outcome. |
| Health spending (% of GDP) | Share of the economy devoted to health. |
| Health spending per person (USD PPP) | The relatable per-capita figure (Canada ≈ US$7,300, mid-pack) — pairs with %GDP. |
| Hospital beds / Practising physicians / MRI units (per capita) | System **capacity** — the inputs that bear on access and wait times, and the closest *internationally comparable* proxies for the wait-times debate (CIHI's actual wait-time data has no automated feed). |

### Education & Innovation ★
| Metric | Why chosen |
|---|---|
| R&D expenditure (GERD, % GDP) | Overall innovation investment. |
| Business R&D (BERD, % GDP) | Private-sector innovation specifically — Canada's is notably low, a competitiveness concern. |
| Researchers per 1,000 employed | The human-capital intensity of the knowledge economy. |

*(PISA scores and tertiary attainment are deferred — the OECD attainment feed mixes
national methodologies and PISA has no clean SDMX feed; flagged in the docs.)*

### Environment ★
| Metric | Why chosen |
|---|---|
| CO₂ per capita | The most directly comparable carbon-footprint measure. |
| CO₂ trend (indexed, 2000 = 100) | Trajectory — is Canada actually cutting emissions? |
| CO₂ productivity (GDP per unit CO₂) | Economic output per tonne — the efficiency lens. |
| Low-carbon electricity (%) | The grid-decarbonisation measure (renewables **+** nuclear — "renewables" alone misleadingly omits nuclear). Leads the energy story. |
| Electricity mix by country | How each peer generates power. |
| Canada's electricity mix over time | The domestic shift (coal phase-down). |
| **Electricity mix by province** (coal/gas/oil split) | The enormous provincial variation — and **coal is broken out from gas** because it emits ~2× the CO₂/kWh (Nova Scotia ~42% coal, Saskatchewan ~28%, Alberta now ~2% after its coal→gas switch, Ontario 0%). |
| Total energy mix (primary) | The honest fuller picture — including transport/heating fuels, where fossil still dominates even though the grid is mostly clean. |

### Society & Well-being
| Metric | Why chosen |
|---|---|
| Happiness / life evaluation (Cantril ladder) | The summary "how is life going?" subjective measure (trend + ranked bar). |
| What underlies the score | The World Happiness Report's explanatory factors (income, social support, healthy life expectancy, freedom, generosity, corruption) — shows *what drives* the headline number. |

## 5. How this informs Canadians about the state of their country

The site does three things at once that a typical stats portal or op-ed does not:

1. **It makes everything comparable.** Every domestic figure is placed against
   advanced-democracy peers and, where one exists, an official benchmark. This is
   the core move: it turns "is this number good?" — which invites partisanship —
   into "here is where Canada sits among comparable countries," which invites
   evidence. The scorecard delivers that verdict-free verdict in ten seconds per
   page; the charts behind it supply the nuance.

2. **It's comprehensive, not cherry-picked.** Nine domains chosen to *describe the
   whole state of the country* — the things people actually live (housing, health,
   incomes, jobs, the cost of living) sitting beside the structural measures
   (productivity, debt, emissions, R&D). Breadth is itself an anti-spin device: you
   can't tell a one-sided story when the adjacent page shows the trade-off.

3. **It's relatable as well as comparative.** Alongside the international indices sit
   figures in plain Canadian terms — median take-home pay, real dollar home prices
   vs. incomes, health spending per person, your province's actual electricity
   sources. The comparative lens gives context; the relatable lens gives a way in.

The payoff is a **shared factual baseline for civic debate.** The site is explicitly
*not* trying to tell Canadians what to conclude about immigration, housing, health
care, or climate. It is trying to make sure that when they argue about those things —
about what's working, what's falling short, and what to do — they're arguing from
the same authoritative, comparable, up-to-date evidence. Every chart shows its
source and date and offers a one-click CSV download, so it functions as a citable
reference, not an opinion piece.

## 6. Integrity, automation, and sources

- **Sources** — all open and attributable: **Statistics Canada** (bulk tables),
  **OECD** (SDMX API), **Our World in Data** (energy, CC-BY), **World Happiness
  Report**. No source on the public site restricts republication.
- **Architecture** — a declarative **indicator registry** (`pipeline/config.py`) is
  the single source of truth; one generic fetcher per source; a weekly GitHub Action
  refreshes data. A **STALE fallback** keeps the last good data if a source is
  briefly down, so a transient outage never blanks a chart or fails the build. Every
  dataset carries a metadata sidecar (source, retrieval date, transformations).
- **One licensing exception, handled.** Absolute resale **house prices by city ×
  dwelling type** exist only in the **CREA MLS® HPI**, whose terms forbid public
  republication without consent. That figure is therefore built **internally only**
  (git-ignored, never published); the public affordability story uses open data
  instead. A permission request to CREA is outstanding.
- **Known gaps / deferred** (candidates, not committed): PISA & tertiary attainment
  (data-harmonisation issues), CIHI wait-times (no feed), business investment,
  trade/current account, top-income shares & wealth, consumption-based CO₂,
  nurses/CT/ICU capacity. These are documented, not hidden.
