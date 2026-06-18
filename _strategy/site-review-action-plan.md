# Site-review action plan (v0 review, 2026-06-18)

*Internal tracker for working through the owner's full-site review
(`DW_CanObs-site-review-2026-06-18.docx`). `_strategy/` is Quarto-ignored. Status keys:
☐ todo · ◐ in progress · ☑ done (working tree, uncommitted) · ⟳ needs owner decision ·
🔬 needs research. Line refs (`§N`) point to the extracted review.*

Locked global rules (owner, 2026-06-18): **sentence case site-wide**; **default load =
Canada + US + Australia + Germany + OECD average** (Sweden/UK coloured but unloaded).

---

## A. Global rules — fix once, apply everywhere (the leverage)

- ☑ **G3 Default comparators on peer lines** — `DEFAULT_VISIBLE_COMPARATORS = [USA, AUS, DEU]`
  in config.py; `peer_comparison_line` + `_by_age` default to it. Sweden/UK keep colour +
  legend-top rank but start `legendonly`; the 11 grey peers stay hidden. Per-chart
  overrides via `initial_visible=[...]`. *(§3, §118, §125, §137, …)*
- ☑ **G2 Remove defensive non-partisan boilerplate** (main + 10 neighbourhood pages,
  2026-06-18; one internal code comment left) — strip "this is descriptive / no
  good-or-bad reading / how high it *should* be is political / shown without a favourable
  direction / not a gap in this site / Descriptive only." Keep the principle ONLY on the
  Landing page + About. *(§64, §76, §98, §266, §290, §327, §336, §388, §418, §538)*
- ◐ **G1 Source-note standard** (bar source notes left-anchored 2026-06-18; time-series +
  map margins/overlaps remaining) — a single consistent placement that never overlaps the
  x-axis label, range slider, map bottom, legend, or clips at the right; never right-
  aligned on ranked bars (left or centre). Layout work across builders; verify per render.
  *(~30+ refs)*
- ☐ **G6 Right-edge x-padding** — small buffer past the latest data point on every time
  series (done inconsistently today). *(§199, §203, §254, §300, §313, §338)*
- ☐ **G7 "Data current to" prominence** — a clear data-currency line near each chart
  title (not only in the small source text), esp. maps + CREA. *(§134, §178, §208, §230)*
- ⟳ **G8 Title policy** — sentence case site-wide (LOCKED); shorten over-long titles; drop
  redundant "Over Time" / "by Term". *(§216, §330, §427, §439, §502, §525)*
- ☐ **G9 Map colourbar titles** — short, split across 2 lines, to reclaim map width;
  general rule. *(§190, §195, §232, §444, §470)*
- ☐ **G10 Bar-vs-line guideline** — single-series counts/rates default to bars (NPR,
  low-income, federal headcount, executives, revenue/spending). Per-chart judgement.
  *(§31, §41, §251, §297, §315, §333, §460)*
- ☐ **G11 Pages stand alone** — remove cross-page "linking" sentences. *(§225, §538)*
- ☐ **G4 Legend scrollbar** — still hijacks page scroll on dropdown/by-age charts;
  the 560→600 fix didn't fully take. Robust site-wide re-fix. *(§49, §53, §127)*
- 🔬 **G5 Y-axis scale navigation** — consistent default range + period-aware rescale
  (autoscale doesn't solve it). Affects inflation, borrowing costs, vaccination, … *(§37,
  §156, §159, §212, §377)*
- 🔬 **G12 Data-currency audit** — many "why does this end in 2023/24?" (US 2025, NAPS,
  productivity, life-expectancy, …). One pass to verify newest vintages. *(§123, §128,
  §130, §359, §372, §381, §404, §490, §504, §542)*

## B. Structure / reorganization (judgement, doable now)

- ☐ Economy: move **Quarterly GDP above** the international GDP comparison *(§121)*; split
  out **Trade** and **Currency** sub-sections *(§146, §148)*; **Borrowing Costs** its own
  page *(§214)*; business-investment cluster into a sub-section *(§140)*.
- ☐ Housing: reorder (lead with the most broadly useful charts), consider splitting +
  a dashboard-style landing; group Rent + Vacancy *(§173, §202)*.
- ☐ Health: split **Health of Canadians** vs **Health-Care System** *(§354, §380)*; fold
  Tobacco/Alcohol into Substance Use *(§386)*; reorganize Substance Use intro *(§387)*.
- ☐ Government: combine Gross/Net debt ranked bars into one dropdown *(§264)*; Defence its
  own sub-section *(§271)*.
- ☐ Environment: **Fire & Ice → two pages** *(§488)*; consider Protected ↔ Ecozones merge
  *(§458)*, Permafrost/Sea-ice placement *(§494)*.
- ⟳ Per-section landing pages? (overview + section visual identity) *(§24)*; blog/updates
  + civics-education under About *(§22, §23)*.

## C. Per-section text + chart fixes (Tier-1 sweep, after the globals)

Captured per page in the review; worked top-to-bottom. Highlights beyond the globals:
Landing (§13–20), Population (§30–58), Diversity/Religion/Citizenship/Languages
(§61–99), Crime (§100–112), Economy (§116–148), Cost of Living (§150–160), Housing
(§163–220), Income (§222–254), Government (§256–350), Health (§352–404), Well-being
(§407–413), Environment (§415–518), Education/Science (§522–552).

## D. Research + owner decision

- 🔬 **Colour system report** (countries *and* provinces) — purpose-built palette tying to
  the brand/visual identity + scientific-viz best practice. Owner wants a report before
  implementation. *(§4)* — the visual-identity colour assessment.
- 🔬 **Comparator stress-test** — are the 17 right? topic-specific additions (China/India
  for CO₂). *(§11)*
- 🔬 **Population-distribution visualization** — explore better ways than the current map;
  survey what others do. *(§423)*; reanalysis climate maps *(§468, §471)*; map parks /
  protected areas *(§461)*.
- 🔬 **Y-axis strategy** (G5) and **legend-scroll** (G4) deep fixes.

## E. New-topic backlog

**Confirmed earlier (2026-06-17):** tax structure & redistribution · household financial
stress · commute · productivity decomposition. **Added by this review:** voter turnout
(federal + provincial) *(§99)* · minimum wage real/nominal *(§224)* · income/wealth
distribution-over-time (age-pyramid style) *(§223)* · government science funding
NSERC/SSHRC/CIHR *(§547)* · tertiary attainment vs peers *(§535)* · representative-
institution tuition *(§536)* · military world map / Canada-vs-world population & area
*(§6, §112)* · CO₂ per GDP intensity *(§516)* · first-time-buyer & family-formation age
*(§9)*. All build-deferred; fold into the topic roadmap.

---

### Batch log
- **2026-06-18 #1:** action plan created; G3 default-comparators implemented; G2
  defensive-boilerplate sweep started (main section pages + source-note tags).
- **2026-06-18 #2:** G2 finished (10 neighbourhood pages, templated find-replace); G1
  started — all ranked/category bar source notes moved off the right edge to left-anchored.
- Next: G1 source-note margins/overlaps across the time-series + map builders (the bulk);
  then sentence-case (G8) sweep; then per-section text + structure.
