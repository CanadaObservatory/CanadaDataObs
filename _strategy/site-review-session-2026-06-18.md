# Site-review autonomous session — 2026-06-18

Branch `site-review-2026-06`, commits **not pushed**. This session worked through the
**safe, unambiguous** items of your June-17 review (`DW_CanObs-site-review-2026-06-18.docx`):
text edits, chart-legibility, title renames, targeted chart-scale fixes. Structural,
colour-system, and new-data items are **left for you** (below) — they need your call or
source validation.

---

## ✅ Done & committed this session (5 commits on the branch)

1. **Lighter line-chart loads** (`e528327`) — your #1 concern, busy peer lines. Added
   `initial_visible` so the busiest charts open with just **Canada + US + the average**
   (plus the specific comparators you named per chart): Real GDP, unemployment, employment,
   current account, average wage, disposable income, R&D → Canada/US/avg; suicide &
   tobacco-alcohol → +UK; maternal → +Germany/UK; happiness → +Australia. Removed the
   Korea (suicide) and Finland/Norway (PM2.5) auto-highlights so those open clean too.
   *(The global default stays Canada + US + AUS + DEU + avg, Sweden/UK coloured-but-hidden,
   as you set in the big-picture note.)*
2. **Prose scrub** (`e528327`) — the defensive/non-partisan boilerplate was already removed
   in an earlier pass; this removed the **specific** asides you flagged: 4 editorializing
   crime lines; the "(both sexes)" + tobacco run-on on Health; income/science cross-page
   linking sentences; spending "A recurring theme:"; the climate trend-line explanation +
   "~75-year records" aside; govt-employment intro reframed, the redundant "public sector
   defined here" box removed, immigration un-bolded, "wave of eventual retirements" dropped.
   Fixed the innovation/science **directory links** that open a file-list on `file://`.
3. **Title renames** (`e528327`) — "Average annual wage (real)"→"Average annual wage";
   "Beyond deaths: hospitalizations"→"Hospitalizations due to opioids"; "How high is
   Canada?"→"Canadian elevation"; "The changing shape of the workforce"→"Executives in the
   federal public service". *("Over Time" was already gone from tuition/revenue-spending.)*
4. **Owner-provided rewrites** (`fd69aef`) — applied your exact text for the **Economy**
   intro, the **"Where People Live"** opening paragraph, the **Housing** opening, and the
   **Religion** long-run + "scale of the shift" paragraphs; trimmed the religion city-mix
   text + removed the Brampton aside + the "2026 Census" parenthetical.
5. **Chart-scale tweaks** (`69fc559`) — childhood-vaccination: dropped the 95%-line label
   (kept the line), floored y at 50%; population growth-rate: capped y at exactly 5%;
   defence: NATO label→"NATO minimum target"; low-carbon electricity: axis now starts where
   the data does (mid-1980s) instead of ~1960.

Builder fix folded in: `stacked_area` bottom margin 80→110 (two-line source note fit).

---

## 🟡 NEEDS YOUR INPUT — nothing done, waiting on you

### Strategic (you flagged these as big efforts)
- **Colour-system report.** You want a deliberate country+province palette tied to the
  brand + viz best-practice. I can produce this as a *written report with options* before
  any implementation — say the word and I'll research it as a standalone deliverable.
- **Comparator stress-test.** "How certain are we about the 17 peers?" + topic-specific
  additions (e.g. **China/India on CO₂**). I can draft an analysis; the change itself is
  your call.
- **A consistent y-axis-navigation strategy** (the recurring one — inflation, borrowing
  costs, bond yields). Plotly's autoscale doesn't do it (it also resets x). This needs a
  site-wide mechanism decision before I build it. Options exist (per-chart sensible default
  ranges; a custom "rescale-to-view" button); I'll prototype once you pick a direction.

### Structure / reorg (sign-off needed — these move content & URLs)
- Per-section **landing pages** for the six areas?
- **Health** → split "Health of Canadians" vs "Health-Care System".
- **Economy** → pull **Trade** and **Currency** into their own sub-sections (both are
  buried); **Borrowing Costs** → its own page; move **quarterly GDP above** the international
  GDP comparison.
- **Housing** → split into >1 page + a "dashboard" landing; reorder so the most-useful
  charts lead.
- **Fire & Ice** → split into **Wildfire** and **Ice**; maybe move permafrost/sea-ice to
  Ecozones/Climate-Change. **Protected areas** → merge with Ecozones?
- **Substance Use** → make opioids a sub-section and bring Health's tobacco/alcohol peer
  chart onto this page.
- A **blog / civics-education** area under About (you marked "eventually").

### New data / charts (need a source + your go-ahead)
- The **4 confirmed adds**: tax structure & redistribution, household financial stress,
  commute, productivity decomposition.
- **Voter turnout** (federal + provincial) — the civic story you raised on Citizenship.
- **Minimum wage** over time (nominal + real).
- **Income distribution over time** (year-slider, like the age pyramid).
- **CO₂ per GDP** (emissions intensity) for the Emissions page.
- **Per-capita** government employment alongside absolute.
- **Provincial** fiscal data (spending / balance / debt).
- **Government science funding** (NSERC/SSHRC/CIHR) over time.
- **Tertiary attainment** over time + vs peers; a representative-institution tuition series.
- Global **choropleths** (military spending; population/area vs the world).
- Households-vs-individuals + nominal-vs-real **toggles** on income/wage charts.
- Rent in **actual $ by city**; vacancy **by city**; CREA dwelling-type dropdown.
- **Reanalysis** temperature/precip maps with a seasonal slider (Today's Climate).
- Map **all federal/provincial parks** (Protected Areas).

### Chart-design judgment calls (line vs bar — you were weighing these)
Population-over-time, Non-permanent residents (+ a stacked NPR breakdown), Low-income rate,
federal headcount, executives, revenue/spending. Each is a deliberate line-vs-bar choice —
tell me your preference and I'll convert.

### Data-currency checks (a batch to verify)
Several "is this really the latest?" flags: US unemployment 2025, life expectancy ending
2023, suicide/tobacco vintages, labour productivity (2024 vs others' 2025), health-capacity
(Australia 2016), food-insecurity 2024, opioids 2025, wildfire 2025. I can audit these
against the live sources and report which are genuinely stale vs. source-limited.

---

## ⏭️ Small items I can do next autonomously (no decision needed)
- **Remove the GHG 2030 target** + reframe ("recent governments have committed to
  reductions; it's been challenging") — you were clear, just needs the prose written.
- **Source-note clipping sweep finish** — the `stacked_area` builder is fixed; a few bespoke
  Environment/Geography charts still place their note deep. Mechanical margin bumps.
- **Province legend-name shortening** ("NWT & Nunavut"; two-line "Newfoundland and
  Labrador") on the population-by-province chart.
- **Dropdown caption clipping** ("Substance" / "Age group" cut off at top) — remove the
  caption or add top room (small builder change).
- **Stray "Show:" text** on the growth-components and religion-long-run charts.
- **Diversity / Citizenship / Substance-Use** remaining prose rewrites you specified
  (derivation wording; 3-group citizenship layout; "who is dying" / "poisoned supply"
  rewordings).
- **Tuition field-of-study** name shortenings (you gave the exact mappings).
- **"Social protection"** relabel on the by-function chart (needs a clearer term — suggest
  "Income support & pensions").

Tell me which of the "next autonomously" items to proceed with, and which structural/data
items to start scoping.
