# External site evaluation — 2026-07-11 (travel chat, rendered site only)

*Archived verbatim from `temp_from_chat/canada-observatory-evaluation.md`. The reviewer*
*saw only the published GitHub Pages content (no repo access, no chart interactivity).*
*Every actionable claim was **verified against the repo and live site on 2026-07-12** —*
*the claim-by-claim verification table and the resulting task list live in*
*`_strategy/launch-plan-2026-09.md` (§0–§1). Notable corrections: the og:image-SVG bug*
*is REAL (confirmed live); the nav inconsistency did NOT reproduce (likely CDN cache at*
*review time); fertility, family-doctor access, and youth unemployment already exist on*
*the site; the peer palette is already CVD-optimized by construction.*

---


**Review date:** July 11, 2026
**Site reviewed:** https://canadaobservatory.github.io/CanadaDataObs/
**Pages examined in depth:** Home, About (Mission & Method), People & Society overview, Crime & Safety, Climate Change, Housing, Data Sources, Open Data: The One Cause, People (About)

**Scope note.** This review is based on the rendered page content and markup. Interactive Plotly charts execute client-side and could not be visually inspected in this pass, so chart-level critique (axis choices, colour rendering, hover design, mobile chart behaviour) is inferred from the surrounding text and stated conventions rather than observed directly. A follow-up visual pass on a phone and a laptop, chart by chart, should be treated as a separate pre-launch task.

---

## 1. Overall assessment

This is a genuinely strong project — unusually so for an independent effort. The mission is crisp, the methodological transparency is at a professional statistical-agency level, and the editorial voice is literate and careful. The "no advocacy, with one deliberate exception" framing is the best single idea on the site: it converts a potential credibility weakness (why should readers trust a neutral-claiming site?) into a distinctive, memorable position, and the Open Data page argues it well.

Three things stand out as best-in-class for this genre:

The **methodological honesty embedded in the narrative** is exemplary. The Climate Change page's handling of homogenized vs. raw temperature series (kept separate, not spliced, with the reason stated), the flagging of the 2011 voluntary-survey census cycle as a lower-quality point, the hate-crime undercounting caveat, the warning that Toronto Police categories are not comparable to StatCan's UCR, and the "read the levels as indicative" note on the DHEA wealth estimates — these are the habits that separate a trustworthy reference from a chart farm. Keep every one of them.

The **question-led homepage** ("Is Canada becoming less affordable?") is exactly the right entry pattern for a civic audience. People arrive with questions, not with a taxonomy.

The **per-page Download data sections**, with StatCan table numbers and licences attached to each CSV, deliver on the open-data promise concretely rather than rhetorically.

The recommendations below are therefore mostly about consistency, trust signalling, and pre-launch hardening rather than direction change. They are grouped by theme, with a prioritized summary at the end.

---

## 2. Data presentation and methodology

**Hard-coded figures in prose will drift from auto-updating charts.** This is the most important structural risk on the site. The narrative is rich with specific numbers — "9.3× in 2024," "roughly tripled since 2014," "about +3.1 °C above the reference period," "roughly three in ten purchases" — while the data pipeline refreshes weekly. Every one of these sentences is a future inconsistency between text and chart, and on a site whose entire value proposition is reliability, a stale number in prose next to a fresh chart is more damaging than no number at all. Three mitigations, in order of preference: (a) compute inline values at render time from the same CSVs the charts use (Quarto supports inline Python expressions, so `{python} f"{ratio:.1f}×"` can replace the literal); (b) where computation is impractical, phrase claims in ways that age gracefully ("has climbed from roughly 5.7× in 2005 to above 9× in recent years"); (c) institute a scheduled text audit — an annual pass, plus a "narrative last reviewed" date in the page footer so readers can see the text's own freshness independently of the data's. Option (a) is worth doing for at least the headline figures on high-traffic pages.

**The site's stated chart conventions are correct — verify they hold everywhere.** Canada in red, peers in grey, a small set of named comparators in colour, benchmarks shown where recognized ones exist, index base years stated, and — notably good — explicit warnings that rebased indices show change rather than levels (the Housing page states this twice, correctly). Two things to confirm in the visual pass: that the palette is colour-vision-deficiency safe (red-on-grey is generally fine; red/blue anomaly bars are fine; check any categorical palettes on the diversity, religion, and energy-mix charts against a CVD simulator), and that "colour indicates direction only" charts don't accidentally imply magnitude.

