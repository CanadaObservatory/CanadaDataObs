# Launch Plan — September 1, 2026 (pre-launch stress test & master to-do)

*Written 2026-07-12. **This is the ACTIVE work plan** — it supersedes
`remaining-work-plan-2026-06-21.md` (whose open items are folded in below) and absorbs
the travel-chat review documents (July 11, from `temp_from_chat/` — refined copies now
in `_strategy/comms/` and `_strategy/site-evaluation-external-2026-07-11.md`).
`long-term-roadmap.md` remains the parking lot for blocked items.*

**Launch:** site live at the custom domain **Sept 1**; recommended public push
**Sept 8–11** (owner decision D1). **Feature freeze Aug 22.** Soft launch ~Aug 24–31.

Effort key: S = hours, M = a day-ish, L = multi-day. 🔶 = owner decision/content
needed before work can finish.

> **Progress update (2026-07-13 — shipped this commit):** G1 (og:image via
> per-dir `_metadata.yml`, render-verified), G4 (tagline → "Data and charts…"), G5
> (weekly→daily wording ×4), G6 core (household-debt narrative, "public anxiety" fix,
> investor-share soften, 2 neutral homepage questions), G3 code side ("Who We Are"
> rename; bio/email still 🔶), D2 (rent caveat), D3 (victimization paragraph, GSS-2019
> figures verified), D4 (Toronto framing ×2), G9 (freshness check + health-issue
> reporting + timeout fix), E5 (`pipeline/check_site.py` wired into the deploy job)
> — **all BUILT**. In the process the stress test found a live incident: the daily
> pipeline had been killed by its 5-minute step timeout mid-registry EVERY DAY since
> ~June 20 while reporting green — ~40 tail indicators (crime severity, homicide,
> wildfire, sea ice, happiness, the environment set) frozen on the STALE fallback.
> The workflow fix + `check_freshness.py` close it; the first post-fix scheduled run
> should be watched (G9-verify), and the standing health issue will list anything
> still stale.

---

## 0. Verification of the external review (2026-07-12 pass)

The July-11 chat review was made from the rendered site only. Verified against the
repo + live site before planning:

| Claim | Verdict | Disposition |
|---|---|---|
| Homepage/overview og:image is an SVG most platforms won't render | **CONFIRMED live** (homepage → `leaf-botanical-cells.svg`; overviews → `leaf-display-maroon.svg`). Cause: Quarto's first-body-image discovery (the hero/overview leaf) beats the site-level `image: og-card.png`. | Gate **G1** |
| Nav menus inconsistent across pages (Immigration, Temperature Maps) | **NOT reproduced** — both present on all pages checked (deploys render the full site). Almost certainly GitHub Pages CDN serving mixed generations around a deploy. | CI guard in **E5**; re-check post-domain |
| "Latest household debt: ranked" has no narrative | **CONFIRMED** ([housing/index.qmd:443](../housing/index.qmd) — heading + chart, no prose) | **G6** |
| Two taglines in circulation | **CONFIRMED** (`_quarto.yml` description/subtitle "Interactive metrics…" vs footer "Data and Charts for Informed Civic Conversations") | **G4** 🔶 |
| Anonymous authorship; GitHub Issues the only contact | **CONFIRMED** (`about/people.qmd` is a TODO scaffold) | **G3** 🔶 |
| "People" nav collision (theme vs About item) | **CONFIRMED** | **G6** |
| No site-content licence / no JSON-LD / no analytics / no 404 page / no robots.txt | **CONFIRMED** (sitemap.xml exists ✓) | **G8, G10, E2** |
| Hard-coded figures in prose will drift | **CONFIRMED, widespread** (e.g. "roughly three in ten", "roughly tripled") | **E1** |
| Palette needs a CVD check | **Mostly already done by construction** — the 17-peer data-ink palette was optimized under CIEDE2000 + deuteranopia/protanopia simulation (2026-06-22); maps are Viridis. Residual: spot-check the few categorical palettes (energy mix, ecozone legend, religion/VM group colours). | **G11** |
| Site says "weekly" refresh | **STALE — pipeline is DAILY** (14:00 UTC cron) in 4 places (about.qmd ×2, index.qmd ×2) | **G5** |
| Missing: fertility chart, family-doctor access, youth unemployment | **WRONG — all three exist** (fertility + 2.1 line on Population; regular-provider CCHS chart on Health-Care System; youth via the age-bracket dropdowns on Economy). Real issue is findability. | **D6** |
| Missing: trade page, K-12/PISA, homelessness, childcare, victimization dimension, completions, French-over-time, precipitation | **Correct gaps** (trade charts exist on the Economy page but there is no dedicated page) | **§2** |
| URL taxonomy ≠ theme taxonomy | Correct, but re-slugging pre-launch is the wrong trade | **E6** 🔶 |

