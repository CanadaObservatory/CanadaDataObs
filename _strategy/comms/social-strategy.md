# Canada Observatory — Communications & Social Media Strategy

*Drafted 2026-07-11 (travel chat, from the published site only); **refined 2026-07-12
against the repo** — corrections from that pass are marked ⟨repo⟩. Platforms in scope:
X, Instagram, Facebook, with Bluesky/Threads as near-zero-cost mirrors.*

**Operating constraint:** one person, a full-time academic job, and a daily-updating
data pipeline. Every recommendation is filtered through sustainability — a strategy
that requires 15 hours a week will fail by October, and a dead social account damages
the brand more than no account.

---

## 1. Objectives and positioning

Social media serves three goals, in priority order:

1. **Establish the site as a citable reference** among journalists, educators, and the
   policy-literate public — the multiplier audience whose use of the site does the real
   distribution.
2. **Build a habit loop** — a recognizable weekly rhythm so followers come to expect
   (and share) the content.
3. **Advance the open-data cause** — the one advocacy position, which doubles as the
   most distinctive content angle available.

The positioning on social must be identical to the site's: *we show the number, the
peer comparison, and the source; you draw the conclusion.* On social platforms this is
a genuinely contrarian stance — the algorithm rewards takes, and this account declines
to provide them. That restraint IS the brand. The moment a post reads as a take, both
political camps will file the account accordingly and the neutrality asset is spent.

**The voice in one sentence:** a knowledgeable friend who shows you the chart, points
at the interesting part, and hands you the source — never tells you what to think
about it.

---

## 2. Audiences, by platform

**X** — journalists, economists, policy analysts, academics, data-literate news
consumers. Where citations and media pickup happen. Highest value per follower;
highest hostility per reply.

**Instagram** — general public 25–45, teachers, students, urbanists, local-curious.
Visual-first; the neighbourhood maps and long-run charts are naturally strong here.
Lowest hostility; best fit for the data-literacy pillar.

**Facebook** — 45+ general public, local community groups, extended networks. The
algorithm suppresses external links, so Facebook works as a *native chart +
conversation* channel, not a traffic channel. Unique strength: city-specific content
travels through local groups ("Winnipeg vacancy rate," "Halifax rents") in ways
nothing else replicates.

**Bluesky / Threads** — much of Canadian academia, science, and data journalism
migrated substantially to Bluesky in 2024–25; marginal cost is near zero because
X-format posts cross-post verbatim. Register the handles at launch, mirror X content,
invest no additional creative effort for the first quarter, review at 90 days. Do not
let them expand the workload.

**Handle hygiene (pre-launch).** ⟨repo⟩ Current handles: **@canobservatory (X)** and
**@canadaobservatory (Instagram)**. Attempt to secure @canadaobservatory on X and
facebook.com/canadaobservatory so the handle is uniform; if the X handle is
unavailable, put the custom domain prominently in every bio so the site name, not the
handle, carries the identity. Suggested one-line bio: *"Interactive charts on Canada —
people, economy, government, health, environment, education. Sources cited, data
downloadable, no advocacy."*

---

## 3. Content pillars

Five pillars, each with a defined job. Every post belongs to exactly one.

### Pillar 1 — Chart of the Week (the anchor)
One flagship chart, same day and time weekly (**Tuesday 9:00 a.m. ET** — clear of
Monday noise and Friday data releases), chosen for civic relevance or a fresh data
update. The habit-forming product; everything else is supplementary. Format: branded
PNG, a two-to-four-sentence neutral read, the source, the link.

### Pillar 2 — Release-day context (the news hook)
When StatCan or the Bank of Canada publishes a headline number, post *the long-run
chart behind the headline* within a few hours. Everyone else posts the monthly number;
CanObs posts the 30-year context.

⟨repo⟩ **The infrastructure for this largely exists already:**
- The pipeline runs **daily at 14:00 UTC (~10:00 ET)** — after StatCan's 08:30 ET
  release window — so release-morning numbers are on the site the same morning. For
  anything time-critical, `workflow_dispatch` on the Actions workflow is the manual
  "refresh now" button. The chat draft's "script a one-command re-render" item is
  therefore already solved.
