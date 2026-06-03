# DataCan — Competitive & Landscape Analysis

> **Internal strategy note — not part of the published site.**
> Lives in `_strategy/` (Quarto ignores `_`-prefixed directories), so it is committed to
> the repo but never rendered or deployed. It characterizes other organizations' funding and
> editorial stance, which would be off-brand on the public, strictly-non-partisan site.
> If we ever want a public "Why this exists / how we compare" page, it should be a separate,
> diplomatically-worded artifact, not this document.

**Date:** 2026-06-03 · **Provenance:** multi-source web research (deep-research harness:
~100 search/fetch agents, with adversarial verification of key claims; corrections folded in).

---

## Why DataCan exists (the North Star this analysis validates)

The project owner's motivation — and the lens for everything below:

> A **stable, continually-updated, interactive place** that people *know* they can return to —
> to see the latest update, **share** it, or **reference** it in a conversation with friends,
> family, or colleagues.

This is defined explicitly **against episodic data journalism** (newspaper "X charts that
explain Canada" features, *The Hub*'s DeepDives, broadcast map stories). That genre does good
work, but it is:

- **not available to everyone** (paywalls), and
- **ephemeral and hard to return to** — you can't easily find it again later, you can't trust
  it's still current, and it isn't built to be cited or re-shared in an ongoing discussion.

DataCan's answer is **permanence + returnability + shareability + currency**, free and open to
all. That is not a "nice to have" — per the landscape below, **it is the gap.** No comprehensive
Canadian comparator combines a permanent home, automatic updates, full interactivity, free/open
access, peer-country benchmarking on every chart, *and* neighbourhood-level detail. The episodic
outlets own attention but not permanence; the report-card incumbents own a brand but gate it
behind paywalls and PDFs; the official portal is permanent but Canada-internal and built for
policymakers. **DataCan's defensible position is the one nobody else occupies.**

---

## Bottom line

DataCan sits at the intersection of three separate, crowded spaces — Canadian *benchmarking*
think-tanks, Canadian *civic-data* sites, and international *"state-of-the-nation"* data
projects. Many players own one or two of DataCan's attributes; **none combines all six** (see
the white-space table). The single closest twin is the Conference Board's *How Canada Performs*;
the most visible new entrant is *CanadaSpends*; the best role models are *USAFacts* and
*Our World in Data*.

---

## The comparators, by overlap

### Tier 1 — Direct conceptual twin

**Conference Board of Canada — "How Canada Performs"** (the org rebranded to **Signal49
Research**, 2026-01-26) · <https://www.conferenceboard.ca/hcp/overview/>
The closest thing to DataCan that exists. Benchmarks Canada — and its provinces — against ~16 of
the wealthiest countries across **six domains: Economy, Innovation, Environment, Education &
Skills, Health, Society** — almost exactly DataCan's thesis and domain set. Latest grades:
B (economy, education, health, society), C (environment), **D (innovation)**. 12th annual edition.

- **Run by:** an independent, non-partisan ~70-year-old applied-research institute (~100 researchers).
- **Where DataCan wins:** (1) it's a **letter-grade report card (A–D)** — an explicit good/bad
  valence DataCan deliberately refuses; (2) **sponsor/membership-funded and partly gated**
  (static reports/PDFs) vs. free + open; (3) **static** vs. interactive Plotly +
  **neighbourhood maps**; (4) DataCan adds whole domains it lacks (public finances, government
  workforce, geography, housing micro-data).
- **Where it wins:** brand recognition, media pickup, institutional authority, provincial grades.
- ⚠️ Non-partisan neutrality is **not** a differentiator here — both are neutral. Differentiate on
  **free + interactive + granular + non-graded.**

### Tier 2 — Partial overlap / strong strategic signal

