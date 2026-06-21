# Review extract (canonical §-numbering = 1-indexed paragraph over the .docx)

§1	Notes about DataCan version 0 on June 17, 2026
§2	Big picture:
§3	It was often the case that the line plots were quite busy, even though we have limited our initial set to Canada and five key comparators. I suggest we change this to loading only Canada plus United States, Australia, Germany, and the OECD peer average. We should leave the Sweden and UK as they otherwise are, i.e., they show a colour and are at the legend top, to reflect their value as comparison countries and continuing the use of these colours in the ranking bar plots.
§4	I’d like a strategic assessment of colours used for the line plots. We have determined a set of colours for countries, but where are these colours coming from? We should create a set that are carefully chosen for this specific site and branding and visual identity as well as scientific visualization best practices. Not only for the countries, but we sometimes have provinces as well. This can be a major effort and report before implementation.
§5	Potential gaps in site content
§6	Military spending and size: could a world map even make sense?
§7	Are there other topics where a global choropleth would be worthwhile?
§8	Missing Middle and Millennial stress topic:
§9	First time home buyer age
§10	Family formation age
§11	How certain are we about the chosen comparators? Let’s stress test that. Also, the consistency is good. But we should assess if there are specific situations where others are relevant: e.g., CO2 emissions could be in context by adding China and India, since they are significant emitters.
§12	Landing page
§13	Remove “CanObs for short”
§14	Start new paragraph for “Where the data allows, maps…” to make it stand out a bit. It’s also a separate topic from international comparisons.
§15	We should clarify that the data files we offer for download and use are in an easy-to-use format to encourage people’s engagement
§16	I thought during conversations about the visual identity products we decided that the six main colours would map onto the six themes. There seems to be an opportunity to use that here in a more visually polished way instead of the pure text that is currently the section descriptions and links
§17	The principles section at the end is good and worth keeping. But it overlaps with an early paragraph that could be cut.
§18	Suggest how we might include links to social accounts, e.g.: https://www.instagram.com/canadaobservatory/ and https://x.com/canobservatory
§19	Should add an upfront statement that a goal is to support conversations about Canada with relevant, timely, and reliable data.
§20	Modest re-write of the “Start with these questions” would be helpful. Let’s assume people are new and remove “New here?” Instead, let’s lead with the idea that we want to help people explore and better understand their own questions. But give a few examples of common and important topics in Canada right now and how our content relates to them.
§21	Overall structure:
§22	Eventually it might be useful to have a blog or space for discussion/update summaries. This could be located within the About section to keep the navbar compact.
§23	Eventually I am also strongly considering whether there should be content about essentially civics education, again under the About. This could give some guidance for how to make simple plots using the data we have, links to resources, and some helpful advice and even very simple code examples. Example: just because two things correlate, doesn’t mean they’re related. There are nice webpages that give examples of spurious correlations with humour like https://www.tylervigen.com/spurious-correlations
§24	Should each of the six sections have its own landing page? This could be an opportunity to give a top-level overview of why it is a pillar of the site and what the section contains. Also could have some visual identity for each section.
§28	Population
§29	/Population & Growth
§30	Population over time:
§31	Advantages of a line plot vs. bar plot here? It’s good as it is, but worth consideration. An advantage of the line is that is aligns with the next plot, but we could have a bar plot here and then add Canada as an option in the ‘by province’ plot but keep it unloaded initially.
§32	Refine text: “steadily” isn’t quite true in the last few years. Remove that word. Remove “as a whole” since that’s already implied by “Canada”.
§33	Population by Province and Territory
§34	This is a bit compressed width-wise due to the legend. There are two options, both involve shortening the longest legend names. Either we keep it as it is but shorten the long names, or we move it below the chart area. It’s probably easiest to keep its location and shorten the long names or split them across two lines. E.g., “Northwest Territories including Nunavut” to be “NWT & Nunavut”. However, two lines help solve the “Newfoundland and Labrador” more sensitively than reducing it to only “Newfoundland” or to “NFL”.
§35	Population Growth Rate:
§36	Source text is overlapping the x-axis scale selection slider
§37	Let’s make the y-axis maximum exactly 5 since it never exceeds 5% and ensure there is still the 5 tick and line. Most of the timeseries is much below that, so we want to maximize the y-axes scale that is sensible for the recent years.
§38	Where Canada’s Population Growth Comes From
§39	There is an odd bit of stray text at the top-right corner of the plot that says “show:”?
§40	Non-Permanent Residents:
§41	This line plot feels more sensible as a bar plot to me.
§42	This plot feels incomplete. There are buttons for up to 20 years but the data only seems to be for the last few years – a big mismatch. And really just looking at a few years isn’t that useful. Also, the text notes this category is composed of a few types of people but there is no breakdown into these categories, which would be more informative (e.g., stacked bar plot).
§43	Age Structure:
§44	Text: remove sentence about “Recent years…. Fill in the working ages” because not all immigration is from people in that 20-30s age bracket. If we were to assert that, we would want to actually know the age structure of immigration and other groups (e.g., asylum claimants) but I’m not sure we want to do that or if it’s even possible. Investigate the available data and note it for future reference.
§45	The “source” text line is being slightly cut off at the bottom.
§46	Median age:
§47	Can this be somehow added to the age structure plot above it? Maybe it deserves its own plot, but worth considering.
§48	Aging Among Peer Countries
§49	Major issue: the legend has a scrolling feature that causes the full webpage to scroll. There seems to be room to avoid this. Check all site figures for this issue.
§50	This also brings to mind another site-wide issue to assess: we have highlighted five countries as the most important comparators. However, adding multiple other lines that are grey makes it challenging to see them distinctly. Especially in cases where either the topic makes a particular country relevant (e.g., Japan) or the user has a particular comparison they want to create. We should consider the option of only loading the key comparators initially but giving the rest their own distinct colours: a challenging task for a list of 17 countries. However, the bar plots and score cards are working well with only highlighting a few key comparators! Maybe that difference is ok?
§51	the bar plot below has blank space between: not ideal. Maybe we move the x-axis label to the top, giving it a dual use of a title and x-axis label
§52	Fertility
§53	the legend scrolling issue
§54	x-axis label to top as title like previous plot
§55	Median Age by Neighbourhood
§56	No notes
§57	Moving within Canada
§58	Add x-axis range slider. Take care not to overlap with the Source text lines.
§61	/Diversity
§62	Text at the top needs revision: remove “(incl. White & Indigenous)” and “(Census)”.
§63	Remove defensive sentence about “This is a descriptive picture… shows where people live.”
§64	Also remove defensive “, not a gap in this site.”
§65	Reword “how the groups are assembled description of categories, which is a bit awkward to read. E.g., “Statistics Canada’s “visible minority” variable (its term) has no distinct White category. Instead, there is only “Not a visible minority” residual that contains both European/White people as well as indigenous peoples. To show Indigenous explicitly, we used the 2021 Census Indigenous identity count, and derived White by using “Not a visible minority” minus Indigenous identity. The three top-level groups (All visible minorities, White and Indigenous) sum to 100%.
§66	Refine the text for the last paragraph in this section, e.g. to something like “For an even finer scale, open a metro’s dedicated map using the links below. These are kept on their own page for load speed, and use Statistics Canada’s smallest standard areas (dissemination areas, roughly 400–700 people in small neighbourhoods):”
§67	“How the Diversity of Canada Has Changed” plot:
§68	we should do what was done in the map: separate the indigenous and white from the “NOVM”.
§69	I thought we had data to 2001?
§70	The Source text line doesn’t overlap with the x-axis label but it is quite close; let’s give just a bit more space.
§72	/Religion
§73	Religion by Neighbourhood:
§74	Let’s phrase the initial sentence to center what people will understand and add census tract in parentheses.
§75	Start a new paragraph at “Religion is self-reported…” to break up the ideas
§76	Remove defensive sentence about “Like the diversity map… there is no good or bad reading”
§77	Remove the text from “no religion / secular is now… to Indigenous identity”
§78	The above removals tightens the text to be more neutral by what it doesn’t call attention to.
§79	How religious affiliation has changed:
§80	There is still an odd “Show:” text line above the plot that seems stranded and unclear in purpose. It’s also partially cut off at the top.
§81	The “Sources” text lines are overlapping the x-axis scale slider, which itself is above the x-axis label.
§82	Revise text: “Canada has recorded religion in its census typically once a decade since 1871, providing a long timeseries that illustrates changes over time. For its first century, Canada was 95% Christian, until the mid-20th century. By 2021, Canadians were 53% Christian while “No religion / secular” rose from 0.2% to 35%. Due to their small sizes, religions other than Christian and Jewish were counted as “other religion” up until 1971. Starting in 1981, this “other” category was ended and a greater list of specific groups were recorded. Muslim, Hindu, Sikh and Buddhist populations have grown noticeably in the 21st century. Use the menu bar to switch between each group’s share of the population and the absolute number of people. The legend allows you to add or remove datasets.”
§83	The scale of the shift:
§84	Could we have a drop down to select the comparison year? E.g., see the magnitude of change relative to 1981, 1991, etc.
§85	Revise text to be more straight forward: “The lines above show direction; this ranks magnitude. Over four decades the Christian share fell significantly, while “No religion / secular” rose almost as much. The Muslim, Hindu and Sikh shares quadrupled since 1981.”
§86	By province and city
§87	The sources text line is overlapping with the x-axis title
§88	Remove text: “(the 2026 Census will add a fourth point when it is released in 2027)”
§89	How the religious mix varies by city, 2021
§90	Remove sentence: “That broader footprint is part of why its Sikh and Hindu shares are so large (Brampton in particular).”
§91	Remove “very” from first sentence
§92	Reword/edit: “The national story plays out differently across the country. Toronto and Vancouver are among the most religiously diverse metros. Each bar is one metro’s full 2021 composition; the segments sum to 100%.”
§93	The source text is cut off at the far right. Suggest a new line for “Cities…”
§94	/Languages
§95	No notes, but we should consider adding a bar plot showing the trends over time like we did for Religion
§96	/Citizenship
§97	Revise for easier reading of the key groups, i.e., after “transparently”, use a new line for each of the three groups and their definitions.
§98	Remove “Descriptive only…” to simplify and avoid seeming defensive.
§99	We had discussed voter turnout, e.g., federal elections, at some point. Is this the right location to add it? We should explore this important civic story. Ideally also provincial elections, e.g., federal and provinces selected from a drop down menu bar.
§100	/Crime & Safety
§101	Remove “ — which is exactly the divergence the next chart isolates.”
§102	What’s rising, and what’s falling?
§103	Can we make this a drop down menu for national, provinces, and top ten cities by population?
§104	Remove “ — shifts that coincide with widely-reported events whose causes lie beyond these counts”
§105	Remove: “This is the statistical counterpart to a common lived experience — that everyday property crime often goes unresolved.”
§106	How metro areas compare and Toronto, neighbourhood by neighbourhood
§107	The source text line is slightly overlapping with the map; add some space.
§108	Is crime seasonal?
§109	Remove ”— a reminder that some crime is shaped by opportunity and the calendar, but most is not”
§111	Overall thought about the People section:
§112	We often hear Canada is a small population country. But this isn’t really true. Out of the ~200 countries we are actually somewhere in the top quartile I think? We are dwarfed by the US and China, but we actually are larger than many countries. Maybe we could add a plot near the top that shows our population relative to the comparison countries we use in the project? Could we even make a test global map that shows how Canada compares by area and population?
§113	Economy
§115	/Growth & Jobs
§116	Economy & Jobs: revise text to: “This section explores how fast the economy is growing, how large it is, productivity, and employment levels. These indicators are placed alongside 17 OECD peers. Inflation and the cost of living have their own page: Housing & Cost of Living.”
§117	Real GDP Growth:
§118	This is a good example of where even the compact five comparators seem difficult to read. In this case, and others, I suggest only plotting Canada, US, and OECD peer average initially on load.
§119	I’m not keen on the use of projections especially since they cannot be clearly identified.
§120	Quarterly GPD Growth:
§121	Let’s put this above the international comparison to give it greater prominence. This will also put the GDP and GDP per capita figures alongside each other; both provide an international comparison.
§122	The pandemic quarters (off-scale) text is overlapping awkwardly with the bar. Can it be moved just above the plot area?
§123	Labour Productivity: why only up to 2024? Other OECD data is already up to 2025.
§124	Unemployment rate:
§125	Another example of a plot that’s difficult to read with all the lines. Let’s only initially load Canada, US, and OECD peer average.
§126	The “Age group” text is partially cut off at the top. This is probably not necessary text.
§127	The legend has a scroll bar, even though it’s not really needed. It seems the site-wide fix for this issue didn’t’ quite work here.
§128	The US data ends in 2024?
§129	Latest Unemployment Rate: Ranked
§130	Missing US value for 2025 is regrettable. Verify it really isn’t available…
§131	Source text line needs a bit more space from the x-axis label
§132	Unemployment by City
§133	Source text line needs a bit more space from the bottom of the map
§134	There needs to be text that clearly and prominently defines when the data is current to. This is critical and only currently found in the small Source text at the bottom.
§135	Employment Rate
§136	Remove the older-worker employment comment at the end of the txt.
§137	Only load Canada, US, and average initially to clear up the legibility
§138	Like elsewhere, recheck for US 2025 data
§139	Business Investment:
§140	This (and related plots) feels like it should be in a separate sub-section to make it easier to find.
§141	Current account balance:
§142	Load only Canada, US, average initially to help legibility.
§143	Remove final sentence “Whether a deficit….”
§144	Nuance about this to think about: isn’t much of Canada’s current account balance related to the sale of oil to the US? Is this a thread worth exploring? This is also related to the “Trade Balance: the US vs. the Rest of the World” plot and text.
§145	Trade Exposure to the United States
§146	This is a useful chart. I worry it has become quite buried in a long long page. This supports moving some of the content into a new sub-section focused on trade.
§147	The Canadian Dollar:
§148	Like the trade plots, I feel like this is so buried its hidden. That’s regrettable since most people will find this recognizable. Perhaps we should have currency as a subsection and also have a few other comparisons, e.g., certainly to the Euro given its trade relationship and most of the other peers are European. I’m less sure if it’s worth also having a comparison to the Japanese Yen?
§150	/Cost of Living
§151	I’m not sure this hits the mark fully in helping Canadians understand why they feel so much financial cost of living pressure.
§152	Top text:
§153	Remove the first sentence
§154	start a new paragraph for the final line about “related cost pressures…” and the links
§155	Inflation
§156	Add an x-axis slider to enable easier access to the earlier values. However, inflation moves past the y-axis scale during a variety of timeperiods. Can we also add a y-axis slider to help users navigate the different scales and timeperiods? This is a very important chart to polish.
§158	Headline, Core, and Food
§159	Due to the spikes in values the y-axis scale is a bit large for the last decade of values. Similar to the previous inflation plot, we need a way to adjust the y-axis for different timeperiods and load with a more suitable scale (e.g., -5% to +12%).
§160	Explore other inflation components that might be useful to illustrate. Even food itself might have components worth breaking down in its own figure?
§163	/Housing
§164	Opening sentence needs revision to ensure it is relevant for the long term. E.g., “How much it costs to rent or buy a home is a defining question for most Canadians.”
§165	Let’s simply say “Inflation has its own page: Cost of Living”.
§166	It is repetitive to keep saying in each sub-section that “Canada is red, …”: let’s put this at the top of the page and remove it from elsewhere. This should be done across the site.
§167	Real House Prices
§168	Why use 2015 as the reference point? It’s ok, but would an earlier year not help people understand it? If there’s a good reason, perhaps we should initially load the chart to begin at 2014 to focus on the 2015 and after timeframe. This would match the following bar chart with the rankings.
§169	I feel some inclination to develop a dashboard that enables users to explore big topics like house prices in one place from different dimensions: e.g., Real Prices, Nominal Prices, Rate of Increase, ratio with income.
§171	House Prices relative to incomes:
§172	Same comments as Real House Price: suggest loading at 2014 onwards.
§173	This is not as clear as I might want, e.g., we should carefull assess the ORDER in which we include the plots, locating the most useful to a broad audience at capturing the story at the top. In this case, I’d say “New Housing Prices in Canada”, “Detached House Prices over Time, by City”, “Home Prices vs. Income”, and “How many years of income a home costs” should be at the top. Given the large number of plots, we should consider if this page should be broken up into more than one page. And seek opportunities to combine into a dashboard like interface – perhaps having that as a landing of the page to tell the main story, and have a longer list of supporting plots that are of interest to fewer people but offer the necessary fulsome treatment of the topic.
§174	New Housing Prices in Canada
§175	Overall, I know the utility of indicies; however, I suspect we should be aware of most people’s greater interest in actual numbers and ensure those are easily seen and earlier. Indicies are needed and should be here, but they are a layer of abstraction.
§176	These are all types of homes? I imagine this would look differently for condos vs detached homes?
§177	Actual Home Prices by City and Type
§178	It’s critical we include an obvious title and text that say the date this data is current to.
§179	The Source text is cut off at the right side.
§180	Don’t bold the CREA permission text; we need to include it but drawing extra attention is unnecessary and distracting. In fact, remove this text from the description paragraph. Let’s simply add it to the earlier sentence in parentheses and to a chart line below the “Source” line text. It looks like this is already in the Source line but is cut off.
§181	The above comments about source text and CREA permission should also be applied to the next plot, “Detached House Prices Over Time, by City”
§182	Detached House Prices Over Time, by City
§183	Do we have the data to have a drop-down selection of housing type, e.g., detached, semi-detached, townhouse, condo?
§184	We regain some width if we simply said Toronto and Vancouver and Montreal. We could add to a caption the clarification that it is the area. If nothing else, please clarify why there’s a difference between Toronto and Vancouver (Greater) and Montreal (CMA)? Maybe all could be CMA, which is short?
§185	How Many Years of Income a Home Costs
§186	This is good. But what else can we do here. E.g., “typical home” vs. selecting variety of home types.
§187	Source text is cut off at the far right side
§188	Home Values by City
§189	Replace “ – a usable proxy” in the first sentence with something more casual/accessible, like “This gives us a reasonable approximation.”
§190	The map (also the census tract map) is a bit constrained in width because of the long colourbar title. Can we shorten this and split across two lines? E.g., “Median /n home value”
§191	The source text line is touching the bottom of the map; add a bit of space.
§192	The final paragraph of this section ahead of the map again raises the idea of having a few consolidated plots and maps somewhere central. E.g., To what extent can we have a single map that enables the user to select what is plotted?
§193	“Dwelling” is not as clear as “home”, but it also raises the question of whether we can map specific types of homes, especially to separate condos from detached homes and those homes that are in between (semis, townhomes).
§194	Affordability by City (home value / income)
§195	Similar to the previous map, its width is constrained by the colourbar title. Start a new line after “home value”, which is also nice for illustrating the division.
§196	Source text line is touching the bottom of the map; add a bit of space.
§197	Rent in Canada
§198	Let’s start the x-axis at 2014 at load to focus on recent data.
§199	On load, the x-limit is awkwardly a bit earlier than the most recent data. It needs to be at the maximum extent.
§200	Do we have the data to have actual typical rent numbers in a set of cities?
§201	Rental Vacancy Rate:
§202	should be located next to Rent in Canada plot.
§203	Let’s push a bit of x-axis room slightly ahead of the data. Right now it looks cut off early but it is actually at the end of the data run.
§204	I worry this is misleading because it is all of Canada. Is there a way to break it down to specific cities also?
§205	Household Debt
§206	It would be useful to mention that much of this debt is in the home mortgage, but note what other types of expenses are often here also.
§207	Latest Household Debt: Ranked
§208	Need to make more clear when the data was last updated. Perhaps a single sentence below the title / before the plot.
§209	The “Source…” text line is oddly pushed to the right side? Also worth giving a small bit more space down from the x-axis label.
§210	Borrowing Costs
§211	The source text line is overlapping with the x-axis range slider. Needs to be moved down a bit.
§212	I worry a bit about how the y-axis is permanently set to the very high rates in the 1980s-era. This pushes the scale so far that recent years’ variability doesn’t look very clear. Maybe additional plotly tools could help or we could take some other approach to enabling the y-axis scale to adjust. This is an issue for other plots, so we need a consistent strategy for the site. I tried using the “autoscale” when I set the x-axis slider to only the most recent 6 years, and it moved the x-axis also to the full dataset, so that tool doesn’t accomplish the y-axis scale issue solution.
§213	Concern: what is the “conventional 5-year mortgage rate” should be commented on further. There is variability of what banks offer, so we need to be clear what this dataset is and means.
§214	Borrowing costs onwards feel like they should be their own page
§215	Government Bond Yields by Term
§216	Shorten title by removing “by Term”
§217	Start a new sentence at “Use the dropdown…” to improve readability.
§218	Shorten text by removing “especially” in the parentheses. Remove the “while…” entirely.
§219	The right edge of the plot and drop down menu seem to be clipped.
§220	Source text line is touching the bottom of the plot; move down slightly for breathing room.
§222	/Income & Inequality
§223	Can we add distribution of income plots like the age plots, where the x-axis allow changing the year? This would allow people to see how the distribution of incomes (or potential wealth, depending on data availability) changes over time.
§224	Should we plot minimum wages over time, with real and inflation-adjusted choices in a drop down?
§225	At the start of the page text, remove “Aggregate growth… another.” Sentence. In general, each page should stand on its own. These linking sentences need to be removed.
§226	Let’s revise top text sentence to “These charts track incomes and wages, including inflation adjusted values”: I’d like us to show both, to help people better understand the implications of inflation-adjusted values. This is not widely appreciated.
§227	Median After-Tax Income in Canada
§228	It would be nice to have the choice between households and individuals. Is that possible to implement?
§229	It would be nice in many such cases to be able to select between nominal and inflation-adjusted (real) dollars .
§230	Source text line should be moved down a bit. Also, the “Latest year” is clipped after that; make that a new line.
§231	Median Household Income by City
§232	Like other maps, the title on the colourbar is compressing the width on the page. We should add a general rule that aims for a limited width on map colourbar titles, utilizing multiple lines and brief titles. In this case, three lines are needed, which is ok given the balance of needs here.
§233	Separating the metro area and census tract maps for loading makes sense, but I do wonder if we re-organize the content into more focused pages, whether we will be able to simply load the full resolution maps.
§234	Source text line is overlapping with the top of the map. Move it down a bit.
§235	Average Annual Wage (Real)
§236	Remove (Real) from the title and leave that type of clarification for the text below.
§237	Let’s only load Canada, the US, and OECD peer average initially. This will help clarity.
§238	What year is the reference for this plot’s “real” inflation-adjusted values?
§239	Latest Average Annual Wage Ranked:
§240	The Source text line is a bit too close to the x-axis label; move it down a bit. It’s also oddly situated to the right side?
§241	Real Household Disposable Income per Capita
§242	Initially load only Canada, US, and OECD average
§243	Growth in Disposable Income since 2007: Ranked
§244	Source text line is awkwardly located at the far right side; we need a new standard to apply across all of these bar ranking plots, e.g., either left or center would be fine, but never the right, which looks odd.
§245	Income Inequality
§246	Why is the data inconsistently available across countries? This is a fairly standard dataset? Australia barely has any data; if that’s true we shouldn’t both loading such limited datasets initially.
§247	2022 data isn’t recent enough to include the Ranked bar plot…
§248	Relative Poverty Rate
§249	Like previous plot, the data sparseness is a problem. At minimum, we should initially load only countries will full data, which appears to be Canada? What’s going on with the rest of them?
§250	Low-Income Rate in Canada
§251	This is a great example of an important strategic decision for discussion about how we create plots: should this be a line plot or a bar plot? What factors influence this choice and what are the advantages of each? I’ve seen quite a few others focus more on bar plots for similar topics.
§252	Food Insecurity
§253	It’s regrettable this timeseries is only starting in 2018.
§254	It feels like the plot should be more up to date than this? It cuts off awkwardly on the right and I don’t see a 2024 tick? In general we should be consistently ensuring a small extra space on the right limit of the plot range. This is often done, but not consistently.
§256	Government
§258	/Government Finances
§259	Is there provincial data for spending, budget balance, debt?
§260	Government Gross Debt:
§261	Needs to clarify for me and for the reader if this accounts for all levels of government? One of the key things we need to be cautious about is that federal debt for Canada is sometimes compared to federal debt in other countries that don’t have our type of provincial layer and thus we look better.
§262	Suggest not loading Sweden and the UK initially here for clarity.
§263	Latest Government Gross Debt: Ranked
§264	Can we combine the Gross and Net ranked plots to be selected from a drop down? I’m looking for opportunities for this type of comparison/flexibility so the pages aren’t so long.
§265	Government Revenue:
§266	Remove “How high it “should” be is a political choice, so this is shown without a favourable direction.” And all similar sentences across the site. This idea is true but should not be repeated in every corner of the site. I’d prefer it be left only discussed on the main landing page and About section.
§267	Government Interest Costs
§268	Initially let’s only load Canada, Australia, Germany, the US, and the OECD peer average to avoid the overlapping clutter.
§269	The ranked bar plot: what is the meaning of the negative % of GDP for some countries? The reader should probably have some text explaining that, e.g., in a very short paragraph after the Ranked bar plot.
§270	Defense Spending
§271	This could be its own sub-section, especially if we find other metrics to add, such as troops and reservist sizes.
§272	Reference line for NATO target: revise the text annotation to simply “NATO minimum target”; it’s already clear from the chart that it is 2%.
§273	Ranked bar plot: Perhaps we should limit the x-axis to 5% (keep a tick label) since that is the new NATO target under discussion. The Israeli spending is unusual and not really a useful benchmark. There can be a subtle annotation about it being off scale.
§276	/Government employment
§277	Recommend cutting: “Governments are large employers. This page asks a deceptively simple question — how many people work for government, and doing what — and answers it from the ground up: first across all levels of government, then drilling into the federal public service. “ and moving the “A companion page..” to the bottom of this intro section.
§278	Employment by Level of Government
§279	Add x-axis scale slider
§280	Would be useful to be able to see per capita as well as these absolute values.
§281	I am keen to see 2025 data added. The next plot has 2025 data?
§283	The Bureaucracy vs the Whole Public Sector
§284	Suggest shorter title, perhaps just “The Public Sector” since the text clarifies
§285	Again, would be useful to have x-axis scale slider
§286	Would be useful to be able to see per capita as well as these absolute values.
§287	The y-axis scale is handled differently here relative to the previous plot, e.g., this one says in the axes label “(thousands)” and in the previous plot, there’s no unit like that but in the tick labels it is “k”, which is the same thing done differently. A deliberate choice should be made about which is more format and be consistent across the plots. I believe the most common standard is to express the quantity scale in the axis title.
§288	The odd bar plot below this, without a title, has its “Source..” text line overlapping with the plot area bottom and the x-axis label; it should be moved down.
§289	Also in this plot’s mouse over text the units aren’t clear. E.g., for educational services it says “1,362” which the x-axis label clarifies is in thousands, but I don’t think we should rely on that for the hover text?
§290	Let’s remove this “How “the public sector” is defined here” box, since this point was made at the top of the page already.
§291	How Canada Compares
§292	This seems to introduce the new term “general government” and intend it means the same as public sector?
§293	Why are some countries missing most of the data here?
§294	Title needed before the ranking plot. And the source text for that ranking bar plot needs to be moved slightly downward to avoid crowding the plot.
§295	Inside the Federal Public Service
§296	Remove explanatory text of “Drag the slider to zoom to a period, and use the dropdown to switch between the total headcount and the number per 1,000 people — which has risen far less, because Canada’s population has grown quickly over the same years.”
§297	This is another good example of a chart that might be better served by a bar plot instead of a line, since it is an integer value of a single variable.
§298	Why isn’t there data before 2010?
§299	The right edge is cut off.
§300	There should be a bit of padding for the axis limits past the very end of the data (e.g., ¼ year), as is done elsewhere.
§302	Which Parts of the Public Service Grew
§303	The Source text is overlapping with the x-axis label and should be moved down.
§304	I suggest we try comparing to 2015 instead of 2025, since this gives a decade of time and it connects to a change in government.
§305	Don’t bold “immigration”
§306	I would be more interested in setting this over time, e.g., a stacked plot like the earlier level of government employment.
§308	Where Federal Public Servants Work
§309	Source text overlaps with the x-axis label; move it down.
§310	It is surprising to see the CRA is the largest federal employment department.
§311	The Changing Shape of the Workforce
§312	Rewrite title: this is really about Executive employment in the federal public service
§313	The plot seems to get clipped at the right edge, and also lacks the bit of a buffer (or maybe it cannot be seen – e.g., I don’t even see a 2025 tick label).
§314	It would have been also worth seeing the actual numbers.
§315	Another case where I wonder if the bar plot would be better than the line.
§316	Is the Treasury Board’s 2017 report about the “Demographic Snapshot of the Federal Public Service” the most updated source for this citation and information? That’s nearly a decade out of date by now.
§317	Who the Public Service Is
§318	Awkward title
§319	Cut “— a wave of eventual retirements”
§320	Aging and Tenure and Sex plots don’t seem to make use of the full page width? Explore a fix for that.
§321	Can we add an x-axis scale slider?
§322	Where they work plot text: revise to “The National Capital Region (Ottawa–Gatineau) is the single largest concentration of public servants, but most public servants work elsewhere around the country.” The source text is overlapping the x-axis label.
§323	Sex: should this be gender? Does the data go any earlier than 2010?
§325	/Federal spending
§326	Can we add a breakdown of international aid spending?
§327	Remove the text “As with the workforce, how much government should spend is a political question. The charts below describe the composition and trend without a favourable direction.” We need to scrub the site of this sort of defensive text. It’s everywhere!
§328	Remove the text “A recurring theme:” and use “…itself: it is…”
§329	Revenue and Spending Over Time
§330	Remove “Over Time” from the title, that’s obvious
§331	Shorten this text intro as much as possible to focus only on what is plotted. And keep the sentence for “The gap…” which is useful.
§332	Add x-axis scale slider.
§333	Consider for both plots here: Should we plot this as a bar plot? The difference in heights of the red and blue bar would be the deficit or surplus. Being able to use the legend to add/remove one of them gives a nice clear plot of only one of them.
§334	The “source” text line is overlapping with the legend in both of these plots.
§335	The Budget Balance, by Era
§336	Remove text “It is descriptive: the shading shows when governments changed, not a claim about cause.”
§337	Add x-axis scale slider
§338	No 2025 value with Prime Minister Mark Carney? Or is the right side clipped off again?
§339	What the Money is Spend On – by Type
§340	Can we get a bit more width here? E.g., change legend entry from “Compensation of employees” to “Salaries”
§341	X-axis scale slider
§342	The breakdown by standard object has a source line that is overlapping with the plot and x-axis label
§343	Which Departments the Money Flows Through
§344	The drop-down menu is overlapping awkwardly with the plotly tools: can this be avoided?
§345	The source text line is overlapping with the plot area and also is clipped on the left side.
§346	The names of the departments are sometimes so long that it seriously compresses the width of the plot. I suggest splitting the names across two lines?
§347	Add “top 10” department option to the drop down and make it the initial load.
§348	What government’s spend on – by Function”
§349	I’m not clear on “social protection” as a concept or term. Re-label with something more obvious.
§350	Source text line is overlapping bottom of chart and the x-axis label. Move down.
§352	Health
§353	/Health & Health Care
§354	Should these two be their own sub-sections? i.e., Health of Canadians and Health Care System. These can be related but are also their own stories. There is such a large amount of content here that it’s hard to navigate through all of it.
§355	Where Canada stands
§356	Odd extra space between the score card and the legend.
§357	Life Expectancy at Birth
§358	At initial load, only include Canada, Australia, Germany, US, and the OECD peer average
§359	Odd that the data ends in 2023? Re-check for recent data.
§360	Remove “(both sexes)” in text
§361	Suicide
§362	At load, only have Canada, UK, US, and OECD peer average
§363	Why data is out of date?
§364	Can we break this down at all by age? Or gender? This is something that has a strong gender and age component.
§365	Mental Health
§366	Looks like this is getting cut off at the right edge. This is a common problem across the site…
§367	Tobacco & Alcohol
§368	Remove “, around 12% of adults — less than half the heaviest-smoking European peers —” from the second sentence to make this a bit less run-on.
§369	Remove “(litres of pure alcohol per person aged 15+)” from the body text for flow.
§370	The “Substance” text is being cut off at the top; simply remove it entirely.
§371	At load, only include Canada, UK, US, and OECD peer average.
§372	Data is of 2022 in the source text but data stops in 2020? Verify there’s nothing more recent.
§373	Diabetes: add brief first sentence justifying why this is worth showing, i.e., a major health risk.
§374	Maternal Mortality: initially load only Canada, Germany, UK, US, and OECD peer average for easier viewing.
§375	Childhood Vaccination
§376	Remove the annotation text for the 95% line because it is making the plot hard to read. Keep the line; it is explained in the text above the chart.
§377	The y-axis scale is not ideal for recent years. It is as low as ~25% because of only Germany. This is a special case; let’s limit the y-axis to 50% as a middle ground. IT’s still going to be a bit challenging to see the structure when viewing 2010 onwards, since everyone is above 80%.
§378	Universal Health Coverage
§379	Verify no further updates to dataset
§380	Health System Capacity: maybe this should be its own sub-section? It should be quick to navigate to, given its importance and likely high interest for readers.
§381	What happened to the recent data? Australia only up to 2016?
§382	Regular Health Care Provider:
§383	I feel like tehre is structure under this plot that needs some investigation. There is a serious issue with doctor availability especially in Ontario right now. Seek more options for surfacing data that supports this issue.
§384	/Substance Use
§385	Remove from the intro text “— deaths, geography and a poisoned supply —”
§386	The Health & Health Care “Tobacco & Alcohol” sub-section should be brought into this page/section.
§387	With this addition, the page will need some minor re-organization. The first intro text dives immediately into opiods, when the page is more general. Opioids will have to become a sub-section with a heading to separate it from the first sub-section, which is more logically Tobacco and Alcohoo.
§388	Remove completely this defensive paragraph: “These charts are descriptive…. Foot of the page.”
§389	Scale of the Crisis
§390	Source line is cut off at the right; start a new line after “Data as of: 2025”
§391	Re-check the 2025 values are not yet available.
§392	A Geography of Risk
§393	Why is Nunavut not shown?
§394	Who is Dying
§395	Reword initial sentence to (1) be clear about the cause (from opioid abuse) and (2) soften a bit from “The dead”. Something like “Those most often dying from the opioid crisis are working aged men”. And drop the “though no age group is untouched”. That is already covered in the plot itself.
§396	A Poisoned, Volatile Supply
§397	Reword “And these are overwhelmingly accidental poisonings, not suicides.” To be something more like “This uncertainty in the composition of the drug being taken has led to accidental poisonings.”
§398	Beyond Deaths: Hospitalizations
§399	Reword title to be “Hospitalizations due to Opiods”
§400	Tobacco, Alcohol, and Cannabis, by Age
§401	With the page re-organization this will move up near the top.
§402	Revise opening two sentences, such as: “Most substance use is of legal substances: tobacco, alcohol, and cannabis. This chart shows the share of Canadians who report each, by age group. Use the Substance menu to switch between them.”
§403	About This Data
§404	Says it is released quarterly but the most recent data here is 2024?
§407	/Well-being
§408	Should we call it happiness?
§409	Or we could add charts from elsewhere, if other related metrics can be identified. Please explore other potential datasets and sources. We could move mental health here.
§410	Happiness Score
§411	At load, only include: Canada, Australia, US, and OECD peer average
§412	What Underlies the Score
§413	The source text is overlapping the legend; move it down to avoid this issue.
§415	Environment
§416	/Where People Live
§417	Remove the opening sentence entirely
§418	The final paragraph in italics is not good. Remove the defensive opening and closing lines about being descriptive and “and the maps carry no “good” or “bad” reading”. All such text must be removed.  However, this paragraph does introduce a concept we should consider deploying at the opening paragraphs of each major section: a sentence noting the key data sources for the section.
§419	Reword the opening paragraph:
§420	“Canada is an expansive country with a diverse physical geography. At 9.98 million km² it is the second-largest country on Earth, with the longest coastline of any nation and roughly a fifth of the world’s fresh water. However, most of that vastness is boreal forest, tundra, rock and ice. Most Canadians live in a narrow band within a few hundred kilometers of the southern border. The maps below describe that geography: where people are, what the land is made of, where the water is, and how fire and ice are changing.”
§421	Where Canadians Live
§422	Replace “zooms into” with “shows”
§423	I’m not satisfied by this figure alone. We need to explore other ways to visualize the population distribution across the geography. Investigate what others have done (not limited to Canada) and offer potential new maps or visualizations.
§424	/Ecozones & Land Cover
§425	The Land opening sentence has no period at the end.
§426	The lay of the land
§427	Note the title only capitalizes the first word. That works well. Across the site there are many titles that capitalize all words, including very minor words, which looks awkward. A standard policy should be implemented across the site for consistency.
§428	What each of these ecozones actually is and means is not given. That’s more of a textbook content that shouldn’t be reproduced here, but maybe we should give a link to definitions, e.g., NRCan if that’s appropriate.
§429	The source text line is a little too close to the plot; add a small distance.
§430	What the land is covered by
§431	When hovering over the city names, there is a hover text error
§432	“Built-up” is unclear. Can we replace with something about urban?
§433	/Elevation
§434	Initial sentence: remove “How high Canada is – “
§435	The shape of the land
§436	Right now this is a favourite of mine.
§437	Should we add markers for other interesting features, like the large ridge feature north of Toronto?
§438	How high is Canada?
§439	Revise title to be “Canadian elevation”
§440	The source text line is overlapping with the x-axis label and being cut off at the bottom.
§442	/Water
§443	A country of fresh water
§444	Title for colourbar should be split across two lines to limit its width and give the map the most width in the page as possible.
§445	The colourbar ticks are only a single tick in the middle. Revise scale of ticks (e.g., 10^3 factor) and add at least two more ticks.
§446	Source text line is touching the bottom of the map; give a bit more space.
§447	Where the water goes
§448	Revise opening sentence to be “Watersheds are natural boundaries shaping the country’s physical geography.”
§450	/Agriculture
§451	What is farmed where
§452	The hover text gives the breakdown horizontally, which is a bit awkward to fit and read
§453	How much of the land is cropland
§454	This might work better at the top
§455	Remove first sentence “The type of farming… is another”
§456	It’s concerning to see all of BC as one area; there are specific smaller regions of higher agricultural use that are not being shown here.
§457	/Protected areas
§458	Should this merge with Ecozones?
§459	How much of Canada is protected
§460	This map isn’t adding much value as a map: it could be a bar plot instead
§461	What would be valuable is actually mapping the protected areas: can this be done?
§462	Important: Can we map all federal and provincial parks? That would be great.
§464	/Today’s Climate
§465	How warm, how cold
§466	This works well enough
§467	Source text line needs to be moved slightly downward to avoid the bottom edge of the map
§468	I would like to see a more continuous representation of the typical temperatures, and ideally with a slider to move through the year. We could use some reanalysis datasets for this.
§469	How wet, how dry
§470	Change colourbar scale to cm to save width
§471	Similar to the temperature plot, it would be nice to – in addition – have a reanalysis version that is covering the full country for typical conditions across the year.
§472	/Climate Change
§473	A warming country
§474	Plot and source text line are cut off at the right side
§475	The North is warming fastest
§476	The source line is a bit too close the the bottom of the chart and also it is cut off at the left side.
§477	Long-run temperatures, city by city
§478	Let’s remove the linear trend lines. These trends are sensitive to what base years are used, opening up an unwelcome line of criticism for this specific project
§479	Remove all text in the first paragraph after “They are different products….” All the way to “period for that).”
§480	Remove text “So these are ~75-year records, against Toronto’s ~180.” Since this is not necessary.
§481	Warming by season
§482	What is missing is not the mean values, but the maximum temperatures. Investigate our ability to add this and whether it is useful information.
§483	Warming spirals: south vs Arctic
§484	The radial tick marks are overlapping with the January outer tick mark and also the lines make it impossible to read most of them. We need a solution to this, e.g., a small wedge for the radial markers that sits on top of the lines to enable visibility; maybe it’s mostly opaque but a bit transparent to allow slight visibility of the lines underneath.
§487	/Fire & Ice
§488	These are thematically and physically different: I suggest they become their own pages, for wildfires (not any fires… we have, for example, no volcanoes) and ice.
§489	Wildfire
§490	Verify 2025 data is not yet available
§491	Note at the bottom that these fires connect to air quality issues across the country, in particular PM2.5 and give a link to that section of the site.
§492	Permafrost
§493	Source text line is touching the bottom of the chart and is above the legend; it needs to be moved sufficiently down to avoid both.
§494	This might actually fit well combined with the ecozones page. Sea ice could move there too or into climate change, since the emphasis is on change over time.
§495	/Air Quality
§496	“All concentration measures here are population-weighted” is that actually true? A bit misleading potentially since the first plot is an index that has nothing to do with population weighting. Remove it from this text. It is already where it needs to be, in the “what Canadians breathe” section text.
§498	Emission of the main air pollutants
§499	Shorten the title to just that first part; let the plot show the second half of the point
§500	The chart seems to have some room on the right side to be a bit wider?
§501	What Canadians breath
§502	Shorten title to just the above point
§503	End the sentence “Fine particular matter…” at “not fallen”. And start a new sentence ~ “One of the largest current drivers of PM2.5 is wildfire smoke,”
§504	It really is unfortunate this dataset only goes to 2023. I was certain NAPS was more current than that?
§505	How Canada’s PM2.5 compares internationally
§506	Worth adding a sentence about the fact that occasionally news headlines claim Canadian PM2.5 is very high, but this is always short lived wildfire-related events.
§507	Why are the data before 2000 only every five years and very similar for all countries? There really isn’t much structure in the values?
§508	For initial load, don’t add the Norway and Finland
§509	The new challenge: wildfire smoke
§510	Why was the 2018’s relatively unremarkable area burned impacting PM2.5 exposure so much? A brief comment about this would be helpful.
§511	Ensure the link to a related plot is updated when that is re-organized.
§512	/Air Quality by City
§513	/Emissions & Energy
§514	Greenhouse Gase Emissions and the 2030 Target
§515	Political/policy targets will change over time. Let’s remove this target. We can comment simply on the fact that all recent governments have committed to GHG reductions but this has been challenging.
§516	We should add CO2 per GDP for emissions intensity: another way to measure the emission levels, alongside the CO2 per capita. It’s also worth adding to the text that a northern climate and long distances contribute to emissions intensity of our society.
§517	Low Carbon Electricity:
§518	The x-axis loads to ~1960 at the beginning but all the data beings in the mid 1980s?
§522	Education & Science
§523	/Education
§524	Undergraduate Tuition Over Time
§525	Remove “Over Time” from title
§526	Can we go further back than 2005? Only if so, add x-axis scale slider
§527	If all provinces are available, I suggest we add at least a few others and keep them muted on load, e.g., Alberta, Nova Scotia, Newfoundland.
§528	The y-axis bottom tick label for $0 is touching the first x-axis tick label for 2005. Suggest adding a small amount to the lower y-axis range to avoid this.
§529	Domestic vs. International Tuition
§530	Adjust the legend entries to avoid compressing the chart width, e.g., use two lines for each entry.
§531	Same y-axis bottom tick overlap as the previous plot.
§532	Undergraduate Tuition by Field of Study
§533	Shorten the very long names, e.g., “Business, management and public administration”  “Business and public admin”; “Visual and performing arts”; “Social and behavioural sciences, and legal studies”  “Social sciences”; “Mathematics, computer and information sciences”  “Math and computer sciences”; “Physical and life sciences and technologies”  “Physical & life sciences”
§534	The source text line needs a bit more space from the x-axis label.
§535	Can we add other related datasets, e.g., comparing tertiary educational attainment over time and vs. peer countries?
§536	Can we get one or two representative institutions’ tuitions to show over time? E.g., University of Toronto Arts & Science and Engineering would be representative.
§537	/Science
§538	Remove “— Canada and OECD peers” from opening line and the later “, comparing Canada with 17 OECD peers”. This is true for the entire site.
§539	Reword the opening sentence to be about the importance of research and knowledge in a modern economy and society.
§540	R&D expenditure
§541	Initially load only Canada, US, and OECD average
§542	Remote data note; this is a site-wide issue and the data here is up to 2025 for Canada and 2024 for most others.
§543	Researchers per 1,000 Employed
§544	It’s very surprising to see the favourable number relative to the US, Germany, Japan, and Switzerland – all genuine research and science powerhouses. Do a sanity check to see if this is misleading.
§545	Australia again has little data: this seems to be a consistent issue across OECD data.
§546	Remove the Note about educational attainment and PISA test scores: this feels like an internal note not something that should be public facing. We should discuss whether there is something we can show that is Canada only, if there is nothing to show for numeracy skills and literacy skills, which would be ideal to have in the Education section.
§547	Important: is there nothing we can show about government science funding over time? E.g., NSERC, SSHRC, CIHR grants? That would be high value.
§549	/Innovation
§550	Remove text from top paragraph that says: “This page is a starting point and will grow over time.”
§551	The link to the business investment overall Economy page doesn’t go to the index, which makes it awkwardly a list of files. Also, it would be preferable to be able to have a link directly to the specific plot of interest on that page.
§552	This page definitely needs more content. There have been decades of work examining the lack of innovation in Canada; there must be something else.
