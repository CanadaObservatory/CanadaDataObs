# Silhouette assessment criteria — classic smooth vs botanical

Decision framework for which leaf carries the identity. Drafted 2026-06-11;
scores cite the comparison boards built during the 2026-06-10/11 sessions.

## A. Design-craft criteria (standard mark practice)

1. **Scale legibility** — crisp and recognizable from 16px favicon to poster.
   The mark's most frequent appearances are its smallest (browser tab, GitHub
   avatar at ~20px, navbar).
2. **Reproduction robustness** — survives one-colour, reversed, grayscale, and
   coarse media (print, stamp, embroidery, low-DPI) without redrawing.
3. **Distinctiveness / ownability** — distance from the thousands of existing
   maple-leaf marks (government, parties, Air Canada, banks, beer). Could you
   pick ours out of a lineup? Could it be protected?
4. **Memorability of gestalt** — could someone sketch it after one glance? Simple
   silhouettes are recalled; detailed ones are merely recognized.
5. **Timelessness** — no stylistic tics that date it to a design era.
6. **System versatility** — composes well with the system's parts: the ring
   monogram, the strata/cells data fills, colour variants, the wordmark.
7. **Optical balance** — clean silhouette, sensible visual centre, no dead weight.

## B. Project-purpose criteria (Canada Observatory specifically)

8. **Authority register** — must read "credible institution," consistent with a
   site competing on stable, citable, comprehensive data (vs ephemeral data
   journalism). Playful or crafty registers are off-mission.
9. **Independence distance** — far from Government of Canada visual territory
   (FIP/insignia — validated empirically by the rejected flag-leaf test, which
   read as the RCAF roundel) AND from party marks. Non-partisan must be visible.
10. **Canada-recognition speed** — a first-time visitor, incl. international,
    should read "Canada" in under a second at whatever size they meet it.
11. **Digital-first weighting** — this brand lives on screens: favicon, social
    avatar, og-cards, chart attribution. Criteria 1–2 therefore carry extra
    weight; paper contexts are rare.
12. **Production simplicity** — one SVG master, scripted regeneration, easy
    handoff to a future designer.

## Scorecard

| # | Criterion | Classic smooth | Botanical | Evidence |
|---|---|---|---|---|
| 1 | Scale legibility | **Strong** | Weak below ~48px | 22px board renders: classic crisp, botanical teeth blur |
| 2 | Reproduction robustness | **Strong** | Partial | fine teeth at risk in coarse media |
| 3 | Distinctiveness | Partial — custom but in the familiar stylized family | **Strong** — most specific drawing, furthest from gov/party/corporate leaves | round-2/3 boards |
| 4 | Memorability | **Strong** — sketchable | Partial — recognizable, not reproducible | gestalt complexity |
| 5 | Timelessness | Strong | Strong | tie |
| 6 | System versatility | **Ring/monogram: strong**; fills at large size: partial | Ring: weak (blurs); **fills: strong** (teeth catch strata bands) | round-3/4 boards |
| 7 | Optical balance | **Strong** | Partial (wide, bottom-heavy at small sizes) | |
| 8 | Authority register | Strong — contemporary civic-data | Strong — heritage/almanac gravitas | tie, different flavours |
| 9 | Independence distance | Strong | **Strong+** (extra distance from all official marks) | flag-test boundary validated |
| 10 | Canada-recognition speed | **Strong** at all sizes | Strong at large, partial when small | |
| 11 | Digital-first weighting | **Favours classic** (favicon/avatar dominate impressions) | — | where the mark actually appears |
| 12 | Production simplicity | **Strong** (1 simple path) | Partial (complex path) | minor criterion |

## Verdict

**Classic smooth is the mark.** The criteria where botanical wins (3, 6-fills, 9+)
are *illustration* virtues; the criteria where classic wins (1, 2, 4, 6-ring, 10,
11) are *identity* virtues — and identity is decided at the sizes where the mark
is actually met (tabs, avatars, navbars). Decisive structural point: at small
sizes a botanical mark would need a simplified companion anyway — and that
companion *is* the classic. Botanical can't be primary even in principle.

**Botanical is demoted from "sibling" to "illustration asset"** — subordinate,
rule-bound:
- May appear only at ≥ ~150px rendered size (hero art, og-card/banner art,
  About-page illustration), and never as *the* identifier.
- Never in: monogram, favicon, avatar, lockups, navbar, chart attribution.
- The monogram (ring + classic leaf) is the single invariant identifier and
  never varies.

