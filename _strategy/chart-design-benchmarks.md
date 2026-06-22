# Chart-design benchmarks: lessons from Canada's data communicators

*Written 2026-06-17. Internal strategy note (unpublished — `_strategy/` is Quarto-ignored).*

**Purpose.** The owner asked whether we could learn from how leading Canadian data
communicators on X construct and design their charts, and translate that into
concrete CanObs changes. This note is the result: a design review of three named
accounts plus the broader scene, the convergent lessons, and a prioritized list of
concrete changes (one already shipped this pass).

---

## TL;DR — the changes

| # | Change | Lesson (whose) | Where | Status |
|---|--------|----------------|-------|--------|
| 0 | **Recession shading** behind macro time series | Dias/Smith + macro convention | `charts.add_recession_bands` + wired into quarterly-GDP chart | **DONE this pass** |
| 1 | **Index-to-base-year toggle** on peer lines (Level ↔ Indexed YYYY=100) | Smith "four views" + Dias + OWID | `peer_comparison_line` opt-in param | Proposed (owner greenlight) |
| 2 | **GDP per-capita-over-time peer line** + the per-capita caveat footnote | Dias (done the non-partisan way) | new chart on `economics/index.qmd`, existing CSV | Proposed |
| 3 | **One-line descriptive chart subtitle** convention | landscape (OWID/banks/von Bergmann) | prose pattern + optional helper | Proposed |
| 4 | **`add_event_markers()`** inflection-annotation helper | Moffatt/Dias | `charts.py` primitive | Proposed (code sketch below) |
| 5 | **WHAM-style affordability stack** (weeks-of-wages) | Moffatt | `housing/index.qmd` | Proposed (Tier 2) |
| 6 | **Population-growth-vs-housing-completions gap** chart | Moffatt | `population/` or `housing/` | Proposed (Tier 2) |
| 7 | **Per-chart metadata / "get the data"** affordance | Smith/USAFacts/OWID/von Bergmann | Quarto helper | Proposed (Tier 2; CREA caveat) |
| 8 | Decade-bar re-cut; starts-per-1,000 map; simulators; annual "charts of the year"; sparkline scorecard cells | various | various | Backlog (Tier 3) |

---

## How this was researched (and the honest limits)

- **X.com itself is unreadable to our tools** — direct fetches return **HTTP 402
  Payment Required**. We cannot scrape feeds, search tweets, or read these accounts
  on X. We reached every subject through their **off-X surfaces** instead (personal
  sites, Substacks, Medium, Thread Reader archives, GitHub, LinkedIn, YouTube show
  notes, think-tank pages, news bylines).
- Four parallel research agents were run (Philip Smith, Mike Moffatt, Richard Dias,
  and a broader-landscape scout). Their full findings are distilled below.