**CanadaSpends** · <https://canadaspends.com/en/about>
Overlaps **only DataCan's public-finances section** — federal spending plus First Nations
financial statements — via slick interactive tools (Tax Visualizer, searchable Spending
Database). **No OECD peer-comparison lens** (DataCan's defining feature) and no other domains.

- **Run by:** "A Project of **Build Canada**," an entrepreneur-led policy initiative (grew from a
  WhatsApp group started by Shopify's Tobi Lütke; ~28–50 tech backers; contributors incl. Shane
  Parrish, Brice Scheschuk, Lucy Hargreaves).
- ⚠️ **Editorial-stance caveat (verified; state neutrally):** CanadaSpends *brands itself*
  non-partisan ("we don't weigh in on whether spending is good or bad"), **but its parent Build
  Canada openly aims to influence policy** (e.g., advocacy around large public-sector job cuts),
  and it has drawn "Are you DOGE?" comparisons and academic criticism. Its "neutral" framing sits
  inside an org with a stated agenda — a contrast DataCan's genuinely backer-free, no-advocacy
  posture can lean into.
- **Lesson to borrow:** polish, memorable naming, a **single killer entry-point tool**, and
  tech-network distribution. It proves there's a real audience for clean, interactive Canadian
  civic data.

### Tier 3 — Official / authoritative baseline (lean on, don't fight)

**StatCan "Quality of Life Hub" + Canada's Quality of Life Framework** ·
<https://www.statcan.gc.ca/hub-carrefour/quality-life-qualite-vie/about-apropos-eng.htm>
The government analogue: **92 indicators across 5 domains** (Prosperity, Health, Society,
Environment, Good governance) + fairness & sustainability lenses. Framework born in Budget 2021
(Finance → Treasury Board → StatCan runs the Hub, launched March 2022). Free, public,
authoritative, neutral — and **explicitly derived from the same OECD well-being lineage** DataCan uses.

- ⚠️ **Two first-pass claims were corrected in verification:** it *is* a general-public resource
  (not just for policymakers), and it *does* contain **some** international comparison (a single
  "Canada's place in the world" indicator page using composite global indices).
- **DataCan's edge, stated precisely:** the Hub is **overwhelmingly Canada-internal** (cuts by
  age/gender/geography) with only that one "place in the world" page, whereas DataCan puts
  **named-17-OECD-peer benchmarking on *every* chart**, adds a unified cross-section narrative,
  modern interactivity, and tract/DA maps. **Strategy: cite it as a source and the trusted
  baseline; don't compete head-on.**

**CIHI's OECD international-comparisons tool** · health-only, interactive, Canada-vs-OECD — proof
the peer-comparison lens exists in Canada but **siloed by topic**. Reinforces DataCan's
"unify it all under one roof" gap-fill.

### Tier 4 — Adjacent: Canadian think tanks (overlapping data, different stance)

| Org | Product | Overlap | Stance |
|---|---|---|---|
| **Fraser Institute** | Economic Freedom index, school report cards (interactive + downloadable) | Adjacent — overlapping econ/fiscal | Libertarian/free-market **advocacy**; private/corporate funding (incl. Koch foundations); ~CA$12M rev |
| **C.D. Howe** | "Toolkit of Economic Indicators" | Adjacent/narrow — macro/monetary, expert audience | Centrist/business **policy advocacy** |
| **IRPP** | Centre of Excellence on the Canadian Federation; *Confederation of Tomorrow* survey | Low/complementary — federalism & opinion | Credibly non-partisan |
| **CSLS** | Index of Economic Well-being; Intl. Productivity Monitor | Adjacent — genuinely peer-benchmarked well-being | Research-neutral, but academic PDFs |

**Lesson:** the think-tank field's data tools are **narrow, expert-facing, and/or
agenda-tethered.** DataCan's *credible, transparent, open-source* non-partisanship is its
differentiator against this whole field.

### Tier 5 — International "state-of-the-nation" genre (role models + infrastructure)

