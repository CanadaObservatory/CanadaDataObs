# Draft — The Conversation Canada

*Drafted 2026-07-11 (travel chat); figures verified against the repo data 2026-07-12 —
see the revision notes. Target: pitch ~Aug 17–21, run launch week (Sept 8–12).*

**Working headline:** Canadians are arguing from different facts. I built a website to give us shared ones.

**Alternative headlines:**
- Why I spent two years building a no-advocacy data site about Canada
- Is crime up? Are wages keeping pace? A new site lets Canadians check for themselves

**Standfirst:** Public data about Canada is world-class but scattered. Canada Observatory gathers it into one continually updated, open reference — and takes no side in what it means.

---

Is crime going up? It depends which crime you mean. Fraud and identity theft have roughly doubled in Canada over the past decade, and shoplifting is up by about two-thirds. Over the same period, break-and-enter and theft from vehicles fell substantially. Overall crime remains well below its levels of the 1990s and 2000s.

Whether "crime is up" is therefore not really a factual dispute. It's a question of which facts you're looking at — and in most arguments, nobody is looking at any of them.

I'm a physicist who has spent his career on measurement: atmospheric instruments, and the unglamorous work of checking whether one instrument's numbers can be trusted against another's. I also teach, and I've been involved in science-policy work for years. From all three vantage points I kept noticing the same problem. Canada produces some of the best public data in the world, but it lives scattered across dozens of agency websites, statistical tables and one-off news charts that are impossible to find again three weeks later. When a question comes up at the dinner table — are incomes keeping up, how fast is Canada warming, how big is government — there was no single place a person could reliably go, check, and cite.

So I built one. [Canada Observatory](URL) is a free, open website of interactive charts on the state of the country: population and immigration, the economy and affordability, government finances, health, the environment, and education and science. The data comes only from authoritative primary sources — Statistics Canada, the OECD, Environment and Climate Change Canada, the Bank of Canada and others — and most of it refreshes automatically as those agencies release. Every chart names its source and the date of its latest data point. Every cleaned dataset can be downloaded for free.

## The rules of the site

Two design decisions matter more than any chart.

The first is context. A number on its own tells you almost nothing; the question is nearly always "compared to what?" So wherever possible, Canada is shown against 17 comparable OECD countries — not just the G7, which leaves out peers like Australia, Sweden, South Korea and the Netherlands. And wherever the data allows, national figures reach down to the neighbourhood: you can zoom a map to your own census tract and see incomes, home values, languages or diversity on your own street's scale.

The second is restraint. The site takes no policy positions. It does not say whether taxes are too high, immigration too fast or health spending too low. It shows the number, the peer comparison, and — where one exists — the recognized benchmark, like the Bank of Canada's inflation target. What the numbers mean is left to the reader.

That restraint is not because the numbers are neutral in their implications. It's because the judgment belongs to citizens, and because a reference only stays useful if everyone can trust it. Disagreement is healthy in a democracy. Arguing from different facts is corrosive. A shared, citable evidence base doesn't end debates — it lets them be about values and trade-offs, which is where they belong.

## What the numbers show when you gather them

Assembling the data in one place has a way of sharpening questions that vague argument blurs.

Housing is the clearest example. In 2005, the benchmark Canadian home cost roughly 5.7 years of a typical household's after-tax income. By 2024 it was over nine. That single ratio, tracked over time, says more about the affordability debate than most of the commentary written about it — and it sits alongside the peer comparison showing how unusual Canada's run-up has been.

Climate is another. Canada is warming at about twice the global rate, and its North faster still. The instrument records behind that statement — some reaching back to 1841 in Toronto — are public, and the site shows exactly which series have been adjusted for station moves and instrument changes, and which haven't. As a measurement scientist, I consider those footnotes the most important part.

And some numbers complicate every tidy narrative at once. Hate crimes reported to police have roughly tripled since 2014, but police data undercounts hate crime, and rising numbers partly reflect greater reporting. The site says so, on the chart. Honest data work means showing the caveat next to the number, not burying it.

## The one cause

I said the site takes no positions. There is one deliberate exception: it openly advocates for the creation, use and open availability of public data itself.