- `pipeline/release_schedule.py` already reads StatCan's machine-readable release
  calendar (the same feed behind their public schedule) and stamps "Next update"
  dates into metadata sidecars. **The social release-day calendar should be generated
  from this same feed**, not maintained by hand.

Calendar anchors: LFS (~first/second Friday), CPI (~mid-month), BoC rate decisions
(8 fixed dates/year), monthly GDP (~month-end), quarterly population estimates
(mid-Mar/Jun/Sep/Dec). Annual set-pieces: police-reported crime (July), NIR emissions
(spring), CMHC Rental Market Report (~Jan–Feb), World Happiness Report (March),
wildfire season (summer, ongoing), **PISA 2025 results (~Dec 2026 — verify the OECD
date; a major education content day, see the launch plan's PISA build item)**.

### Pillar 3 — Data literacy ("How to read this")
Short general-principle posts on interpreting data: why an index of 100 isn't a level,
what a rebased chart can't tell you, why per-capita changes rankings, what "median"
hides, why the 2011 census point is flagged, survey vs. administrative data. Three
virtues: evergreen (batchable months ahead), genuinely differentiated, and *politically
safe* — the least attackable content the account can produce. On Instagram this pillar
becomes carousels — the highest-performing format there and the natural container for
"concept, example, takeaway."

### Pillar 4 — Local lens (the shareability engine)
City- and neighbourhood-level content: typical rent in a city, how a city's crime
severity compares across the ~40 metros, census-tract map crops. People share content
about *their* place at rates national charts never achieve. One national chart yields
10+ city variants; a Python loop over the existing per-city data can generate a
season's worth in an afternoon. Primary Facebook content and the Instagram growth
engine. **Rotate cities deliberately** — a visible Toronto skew on social would
compound the site's Toronto-heavy local layers.

### Pillar 5 — Open data & behind the build
The one cause, plus process content: why a series is flagged, what a homogenized
temperature record is, "this chart exists because a public agency published X openly."
Modest reach, but it recruits exactly the contributors, academics, and journalists the
project most needs. Monthly cadence is enough.

**Deliberately absent:** hot-take commentary on political events; dunks (including on
bad charts by named outlets — critique the pattern, not the person); engagement-bait
polls on contested questions; posting *during* fast-moving political news cycles when
any chart will be conscripted as ammunition. Silence during a firestorm is a
positioning choice.

---

## 4. Visual and voice system for social

**One template, three crops.** ⟨repo⟩ This is **`pipeline/social_cards.py`**, which
already exists (v1 = the CPI "latest release" card in the brand identity — off-white
field, cells leaf, locked palette — rasterized via the qlmanage→sips recipe, macOS-
local). `SOCIAL_FORMATS` there is already the canonical size set (portrait 1080×1350 /
square / 16:9 / OG 1.91:1 — full per-network notes in the social-image-sizes reference
memory). Remaining build, in order:

1. **Per-aspect layout pass** — v1 composes 1:1 only; portrait/landscape/OG need
   element reflow (flagged in the file's own header).
2. **A generic chart→card path** for arbitrary site charts —
   `pipeline/build_static_charts.py` is the working Plotly+kaleido prototype (drops
   legend-only peers, tall-canvas relayout); it needs the brand font embedded and a
   loop over chosen charts.
3. **Rasterizer decision** — qlmanage is macOS-only; CI auto-generation needs resvg or
   cairosvg (or the kaleido path). Local monthly batching is acceptable for launch;
   don't block on CI.

**The footer is non-negotiable on every image:** `Source: Statistics Canada, Table
XX-XX-XXXX · canadaobservatory.ca`. Charts *will* be screenshotted and recirculated
without the caption; the footer is the only branding and provenance that survives.
Marketing and misuse-mitigation in one line.

Per-theme accent colours: ⟨repo⟩ the six area colours are locked in
`visual_assets/brand/palette.md` (the area mapping behind the banner motifs) — carry
them into the templates so the feed develops a recognizable rhythm.

**Alt text on every image, every platform, no exceptions.** All three platforms
support it; its absence is the kind of detail critics of a "for everyone" site will
notice. One-sentence description plus the headline number suffices.

**Caption voice rules:**
- Lead with the observation, not the site ("Canada's homicide rate is near a 60-year
  low" — never "New chart on our site!").
- One claim per post; the thread or carousel adds dimensions.
- Numbers in captions must match the chart being posted — a screenshot with a wrong
  number is permanent. Pull caption numbers from the same CSVs the chart uses.
- Hedge honestly but briefly ("Police-reported; victimization surveys tell a fuller
  story — details on the site").
- Never argue a conclusion. When the chart is politically charged, the caption gets
  *more* boring, not less.

---

## 5. Launch plan

### Phase 0 — Pre-launch gate (do not announce before these are done)
1. OG/social-card images fixed to PNG site-wide and validated in real pastes (X,
   Slack, iMessage, LinkedIn Post Inspector). ⟨repo⟩ **Confirmed live bug**: the
   homepage and overview pages currently emit SVG og:images — launch-gate G1 in the
   launch plan.
2. Custom domain executed, so launch links are the permanent links (gate G2).
3. The diversity/religion map framing published where screenshots will point (the
   pages carry framing; make sure the social-facing crops carry the one-line version).
4. Handles secured and bios written.
5. **Six to eight weeks of Pillar 3 + Pillar 4 content batched and scheduled** (Meta
   Business Suite for IG+FB; Buffer free tier for X). The launch will consume
   attention; the pipeline of ordinary posts must already exist so week 3 doesn't go
   silent.
6. Corrections protocol written down (Section 6).

### Phase 1 — Soft launch (1–2 weeks, late August)
Share personally and quietly: colleagues, the Evidence for Democracy network,
data-minded academics, friends who will actually click around. Goal: shake out bugs
under friendly eyes, and seed the accounts with 5–10 posts so they don't look newborn
when strangers arrive. Follow relevant Canadian data/econ/policy/journalism accounts
during this window.

### Phase 2 — Public launch week (day-by-day)
- **Day 1 (Tue):** launch thread on X — what the site is, the six themes, 4–6
  strongest charts as images, the "no advocacy except open data" line, the link.
  Mirror as an IG carousel (one frame per theme, theme-colour leaves) and a Facebook
  post. Pin everywhere.
- **Day 2:** the "Start with these questions" post — the homepage question list as
  carousel/thread, each question paired with its chart.
- **Day 3:** strongest single chart, pure Pillar-1 treatment — demonstrate the
  ongoing product, not just the announcement.
- **Day 4:** the open-data manifesto post — why the site exists, the one cause, the
  invitation to download the CSVs. The post academics and civic-tech people share.
- **Day 5:** a local-lens post — the neighbourhood-level capability is the site's most
  demo-able feature.
- **Days 6–7:** rest; reply to everything worth replying to.

### Phase 3 — Earned distribution (launch week and after)
The three platforms alone will not launch this site; the multipliers will:
- **Direct outreach to 10–15 data-friendly Canadian journalists and newsletter
  writers** (economics, housing, demography beats). Short personal note: what it is,
  everything citable and downloadable, two or three charts relevant to their beat. No
  embargo theatre — a useful tool, offered.
- **Reddit, done carefully:** r/canada, r/CanadaPolitics, r/dataisbeautiful, city
  subs — a genuinely open-data project presented humbly by its builder plays well;
  anything that smells of marketing is punished. One well-crafted post per community,
  spaced, engaging in comments.
- **Hacker News ("Show HN")** — the open-source pipeline angle reaches exactly the
  contributor audience.
- **Academic and teaching networks** — quantitative-methods and Canadian-studies
  colleagues, relevant listservs: the CSVs are classroom-ready. Teachers are the
  highest-retention audience available.
- **Policy Options / The Hub** — a "why I built a no-advocacy data site" essay pitched
  post-launch converts the launch into a durable, linkable artifact and addresses the
  authorship-trust point head-on.

---

## 6. Ongoing operations

### Weekly rhythm (target ≤3 hours/week after the first month)

| Day | X | Instagram | Facebook |
|---|---|---|---|
| Tue | Chart of the Week | Chart of the Week (portrait) | Chart of the Week |
| Thu | Data-literacy or local-lens | Carousel (literacy) or map post | Local-lens post |
| Release days | Context chart within hours | Story only (low effort) | Skip unless local angle |
| Ad hoc | Replies; one RT/QT of good data journalism | Stories: site features | — |

Cadence floor: 2/week X, 1–2/week Instagram, 1/week Facebook. Far better to hold this
floor for a year than to post daily for six weeks. Batch on a fixed monthly block;
release-day posts are the only truly live work.

### The pipeline advantage
The daily refresh should eventually emit social candidates automatically: a script
that flags series with notable movement (new max/min, largest change in N years, new
vintage) and renders the branded PNG in all three crops — the human job reduces to
curation and caption. ⟨repo⟩ Build this as an extension of `social_cards.py` +
`release_schedule.py`; it is a post-launch automation, not a launch gate. Keep a
running backlog file of post ideas — the site's section intros are essentially
pre-written post copy.

### Community management and the neutrality playbook
- **Reply to:** genuine questions, correction reports, journalists, teachers,
  good-faith methodological challenges. These replies *are* the brand.
- **Do not reply to:** partisan framing demands, bad-faith quote-tweets, anyone
  arguing about conclusions. The account discusses data and methods only. One polite
  methods-level response maximum, then disengage. Never delete a post for being
  unpopular — only for being wrong.
- **When a chart is wrong:** correct fast and visibly. Reply to the original post with
  the correction, edit where the platform allows, post a standalone correction if the
  error spread, and log it on the public corrections note (launch-gate G10). A crisp
  correction is a trust *gain* for this brand; a quiet deletion is a
  scandal-in-waiting.
- **When a chart is misused** (cropped, recaptioned, conscripted into a partisan
  fight): the on-image footer is the primary defence. Intervene only when the
  misrepresentation is factual and significant — one flat reply stating what the chart
  actually shows, with the link. Do not chase it across the platform.
- **Both-sides attacks are the success condition.** Accusations of bias from opposite
  directions on the same chart are evidence the positioning works.
- Time-box: a 20-minute engagement window daily beats ambient availability — for the
  account's tone and for sanity.

---

## 7. Measurement

Ignore follower counts for six months; they measure the algorithm, not the mission.
Track:
1. **Citations and pickups** — journalists, newsletters, teachers using or linking the
   site (search alerts on the name + domain). The true KPI.
2. **Site sessions from social** — UTM-tag every posted link
   (`utm_source=x/instagram/facebook, utm_medium=social,
   utm_campaign=cotw/launch/release`), attributed by the privacy-respecting analytics
   from launch-gate G8.
3. **CSV downloads / repo traffic** — GitHub provides this; it measures the open-data
   mission directly.
4. **Saves and shares over likes** on IG/FB — the reference-value signals.
5. **Post-format learning** — quarterly: which pillar/format/topic earned
   disproportionate reach per platform; reallocate. Expect local-lens to win Facebook,
   carousels Instagram, release-day X — but let the data overrule the prediction,
   on brand.

At 90 days: review the Bluesky/Threads mirrors, retire whichever pillar is
underperforming *and* burdensome, decide whether the cadence floor can rise.

---

## 8. Risks specific to this project

- **The neutrality paradox:** growth is fastest for accounts with takes. Accept
  slower, higher-quality growth; the compounding asset is citability, not reach.
- **Screenshot decontextualization** of the demographic maps: mitigated by the
  on-image footer, the on-page framing, and a pre-written worst-case response (the
  "hard answers" doc, launch-gate G13).
- **Anonymity under fire:** "who runs this account?" is a standard attack. The
  authorship decision (launch-gate G3) must be settled before launch, not during a
  pile-on.
- **Burnout / abandonment:** the visible failure mode of solo civic projects is the
  account that stops in month three. Floor cadence, batching, and automation exist to
  prevent it; in a hard month, drop to Chart of the Week only — never to zero.
- **Platform risk on X:** the Canadian civic conversation is genuinely split across X
  and Bluesky; the mirror strategy hedges at near-zero cost.
