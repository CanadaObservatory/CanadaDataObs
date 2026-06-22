# Comparator stress-test — should the 17-peer set change?

**Owner priority #2 (2026-06-18). Analysis + recommendation for discussion — no change yet.**

The owner asked: how certain are we about the chosen comparators? Are there situations where others
are relevant (e.g. **China/India on CO₂/air quality**), and should we add other **European** peers
already in the OECD data? With the standing constraint that the **legend can't grow** without
re-triggering the scroll problem.

## The current set
**17 peers** = G7 (US, UK, France, Germany, Italy, Japan) + Australia, South Korea, Netherlands,
Sweden, Switzerland, Norway, Denmark, Finland, Israel, New Zealand. **Dropped earlier:** Belgium &
Austria (redundant with NL/Germany/Switzerland), **Ireland** (multinational profit-shifting inflates
its GDP/productivity). The set is deliberately *advanced, high-income, democratic OECD* — a group
Canada genuinely benchmarks against across every topic.

## The principle that should decide this
**Consistency is the moat.** The site's value is that you *always know who Canada is being compared
to* — the same peer group on every page. Per-topic country swaps erode that. So the bar for change
should be high, and changes should be **global** (same set everywhere), not ad-hoc. The owner's
instinct is right: "the more we do this ad hoc, the more we sacrifice consistency." Two things follow.

### 1. China & India on emissions / air quality — a *principled* exception, not ad-hoc
On emissions and air quality the **purpose of the comparison changes**. Everywhere else the frame is
"how does Canada rank *among peers*." For CO₂ and PM2.5 the meaningful frame is "where does Canada sit
in the *global* picture" — and China (~28% of global CO₂) and India (~7%) *are* that picture. Leaving
them out makes Canada's ~1.5% read in a vacuum. Because this is a **different analytical frame (global
context, not peer benchmarking)**, adding them *only here* is consistent reasoning, not an ad-hoc
swap — provided it's framed that way on the page ("global context; not OECD peers").

**Recommendation:** yes — surface China + India on the **emissions** and **air-quality** charts.
Cleanest execution is a **purpose-built "global context" comparison** for those charts (Canada + the
big emitters + a few peers) rather than bolting two lines onto the 17-peer template — that keeps the
17-peer set's meaning intact everywhere else *and* sidesteps the legend ceiling (a curated 6–8-line
chart, not 19).
**Data check before building:** OWID (CO₂, already used) includes China/India. For **PM2.5**, the
OECD Green Growth dataflow currently driving that chart is OECD-members-only — China/India would need
the **World Bank / OWID** PM2.5 series instead. Verify coverage there before committing the air-quality
piece.

### 2. India/China elsewhere — no
India is not a useful comparator for health, income, education, fiscal, etc. (different development
tier) — agreed. China only if a specific chart's story is genuinely global-scale, which is rare;
default **no**, to protect the consistency moat.

### 3. Adding European peers — assessed, and the answer is mostly no
Which advanced European countries are missing from the set?
- **Spain** (~48M, large advanced economy) — the *one* genuinely defensible omission; would broaden
  southern-Europe representation.
- **Belgium, Austria** — dropped as redundant; re-adding adds little distinct signal over NL /
  Germany / Switzerland.
- **Poland, Czechia, Portugal, Greece** — lower-income / different tier; including them changes the
  *character* of the peer group (it's deliberately a high-income set).
- **Ireland** — the GDP-distortion reason still holds for economic indicators; including it only for
  non-economic charts would be exactly the per-topic inconsistency we're trying to avoid.

So the only real candidate is **Spain** — and here the **legend constraint is decisive**: the peer
line charts already fit *exactly* 18 entries (17 + average) at 600px, and any addition (even drawn
grey) adds a legend row and re-triggers the scroll-capture problem. The marginal value of Spain does
**not** justify reopening that. **Recommendation: keep the set at 17; do not grow it.**

## Bottom line
1. **Keep the 17-peer set** as the consistent, global standard. Don't grow it (legend ceiling vs.
   marginal benefit — only Spain was even arguable).
2. **Emissions + air quality get a deliberate "global context" treatment** with China + India
   (curated small set, framed as global-not-peer; verify PM2.5 data source first).
3. **No other per-topic additions** — India/China stay out elsewhere to protect consistency.
4. **Reaffirm the existing drops** (Belgium/Austria redundant, Ireland GDP-distorted).

Net: the stress-test *validates* the current set. The only change worth making is the global-context
emitters view on the two climate/air pages — which is additive and doesn't touch the peer standard.
This also dovetails with the colour report: a curated 6–8-line emitters chart stays well under the
~8–12 colour ceiling, so China/India can have clear fixed colours there without strain.