Also verified for the article drafts: crime 2014→2024 Canada rates — fraud +89%,
identity theft +124%, shoplifting +66%, B&E −32%, theft-from-vehicle −43%; hate-crime
rate 3.7→11.9 (peak 12.1 in 2023); Toronto temperature record 1841–2025. All match
the drafts' claims (details in each draft's notes).

**Found by the repo-side stress test (not in the external review): the daily
pipeline was being killed by its 5-minute step timeout.** Step runtime ~5.2 min
against `timeout-minutes: 5`, masked by `continue-on-error` — daily commits touched
a variable prefix of the registry (118 sidecars one day, 57 the next) and the tail
indicators' `retrieved_at` froze at 2026-06-20. Fixed under G9 (timeout 25 min +
freshness check + standing health issue).

---

## 1. Launch gates (blocking or near-blocking)

**G1. Fix og:image site-wide (S–M).** Add an explicit `image:` to page metadata so
Quarto's first-image discovery never wins: per-directory `_metadata.yml` (12 exist;
**create the missing `wellbeing/` and `about/`**) + front matter on root pages
(`index.qmd`, `about.qmd`). v1: point everything at the existing
`visual_assets/brand/social/og-card.png`; per-theme PNG cards (rasterize the six area
marks via the qlmanage→sips recipe) are a nice upgrade, not a gate. Validate with
**real pastes** — Slack, iMessage, LinkedIn Post Inspector, an X draft — not just a
meta-tag checker. Add the CI assertion (E5) so an SVG og:image can never ship again.

