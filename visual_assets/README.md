# Visual assets — Canada Observatory

Brand assets for the site. **SVGs are the masters; PNGs are derived exports.**
Internal working directory — nothing here is served directly until wired into
`_quarto.yml` / `custom.scss`.

## Structure

```
brand/                  ← the landed identity (stable set)
├── botanical/                  THE design — one display leaf + THE SEAL for tiny:
│                               leaf-botanical.svg (display cut, ≥~48px);
│                               leaf-botanical-cells.svg = THE default expressive mark
│                               (bisectors C=(50,44), maroon stem cell);
│                               leaf-botanical-strata.svg = the variety fill ("stability");
│                               monogram.svg = THE SEAL (maroon disc r47 +
│                               off-white LINE leaf sw5 @0.78 — the tiny mark,
│                               adopted 2026-06-11 after both small-cut rounds
│                               failed) + -reversed (off-white disc, maroon
│                               leaf) + -cells (off-white disc, cells-arc leaf);
│                               lockup-horizontal.svg + lockup-stacked.svg
│                               (seal over centered CANADA/OBSERVATORY) +
│                               lockup-stacked-cells.svg (cells-filled display
│                               leaf over the wordmark) + wordmark-canobs.svg
│                               (the O = the seal);
│                               solid/ = 8 palette colours × the DISPLAY cut
│                               (the 8 small-cut solids are retired →
│                               initial_drafts/superseded-small-cut/);
│                               outline/ = the display cut as STROKE only (added
│                               2026-06-11): maroon/navy/black/offwhite singles
│                               (sw 2.4) + leaf-outline-cells (the six palette
│                               colours mapped to outline ARCS — wedge-clipped
│                               strokes of one path, no path surgery; sw 2.6)
├── classic/                    RETIRED archive (2026-06-11 swap executed) — kept for
│                               history only; nothing references it
├── mark-northstar.svg          approved secondary motif (footer, About, map markers)
├── palette.md                  the locked palette — 8 colours + 2 utility tints (source of truth)
├── palette-sheet.svg / .png    the palette as a one-page infographic (swatches, tints,
│                               WCAG pairings, rules, area mapping) — regenerate after
│                               any palette change
├── typography.md               the font framework + audit. **Radio-Canada ADOPTED
│                               2026-06-11** — wired site-wide (custom.scss + the
│                               global Plotly template in pipeline/charts.py) and
│                               across all masters
├── fonts/                      self-hosted Radio-Canada variable woff2 (latin +
│                               latin-ext, roman + italic, ~176 KB total)
├── favicon/                    favicon.svg (THE SEAL, transparent corners) + 16/32 PNG,
│                               apple-touch.svg → 180/192/512 (FULL-BLEED maroon +
│                               off-white line leaf — iOS rounds its own corners).
│                               No .ico (no ImageMagick on this machine; SVG/PNG
│                               is fine for Quarto + modern browsers)
├── social/                     og-card 1200×630 (off-white + CELLS leaf — the default
│                               link-share card, wired into _quarto.yml) and
│                               og-card-strata (the variety variant);
│                               linkedin-banner 1584×396 (cells) + linkedin-banner-strata;
│                               github-social-preview 1280×640 (navy, wheat display cut)
│                               + github-social-preview-cells (off-white + CELLS — the
│                               multicoloured alternate),
│                               github-avatar 512 (full-bleed maroon + off-white
│                               LINE leaf — the seal register; survives GitHub's
│                               ~20px rendering),
│                               avatar-cells + avatar-strata (1024², off-white + navy
│                               ring — the light profile-photo pair; circle-safe;
│                               serve X / Instagram / Facebook alike),
│                               x-header 1500×500 (X/Twitter profile header — same size
│                               fits Bluesky + Mastodon; navy + wheat display cut)
│                               + x-header-cells (off-white + CELLS — the multicoloured
│                               alternate; every banner now has a cells option),
│                               facebook-cover 820×312 (cells; text inside the ~640px
│                               mobile-safe centre), instagram-card 1080×1080 (stacked
│                               lockup tile — profile grid / first post; IG itself has
│                               no banner, just the square profile photo);
│                               -line variants (2026-06-11): og-card-line +
│                               linkedin-banner-line (cells-arc OUTLINE leaf on
│                               off-white) and x-header-line +
│                               github-social-preview-line (off-white line leaf
│                               on navy) — the outline family as featured mark
└── motifs/                     banner-people / banner-environment (wave bands —
                                template for the other four areas),
                                divider-ranking.svg (the house motif: peer dots
                                grey, Canada maroon, deliberately mid-pack)

studies/                ← active explorations (promote winners into brand/):
                          cells-lines/ = cell-division variants of the botanical
                          cells design (r0=current…v4) + lines-alone diagnostics;
                          v2r = the refined anatomy version (lobe = cell, maroon
                          crown, sinus-threading boundaries);
                          ring-width/ = the −20% ring decision record (ADOPTED
                          2026-06-11 → 4.4 kit-wide);
                          underline-wheat/ = the Wheat-rule decision record
                          (ADOPTED 2026-06-11 → all 10 social cards);
                          outline/ = first outline exploration (PROMOTED
                          2026-06-11 → brand/botanical/outline/);
                          small-cut-v2/ = rebuilt-silhouette candidates A–D —
                          ALL REJECTED (owner 2026-06-11: "flying rodent" —
                          a dark solid wide-lobed leaf at tiny sizes reads bat;
                          don't re-attempt solid-silhouette tiny leaves);
                          tiny-mark/ = the v3 round that settled it:
                          **L2 line-leaf-in-disc seal ADOPTED (owner
                          2026-06-11: "L2 confirmed") → now brand/botanical/
                          monogram.svg + the whole tiny family**; L1 bare line
                          leaf + S1/S1b/S2 north-star options = the also-rans;
                          true 1x+2x board = the decision record

initial_drafts/         ← archive: ChatGPT/openart raster attempts (no alpha,
                          inconsistent marks), superseded SVG directions
                          (split-leaf bars, angular/soft leaves, mountain, stripes,
                          chartline, botanical monograms, the flag-true test set),
                          superseded-small-cut/ (leaf-botanical-small.svg + the
                          8 small-cut solids, retired by the seal 2026-06-11),
                          and the original 7-colour palette PDF (predates Prairie Gold)
```

