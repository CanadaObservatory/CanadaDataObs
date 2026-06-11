# Visual assets — Canada Observatory

Brand assets for the site. **SVGs are the masters; PNGs are derived exports.**
Internal working directory — nothing here is served directly until wired into
`_quarto.yml` / `custom.scss`.

## Structure

```
brand/                  ← the landed identity (stable set)
├── botanical/                  THE design — one leaf, two optical cuts:
│                               leaf-botanical.svg (display cut, ≥~48px),
│                               leaf-botanical-small.svg (small cut, <~48px);
│                               leaf-botanical-cells.svg = THE default expressive mark
│                               (bisectors C=(50,44), maroon stem cell);
│                               leaf-botanical-strata.svg = the variety fill ("stability");
│                               monogram.svg (ring + small cut, maroon) + -reversed
│                               (off-white ring + wheat, for dark bg) + -cells;
│                               lockup-horizontal.svg + lockup-stacked.svg +
│                               lockup-stacked-cells.svg (mark over centered
│                               CANADA/OBSERVATORY) + wordmark-canobs.svg;
│                               solid/ = 8 palette colours × both cuts (16 files)
├── classic/                    RETIRED archive (2026-06-11 swap executed) — kept for
│                               history only; nothing references it
├── mark-northstar.svg          approved secondary motif (footer, About, map markers)
├── palette.md                  the locked palette — 8 colours + 2 utility tints (source of truth)
├── palette-sheet.svg / .png    the palette as a one-page infographic (swatches, tints,
│                               WCAG pairings, rules, area mapping) — regenerate after
│                               any palette change
├── favicon/                    favicon.svg (bare botanical SMALL cut, maroon) + 16/32 PNG,
│                               apple-touch-icon (180) + icon-192/512 (navy bg, off-white
│                               ring, wheat small cut). No .ico (no ImageMagick on this
│                               machine; SVG/PNG is fine for Quarto + modern browsers)
├── social/                     og-card 1200×630 (off-white + CELLS leaf — the default
│                               link-share card, wired into _quarto.yml) and
│                               og-card-strata (the variety variant);
│                               linkedin-banner 1584×396 (cells) + linkedin-banner-strata;
│                               github-social-preview 1280×640 (navy, wheat display cut),
│                               github-avatar 512 (ring + wheat SMALL cut on navy —
│                               survives GitHub's ~20px rendering),
│                               avatar-cells + avatar-strata (1024², off-white + navy
│                               ring — the light profile-photo pair; circle-safe;
│                               serve X / Instagram / Facebook alike),
│                               x-header 1500×500 (X/Twitter profile header — same size
│                               fits Bluesky + Mastodon; navy + wheat display cut),
│                               facebook-cover 820×312 (cells; text inside the ~640px
│                               mobile-safe centre), instagram-card 1080×1080 (stacked
│                               lockup tile — profile grid / first post; IG itself has
│                               no banner, just the square profile photo)
└── motifs/                     banner-people / banner-environment (wave bands —
                                template for the other four areas),
                                divider-ranking.svg (the house motif: peer dots
                                grey, Canada maroon, deliberately mid-pack)

studies/                ← active explorations (promote winners into brand/):
                          cells-lines/ = cell-division variants of the botanical
                          cells design (r0=current…v4) + lines-alone diagnostics;
                          v2r = the refined anatomy version (lobe = cell, maroon
                          crown, sinus-threading boundaries)

initial_drafts/         ← archive: ChatGPT/openart raster attempts (no alpha,
                          inconsistent marks), superseded SVG directions
                          (split-leaf bars, angular/soft leaves, mountain, stripes,
                          chartline, botanical monograms, the flag-true test set),
                          and the original 7-colour palette PDF (predates Prairie Gold)
```

## System rules

- **Which silhouette when:** see `brand/DESIGN-CRITERIA.md` incl. the addendum —
  **the botanical is the identity at every size, via two optical cuts**: display
  cut ≥~48px; small cut below that (favicon, avatar, in-ring monogram, navbar).
  The classic is retired (archive only). **Cells (bisectors, maroon stem cell) =
  the default expressive mark for site/products; strata = the variety fill** —
  its horizontal "stability" register has a place, owner-confirmed. Multi-colour
  fills never below ~96px. The monogram never varies. No third leaf styles.
- **Solid-leaf utility set:** default maroon; reversed off-white; premium reversed
  = wheat gold on navy. **Never a bare bright-red leaf** (federal-party territory),
  never the 11-point flag leaf, never red-white-red panel compositions, never the
  Government of Canada FIP look. (The flag-leaf rule is owner-confirmed by
  experiment, 2026-06-11: a full flag-true test set was built and rejected — the
  flag leaf in the ring monogram instantly reads as the RCAF roundel / "Avro
  Arrow". Archived in initial_drafts/test-flag-leaf/; don't re-propose.)
- **Prairie gold never carries text** on light backgrounds; pair it with navy ink.
  Link-blue on off-white uses the darkened tint (see palette.md).
- **Chart colours are a separate system.** Canada-red `#d62728`, comparator
  colours, and peer grey are data ink (`pipeline/config.py`) — keep them out of
  chrome, and keep brand colours out of charts.
- **Motifs are chrome, never content:** nothing decorative may be mistakable for a
  real chart or carry valence (no rising-line ornaments). On chart-heavy pages the
  right motif count is usually zero.

## Regenerating exports

```bash
qlmanage -t -s 1024 -o /tmp brand/favicon/favicon.svg   # SVG → /tmp/favicon.svg.png
sips -z 32 32 /tmp/favicon.svg.png --out brand/favicon/favicon-32.png
```

## Next steps (not yet done)

1. Wire `favicon:`, `open-graph`/`twitter-card` + `image:` into `_quarto.yml`.
2. Palette → `custom.scss` (navbar navy, darkened-lake links, heading colours);
   re-verify the navbar's 39px no-clip slack at the 992px breakpoint after any change.
3. Upload github-avatar + social-preview to the GitHub org/repo settings.
4. Outline the lockup text (or confirm Lato webfont availability) for final masters.
5. A `build_brand.py` exporter to replace the manual qlmanage/sips steps.
6. French lockup variant ("Observatoire du Canada") when the FR build lands.