This ratifies the de-facto arrangement already wired into the site, but converts
it from habit to rule — and resolves the one open vulnerability (two leaves
diluting identity) by making one of them clearly the brand and the other clearly
art.

## Evidence: scale-evidence.png

`brand/scale-evidence.png` (2026-06-11) shows true rasterizations of both leaves
and both monograms at 64/48/32/24/16 px, plus nearest-neighbour magnifications of
the 16 px and 24 px renders. What it demonstrates: at 16 px the classic leaf keeps
a solid maroon mass with resolved lobes and a visible stem, while the botanical's
teeth fall below pixel size and anti-alias into pale fog — roughly half its
remaining ink is sub-pixel fringe, and the thin stem vanishes entirely. The same
comparison inside the ring is worse (the leaf area is 38% smaller there).
Secondary finding: the ring itself washes out at 16 px regardless of leaf — which
is why `favicon.svg` is the bare classic leaf, not the monogram.

## Addendum — owner re-weighting (2026-06-11, supersedes the verdict above)

On reviewing the scale evidence the owner re-read criterion 1 and re-weighted
criterion 3, and both moves are accepted:

1. **Crisp ≠ recognizable.** At 16 px the classic renders *solid* but reads as a
   generic star — its crispness was scored as if it were recognizability. At
   favicon sizes ALL maple marks degrade; the question is what survives, and what
   survives of the classic is not distinctly a maple leaf either.
2. **Distinctiveness is the point, not an illustration virtue.** The botanical's
   advantage — staying visibly different from every other maple-leaf mark — holds
   at every *legible* size, which is where identity is actually formed.

**Revised resolution: one leaf, two optical cuts** (the type-design model —
display vs text sizes), instead of two different leaves:

- `leaf-botanical.svg` — **display cut** (≥ ~48 px): the full drawing.
- `leaf-botanical-small.svg` — **small cut** (< ~48 px: favicon, avatar, in-ring
  monogram, navbar): same wide five-lobe gestalt and U sinuses, teeth removed,
  stem thickened, features sized to survive 1 px at 16. Pixel evidence: at 16 px
  it keeps a coherent wide leaf mass, both lateral wings at full strength, and a
  visible stem — no fog (vs the display cut) and no star read (vs the classic).
- **Classic smooth: retired** (archive on confirmation). The earlier "the
  simplified companion IS the classic" argument was wrong — a simplified
  *botanical* keeps the family identity; the classic was a different leaf.

Status: **executed 2026-06-11** — full kit rebuilt on the botanical (monogram +
reversed + cells variants, favicon family, avatar, lockups, og/linkedin cards
with the cells fill as default and strata kept as the variety variant, solid
matrix of 8 palette colours × both cuts). Classic family archived in
`brand/classic/`; nothing references it.

**Second correction (owner, 2026-06-11): scale legibility demoted from weighted
criterion to threshold check.** The 16 px case barely exists in practice:

- Where the mark actually renders: browser tab (16 *CSS* px — but on HiDPI
  displays, i.e. most modern devices, browsers rasterize 32–48 physical px, and
  our favicon is SVG-first so it renders at device resolution; true 16-physical
  is legacy 1× hardware); GitHub avatar (20 px in commit lines, 48+ elsewhere);
  social-feed avatars (~40–48 px); og-cards (~500 px leaf); page/About headers
  (large); chart attribution (text only, no mark at all).
- Frequency ≠ identity formation. Tabs are the most *frequent* impression but
  their job is findability — at that size the maroon colour and a leafish blob do
  all the work; lobe articulation contributes nothing. Identity is formed at
  ≥40 px (feeds) and ≥200 px (cards, headers), where the botanical is fully
  itself.
- Therefore: small-size rendering only needs to pass a floor (clearly a
  maroon-leaf mark, not broken). Both botanical cuts pass at 32 px; the small cut
  passes at 16. The two-cut system stays as zero-cost insurance for legacy 1×
  contexts, not as a decision driver — and with that, no criterion favours the
  classic at any weight.

## Cheap empirical checks (optional, owner-runnable)

- **Tab test:** pin the favicon among 10 busy tabs — find it in <2s?
- **Sketch test:** show someone the mark for 5s; ask them to draw it.
- **Squint test:** both marks at 24px at arm's length — which still says maple?
- **Lineup test:** place the mark among Air Canada / party / GC leaves — does it
  hold apart? (Classic passed informally; botanical passes trivially.)