**One section appears unfinished.** "Latest household debt: ranked" on the Housing page contains only the line "Data current to 2025." — no narrative, unlike every sibling section. Either it's a placeholder or a build artifact; either way it reads as a gap and should be caught by the content audit.

**Accessibility of interactive charts needs a deliberate decision.** Plotly output is largely opaque to screen readers, and a civic-data site should be usable by everyone. Full remediation is impractical, but a reasonable standard is achievable: a one-sentence takeaway in the prose adjacent to every chart (mostly already present — formalize it as a rule), meaningful `aria-label`s or figure captions on chart containers, and the CSV link as the machine-readable fallback. The decorative banner SVGs correctly carry empty alt text; the leaf marks carry good descriptive alt text — that discipline should extend to charts.

**Per-chart provenance is inconsistent in one respect.** Some sections carry a visible "Source: … | Data as of: …" line (clearance rates, hate crime); the About page promises every chart shows the date of its most recent data. Make the source-and-vintage line a uniform, templated element on every chart rather than something that appears in some sections' prose and not others — it's a trust feature, and uniformity is what makes it legible.

**Consider a data dictionary.** The CSVs are the product for the student/journalist audience. A short README or per-file dictionary (column meanings, units, geography codes, vintage, source table) — even auto-generated — would meaningfully raise their usability and is cheap relative to the pipeline work already done.

---

## 3. Narrative and voice

The voice is a real asset: precise, warm, and confident without being breezy. The planned voice pass should focus on three specific patterns rather than tone.

**Em-dash and contrast-construction density.** The "— not X, but Y —" construction and mid-sentence em-dash asides appear multiple times per paragraph on most pages. Individually each is fine; cumulatively they create a recognizable tic and lengthen sentences. A mechanical pass — count em-dashes per paragraph, cap at one where possible — will tighten the prose more than any stylistic rewrite.

**Bolding as instruction.** Interaction instructions ("**Use the dropdown** to switch…") are helpful but currently live as bolded prose fragments scattered through paragraphs. Consider a consistent visual convention — a small styled hint line under each chart — so instructions stop competing with substantive emphasis. Right now bold does triple duty (key findings, defined terms, UI instructions), which dilutes all three.

**Audit interpretive claims against the neutrality pledge.** The site promises "descriptive, not prescriptive," and mostly delivers, but a few lines cross from describing the data into characterizing public psychology or debate without citation: "the categories driving public anxiety" (Crime & Safety) asserts a causal claim about anxiety that no chart on the page supports; "a shift at the centre of recent debate about housing demand" is safer but still editorial. These are small, but the neutrality claim is load-bearing — critics will hunt for exactly these sentences. The fix is usually a lighter phrase: "the categories most prominent in public discussion" is defensible; "driving public anxiety" is not. A one-time audit with this specific lens is worth an afternoon.

**The homepage question list skews toward anxieties.** Affordability, crime, warming, government size — all legitimate, all currently salient, and all framed around worry. One or two curiosity-driven or neutral-valence questions ("How long do Canadians live, and how is that changing?", "What does Canada's land actually look like?") would broaden the invitation and subtly reinforce that the site isn't a grievance dashboard.

---

## 4. Subject organization and information architecture

**The URL taxonomy no longer matches the theme taxonomy, and this should be reconciled before launch, not after.** The six public themes are clean, but the directory structure underneath shows the project's growth history: People & Society lives at `/population/`, but Crime & Safety lives at `/wellbeing/`; Government splits across `/fiscal/` and `/government/`; Environment spans `/geography/` and `/environment/`; Housing and Income are top-level directories while their siblings nest under `/economics/`. Readers won't consciously notice, but it has three real costs: shared and cited URLs communicate the wrong section; the same page (Crime & Safety) appears under People in the nav while its URL says wellbeing; and any future restructuring will break the "stable link you can bookmark" promise. Since stable URLs are an explicit product feature, the window to rationalize slugs closes at launch. If a full re-slugging feels too disruptive, at minimum add redirects-by-design (Quarto `aliases`) now so future moves are non-breaking, and document the mapping.

**Navigation menus are inconsistent across pages.** The People dropdown on the homepage includes Immigration; the same dropdown on the People & Society overview page omits it. Temperature Maps appears in some pages' Environment menu and not others'. This is almost certainly stale incremental rendering — pages built at different times carrying different nav snapshots — and the fix is a full-site rebuild plus a CI check (a simple script diffing the nav block across all rendered HTML files would catch this permanently). Related: the dropdown group labels ("The economy," "Cost of living & affordability," "The Land," "Climate & Atmosphere") render in the markup as bare, unlinked list items with stray separators around them; confirm in the browser that these display as intentional group headers rather than dead menu entries, and that no dangling empty bullet renders in the Economy menu (one appears in the homepage markup).