A project like this can only exist because public agencies count things carefully and publish the results for anyone to use, under open licences, in machine-readable form. That quality is a choice Canada has to keep making. The site carries a scar that shows what happens otherwise: in 2011, the mandatory long-form census was replaced with a voluntary survey, response rates fell, and the data suffered. Wherever 2011 appears in the site's census-based charts, it is flagged as the weak point in the line. When collection weakens, the gap never fully heals.

Statistics Canada is internationally respected, and the open-data infrastructure built over the past decade — open licences, public APIs, municipal data portals — is a quiet national asset. It deserves defending, and using.

## An invitation

Canada Observatory is independent, with no sponsor, no political affiliation and no paywall. The code and the cleaned data are public. If you're a teacher, the datasets are classroom-ready. If you're a journalist or researcher, everything is citable and traceable to its source. If you're anyone else, start with a question you've actually argued about lately — the site's front page lists the most common — and see what the numbers say.

You may not change your mind. But you'll be arguing from the same facts as the person across the table, and in a democracy, that's most of the battle.

---

## Notes for revision (not part of the article)

1. **Word count:** ~950 words, in The Conversation's typical 800–1,000 range.
2. **Figure verification — first pass done 2026-07-12 against the repo CSVs**
   (`statcan_crime_by_type.csv`, Canada rates per 100k, 2014→2024):
   - Fraud **+89%**, identity theft **+124%** → "fraud and identity theft have
     roughly doubled" is accurate as a pair statement; keep.
   - Shoplifting **+66%** → "up by about two-thirds" ✓ exactly.
   - Breaking & entering **−32%**, theft from a vehicle **−43%** → "fell
     substantially" ✓.
   - All Criminal Code (excl. traffic) **+12%** since 2014 but the long-run CSI shows
     current levels well below the 1990s–2000s → the "overall crime remains well
     below" sentence ✓ (it reads on the long-run chart, not the 2014 base).
   - Hate crime rate **3.7 (2014) → 11.9 (2024)**, peak 12.1 in 2023 → "roughly
     tripled" ✓.
   - Toronto temperature record: site data runs **1841–2025** ✓.
   - "Warming at about twice the global rate" — the standard ECCC/CCCR statement;
     confirm the site page carries it verbatim before submission.
   - **Re-verify all of the above the week of submission** — the pipeline updates
     daily and 2025 crime data lands ~July 2027, so drift risk before Sept is low but
     non-zero.
3. **The housing ratio (5.7× → over 9×) is CREA-derived** (the site computes it at
   render time from the CREA MLS® HPI composite ÷ real median income). Citing the
   ratio as a fact in an article is fine; if an editor asks for sourcing, attribute
   "CREA MLS® Home Price Index; Statistics Canada median after-tax income" — do not
   hand over the underlying CREA series. The "over nine" phrasing (rather than a
   hard "9.3") is deliberate graceful-aging.
4. **Cadence phrasing:** the draft says "refreshes automatically as those agencies
   release" — matches the daily pipeline; do not say "weekly" (stale).
5. **The Conversation requires a disclosure statement** — draft: "Dan Weaver is an
   Associate Professor, Teaching Stream, at the University of Toronto Scarborough.
   Canada Observatory is an independent personal project with no funding, sponsorship,
   or institutional affiliation. He has previously volunteered with Evidence for
   Democracy." (Aligned with the Crucible byline; owner to confirm accuracy.)
6. **The URL placeholder** resolves once the custom-domain cutover (launch-gate G2)
   is done — use canadaobservatory.ca, never the github.io URL, in anything pitched.
7. **Angle chosen:** personal + measurement-scientist framing, leading with the crime
   example because it demonstrates the product in one paragraph. Alternative leads:
   the housing ratio (broadest resonance) or the 2011 census story (strongest
   open-data hook, but more inside-baseball).
8. **Editors will cut** — most cuttable: the climate paragraph and the second half of
   "The one cause." Load-bearing: the lead, the two design rules, the closing line.
9. **Overlap guard:** the 2011 census story appears in all three pieces at different
   depths (intentional — one identity, three audiences). If this piece and the news
   op-ed run close together, trim the census paragraph in one of them so the overlap
   is thematic rather than verbatim.
