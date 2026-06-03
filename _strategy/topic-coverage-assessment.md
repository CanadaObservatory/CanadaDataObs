# DataCan — Hot-Topic Coverage Assessment

> **Internal strategy note — not published** (`_strategy/` is Quarto-ignored). Companion
> raw research with full citations: `_strategy/topic-coverage-research-raw.md`.

**Date:** 2026-06-03 · **Provenance:** custom multi-agent research workflow (6 parallel
angles: polling, news, social/comparators, underlying data series, 2026 issues, question
framing) cross-checked against the live coverage audit (the 64-indicator registry + every
chart heading). **Status:** Tier A implementation started (quarterly-GDP recession view +
US-anchored GDP-per-capita).

---

## The core finding

There is a **mismatch between where DataCan is strongest and where Canadians are most
anxious.** DataCan's signature move — *every indicator vs. 17 OECD peers* — is ideal for
"how does Canada rank?" questions (health inputs, R&D, emissions, inequality). But the
**top-anxiety questions of 2026 — cost of living, recession, housing, jobs — are best
answered by a Canada-only long time series with the right benchmark line** (the Bank of
Canada target band, a 0%-growth line, recession shading), not a peer ranking. We mostly
*have the data*; the gap is largely **framing**, plus a few real **dataset gaps** (US trade,
healthcare wait times, absolute emissions).

**The viral-metric pattern.** The Canadian data that actually circulates is almost always
**(1) per-capita or per-worker, (2) benchmarked against the US, (3) a rate-of-change
("worst in X years"), or (4) a "more than [sympathetic thing]" comparison** (debt interest
> the Canada Health Transfer). DataCan already charts the *substance* of nearly all of it;
the value-add is leading the relevant charts with those specific cuts as the default view.

---

## Topic-by-topic: salience vs. coverage

Salience = share naming it a top issue (Abacus / Angus Reid, early–mid 2026).