**"People" means two different things in the nav.** The top-level theme (demographics) and the About sub-item (the team) share a name. Rename the About item — "Who We Are" or "About the Project" — to remove the collision.

**Section overview pages omit some children.** The People & Society overview page cards don't include Immigration, though it exists as a page. Overview pages should be generated from, or checked against, the same source of truth as the nav.

**Long pages: the structure is right, keep an eye on weight.** Housing runs to roughly two dozen sections. The organization within it is actually excellent — the "Where Canada stands" scorecard up front is the correct pattern, and heavy neighbourhood maps have already been offloaded to dedicated pages. The residual risk is load time and scroll fatigue on mobile with ~20 Plotly figures on one page. Two options if the visual pass confirms a problem: split Housing into Prices / Renting / Debt (with the scorecard on a landing stub), or lazy-load charts below the fold. Measure before deciding.

---

## 5. Civic relevance and coverage

The six themes cover the large majority of what Canadians actually argue about, and the "Start with these questions" list maps well onto 2026's live debates. Gaps worth considering, roughly in order of civic salience:

**Democracy and elections.** Voter turnout apparently exists inside Citizenship, but democratic participation, electoral results over time, and trust-in-institutions measures (StatCan's Social Survey has trust modules) are central civic topics with authoritative sources. This could be a modest page rather than a theme.

**Indigenous data beyond boundaries.** Indigenous Lands maps legal boundaries, which is valuable, but well-being, language vitality, and demographic data exist in the census and dedicated StatCan programs. This area needs genuine care — engagement with OCAP principles and the distinction between data *about* and data *governed by* Indigenous communities — so it may be better done deliberately post-launch than quickly before. But a short statement acknowledging the choice and the intent would be better than silence.

**Bilingualism.** For a project whose mission is *Canadian* civic conversation, an English-only site is a real limitation and, in some rooms, a credibility issue. Full translation is a large lift; a stated roadmap ("French interface planned; chart labels are being designed for translation") costs little and signals seriousness. If Quarto's multilingual support is used eventually, designing chart-label pipelines for it now is much cheaper than retrofitting.

**Local depth is currently Toronto-only.** Neighbourhood crime, seasonality, and the warming-spiral comparison all anchor on Toronto. The reason (data availability, your own location) is legitimate and partially stated, but a Canada-branded site should name it explicitly and sketch the expansion path — Vancouver, Montréal, Calgary, and Ottawa all run open-data portals with comparable crime layers. A single sentence per Toronto-specific section ("Toronto is shown because its police service publishes the most complete open neighbourhood data; other cities will be added as their portals allow") converts a perceived bias into a demonstration of the open-data thesis.

---

## 6. Branding and identity

**The identity system is well conceived — the leaf-with-six-cells mark mapping to six theme colours, per-theme solid leaves on overview pages, banner motifs, a consistent `#17324D` theme colour, and prepared OG cards.** That's more brand infrastructure than most independent data sites ever build. Two concrete problems and two consolidation issues:

**The homepage social-card image is an SVG, and most platforms won't render it.** The homepage and the theme overview pages point `og:image` / `twitter:image` at `.svg` files (`leaf-botanical-cells.svg`, `leaf-display-maroon.svg`). X, Slack, iMessage, LinkedIn, and most link-preview services do not rasterize SVG; those shares will show a blank or fallback card. The About and topic pages already use a proper 2400×1260 `og-card.png` — extend that pattern site-wide, ideally with per-theme PNG cards (the assets clearly exist as SVG sources). Given that social sharing is part of the launch plan, this is a high-priority, low-effort fix. Validate with the X Card Validator and a Slack paste before launch.

**The name is fragmented across four surfaces.** Canada Observatory (brand), CanObs (shorthand), `CanadaDataObs` (repo and URL path), `@canobservatory` (X) vs `@canadaobservatory` (Instagram). None of these is individually wrong, but together they blur searchability and make the project look less finished than it is. The two fixes with the best leverage: register a custom domain (canadaobservatory.ca is the obvious candidate) and point GitHub Pages at it — this simultaneously fixes the repo-name-in-URL problem, shortens every shared link, and is dramatically easier before external links accumulate; and consider renaming the repo to `canada-observatory` or similar (GitHub redirects old repo URLs automatically, so this is low-risk — but do it before the CSV download links are widely cited, since raw-content URLs embed the repo name).

**Two taglines are in circulation.** The masthead/OG description says "Interactive metrics for informed civic conversations"; the site footer says "Data and Charts for Informed Civic Conversations." Pick one. The footer version is plainer and arguably stronger ("metrics" is colder than "data and charts"), but either works — the point is one.

**Anonymous authorship is the single biggest trust gap on the site.** The People page names no one. For a project whose entire pitch is trustworthiness and whose stated audience includes journalists, an unnamed operator is a meaningful credibility discount — a reporter deciding whether to cite the site will look for a person, credentials, and a conflict-of-interest statement, and currently finds only a GitHub link. A short authorship statement — name, professional background in measurement/validation science, the independence and funding disclosure already drafted — would materially strengthen every other claim the site makes. If pseudonymity is a deliberate choice, it deserves an explicit sentence explaining it; silence reads as an oversight. Relatedly, GitHub Issues as the only contact channel is high-friction for exactly the journalist/educator audience named on the homepage; a simple email address fixes that.

---

## 7. Technical, SEO, and discoverability

**Add schema.org `Dataset` markup for the downloadable CSVs.** This is the highest-leverage discoverability move available: Google Dataset Search indexes JSON-LD `Dataset` records, and a site offering dozens of cleaned, licensed, regularly updated Canadian datasets is precisely its target content. It's also perfectly aligned with the open-data mission. Quarto can inject per-page JSON-LD via `include-in-header`; each Download data entry has all the required fields already written (name, description, licence, distribution URL, temporal coverage).

**State a licence for the site's own content.** The Data Sources page is meticulous about upstream licences, and the code is open source, but the site's compiled text, charts, and cleaned CSVs carry no explicit licence of their own. A footer line ("Text and charts CC BY 4.0 unless noted; underlying data per source licences; CREA series excluded") tells teachers and journalists what they can reuse — which is the point of the project.

**Confirm the basics before launch:** a sitemap.xml and robots.txt (Quarto generates the former with `site-url` set), canonical URLs (which the custom domain decision affects — decide the domain first), 404 page, and that the promised stable per-chart anchor links survive heading edits (Quarto derives IDs from heading text; a heading rewording silently breaks every existing deep link — consider explicit `{#id}` anchors on chart headings as a policy).

---

## 8. Prioritized recommendations

**Before launch (blocking or near-blocking):**
1. Fix SVG social-card images — PNG OG cards on every page; validate previews on X and Slack.
2. Decide the custom domain and (if renaming) the repo name now, while URLs are cheap to change; add Quarto aliases/redirect policy for any slug rationalization.
3. Full-site rebuild plus a CI nav-consistency check to eliminate stale menus (Immigration, Temperature Maps discrepancies) and any dead group-label artifacts.
4. Add an authorship statement and an email contact.
5. Complete or remove the empty "Latest household debt: ranked" narrative; run the planned content audit with a specific eye for placeholder sections and hard-coded figures.
6. Choose one tagline.

**Shortly after launch (high value, not blocking):**
7. Move headline in-prose figures to computed inline values, or adopt graceful-aging phrasing plus a "narrative reviewed" date.
8. Add schema.org Dataset JSON-LD and a site content licence statement.
9. Neutrality-audit pass on interpretive phrases; add one or two neutral-valence homepage questions.
10. Uniform source-and-vintage line on every chart; one-sentence prose takeaway per chart as an accessibility rule.
11. Explain the Toronto-only local layers in-page and sketch the multi-city roadmap.

**Roadmap items:**
12. Data dictionary for the CSVs.
13. Democracy/elections page; deliberate approach to Indigenous data beyond boundaries.
14. Bilingual roadmap statement, with chart-label pipelines designed for translation.
15. Mobile performance pass on the longest pages (Housing); split or lazy-load if measurement warrants.

---

## 9. Closing note

The hard parts of this project — pipeline reliability, source discipline, methodological honesty, a coherent identity system — are done, and done well. Nearly everything above is finishing work: consistency between surfaces that were built at different times, and trust signals (a name, a domain, a licence, uniform provenance lines) that convert internal rigour into externally legible credibility. The one structural item worth genuine engineering time is the prose-vs-pipeline freshness problem; everything else is a checklist.
