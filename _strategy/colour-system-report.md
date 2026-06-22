# Colour-system report — categorical palettes for Canada Observatory

**Owner priority #2 (2026-06-18). This is a report for discussion — no implementation yet.**

The owner's brief: we have a set of colours for the comparison countries, but where do they come
from? Determine which lists need colour sets, research best practice (scientific visualization +
public communication), consider colours culturally associated with the top comparators
(Canada = red, US = blue), and propose a deliberate set.

---

## (a) Which lists actually need a colour set

| List | Count | Current source | State |
|---|---|---|---|
| **Comparison countries** | **18** (Canada + 17 OECD peers) | matplotlib **tab20**, hand-assigned in `config.py` (`COMPARATOR_COLORS` 5 + `PEER_EXTRA_COLORS` 11 + Canada red + 2 greys) | **The flagship list. Needs deliberate choice.** |
| **Provinces & territories** | **13** | fall through to `SERIES_PALETTE` (a Tableau-10-style set), **cycled by index — no fixed identity** | **The other hard list. Needs a system.** |
| The six thematic areas | 6 | brand `palette.md` (locked) | ✅ Solved (brand). Leave as-is. |
| Story groups (religion ~9, energy ~7, gov't levels/sectors, age 4) | ≤9 each | `RELIGION_HISTORY_COLORS`, `SERIES_PALETTE`, ad-hoc | ◑ Mostly fine (all under the ceiling); align opportunistically. |
| Map scales (income, density, diversity, religion) | continuous | Viridis / Cividis / YlOrRd (sequential, perceptually uniform, CVD-safe) | ✅ Sound — a *separate* best-practice axis from categorical. Leave as-is. |

**The structural fact that drives everything:** the two lists the owner cares about —
**countries (18) and provinces (13) — both exceed the number of colours a human can tell apart at
once.** That ceiling is ~8–12 (below). So "find 18 distinct country colours" is not a solvable
problem; the question is how to *manage* a list that's bigger than the ceiling. (The 6 areas and
the story groups are under the ceiling and are comparatively easy.)

---

## (b) Best practice

### Scientific-visualization lens
1. **Perceptual distinctness, not RGB spacing.** Categorical colours should be ~equidistant in a
   *perceptual* space (CIELAB / CAM02-UCS). Colours that look evenly spaced on a screen picker can
   be perceptually lopsided. Purpose-built qualitative palettes already do this.
2. **Colour-blindness is the binding constraint.** ~8% of men have red–green CVD
   (deuteran/protan). Categories must never be separable by red-vs-green *alone*. The canonical
   CVD-safe categorical palettes:
   - **Okabe–Ito (2008)** — 8 colours engineered to stay distinct under all CVD types. The de-facto
     standard for accessible categorical encoding.
   - **Paul Tol's** qualitative schemes (bright/muted/light) — CVD-safe, deliberately **capped at
     ≤9–10** because the authors won't claim distinctness beyond that.
   - **ColorBrewer** (Brewer) qualitative sets (Set2/Dark2/Paired) — many flagged colourblind-safe,
     also capped ~8–12.
3. **The hard ceiling: ~8–12 simultaneous categories.** Every authoritative source stops there.
   Beyond it, colours collide — worse for CVD viewers, at small sizes, and on thin lines. This is a
   *perceptual* limit, not a tooling one. **It is exactly why 18 countries and 13 provinces can't all
   be simultaneously legible**, and it validates two existing design choices: the
   grey-until-activated peer lines (only ~6 colours shown at once) and the legend-size / scroll
   guardrail.
4. **Make the focal series the most salient** by *more than hue*: highest chroma + distinct
   lightness + width + markers. (Canada-red, bold, with markers, already does this — keep it.)
5. **Respect the white background.** Pure yellow and very light tints fail contrast for thin lines
   on white — avoid them for *lines* (they're fine as area fills or map bins).

### Public-communication lens
1. **Cultural/semantic association lowers cognitive load** — red→Canada, blue→US are read
   instantly. But associations **collide** (a great many flags are red/white/blue) and several flag
   colours (yellow, black) are poor for lines on white. So association is a useful **anchor for the
   few focal entities, not a rule for all 18**.
2. **Consistency is a feature.** One country = one colour *everywhere* builds a learnable visual
   language. The site already commits to this; keep it.
3. **Brand harmony.** Today the chart palette (raw tab20) is a *separate* system from the CanObs
   brand palette (maroon / navy / lake blue / wheat / etc.). Aligning at least the focal colours to
   the brand makes the charts feel part of the site rather than a matplotlib default.
4. **Never colour-only.** Pair colour with direct labels / markers / order so the chart survives
   greyscale printing and CVD. (The scorecards and ranked bars already lean on position, not just
   hue — good.)

### The synthesis
Don't chase 18 distinct colours. Adopt a **two-tier system** (which the country charts already
approximate, and which provinces lack):