| Project | What it is | Relationship to DataCan |
|---|---|---|
| **USAFacts** · [usafacts.org](https://usafacts.org/about-usafacts/) | Nonpartisan, government-data-only US civic site | **Tone/mission twin.** "We don't tell you what to think." Source-button on every viz; CC-licensed; top reliability/lowest-bias on the 2026 Media Bias Chart. **Funded solely by Steve Ballmer** — independence via single patron, but key-person risk; not replicable solo. |
| **Our World in Data** · [ourworldindata.org](https://ourworldindata.org/funding) | Oxford + Global Change Data Lab (UK charity #1186433) | **Role model + a source DataCan consumes** (complementary, global/topic-first). ~89M visitors/yr. **Sustainability template:** grants (Gates, Quadrature) + **4,000+ reader donations** + audited public accounts. |
| **OECD Better Life Index / Well-being Data Monitor / Data Explorer** | Official peer-comparison tools; Data Explorer is DataCan's upstream SDMX feed | **Authoritative adjacent + infrastructure.** BLI's **user-weighting** is a borrowable feature; all are well-being-only or generic/country-neutral — no single-country narrative. (Well-being Data Monitor launched 2025-11.) |
| **Gapminder** | Rosling non-profit fighting misconceptions | **Tone ancestor.** Lesson: a memorable interaction hook (Dollar Street) drives reach. Global, not single-country. |
| **World Bank DataBank (WDI)** | ~1,486 indicators × 266 countries | Raw-data backbone DataCan consumes; powerful but uncurated, no Canada lens. |
| **UK ONS Well-being dashboard / Germany "Gut leben in Deutschland"** | National-statistics-office dashboards | **Lessons:** ONS's **headline-set + update-cadence discipline**; Germany's **mass public consultation** (~16,000 people) as trust/engagement. Neither is peer-benchmarked. |

**CensusMapper** · <https://censusmapper.ca/> — the one true comparator for **DataCan's
neighbourhood maps**: a long-running solo open project (Jens von Bergmann) turning StatCan census
into zoomable choropleths. **Validates the small-team open-data model**, but is map-first /
census-only (no indicator dashboards, no peer benchmarking) — complementary, not a twin.

**Episodic data journalism** (*The Hub* "DeepDive," *Globe and Mail* "X charts," *CBC* ArcGIS
maps) — uses the same "Canada vs. OECD" lens but as **one-off, often paywalled, sometimes
advocacy-framed articles**, not a standing portal. They compete for *attention* on single
indicators; **they leave the permanent, browsable portal niche open — which is exactly DataCan's
founding motivation (see "Why DataCan exists").**

---

## Synthesis

### Overlap, ranked
1. **Direct twin:** Conference Board *How Canada Performs* (same thesis; different format/access/valence).
2. **Partial twins:** CanadaSpends (fiscal only, no peer lens) + StatCan QoL Hub (comprehensive + official, but Canada-internal).
3. **Tone/mission twins (international):** USAFacts, then OWID.
4. **Adjacent:** Fraser / C.D. Howe / CSLS / OECD BLI / CIHI.
5. **Complementary infrastructure:** OECD Data Explorer, World Bank DataBank, Our World in Data (DataCan consumes these).
6. **Feature-overlap only:** CensusMapper (the maps).

### Lessons from their strengths
- **Source-button discipline (USAFacts):** one-click link to the raw dataset + date + agency on
  *every* chart. DataCan already has metadata sidecars — surface them in the UI.
- **Diversified, transparent funding (OWID):** grants + reader donations + published accounts —
  the antidote to the solo-project and single-patron risks.
- **A killer entry tool (CanadaSpends' Tax Visualizer; Gapminder's Dollar Street):** one
  memorable, sharable interaction as a front door.
- **User-weighted scorecard (OECD BLI):** let visitors weight domains to build *their* "Canada
  scorecard" — engagement + neutrality (the user, not us, assigns importance).
- **Headline set + visible cadence (ONS):** a small "headline indicators, updated weekly" banner;
  DataCan's automated weekly pipeline is a genuine advantage worth showing off via a prominent
  "last updated."
- **Consultation as trust (Germany):** even a lightweight "suggest an indicator" invites ownership.

### The white space — gaps DataCan fills
No competitor combines **all six** of DataCan's attributes; each owns only a subset:

| Attribute | Who else has it | Who *lacks* it |
|---|---|---|
| Single-country (Canada) focus | StatCan Hub, CanadaSpends, How Canada Performs | OWID, OECD, World Bank, Gapminder |
| Comprehensive 11-domain breadth | StatCan Hub, How Canada Performs | CanadaSpends, CIHI, CensusMapper, think tanks |
| **Per-chart OECD-peer benchmarking** | How Canada Performs (graded), CIHI (health only) | StatCan Hub, CanadaSpends, most others |
| Genuinely non-partisan + backer-free | StatCan Hub, USAFacts (patron), CensusMapper | Think tanks, CanadaSpends (advocacy parent) |
| Free / open / no-login / interactive | CanadaSpends, OWID, USAFacts, CensusMapper | How Canada Performs (gated), think-tank reports |
| Neighbourhood (tract/DA) granularity | CensusMapper | Everyone else |
| **Permanent, returnable, citable, continually updated** | StatCan Hub, OWID, USAFacts | Episodic journalism (the founding motivation) |

**That intersection is unoccupied. It is DataCan's moat.**

### Strategic risks & advice
- **Sustainability / key-person risk** (solo project): adopt the OWID path (charity + grants +
  reader donations) before scale becomes a liability.
- **Distribution gap:** *How Canada Performs* and legacy outlets own media mindshare; CanadaSpends
  owns a tech-network megaphone. DataCan's moat is **breadth + the peer lens + real independence +
  permanence**, but it needs a distribution story (a memorable hook tool, shareable chart embeds,
  an annual "State of Canada" release moment).
- **Don't out-neutral the neutral incumbents — out-*scope* and out-*interact* them.** Against
  How Canada Performs: "free, interactive, no letter grades, down to your neighbourhood." Against
  StatCan: "every indicator vs. 17 named peers, in one narrative."
- **Guard the credibility moat:** as a genuinely backer-free site, say so explicitly on the About
  page — the one thing CanadaSpends and the think tanks can't claim.

---

## How this informs next steps

Concrete, prioritized actions derived from the analysis (each maps to a gap or a borrowed lesson):

1. **Make permanence & shareability first-class and visible** *(directly serves the North Star)* —
   prominent "last updated" date sitewide; **stable per-chart permalinks**; one-click "share this
   chart" (link + image/social card); lightweight chart **embeds**. This is the literal answer to
   the episodic-journalism gap: people must *know* they can return, cite, and share.
2. **Surface sourcing per chart (USAFacts pattern)** — turn the existing metadata sidecars into a
   visible "Source · dataset · date" affordance on every figure. Cheap trust win.
3. **Sharpen the About page** — state the differentiation plainly: free + interactive +
   peer-benchmarked-on-every-chart + non-graded + **independent/no funders** + neighbourhood-level
   + permanent & updated. Contrast (diplomatically) with episodic features and gated report cards.
4. **Add a memorable front-door tool** — e.g. a user-weighted **"Build your Canada scorecard"**
   (OECD-BLI-style) or lead with the **"find your neighbourhood"** map as an entry hook.
5. **Show the cadence** — a "headline indicators, refreshed weekly" element that advertises the
   automated pipeline as a feature.
6. **Plan sustainability early (OWID model)** — if scaling beyond solo, a charity/grants + reader-
   donation path; publish methodology/transparency to match.
7. **Optional public-facing "Why DataCan / how we compare" page** — a separate, neutral, *no-named-
   competitors* rewrite of the positioning (not this internal doc) if we want a marketing surface.

---

## Sources

[conferenceboard.ca/hcp](https://www.conferenceboard.ca/hcp/overview/) ·
[canadaspends.com/en/about](https://canadaspends.com/en/about) ·
[thelogic.co — Build Canada launch](https://thelogic.co/news/build-canada-launch-tech-politics/) ·
[StatCan Quality of Life Hub](https://www.statcan.gc.ca/hub-carrefour/quality-life-qualite-vie/about-apropos-eng.htm) ·
[StatCan — Canada's place in the world](https://www.statcan.gc.ca/hub-carrefour/quality-life-qualite-vie/good-governance-saine-gouvernance/canada-place-world-canada-place-monde-eng.htm) ·
[usafacts.org/about](https://usafacts.org/about-usafacts/) ·
[ourworldindata.org/funding](https://ourworldindata.org/funding) ·
[OECD Better Life Index](https://www.oecd.org/en/data/tools/oecd-better-life-index.html) ·
[OECD Well-being Data Monitor](https://www.oecd.org/en/data/tools/well-being-data-monitor.html) ·
[censusmapper.ca](https://censusmapper.ca/) ·
[CIHI OECD tool](https://www.cihi.ca/en/oecd-interactive-tool-international-comparisons) ·
[Fraser Institute](https://en.wikipedia.org/wiki/Fraser_Institute) ·
[C.D. Howe Toolkit](https://cdhowe.org/publication/toolkit-economic-indicators/) ·
[CSLS — Index of Economic Well-being](https://www.csls.ca/iwb.asp) ·
[The Hub — DeepDive example](https://thehub.ca/2026/03/20/why-canadas-gdp-per-capita-crisis-is-real-deepdive/)
