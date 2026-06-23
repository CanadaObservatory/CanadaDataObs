# Canada Observatory — Long-Term Planning / Parking Lot

Ideas worth doing but **parked** — blocked on an authoritative data source, an owner
decision, or a future milestone (e.g. the next census, a site launch). This is distinct
from the **active** near-term list in `remaining-work-plan-2026-06-21.md`; promote an item
from here into that plan once it is unblocked.

**Project data rules that gate these:** authoritative *primary* sources only (StatCan /
OECD / World Bank / OWID / Bank of Canada / official agencies — never Wikipedia or
third-party compilations, even as a cross-check); no hardcoded values that can't
auto-refresh; non-partisan, descriptive framing.

---

## Blocked on an authoritative source

### Provincial voter turnout (review §99) — on hold 2026-06-22
Add **provincial general-election** turnout alongside the existing **federal** series in
the Voting section (`population/citizenship.qmd`), ideally as a federal-vs-province
dropdown. Owner: an important civic story worth telling.

**Blocker:** there is **no single authoritative, refreshable source** for provincial
general-election turnout. Provincial elections are run by **10 separate agencies**
(Elections Ontario, Elections BC, Élections Québec, Elections Alberta, …) in inconsistent
and often PDF-only formats; pan-Canadian compilations that exist are third-party
(e.g. Wikipedia, CCSD) and so are off-limits under the authoritative-source rule. Building
it now would mean either fragile per-agency scrapers or hardcoded figures — both against
the project's data rules.

**Paths when revisited:**
1. **Manual per-province compilation** — a `fetch_crime.py`-style *annual* builder that
   hand-assembles each agency's official historical turnout table (elections are
   infrequent, so a once-a-year refresh is acceptable). Most faithful; bespoke and
   only as current as it is maintained.
2. **Interim / complement — federal turnout *by province*** — Elections Canada open data
   ("Turnout by Age, Gender and Province", GE38–GE45, 2004–) is clean and refreshable. It
   answers "which provinces vote most in *federal* elections", not provincial-election
   turnout, but is a sourceable geographic voting view in the meantime.

Federal turnout (Elections Canada, 1867–) + turnout by age are already live in the Voting
section, so the core of §99 is covered.

---

## See also (deferred items already tracked elsewhere)
- `remaining-work-plan-2026-06-21.md` — **Tier 5** (new data needing sourcing: government
  science funding / tri-council, tertiary attainment, PIAAC, representative-institution
  tuition, languages-over-time, doctor availability by province/age, suicide by age/sex,
  actual rent $ by city, international aid, reanalysis climate maps) and **Data-blocked**
  (productivity decomposition — OECD PDB outage; source-limited latest years).
- Project memory deferral notes: homeownership rate (revisit at 2026 Census tenure),
  top-income/wealth shares (WID), PISA, the Leiden Ranking science-output chart,
  the crime perception / "fear gap" survey layer, federal public service by occupational
  group, the pipelines map, UCASS faculty salaries (conflict-of-interest).
- `census-2026` refresh roadmap (memory) — re-run census-derived content per topic as the
  2026 Census releases through 2027.
