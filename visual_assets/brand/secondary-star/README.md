# Secondary mark — the 12-point observatory star

A **secondary** geometric mark for Canada Observatory, derived structurally from the
primary sugar-maple **leaf-cells** logo. It reads as a compass / observatory star with a
snowflake character. It is **not** a replacement for the leaf (the identity) or the seal
(the tiny mark) — it is a sibling that grows out of them.

**The connection — `star12-proof.svg` / `.png` (keep this).** The most important file
here: it overlays the star on the faded leaf and shows that the six **short** points sit
exactly on the leaf-cells' six skeleton rays, and the six **long** points bisect the gaps
(through the wedge centres). The star *is* the leaf's skeleton, generalised — not a
separate idea. It explains the whole system; use it as the hook anywhere the two marks are
shown together.

## Construction
Twelve points from one centre: 6 short points on the leaf's six (irregular) rays + 6 long
points bisecting the gaps. The slight irregularity carries the leaf's real geometry — it
is not a mechanical clock-face. The central hub was removed (points converge to a clean
centre). All files are `viewBox="0 0 100 100"`.

## The set & how to use each

### Use — filled, expressive (the leads)
- **`star12-leaf-navy.svg`** — white snowflake points + the six area colours on navy. The
  lead expressive mark.
- **`star12-leaf-light.svg`** — the same on off-white; navy appears once (its single long
  point), short points off-white-outlined slate.
- `star12-leaf-seal.svg` — the maroon-disc register sibling.

### Use — single colour, full outline (the workhorses)
The mono full outline in each brand colour. Dark inks are transparent (drop on any light
page); light inks carry a disc.
- **Light register:** `…-navy`, `-maroon`, `-lake`, `-boreal`, `-slate`, `-ochre`
  (deep-ochre = the light-safe gold), `-linkblue`.
- **On a disc:** `…-offwhite-on-navy`, `-wheat-on-navy`, `-gold-on-navy`, `-seal`
  (off-white on maroon).
- `star12-outline-cells.svg` — the lighter **outer-edge** colour option (12 chevrons, no
  inner structure).

### Keep — reference only (`reference-only/`, not for current use)
Liked and on file, but with no practical use identified yet:
- **`star12-fulloutline-cells.svg`** — white inner spikes + the six area colours on an
  off-white disc. Aesthetically the strongest version; kept for the record.
- `star12-fulloutline-cells-inner-bordergrey.svg` — the disc-free "faded white" variant.
- `star12-duo-*.svg` — two-tone (navy-gold is the softest; maroon-navy is bolder).

## Rules
1. **Secondary only.** Never the primary logo, the favicon, or the navbar mark — the leaf
   is the identity, the seal is the tiny mark. Two competing identifiers dilute.
2. **Display / secondary sizes only.** The line versions collapse below ~20px; use a
   disc/solid register if a small size is ever needed (the seal already owns the tiny slot).
3. **Line weight — the current weight is the MAX; never go larger.** The set is drawn at
   stroke-width **1.5** (in the 100-unit viewBox). A **lighter** option (≈1.2) is allowed
   for delicate / large-display use — regenerate from the study generators
   (`../../studies/snowflake-star/_gen*.py`, the `w=` / `WT` constant). Do **not** go heavier.
4. **Grounds.** Dark inks on light; light inks (off-white/wheat/gold) on a navy or maroon
   disc. The colour versions need a light/off-white ground (the dark points must read); the
   white-inner cells carries its own off-white disc so it reads on any page.
5. **Palette.** Locked 8-colour set only; gold → deep ochre for thin strokes on light.
6. **Not on the site yet.** Adopted into the brand kit as the secondary-mark set, but not
   placed on any page. See `studies/snowflake-star/STUDY.md` §13 for the full assessment and
   the proposed home (an About → "Our marks" page).

`secondary-star-overview.png` is the visual index of this folder. Full history, every
iteration, and the rejected directions live in `studies/snowflake-star/`.

## Future work
- **Leaf → star morph animation** (logged 2026-06-25). The derivation *is* the story —
  animating the leaf-cells dissolving into the 12-point star would be the hook for the
  About → "Our marks" page (and/or a small landing flourish). Morph filmstrips already
  exist in `studies/snowflake-star/` (`_gen3.py`, `morph-*.svg`); turn one into SMIL/CSS
  when that page is built.