## System rules

- **Which mark when:** see `brand/DESIGN-CRITERIA.md` incl. Addendum 2 —
  **the display-cut botanical is the identity at ≥~48px; THE SEAL (maroon disc +
  off-white line leaf) is the mark below that** (favicon, avatars, monogram,
  any future navbar mark). Both small-cut rounds were rejected (v1 "three
  spikes / Bart Simpson", v2 "flying rodent") — **never re-attempt a
  solid-silhouette tiny leaf**. The classic is retired (archive only).
  **Cells (bisectors, maroon stem cell) = the default expressive mark for
  site/products; strata = the variety fill** — its horizontal "stability"
  register has a place, owner-confirmed. Multi-colour fills never below ~96px.
  The seal never varies. No third leaf styles.
- **Solid-leaf utility set:** default maroon; reversed off-white; premium reversed
  = wheat gold on navy. **Never a bare bright-red leaf** (federal-party territory),
  never the 11-point flag leaf, never red-white-red panel compositions, never the
  Government of Canada FIP look. (The flag-leaf rule is owner-confirmed by
  experiment, 2026-06-11: a full flag-true test set was built and rejected — the
  flag leaf in the ring monogram instantly reads as the RCAF roundel / "Avro
  Arrow". Archived in initial_drafts/test-flag-leaf/; don't re-propose.)
- **Prairie gold never carries text** on light backgrounds; pair it with navy ink.
  Link-blue on off-white uses the darkened tint (see palette.md).
- **Ring weight = 4.4** on the 100-unit ring (−20%, owner 2026-06-11) wherever
  an open ring still appears (instagram-card, avatar-cells/strata, north-star
  contexts). The monogram family no longer uses a ring — the seal's disc is
  solid; its line-leaf stroke is sw 5 at leaf scale 0.78 (≈3.9/100 of the
  disc), heavy enough to hold ≥1px at 16px favicon size.
- **Card underline rule = Wheat #D9B36C** (owner 2026-06-11): softer than
  Prairie Gold on light cards, and on navy it harmonizes with the wheat leaf
  (while being brighter, 6.6:1 vs 4.9:1). Prairie Gold remains a FILL colour
  (cells/strata bands, solid gold leaves) — never the rule.
- **Outline family = display register ONLY** (≥~96px): strokes are 2.4–2.6 per
  100 units, so below ~48px they render under 1px and fade — standalone
  outlines never serve small/UI contexts (the SEAL covers those; its stroke is
  ~60% heavier and backed by the disc). leaf-outline-cells never sits on navy
  (its navy arc vanishes); use leaf-outline-offwhite there.
- **Chart colours are a separate system.** Canada-red `#d62728`, comparator
  colours, and peer grey are data ink (`pipeline/config.py`) — keep them out of
  chrome, and keep brand colours out of charts.
- **Motifs are chrome, never content:** nothing decorative may be mistakable for a
  real chart or carry valence (no rising-line ornaments). On chart-heavy pages the
  right motif count is usually zero.

## Regenerating exports

```bash
python3 visual_assets/build_brand.py   # PNGs (2x) + favicon ladder + outlined SVGs
```

- **PNG exports ship at 2× their nominal size** (e.g. og-card.png = 2400×1260)
  — supersampled for Retina crispness; every platform accepts oversized
  uploads and downscales.
- **`*-outlined.svg` distribution copies** sit beside each text-bearing master:
  text converted to vector paths (layout verified by pixel-diff against the
  live-text renders, <1% divergence = AA noise), so they display identically on
  machines without the font — use these when sharing SVGs outside the repo or
  expecting GitHub previews to look right. The live-text masters remain the
  editable sources.
- Masters with live text render via qlmanage, which uses installed system
  fonts — the Radio-Canada static instances must be in `~/Library/Fonts/`
  (`RadioCanada-{Regular,SemiBold,Bold}.ttf`; see typography.md for the
  fontTools instancing recipe).

## On-site wiring status (2026-06-11)

Done: favicon/OG/twitter-card in `_quarto.yml`; palette + Radio-Canada in
`custom.scss`; `build_brand.py` exporter + outlined distribution copies;
**landing hero** (cells leaf floated beside the intro, `.hero-leaf`); **footer**
(inline-SVG maroon NORTH STAR — the approved secondary motif). **The seal
family landed 2026-06-11** (favicon/apple-touch/avatar/monogram/lockups all
regenerated). A navbar mark remains **deliberately absent**: the small cut was
rejected there ("three spikes") and removed; the SEAL is the first viable
candidate to try beside the wordmark, but adding it is an owner call — the
992px no-clip/baseline-parity check applies (see CLAUDE.md).

## Next steps (not yet done)

1. Upload github-avatar.png + github-social-preview.png to the GitHub
   org/repo settings (MANUAL — github.com has no API for either). Unblocked:
   the avatar is now the seal-register full-bleed mark.
2. Area banner motifs: only People + Environment waves exist — build the other
   four before deploying section-page banners (motifs are chrome, never content).
3. French lockup variant ("Observatoire du Canada") when the FR build lands.
4. Optional, owner call: try the SEAL beside the navbar wordmark (the first
   tiny mark that might survive there; re-verify 992px baseline parity).