- **Verification caveat:** the fetch tooling reads page *text/captions/methodology*,
  not chart *pixels*. So chart-construction logic, titling philosophy, sourcing
  habits, and tooling are well-evidenced; exact colours/fonts/spacing are described
  (often from the pages' own words), not pixel-confirmed. For live/current plots, the
  only path is the Claude-in-Chrome extension against an authenticated X session.

---

## The four sources

### Philip Smith (@PhilSmith26) — the closest analog to us
Former StatCan Assistant Chief Statistician (national accounts). Builds
**self-updating Canadian-economy dashboards** — a macro one (254 series) and a
provincial one (691 series) — plus a full StatCan table explorer ("Tabler"). The
philosophical sibling of CanObs, and a near-total validation of our architecture.

- **The "four views per indicator" lever (his signature):** every dashboard chart
  can be shown as **Level / % change / YoY % / 13-month MA** at the user's option;
  his Tabler extends this to a full transform menu incl. **Index (rebase to 100),
  Shares-of-a-total, annualized 3/6-mo rates**. One interface, learned once, applied
  to every indicator. **This is the single highest-value steal** (→ change #1).
- **Normalization, justified in prose:** %-of-GDP for long fiscal series, **log
  scale** for exponential long series, **index-to-100** for cross-metric
  comparability — and he *explains why* in the text each time ("comparing deficits in
  dollars over 158 years is apples to oranges").
- **Titles are neutral/descriptive, not takeaway headlines** — the conclusion lives
  in surrounding prose. He is independent confirmation that our `##`-as-title,
  non-editorial approach is right for a citable resource.
- **Trust through visible provenance:** source + vector ID + seasonal-adjustment
  status + preliminary-estimate flags shown *on* the dashboard; revision/vintage
  analysis as its own product. Metadata is a feature, not a footnote.
- **Evergreen by construction:** dashboards auto-refresh after StatCan's 8:30am Daily
  — a bookmark never goes stale. (Our weekly cron + STALE fallback is the static-site
  equivalent; keep it — it's more robust for a citable archive and works from
  `file://`.)
- **Don't copy:** his utilitarian, brand-less, table-dense "instrument panel"
  aesthetic, and the "254 series, all at once" *browser* model — CanObs is a *curated
  story per theme* with a real visual identity. Curation is our feature.

### Mike Moffatt (@MikePMoffatt) — the framing/editorial lesson
Economist (Missing Middle Initiative). Canada's most prolific housing/affordability
chart-poster. His charts mostly live on the **MMI Substack**, run deliberately as a
"small, fast, frequent, graphics-heavy" operation modelled on bank economics notes.

- **Signature construction = the gap between two series** (population growth vs
  homebuilding; need vs starts; the 1980s vs now). The *gap itself* is the chart.
- **Decompose to reset intuition:** his WHAM ("Weekly Housing Affordability Metric")
  splits affordability into **(a) weeks of pre-tax wages to save a 20% down payment**
  + **(b) weeks of wages for 5 years of mortgage payments** — exposing the
  down-payment barrier that a plain price-to-income ratio hides. Brilliant, and
  reproducible from our data (→ change #5).
- **Concrete relatable anchors:** a *specific* home in a *specific* city/year ("a
  London home at $163,200 in Jan 2005 = 42 weeks of the median wage"), real-dollar
  inflation adjustment, per-1,000 regional normalization, decade-bar re-cuts to kill
  annual noise.
- **Self-documenting titles:** what / units / geography baked into the title so a
  screenshot stands alone.
- **Don't copy (advocacy edge):** he *grades* governments (letter-grade housing
  "report cards"), asserts causal blame (DCs "the biggest contributor to the crisis"),
  and uses incredulity anchors ("a $66 coffee"). CanObs must stay descriptive — show
  DCs, starts, prices side by side and let the reader connect them; never grade a
  province or assert the causal link. A "gap" chart must be vs **population growth /
  household formation** (data-derived), never vs an advocacy "homes we need" target.

### Richard Dias (@RichardDias_CFA) — the per-capita lens (handle with care)
Global macro strategist (PGM Global / IceCap; The Loonie Hour). His core output is a
narrated chart deck, "Canada's Lost Decade," built around **per-capita GDP
stagnation since ~2014**.

- **Per-capita is the whole thesis:** he distrusts aggregate GDP ("fake GDP growth")
  and reframes everything per person. His hero chart is **real GDP per capita,
  Canada vs US, indexed**, diverging at a ~2014 inflection.
- **Setup-then-reveal:** lead with the flattering aggregate ("Canada leads the G7 on
  growth"), then divide by population to flip it — the reader feels they discovered
  the gaslight.
- **Indexing to a common base year** so a cumulative gap is the visual punchline;
  US as the primary named anchor; OECD/IMF for "worst except Luxembourg" ranking;
  end-labelled lines; recession shading.
- **Don't copy — and add what he omits:**
  - His **titles and tone** are evaluative/partisan ("Lost Decade," "The Immigration
    Fiasco," "Too Many Passengers," "it ain't pretty"). Ours stay neutral.
  - **The cherry-picked baseline.** The whole genre hinges on starting at ~2014 (the
    pre-oil-crash peak), which maximizes the apparent gap. If we index, **let the
    user choose the base year** and **show the full series** so the choice is
    transparent.
  - **Carry the per-capita caveats he skips** — this is exactly our non-partisan
    value-add. GDP-per-capita comparisons (esp. Canada vs US) are loaded: US
    per-capita is flattered by **longer average hours worked** and denominator
    differences; per-capita ignores leisure/time value; StatCan and IRPP both argue
    it's a flawed welfare proxy. **Wherever we lead with per-capita, footnote this**
    (→ change #2).

### The broader scene (the landscape scout)
- **Most relevant kindred spirits:** **Trevor Tombe / Finances of the Nation**
  (financesofthenation.ca — a non-partisan, citable, downloadable fiscal-data resource
  with **policy simulators**; our closest mission-twin) and **Jens von Bergmann /
  MountainMath / CensusMapper** (the maps + reproducibility gold standard; open R
  packages `cancensus`/`cansim`). Then Stephen Gordon (WCI blog + a "data sources for
  Canadian economists" page), Kevin Milligan (tax/inequality), Ben Rabidoux (housing,
  paywalled), bank economics desks (RBC/TD/Scotia chart packs), Better Dwelling.
- **Design role models:** **Our World in Data** (the interactive-explorer gold
  standard — chart/map/table toggle, entity highlight, axis-normalize, download
  SVG/PNG/CSV) and **USAFacts** (the non-partisan, comprehensive, "let the numbers
  speak" positioning twin — per-chart "source" button).
- **Tools:** the reproducible culture is **R → ggplot / Plotly** (our Quarto+Plotly
  is right in it); newsrooms use **Datawrapper/Flourish** (the legibility benchmark);
  bank desks ship static **Excel/PDF** chart packs. *The gap to close isn't the engine
  — it's Datawrapper-grade legibility discipline on top of Plotly.*

---

## Convergent lessons (where ≥2 sources independently agree)

1. **A uniform "view" transform on each chart** — Level / YoY% / Indexed / per-capita.
   (Smith's whole product; OWID's normalize toggle; Dias's indexing.) → #1, #2.
2. **Recession / era shading** on macro time series. (Dias; Smith; bank desks;
   C.D. Howe dates are authoritative.) → **#0 (done).**
3. **Provenance is non-negotiable and should be *visible per chart*** — source + table/
   vector ID + last-updated, ideally a link to the data. (Smith's metadata panels;
   USAFacts source button; OWID overlay; von Bergmann reproducibility.) → #7.
4. **Normalize before you compare** — per-capita / per-1,000 / index, *and say why*.
   (All four.) → #2, #6, and a standing editorial habit.
5. **One chart, one message, screenshot-complete** — units + geography in the title so
   a lifted PNG self-documents. (Moffatt; Smith; Datawrapper.) → #3.
6. **Entity highlighting over rainbow spaghetti** — highlight the focal series, mute
   the rest, reveal others on interaction. *We already do this well* (Canada-red +
   grey-until-active peers); we're ahead of most here. Hold the line.
7. **Neutral titles for a citable resource** (Smith) **vs. takeaway titles for
   shareability** (banks/von Bergmann) — a real tension, resolved next.

---

## The titling tension, resolved

The landscape scout flagged "takeaway titles" as our biggest upgradeable gap; Smith
and our own non-partisan stance argue for neutral titles. **Both are right, and the
resolution is a descriptive — not evaluative — one-line subtitle under the neutral
`##` heading.** State the fact, not the verdict:

- ✅ "Real GDP per capita rose 0.7% over 2014–2024; the OECD median rose ~5%."
- ✅ "Canada has 2.6 hospital beds per 1,000 people — below the peer median of 4.3."
- ❌ "Canada's productivity emergency." ❌ "Housing is dangerously unaffordable."

The fact *is* the takeaway when the comparison is built in; we never need the
adjective. This keeps the screenshot-complete, shareable quality without crossing into
advocacy. (→ change #3.)

---

## Concrete DataCan changes

### Tier 0 — shipped this pass

**#0 — Recession shading (`add_recession_bands`).** New reusable helper in
`charts.py` + a `CANADA_RECESSIONS` constant (C.D. Howe Business Cycle Council dates:
1981–82, 1990–92, 2008–09, 2020 — immutable historical facts, sourced in the code
comment). Wired into the **quarterly-GDP chart** on `economics/index.qmd` (its natural
home — the chart is explicitly about recessions): neutral-grey bands drawn *below* the
bars, visible when the slider zooms out past 2008; prose now names the Council as the
official arbiter; source note credits it. Reusable on any Canada macro series (policy
rate, unemployment, …). Verified: page renders, band dates embedded in the figure JSON.

### Tier 1 — high value, low controversy (recommend next, owner greenlight)

**#1 — Index-to-base-year toggle on peer lines.** Add an opt-in `index_views=` to
`peer_comparison_line` (existing callers unaffected). Precompute, per country, a
rebased copy `y_idx = y / y[base] * 100`, and add a Plotly `updatemenus` with
**Levels / Indexed (YYYY=100)** — same restyle idiom as `lines_over_time(measures=…)`.
Crucially, **expose the base year as a control** (or default it to `initial_start`,
shown in the y-title) so we never hard-code a single flattering baseline — the
explicit antidote to the Dias cherry-pick. This generalizes Smith's "four views" into
our existing machinery.

**#2 — GDP per-capita-over-time peer line + the caveat footnote.** We already fetch
`oecd_gdp_per_capita.csv` (per-capita PPP **levels, 2000–**, all peers) but only draw
it as a latest-year ranked bar. Add a `peer_comparison_line` of it (with #1's index
toggle) on `economics/index.qmd` — this is Dias's hero chart done the non-partisan way
(full series, user-chosen base). **Required companion: a standing caveat note**, e.g.:
> *Per-capita GDP is a partial measure of living standards. Cross-country gaps partly
> reflect differences in average hours worked and in how populations are counted, and
> the measure says nothing about how income is distributed or about leisure. Read it
> alongside median income, wages, and hours.*
Optional extension: add an **aggregate real-GDP level** peer series (OECD has it) to
draw the aggregate-vs-per-capita twin — but that's a new indicator; the per-capita
line alone is the high-value, zero-new-data win.

**#3 — Descriptive one-line subtitle convention.** Adopt a house rule: every chart `##`
gets a one-line *descriptive* lead (fact-with-comparison, never a verdict — see the
resolution above). Mostly a prose pattern; optionally a tiny `chart_caption()` helper
emitting a muted line so it travels into a screenshot. Cheap, high-impact, protects
non-partisanship.

**#4 — `add_event_markers()` inflection helper.** Sibling of `add_recession_bands`;
draws labelled vertical lines at dated turning points (Moffatt/Dias annotate the line
*on* the line). Sketch:
```python
def add_event_markers(fig, events, *, color="#888", dash="dot", label_color="#666"):
    """events: list of (date, label). Dotted vertical line + top label at each —
    for marking dated inflection points (a rate-hike cycle start, a methodology
    break, a policy date) on a date-axis time series."""
    for date, label in events:
        fig.add_vline(x=date, line=dict(color=color, dash=dash, width=1))
        fig.add_annotation(x=date, y=1.0, yref="paper", yanchor="bottom",
                           text=label, showarrow=False, textangle=0,
                           font=dict(size=9, color=label_color))
    return fig
```
Hold until there's a chart that needs it (don't add dead code) — candidates: the BoC
policy-rate-vs-inflation chart, NHPI/rent.

### Tier 2 — higher effort or more editorial (worth doing, needs design sign-off)

**#5 — WHAM-style affordability stack.** Reproduce Moffatt's two-component affordability
view from data we already have: real median income (`statcan_median_income`), the CREA
benchmark price (via `crea.py`, **display-only**), and the 5-year conventional mortgage
rate (`boc_rates` `V80691335`). Stack **"weeks of median wages to save a 20% down
payment"** + **"weeks of wages for 5 years of mortgage payments."** More informative
than the current price-to-income line. **Constraints:** strictly descriptive ("weeks of
median wages," no incredulity framing); CREA stays charts-only (never a CSV download);
carry `crea.ATTRIB`.

**#6 — Population-growth-vs-housing-completions gap.** Two series — annual population
growth (`statcan_population_components`) and housing completions/starts
(`statcan_housing_starts`) — as a gap or decade bars. **Descriptive guardrail:** plot
growth vs building, NOT vs a modelled "homes we need" target (that's contestable
advocacy). Add a one-line methodology note that Canada counts starts later than the
US/UK/AUS (Moffatt's genuinely clarifying point) so cross-country starts aren't
misread.

**#7 — Per-chart metadata / "Get the data" affordance.** A Quarto `<details>` helper
reading the existing JSON sidecar: source · StatCan/OECD/vector ID · frequency · units
· last-updated · (optionally) a link to the CSV. Operationalizes the "stable, citable"
mission. **Two hard caveats:** (a) **CREA figures must never offer a data download**
(redistribution) — the helper must be opt-out for those; (b) publishing CSVs means
declaring them in `project.resources` — a deliberate step, not automatic.

### Tier 3 — backlog / aspirational

- **Decade-bar re-cut** option for noisy annual series (population components, net
  migration) — a small data transform in the qmd; `single_bar` already does the bars.
- **Housing-starts-per-1,000-population** provincial/CMA choropleth — needs a by-geography
  starts pull (current `housing_starts` is Canada-only); flag the data gap.
- **Policy simulators** (Finances of the Nation's killer feature) — a slider-driven
  fiscal/demographic projector; standout, mission-aligned, but a real build.
- **Annual "N charts that defined the year"** curated recap page (RBC/Maclean's
  franchise) — a shareable, seasonal entry point for a returnable resource.
- **Sparkline trend cells** in the "Where Canada Stands" scorecard (USAFacts) — adds
  magnitude/trend to the rank dots.
- **A "how this is built / data pipeline" reproducibility page** — von Bergmann-style;
  a differentiator no bank shop or Better Dwelling can match. (We already *are* this
  internally via the registry; surfacing it is the move.)

---

## Topic / coverage gaps (from the same research)

Distinct from the design changes above: topics/charts the leading Canadian data
communicators cover that CanObs does not. Gap-checked against the live site and the
June-3 `topic-coverage-assessment.md`, so this is only what's additive. The field's
centre of gravity — especially the most-followed accounts — is "within-Canada,
decomposed, mechanism-revealing" charts, the inverse of our OECD-peer-ranking strength.

**✅ Confirmed for the backlog (owner, 2026-06-17) — build deferred pending the full-site review:**
- **Tax structure & redistribution** (Milligan) — effective/marginal rates, who pays,
  tax-and-transfer; deepens the June-3 "total-tax-to-GDP" aggregate. *Open question:
  which StatCan tables are reproducible vs modelled — pre-scope before building.*
- **Household financial stress** (Rabidoux) — debt-service ratio (BoC), consumer
  insolvencies (OSB), mortgage arrears (CMHC/BoC). Open + auto-refreshable; new topic.
- **Commute / journey to work** (von Bergmann) — mode + duration; Census, mappable like
  our existing census layers (5-yearly).
- **Per-capita / productivity decomposition** (Smith, Dias) — capital-deepening × hours ×
  participation × population composition (isolating the NPR share); derive from
  OECD/StatCan series we mostly hold. New chart genre.

**Candidates raised but not selected (this round):** down-payment affordability / "WHAM"
(Moffatt — overlaps the design proposals), population-growth-vs-housing-supply gap
(Moffatt), fiscal federalism / equalization (Tombe), business & consumer confidence
(Dias/banks; licensing to check), data revisions/vintages (Smith, niche).

**Already deferred:** homeownership/tenure (→ 2026 Census); wealth/net-worth distribution
(WID patchy — but **StatCan DHEA** = wealth by quintile, quarterly, is a cleaner path to
revisit).

---

## What we will NOT copy

- **Evaluative/partisan titles and tone** (Dias's "Lost Decade / Fiasco"; "dangerously
  unaffordable"). Neutral, descriptive, comparison-built-in.
- **Graded scorecards with a valence on contested policy** (Moffatt's letter-grade
  housing report cards). Our scorecard only assigns a `good` direction where
  "favourable" is uncontroversial — a housing-policy grade fails that test.
- **Asserted causal/blame chains** (immigration → stagnation; DCs → crisis). Show the
  components side by side; let the reader connect them.
- **Cherry-picked baselines** — let the user choose the index base; show full history.
- **Hand-dropping "inconvenient" countries** (Dias's "Luxembourg isn't a real country").
  Our exclusions (Ireland — multinational accounting) stay *principled and documented*.
- **Dual axes, truncated bar baselines, rainbow spaghetti** — already avoided; keep it.

---

## Monitoring shortlist (8 off-X surfaces — no X account needed)

| Source | URL | Channel | Why |
|--------|-----|---------|-----|
| Mountain Doodles (von Bergmann) | doodles.mountainmath.ca | Blog + RSS | Reproducible census/housing viz; maps benchmark |
| Finances of the Nation (Tombe) | financesofthenation.ca | Site | Mission-twin; fiscal data + simulators |
| Missing Middle Initiative (Moffatt) | missingmiddleinitiative.ca | Substack (RSS) | Graphics-heavy housing microresearch |
| Philip Smith | philip635.substack.com | Substack | Method-forward macro dashboards |
| Worthwhile Canadian Initiative (Gordon) | worthwhile.typepad.com | Blog | Macro/labour charts + data-source curation |
| RBC Economics | rbc.com/en/economics/canadian-analysis | HTML/PDF | Polished macro chart packs |
| Our World in Data | ourworldindata.org | Site + RSS | Interactive-explorer design model |
| USAFacts Viz Lab | usafacts.org/visualizations | Site | Non-partisan, comprehensive design model |

---

## Sources (representative; full set in the research run)

- Philip Smith: philip635.substack.com (+ `/p/two-new-canadian-economy-dashboards`),
  philipsmith.ca dashboards/Tabler, github.com/PhilSmith26 (NatAcctsBrowser, RTSrevs).
- Mike Moffatt: threadreaderapp.com/user/MikePMoffatt, missingmiddleinitiative.ca
  (WHAM, "end of natural population growth", housing-starts-measurement posts).
- Richard Dias: LinkedIn "Canada's Lost Decade", NBC/NBF "lost decade" market-view PDF,
  The Loonie Hour; counter-sources for the per-capita caveat — StatCan "GDP per capita:
  return to trend" (36-28-0001), IRPP/Policy Options "Canada is not poorer than Alabama".
- Recession dates: C.D. Howe Institute Business Cycle Council (cdhowe.org) + Philip
  Cross, "Turning Points: Business Cycles in Canada since 1926".
- Landscape: financesofthenation.ca, doodles.mountainmath.ca (CensusMapper 2.0),
  ourworldindata.org/redesigning-our-interactive-data-visualizations, USAFacts design
  case studies, Datawrapper Academy.