| # | Topic (salience) | The question people ask | DataCan today | Verdict |
|---|---|---|---|---|
| 1 | **Cost of living** (~66%, #1) | "Is the cost of living still rising?" | CPI YoY + BoC band (on Housing page) | **MODIFY** — surface prominently; add a **food** cut (81% cite groceries) + a cumulative "prices since 2020" level |
| 2 | **Economy / recession** (~39%, #2) | *"Are we in a recession?"* | Annual real GDP growth vs peers | **ADD** — Canada **quarterly** real GDP (36‑10‑0104) with a 0% line + recession shading |
| 3 | **Trump / US tariffs / trade** (~36%, #3) | "What's the trade war doing to us?" | Only current account + defence | **ADD** — **exports-to-US share + trade balance** (12‑10‑0011). *Biggest gap vs. salience.* |
| 4 | **Falling behind the US / productivity** (top-5; #1 *viral* chart) | "Are we falling behind the US?" | GDP/capita + productivity vs OECD (US in grey) | **MODIFY** — **anchor the US as an explicit comparator**; indexed Canada-vs-US gap |
| 5 | **Healthcare** (~35%, #4) | "Is healthcare getting worse?" (wait times, family doctor) | Inputs vs peers (spend, doctors, beds, MRI, avoidable mortality) | **ADD** — wait-times % meeting benchmark + share without a family doctor (CIHI/Angus Reid; *manual, no feed*) |
| 6 | **Housing** (~32%, #5; ~60% for under-30s) | "Is housing getting less affordable?" | Deep: price-to-income, value-to-income maps, CREA, NHPI, rent, starts, vacancy, debt | **KEEP** (light: mortgage-cost-%-of-income; CMHC supply gap) |
| 7 | **Immigration / population** (~23%, #6) | *"Is immigration too high?"* | Population total/growth/components/NPR vs peers | **MODIFY** — decompose **natural vs permanent vs temporary**, annotate the levels-plan cut, target-vs-actual |
| 8 | **Deficit / debt** (prompted: 71% worried) | *"Is the budget balanced — vs past governments?"* | Balance/debt/revenue/interest vs peers + federal 1961– | **MODIFY** — **by-government/era markers** + **forward-projection segment** (Budget vs PBO) + **net debt vs the 17-peer set** (not "vs G7") |
| 9 | **Jobs / unemployment** (~15%, #7) | "Can I get a job?" | Unemployment + employment vs peers + city map | **MODIFY** — add **youth (15–24)** + Canada monthly with recession shading |
| 10 | **Crime** (~14%, #8) | "Is crime going up?" | CSI + homicide vs peers + city map | **KEEP** (light: violent vs non-violent split) |
| 11 | **Climate / emissions** (~13%) | "Are we hitting our targets?" | CO2 per-capita/indexed/consumption vs peers, energy mix, wildfire | **ADD** — absolute **GHG (Mt CO₂e) with the 2030 target line** (ECCC NIR) |
| 12 | **Size of government** (viral) | "Is government bigger than it used to be?" | Government section: employment by level, spending 1961–, by dept/type/function | **KEEP** (light: per-capita "servants per 1,000"; public-sector share over time) |
| 13 | **Taxes** (policy-salient) | "Am I paying more tax than before?" | Govt revenue %GDP vs peers | **MODIFY/ADD** (lower) — total-tax-to-GDP over time + annotate 2025–26 changes |
| 14 | **Defence** (timely inflection) | "Are we pulling our weight in NATO?" | Defence %GDP with NATO 2% line | **MODIFY** — flag **2% achieved (2025‑26)** + add **5%-by-2035** line |
| — | **Inequality/poverty** (~12%), **Happiness** (viral each March) | — | Income/Gini/poverty/LIM-AT/food insecurity; happiness + factors | **KEEP** — well covered |

---

## Priorities

**Tier A — high impact, data already in hand (mostly MODIFY):**
1. **Quarterly GDP recession view** (#2) — answers "Are we in a recession?"; very timely (technical recession Q4 2025/Q1 2026). *New StatCan series 36‑10‑0104.*
2. **Anchor the US on GDP-per-capita & productivity** (#4) — the #1 viral chart genre; data already pulled (US is in the peer CSV).
3. **Fiscal: era markers + projection segment + net debt vs the peer set** (#8) — answers "budget balanced vs former governments"; the live story is the *track* (Budget vs PBO).
4. **Population components reframe** (#6) — decompose + annotate the immigration cut.
5. **CPI prominence + food cut** (#1).

**Tier B — new datasets (more work):**
6. **Exports-to-US + trade balance** (#3) — defining 2025–26 issue, no dedicated treatment.
7. **Absolute GHG + 2030 target line** (#11).
8. **Healthcare wait times / doctor access** (#5) — the public's actual health question; manual/annual (no automated feed — known-hard).

**Strategic (ties to the mission + landscape work):**
9. A **"Questions Canadians Are Asking"** entry layer — plain-language questions routing to the
   right chart (the USAFacts/returnable-reference pattern; fixes the salience-vs-strength
   mismatch). For top-anxiety questions, **lead with Canada-only time series + the right
   benchmark line**, not a peer ranking.

---

## Editorial guardrails (keep it non-partisan)

- **Avoid the media's "vs G7" framing.** Use the full **17-OECD peer set** (the project's
  standard). The G7 omits valid comparators (the Nordics, Australia, South Korea, the
  Netherlands, Switzerland, New Zealand) and is often used misleadingly. The **US appears as a
  named member of the peer set**, anchored when a question is explicitly US-relative — *not* as
  a G7 device. See [[feedback_avoid_g7_comparisons]].
- **By-government/era markers** = neutral factual timeline shading (like recession shading), no
  "who's to blame."
- **No scorecard valence** on contested measures — extend the existing discipline (revenue,
  current account) to **immigration levels, government size, and taxes**.
- **Energy ≠ pipeline politics** — chart the mix, not the project fights.
- Treat advocacy framings (Fraser's "Tax Freedom Day"; contested headcount definitions) as
  *framings to note*, not numbers to adopt — stick to StatCan/OECD macro series.

---

## The two worked examples (from the brief)

- *"Are we in a recession?"* → quarterly real GDP with a 0% line + recession shading
  (StatCan 36‑10‑0104). We currently have only **annual** GDP growth vs peers. → **ADD** (Tier A #1).
- *"Is the budget balanced — vs former governments?"* → the federal 1961– deficit line (we have
  it) **plus neutral by-era markers and a forward-projection segment** (Budget 2025 vs PBO). →
  **MODIFY** (Tier A #3).

Full salience figures, trends, headlines, and source URLs: `topic-coverage-research-raw.md`.