- **Tier 1 — a small, fixed, deliberately-chosen "identity" set** for the focal entities: Canada +
  the 5 named comparators; and the ~5–6 largest/most-relevant provinces. Chosen for *mutual
  distinctness + CVD-safety + brand harmony + (where free) association*.
- **Tier 2 — grey-until-activated** for the long tail, so only ~6 colours are ever shown at once —
  staying under the perceptual ceiling and inside the legend. Each tail entity still owns a fixed
  colour the instant it's activated (already true for countries via `PEER_EXTRA_COLORS`).

This keeps every view under the ceiling *by construction*, which no flat 18- or 13-colour palette
can do.

---

## (c) Colours associated with the comparators — how far it gets us

| Country | Flag / association | Usable for a line on white? |
|---|---|---|
| **Canada** | **red** | ✅ Anchor. (Brand maroon #800000 is too dark for a line → use a brighter Canada-red.) |
| **United States** | **blue** | ✅ Anchor. (Brand Deep Navy is the site's *chrome*; a medium blue reads better as data.) |
| United Kingdom | red + blue | ✗ both taken → fall back to a distinct hue (purple/teal). |
| Germany | black + red + gold | ✗ black harsh on white, red taken, gold low-contrast → distinct hue. |
| Australia | green + gold (sporting) | ◑ green clashes with a German green; **orange** (sun/outback) is a fair loose fit + distinct. |
| Sweden | blue + yellow | ✗ blue taken, yellow low-contrast → distinct earthy/teal hue. |

**Honest finding:** association cleanly fixes only **Canada-red and US-blue**. Past those, flag
colours either collide or are unusable on white. So the recommendation is: **anchor the two
unambiguous ones, then choose the rest for distinctness + brand harmony + CVD-safety, using loose
association only as a tie-breaker** (e.g. keep Australia = orange). Forcing weak flag matches would
trade legibility for a connection most readers wouldn't even make.

---

## (d) Proposal

### Countries — a CVD-safe focal set (Tier 1), brand-anchored
Base the 6 focal colours on **Okabe–Ito** (already CVD-safe and close to today's choices), adjusting
Canada/US to anchor on association and to harmonise with the brand:

| Entity | Proposed | Okabe–Ito / note |
|---|---|---|
| Canada | red `#D55E00`→`#d62728` family | vermillion; keep bold + markers |
| United States | blue `#0072B2` | blue |
| Australia | orange `#E69F00` | orange (sun/outback tie-breaker) |
| Germany | bluish-green `#009E73` | distinct from US blue + AUS orange |
| United Kingdom | reddish-purple `#CC79A7` | distinct; "not flag-literal but clear" |
| Sweden | sky-blue `#56B4E9` | distinct from US blue by lightness |

(These are *near* the current set — the change is making them a **deliberate, documented, CVD-tested
focal palette** rather than incidental tab20 members, and verifying the six survive CVD simulation
together.) The other 11 peers keep their fixed Tier-2 colours (`PEER_EXTRA_COLORS`), grey until
activated — that system stays.

### Provinces — give them the same two-tier system they currently lack
Today provinces just cycle `SERIES_PALETTE` by index, so the same province can be a different colour
on different charts. Fix that:
- Assign the **largest / most-frequently-charted provinces** (ON, QC, BC, AB, + the chart's
  highlighted one) **fixed identity colours** from a CVD-safe set (Tol-muted or Okabe–Ito), reused
  on every provincial chart.
- Smaller provinces/territories → grey-until-activated, mirroring the country pattern.
- Where a province palette and the country palette can share a brand-aligned base, do so for site
  coherence (but the two lists never appear on the same chart, so collisions don't matter).

### Leave alone
The **6 brand area colours**, the **map sequential scales**, and the **small story-group palettes**
(all already under the ceiling / on a sound separate axis).

### If we ever must show many at once
Add a non-colour channel — direct line-end labels, facet/small-multiples, or interaction (hover to
highlight). That's the only honest way past the ~8–12 ceiling; more hues won't do it.

---

## Suggested next step
If this framing is right, the implementation is small and contained: a documented focal-palette block
+ a province identity map in `config.py`, a CVD-simulation check on the focal six, and (optionally)
brand-aligning the anchor reds/blues. I'd bring back the exact hex set + CVD-simulation screenshots
for final approval before touching `config.py`. **Open questions for the owner:** (1) how tightly to
hug the brand palette vs. keep the established near-tab20 look; (2) which provinces get Tier-1
identity colours; (3) whether to keep Canada's current `#d62728` red or move to a brand-tied red.
