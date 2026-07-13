# Canada Observatory — 12-Month Timeline (July 2026 – September 2027)

*Drafted 2026-07-11 (travel chat); **refined 2026-07-12 against the repo and the
census-2026 schedule**. Integrates the site-audit fixes, the communications strategy,
the three written pieces, and the external data calendar into one sequence. The
authoritative pre-launch task list is `_strategy/launch-plan-2026-09.md` — Phase 1
below is a summary of it, not a second list.*

Dates for external releases are approximate where marked (~); pin them from
statcan.gc.ca/en/release-schedule as they publish. ⟨repo⟩ Two pins already known:
the **first 2026 Census release (population & dwelling counts) is 2027-02-10**, and
the pipeline is **daily** (14:00 UTC, after StatCan's 08:30 ET window), so release-day
site freshness is already automatic.

**Standing weekly rhythm (from launch, throughout):** Chart of the Week every Tuesday;
second post Thursday; release-day context posts as they occur. This document lists
only what sits *on top of* that rhythm.

**Recurring monthly data anchors:** LFS (~first/second Friday), CPI (~mid-month),
monthly GDP (~month-end), BoC rate decisions (8 fixed dates/year). Quarterly
population estimates: ~mid-Sept, ~mid-Dec, ~mid-Mar, ~mid-June.

---

## Phase 1 — Pre-launch (July 12 – August 31, 2026)

**See `launch-plan-2026-09.md` for the full gated checklist.** In brief:

### July
- **Site (launch gates):** PNG OG cards site-wide + validation; custom-domain cutover
  (+ Cloudflare decision); tagline unification; authorship + project email; analytics
  + Search Console; security lockdown (2FA everywhere); trust pages (FAQ, privacy,
  content licence, corrections note); neutrality/content audit incl. the empty
  household-debt narrative.
- **Content quick wins:** victimization paragraph on Crime & Safety; CMHC
  purpose-built rent caveat; Toronto-only framing sentences. (The chat's "fertility
  chart" quick-win is already built — fertility-vs-peers with the 2.1 replacement line
  is live on Population; the July task is findability, not construction.)
- **Decisions to close this month:** domain (execute), repo rename (if any),
  authorship/anonymity, tagline, content licence, launch-push date (Sept 1 vs 8).

### August
- **Site:** voice pass + hard-coded-figures triage (computed-inline pilot on headline
  pages); Trade-page build on a branch (ship-or-hold decision Aug 18); QA sweeps
  (phone + laptop chart-by-chart, Lighthouse on Housing, link checker); **feature
  freeze Aug 22**; tagged v1.0 at launch state.
- **Comms build:** finish `social_cards.py` per-aspect layouts; batch 6–8 weeks of
  literacy + local-lens posts and schedule them; pre-draft the five hard answers;
  media kit; corrections protocol.
- **Articles:** finalize The Conversation draft; verify all figures against the live
  site (first pass done 2026-07-12 — see the draft's notes); **pitch The Conversation
  ~Aug 17–21** (they commission before writing is final; 1–2 week lead typical —
  confirm current process). Finalize Crucible draft; check STAO submission process.
- **Late Aug:** soft launch to friendly network (colleagues, E4D contacts); seed
  accounts with first posts; bug-triage weekend.

---

## Phase 2 — Launch (September 2026)

**Scheduling note (owner decision):** Sept 1 is the Tuesday *before* Labour Day
(Sept 7) — a low-attention news week, and U of T term prep. Recommended: site goes
live Sept 1 (real but quiet), full public push **Sept 8–11**, the classic
back-to-attention window. Same launch, better acoustics.

- **Sept 1 (Tue):** site live at the custom domain; first Chart of the Week; quiet
  announcement to the soft-launch network.
- **Sept 8–12:** launch week per the day-by-day plan (launch thread → questions
  carousel → chart demo → open-data manifesto → local lens). The Conversation piece
  ideally runs this week. Journalist outreach emails (10–15) go out Tue–Wed.
- **Sept 14–25:** Reddit posts (spaced: r/dataisbeautiful, r/canada, city subs),
  Show HN, teaching-network notes. **Submit Crucible piece to STAO** (aim: winter
  issue / semester-2 planning season).
- **Data days to hit:** LFS (~Sept 4), CPI (~mid), BoC (~mid), quarterly population
  estimates (~Sept 16–17 — a strong week-3 content moment), GDP (~end).
- **Site:** nothing new ships this month. Launch, listen, fix.

### October
- **Comms:** first full month of standing rhythm; STAO conference is typically
  November — if pursuing a workshop/exhibitor angle, contact now (optional stretch).
- **Articles:** pitch Policy Options or The Hub with the second angle (civic-data
  essay); Nightingale pitch if energy allows.
- **Site:** begin the **2026 Census readiness project** — new dissemination
  geographies, tract-boundary changes, pipeline design for release-day ingestion (the
  big engineering block of the year; starting now means February is calm). Also start
  the post-launch build queue (Trade page if held; PISA sourcing — results expected
  ~Dec 2026).
- **Data days:** LFS, CPI, BoC (~late Oct), GDP.

### November
- **Site:** census readiness continues; post-launch queue items (French-over-time if
  not shipped; JSON-LD/data dictionary).
- **Comms:** CMHC fall rental-survey collection happens now (report lands winter) —
  tee up housing content. STAO conference (~mid-Nov) if pursued.
- **Data days:** LFS, CPI, GDP — quiet month, good for evergreen literacy content.

### December
- **~Early Dec (verify date):** **PISA 2025 results** — if the PISA page shipped, this
  is its content moment; if not, release-day prose + the peer chart fast-follow.
- **Day ~90 review (early Dec):** pillar performance, platform mix, Bluesky/Threads
  decision, cadence adjustment. First public "what's new & what's next" roadmap post.
- **Data days:** LFS, CPI, BoC (~early Dec), quarterly population estimates (~mid-Dec),
  GDP.
- **Comms:** year-in-data retrospective ("12 charts that explained Canada in 2026") —
  strong shareable format. Light posting over the holidays — floor cadence only.
- **Op-ed:** final figure verification; outlet order confirmed (release date is known:
  2027-02-10).

---

## Phase 3 — The census year begins (January – April 2027)

### January
- **Site:** census ingestion pipeline finished and dry-run against 2021 data; framing
  notes pre-written for the new sensitive topics (sexual orientation, homelessness,
  general health — all first-time census content, heavily covered later in the cycle).
- **Comms:** CMHC Rental Market Report (~late Jan/Feb) — major housing content day.
  New-year data-literacy series.
- **Op-ed:** on the shelf, hooks A–D ready; submit to outlet #1 ~Feb 1–3.

### February — **the census moment: first release 2027-02-10**
- **Op-ed submitted** ~1 week before release day (editors plan census coverage in
  advance); Version A hook updated to the actual headline on the day.
- **Site:** same-day ingestion; updated population pages and maps live release
  morning if the dry run held.
- **Social:** full release-day treatment — the long-run chart behind every headline;
  local-lens variants for 8–10 cities over the following week.
- The single highest-leverage week of the twelve months. Protect it in the teaching
  calendar now (U of T reading week is mid-Feb — check collide vs. align).

### March
- World Happiness Report (~Mar 20) — reliable annual content day (bump `WHR_URL`).
- Quarterly population estimates (~mid-Mar); BoC (~early Mar).
- **Articles:** if the op-ed ran, pitch the teacher follow-up ("teaching the 2026
  census") to OAME/OHASSTA for spring issues.

### April
- Federal budget (typically ~late Mar–Apr): fiscal pages' news moment; context charts
  ready (spending/GDP, debt service, peer comparisons).
- Earth Day (Apr 22): climate-pages feature week.
- **~Apr–May (2021 pattern):** second census release — age, sex at birth/gender,
  dwelling types. Release-day treatment again.
- **Site:** quarterly metrics review #2; French roadmap statement published if not
  already (the statement is cheap and pre-launch-able; the build is not).

---

## Phase 4 — Sustaining (May – September 2027)

### May
- Census Day anniversary (May 12) — natural open-data content moment.
- NIR emissions inventory (~spring) — environment content day (bump `GHG_RELEASE`).
- **Site:** second-priority gap additions (homelessness pairs with the census
  homelessness content coming later in the cycle).

### June
- Quarterly population estimates (~mid-June); BoC; wildfire season begins — the
  wildfire/air-quality pages become the summer's recurring content engine (sadly
  reliable).
- End-of-school-year teacher content: "datasets for next year's courses."

### July
- Annual police-reported crime statistics (~late July) — major release day for the
  crime pages, now with the victimization framing in place (re-run `fetch_crime.py`).
- **~Summer 2027 (2021 pattern):** census releases continue — families/households/
  language and income were the 2021 mid-year drops. Income release is a top-three
  content day of the year.
- One-year retrospective planning.

### August
- Quiet month historically — batch fall content; site maintenance window; draft the
  anniversary piece.

### September 2027 — one year
- **Anniversary review:** traffic, citations, CSV downloads, what got used vs. what
  didn't; publish a transparent "year one by the numbers" post (the site reporting on
  itself — perfectly on-brand).
- Remaining 2026 Census thematic releases continue into late 2027–spring 2028
  (immigration/ethnocultural, education/labour, and the first-ever sexual
  orientation, homelessness, and general-health content — each a planned content
  moment with framing notes ready).
- Decide year-two ambitions: bilingual build, multi-city local layers, education
  partnerships.

---

## Key gates and dependencies (the short list)

1. **OG cards + domain** gate the launch (July).
2. **The Conversation pitch** gates launch-week earned media (mid-Aug).
3. **Census pipeline dry-run** gates the 2027-02-10 moment (done by end of Jan).
4. **Op-ed figure verification** gates the February submission (Dec–Jan; the release
   date itself is already pinned).
5. **Framing notes for new census topics** gate safe participation in the sensitive
   releases (written Jan, used late 2027).

## Dates to verify when schedules publish
- StatCan 2026 Census release schedule beyond the first release — repattern
  Apr-onward items to actual dates.
- LFS/CPI/GDP/BoC exact dates per month (all pre-published; cross-check against
  `pipeline/release_schedule.py`'s feed rather than hand-copying).
- OECD's PISA 2025 results date (~Dec 2026).
- The Conversation and STAO current submission processes (Aug).
- CMHC Rental Market Report timing; annual crime-stats date; NIR date; U of T reading
  week 2027.