**G2. Custom-domain cutover (M; do FIRST — everything downstream embeds URLs).**
canadaobservatory.ca is purchased (DNS pending). Sequence: (1) DNS per GitHub Pages
docs (apex A/AAAA + `www` CNAME); (2) repo Settings → custom domain + enforce HTTPS
(commits a CNAME file — add it to the repo so deploys don't drop it); (3) flip
`site-url` in `_quarto.yml`; (4) **update the absolute URLs in
`_includes/brand-head.html`** (they hardcode the github.io prod URL — a known
gotcha). The complete inventory (audited 2026-07-13): `_quarto.yml:22` site-url +
brand-head.html's 4 links (font preload, SVG favicon, apple-touch-icon, icon-192);
optional cosmetic: the `+https://canadaobservatory.github.io` User-Agent strings in
`build_naps_cities.py` / `fetch_air_quality.py` / `fetch_climate.py`;
(5) re-verify og:image absolute URLs, sitemap, canonical; (6) Search Console/Bing
properties for the new domain, submit sitemap; (7) update README + social bios.
GitHub 301-redirects github.io→custom-domain automatically, so old links survive.
🔶 **D4 repo rename** (`CanadaDataObs` → e.g. `canada-observatory`): GitHub redirects
repo + raw URLs; with the custom domain the Pages path change is invisible. If
renaming ever, do it in the same window as the cutover, before external citations
accumulate. Recommend: yes, same day.
🔶 **D7 Cloudflare free tier in front** (caching/bandwidth headroom against the
~100 GB/month Pages soft limit — the pages are heavy). Recommend: yes at cutover
(SSL "Full", respect underscored asset paths). If deferred, revisit before any
Reddit/HN push.

**G3. Authorship, contact, and the People page (S code + 🔶 owner content).**
(1) Owner writes the who-we-are bio (name, measurement-science background,
independence + funding disclosure — the single biggest trust gap per the review);
(2) project email alias (e.g. `hello@canadaobservatory.ca` via the registrar's/
Cloudflare's free email routing) — needed for the People page, press, article
bylines, and **account recovery**; (3) rename the About menu item "People" → "Who We
Are" (collision with the People theme); (4) keep GitHub Issues as the corrections
channel alongside email. If any pseudonymity is retained, state it explicitly —
silence reads as oversight.

**G4. One tagline (S 🔶 D2).** Pick between "Interactive metrics for informed civic
conversations" (description/subtitle) and "Data and Charts for Informed Civic
Conversations" (footer). Recommend the footer version (plainer; "metrics" is colder) —
then apply to `_quarto.yml` description, index subtitle, og description, and social
bios.

**G5. Cadence-claim fix (S).** Four spots say "weekly"
([about.qmd:19](../about.qmd), about.qmd:44, [index.qmd:16](../index.qmd),
index.qmd:134) but the pipeline runs daily. Wording that ages well: "checked daily;
most series refresh automatically as their sources release."

**G6. Content & neutrality audit (M).** One pass, three lenses:
- **Placeholders:** write the missing "Latest household debt: ranked" narrative;
  sweep for any heading followed by no prose (add the detector to E5).
- **Neutrality:** fix "the categories **driving public anxiety**"
  ([wellbeing/crime-safety.qmd:163](../wellbeing/crime-safety.qmd)) → "most prominent
  in public discussion"; review "at the centre of recent debate" (housing:291 —
  borderline, softer optional); audit for other uncited public-psychology claims.
  Critics will hunt exactly these sentences; the neutrality claim is load-bearing.
- **Voice:** the em-dash / "not X, but Y" density pass; move "**Use the dropdown**"
  instructions toward a consistent hint-line convention (bold currently does triple
  duty: findings, terms, UI).
- **Homepage questions:** add 1–2 neutral/curiosity-valence questions so the list
  isn't all anxieties — "How long do Canadians live, and how is that changing?",
  "How many children are Canadians having?" (also fixes fertility findability, D6).
  🔶 D9 wording.

**G7. Security lockdown (S; do this week).** Unique passwords + authenticator-app
2FA on GitHub, domain registrar, email, and all social accounts; recovery = the
project alias. GitHub is the site, the data, AND the deploy pipeline — an account
takeover during launch week is the true worst case and costs nothing to prevent.

**G8. Analytics + discoverability (S–M 🔶 D6 provider).** Privacy-respecting
analytics on every page (GoatCounter free / Plausible ~€9 mo — either fits the
ethos; recommend starting GoatCounter, swap later if limits chafe) + Google Search
Console + Bing Webmaster with sitemap submitted. Document the UTM scheme
(`utm_source=x|instagram|facebook, utm_medium=social, utm_campaign=cotw|launch|release`).
Launch week is the best data the site will ever get; don't lose it. Disclose the
counter in the privacy note (G10).

**G9. Pipeline ops hardening (S–M).** (1) Failure notification: the daily workflow
currently swallows failures (`continue-on-error` + 5-minute timeout) — add a final
health-check step (did every expected CSV update? does any STALE streak exceed N
weeks?) that opens/updates a GitHub issue on failure; (2) measure the pipeline's
actual runtime and raise `timeout-minutes` with margin (silent mid-run kills =
silent staleness); (3) tag **v1.0.0** at launch state (site + data) for clean
rollback; document the rollback (revert → push → redeploy).

**G10. Trust pages (M 🔶 D5 licence).**
- **FAQ**: who runs this / who funds it / why 17 peers (not G7) / why is Toronto the
  local-detail city / why English-only for now (bilingual roadmap statement) / why
  isn't topic X here (link the public roadmap) / how corrections work / how
  Indigenous data is approached (boundaries mapped from official sources; broader
  well-being data deliberately deferred pending engagement with OCAP principles —
  the acknowledgement the review asked for).
- **Privacy note**: no ads, no tracking beyond privacy-respecting page counts.
- **Content licence** 🔶: recommend footer + About line — "Text and charts CC BY 4.0;
  underlying data per source licences (see Data Sources); CREA series excluded
  (charts displayed with permission, not redistributable)."
- **Corrections note/log**: the visible promise + the log location (can live in the
  FAQ until the first correction exists).
- **Public roadmap / known-issues page**: converts the coverage-gaps list into
  visible intent ("planned: trade, PISA when 2025 results land, homelessness,
  French").

**G11. QA sweep (M–L; two rounds — Aug 4 wk and post-freeze Aug 24 wk).**
Chart-by-chart phone + laptop pass (the one thing the external reviewer explicitly
could not do): hover/dropdown/slider behaviour on mobile, legend fit, source-note
clipping, dark-basemap maps, the menu group-headers rendering, no dead menu bullets.
Lighthouse on the heaviest pages (Housing ~2-dozen charts — measure before deciding
any split; the split/lazy-load decision is post-launch D11). Link checker over
`_site` (internal anchors + every Download-data link). CVD spot-check of the
remaining categorical palettes (energy mix, ecozones, religion/VM lines). **Re-verify
the navbar-brand no-clip rule at 992px** (mandatory after any nav/brand change —
G3/G4 touch the navbar). Confirm GitHub org avatar + repo social-preview images are
uploaded (manual settings, no API).

**G12. File the CREA permission (S).** The letter/email goes in `internal/`
(gitignored) with a pointer note in CLAUDE.md — it's the one licensing arrangement
someone might challenge.

**G13. Comms pre-launch package (M–L; detail in `comms/social-strategy.md`).**
Handles secured (try @canadaobservatory on X; register Bluesky/Threads/Facebook;
uniform bios) · `social_cards.py` per-aspect layouts finished (portrait/16:9/OG;
local qlmanage batching is fine for launch — CI rasterizer is post-launch) · 6–8
weeks of Pillar-3/4 content batched & scheduled · five hard answers pre-drafted
(who funds you / left or right / crime data ignores unreported crime / why map
ethnicity by neighbourhood / why trust an anonymous site — the last dissolves if G3
lands) · media kit (boilerplate ¶, logo files, 5 exemplary chart PNGs, contact) ·
corrections protocol written · journalist list (10–15, beat-matched) with notes
drafted.

**G14. The Conversation pitch (S; ~Aug 17–21).** Gates launch-week earned media.
Draft is ready (`comms/article-conversation.md`, figures verified 2026-07-12);
re-verify numbers the week of submission; needs G2 (domain) + G3 (disclosure/email).

---

## 2. Data & plotting work

### 2a. Pre-launch content fixes (small, ship with the audit)
- **D1. Household-debt narrative** — covered in G6. (S)
- **D2. CMHC rent caveat** (Housing): the $-rent chart covers **purpose-built rental
  only** — the condo/secondary market where much recent pain concentrates is not in
  the survey. One sentence. (S)
- **D3. Victimization dimension** (Crime & Safety): the page is entirely
  police-reported — the first thing a knowledgeable critic will raise. Minimum: a
  short sourced paragraph on the GSS Survey on Victimization (most crime never
  reported; reporting rates differ by offence and move over time — the same honesty
  pattern as the hate-crime caveat). Stretch: one chart of %-reported-to-police by
  offence type (GSS 2019). **Check first whether the 2024-cycle victimization
  results have been released** (the survey runs ~5-yearly: 2014, 2019, 2024). (S
  prose / M chart)
- **D4. Toronto-only framing** (crime neighbourhoods map, bike-theft seasonality,
  warming spirals): one sentence each — "Toronto is shown because its police
  service/its 1841 record is the most complete openly published; other cities will
  be added as their portals allow." Converts a perceived bias into the open-data
  thesis. (S)
- **D5. Homepage question router adds** — the neutral-valence questions from G6,
  each linking an existing chart. (S)
- **D6. Findability fixes for "already exists" items**: fertility (add to question
  router), youth unemployment (one prose sentence pointing at the age dropdown +
  possibly a direct anchor), family-doctor access (already prominent on
  Health-Care System — no action). (S)

### 2b. Pre-launch build candidate (branch now, ship-or-hold Aug 18)
- **D7. Trade & the Canada–US relationship page (L).** The single most-requested
  missing topic in a tariff-dominated news cycle; the only chats-identified gap
  worth pre-launch build risk. Seed with the existing US/EU/China export-share +
  balance charts (12-10-0011-01, currently on the Economy page — leave a stub or
  cross-link there); add: trade % of GDP over time (exports+imports, OECD/WB),
  goods vs services split, top partner shares over time, and **interprovincial
  trade** (StatCan interprovincial trade flows — sourcing pass for the table id) —
  the "internal trade barriers" civic angle. Mind the existing gotcha memory: UK
  ranks are a gold-to-London artifact; EU members double-count inside the EU
  aggregate. Descriptive framing; no tariff-policy commentary; **no hardcoded
  tariff timelines** (news-dated annotations only if sourced to an official
  document). If not solid by Aug 18, it becomes the first post-launch ship — the
  launch does not depend on it.

### 2c. Post-launch build queue (priority order; sourcing status noted)
1. **PISA / K-12 outcomes** — build against PISA 2022 in Oct–Nov so the page is
   live **before the PISA 2025 results (~Dec 2026, verify date)**; probe the OECD
   Data Explorer for a PISA SDMX flow first (the old blocker was no clean feed —
   the Explorer migration may have changed this); scores are immutable historical
   constants, so even a file-based fetcher fits the rules. Math/reading/science
   mean scores, Canada vs peers + over time.
2. **French-at-home over time** (Languages page) — national + Quebec shares from
   decennial/quinquennial censuses, `history_lines`-style one-time builder (the
   religion long-run is the template; historical-splice rule applies). One of the
   country's oldest civic debates; cheap relative to salience. (M) *Could pull
   forward to pre-launch if Trade holds.*
3. **Housing completions** alongside starts (CMHC starts/under-construction/
   completions table — verify 34-10-0126; starts can stall, completions tell the
   supply story honestly). (S–M)
4. **Childcare fees** — StatCan now surveys median fees by city ($10/day rollout
   context); sourcing pass for the table, then a ranked bar + over-time. (M)
5. **Democracy mini-set** (Government or Citizenship): federal election results
   over time (Elections Canada open data), trust-in-institutions (StatCan Social
   Survey series); provincial turnout stays parked (no authoritative source — see
   long-term-roadmap.md). (M–L)
6. **Homelessness** — Infrastructure Canada point-in-time counts + shelter
   capacity; imperfect but citable; needs careful descriptive framing and pairs
   with the census homelessness content later in the cycle. (L, sourcing pass
   first)
7. **Precipitation & extremes** (Climate Change): AHCCD adjusted precipitation via
   the same GeoMet path as temperature; extreme-heat days can ride the ERA5
   daily-max work already scripted (`pull_era5_dailymax.py`). (M–L)
8. **Incarceration rate** — StatCan 35-10-0154 for Canada; peer comparison is the
   hard part (no OECD series; World Prison Brief is third-party → off-limits), so
   likely Canada-only with a note. (M)
9. **Mortgage renewal wall** — investigate whether BoC publishes a refreshable
   series (FSR chart data); if it's one-off analysis, **decline** under the
   no-hardcoded-projections rule and cover in prose with a citation. (S to
   investigate)
10. **AIC per-capita** (Living Standards headline) — already-deferred sourcing pass
    (the HCPC flow lacks it; needs AIC-total ÷ population from the non-HCPC
    table). Consider a research agent. (M sourcing)

**Also in the post-launch engineering queue:** the parked housing-dashboard
redesign 🔶, mobile Phase 2, bilingual `/fr` decision (the *statement* ships at
launch in the FAQ; the build is a year-two candidate), multi-city local crime
layers, DA-tier languages/citizenship maps.

### 2d. Chats' gap list — already-covered corrections (for the record)
Fertility ✓ (Population, WB TFR + 2.1 line) · family-doctor access ✓ (Health-Care
System, CCHS 86% 2022) · youth unemployment ✓ (age-bracket dropdowns) · tertiary
attainment ✓ (Education, 37-10-0130 with built-in OECD average) · voter turnout ✓
(Citizenship, 1867– + by age). The lesson is **findability**, not coverage — hence
D5/D6 and the question-router adds.

---

## 3. Prose–pipeline consistency & site engineering

- **E1. Computed inline figures (M–L; the one structural item worth real
  engineering time).** The prose is rich with numbers ("9.3×", "roughly tripled",
  "+3.1 °C") while data refreshes daily — every one is a future text-vs-chart
  inconsistency on a site whose value proposition is reliability. Build a small
  helper (e.g. `pipeline/prose.py`: `latest(csv, col, fmt)`, `change_since(csv,
  col, year)`, `ratio_of(...)`) and use Quarto inline `` `{python}` `` for the
  **headline figures on the highest-traffic pages first** (Housing, Crime, Climate,
  Population). Everything not converted gets graceful-aging phrasing ("has climbed
  from roughly 5.7× in 2005 to above 9× in recent years"). 🔶 D10: whether to add a
  per-page "narrative last reviewed" date. Policy for new prose: computed or
  graceful, never a bare literal that a chart will contradict.
- **E2. schema.org `Dataset` JSON-LD (M).** Auto-generate per-page JSON-LD from the
  existing metadata sidecars (name, description, licence, temporalCoverage,
  distribution → the CSV URL) — Google Dataset Search indexes exactly this, and a
  site of cleaned, licensed, regularly updated Canadian datasets is its target
  content. The sidecars already hold every required field. Pre-launch if time
  permits; else first post-launch engineering.
- **E3. Data dictionary (M, post-launch).** Auto-generated per-section download
  docs from the same sidecars (columns, units, geography codes, vintage, source
  table). The CSVs are the product for the student/journalist audience.
- **E4. Accessibility pass (M).** Formalize the one-sentence-takeaway-per-chart
  rule (mostly true already — audit in G6); aria-labels/captions on chart
  containers; CSV link as the machine-readable fallback; alt text discipline
  extends to social images (G13).
- **E5. CI guards (S–M).** (1) og:image-is-PNG assertion; (2) nav-consistency diff
  across rendered HTML; (3) heading-with-no-prose placeholder detector; (4) link
  checker (lychee) on a weekly schedule, not per-deploy. Each is a small script in
  the deploy workflow.
- **E6. URL/aliases policy (S 🔶 D8).** Do NOT re-slug before launch (the taxonomy
  mismatch is real but invisible to readers; stable URLs are the product feature,
  and the custom domain hides the repo name). Adopt the policy now: any future page
  move ships with Quarto `aliases:`; document the section↔directory mapping in
  CLAUDE.md.
- **E7. Doc hygiene (S, rolling).** CLAUDE.md has drifted from the repo (daily-not-
  weekly cron; missing: overview pages, Provincial Finances, Indigenous Lands,
  Temperature Maps split, parks, IMDB earnings, asylum outcomes, social_cards/
  release_schedule/static-charts modules). Update after the launch-gate changes
  land so it describes the launched site.

---

## 4. Communications & strategy (implemented docs)

The full comms system now lives in `_strategy/comms/`:
- **`social-strategy.md`** — platforms, five pillars, voice, launch phases,
  neutrality playbook, measurement. Key repo corrections baked in: the pipeline is
  already daily with `workflow_dispatch` as the release-morning button;
  `release_schedule.py` should generate the release-day calendar;
  `social_cards.py`/`build_static_charts.py` are the card template (finish
  per-aspect layouts; CI rasterization post-launch).
- **`launch-timeline.md`** — the 12-month sequence (Sept 2026 launch → census
  moment **2027-02-10** → one-year review), with the standing weekly rhythm and
  data-day anchors.
- **`article-conversation.md`** (pitch ~Aug 17–21; figures verified 2026-07-12),
  **`article-crucible.md`** (submit ~mid-Sept; the stale "planned education
  section" line fixed), **`article-oped-census.md`** (hold for 2027-02-10;
  submission ~Feb 1–3).

Comms deliverables tracked as launch gates: G13 (package) and G14 (pitch).
Measurement from day one: citations/pickups (the true KPI), UTM'd sessions, CSV
downloads/repo traffic, saves-over-likes; 90-day review early Dec.

---

## 5. Ops, security & resilience (mostly folded into gates)

G7 (2FA everywhere) · G9 (alerts, timeout, v1.0.0 tag, rollback) · G2/D7
(Cloudflare) · G10 (corrections protocol) · plus: keep launch week's evenings
time-boxed (20-minute engagement windows), and hold the floor cadence rather than
sprinting. GitHub Pages bandwidth (~100 GB/mo soft) is the scaling constraint a
front-page Reddit/HN hit could brush — Cloudflare is the cheap insurance.

---

## 6. Owner decisions needed (consolidated)

| # | Decision | Recommendation |
|---|---|---|
| D1 | Launch acoustics: everything Sept 1, or live Sept 1 + public push Sept 8–11 (post-Labour-Day)? | Live 1st, push 8th–11th |
| D2 | Tagline | "Data and Charts for Informed Civic Conversations" |
| D3 | Authorship depth on Who We Are (bio content) | Name + measurement-science background + independence/funding disclosure |
| D4 | Repo rename at domain cutover? | Yes — `canada-observatory`, same day as G2 |
| D5 | Site-content licence | CC BY 4.0 (text + charts), data per source, CREA excluded |
| D6 | Analytics provider | GoatCounter (free) to start |
| D7 | Cloudflare in front of the domain | Yes at cutover |
| D8 | Re-slug URLs pre-launch? | No — aliases-by-design policy instead (E6) |
| D9 | Homepage neutral-question wording | Life expectancy + fertility candidates in G6 |
| D10 | "Narrative last reviewed" footer date | Optional; decide with E1 pilot |
| D11 | Housing page split/lazy-load | Measure first (G11); post-launch decision |
| D12 | Try to obtain @canadaobservatory on X? | Attempt once; else domain-forward bios |

---

## 7. Calendar — now to launch

| Week of | Site / data | Comms / admin |
|---|---|---|
| **Jul 13** | G1 og:image fix + validation; G5 cadence fix; G6 audit begun | **Decisions week** (D1–D9); G7 security lockdown; G2 domain cutover started; email alias |
| **Jul 20** | G2 finished (site-url, brand-head, Search Console); G6 audit done (household debt, neutrality, questions); G3 People page wiring | 🔶 owner bio drafted; G8 analytics live; handles secured |
| **Jul 27** | G9 ops hardening; E5 CI guards; D2–D6 content fixes; **D7 Trade branch opened** | G10 trust pages drafted (FAQ/privacy/licence/roadmap); G12 CREA filed |
| **Aug 3** | Trade build; French-over-time if capacity; **G11 QA round 1** (phone/laptop, Lighthouse, links, CVD) | G13: social_cards layouts; media kit; hard answers; batch content started |
| **Aug 10** | QA fixes; E1 computed-figures pilot on Housing/Crime | Content batch finished & scheduled; journalist list; **G14 Conversation final verify** |
| **Aug 17** | **Aug 18: Trade ship-or-hold**; remaining polish | **Pitch The Conversation (Aug 17–21)** |
| **Aug 24** | **Feature freeze Aug 22**; G11 QA round 2 (regression: navbar 992px, autoscale, legends); tag v1.0.0-rc | **Soft launch** to friendly network; seed accounts; bug-triage weekend |
| **Aug 31** | Fixes only; tag **v1.0.0** | **Sept 1: live at canadaobservatory.ca**, first Chart of the Week, quiet announce |
| **Sep 7** | Nothing ships. Launch, listen, fix. | **Sept 8–11 public push**; journalist emails; Conversation runs |
| **Sep 14+** | — | Reddit (spaced), Show HN, teaching networks; **Crucible to STAO**; data days (pop estimates ~Sept 16) |

Post-launch: per `comms/launch-timeline.md` — census-readiness engineering starts
October; PISA moment ~December; census moment **2027-02-10**.

---

## 8. Deliberately NOT before launch

Re-slugging URLs · housing-dashboard redesign · bilingual build (statement only) ·
PISA/homelessness/childcare/democracy builds (queued) · Indigenous data beyond
boundaries (FAQ statement of approach instead — deliberate, OCAP-aware) · CI card
rasterization · data dictionary + JSON-LD if time runs short (first post-launch) ·
occupation-series revival · anything that reopens the navbar/brand layout in the
freeze window.
