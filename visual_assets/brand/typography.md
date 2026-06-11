# Typography — decision framework and audit

Drafted 2026-06-11, mirroring the palette and silhouette processes: criteria
first, then an evidence-based assessment. Decision pending owner sign-off;
the incumbent remains the default until then.

## The incumbent (never deliberately chosen)

- **Site text: Lato** — inherited silently with the Bootswatch *flatly* theme,
  loaded from the Google Fonts CDN by the theme's CSS. Stack: Lato →
  system-ui fallbacks.
- **Charts: no font was ever set.** Plotly's default stack requests Open Sans,
  which the page never loads, so all ~140 charts actually render in the
  browser's **Verdana/Arial fallback**. The site's most important typography is
  an accident. Whatever family wins, fixing this inconsistency (set
  `layout.font` globally in `pipeline/charts.py`) is the real payoff.

## Criteria

Craft:
1. **Digits tabular BY DEFAULT** (decisive) — Plotly SVG text cannot enable
   OpenType features, so axis labels/tables align only if the font's default
   figures are equal-width. Measured from `hmtx`, not vendor claims.
2. **Small-size legibility** — x-height, open apertures, Il1/0O distinction at
   the 10–11 px chart sizes the site uses everywhere.
3. **Family range** — weights for UI (400/600/700); a width (condensed) axis is
   a genuine asset for dense chart labels; variable font = one small file.
4. **Self-hostable, OFL licence** — no CDN dependency (privacy for a civic
   site; the flatly theme currently pings Google's CDN), no cost, no breakage.

Purpose:
5. **Bilingual readiness** — full French diacritics incl. œ/Œ and guillemets;
   bonus for French-first design heritage (the FR build is on the roadmap).
6. **Authority register** — credible-institutional, not playful; suits "the
   stable, citable almanac".
7. **Distinctiveness vs ubiquity** — Lato/Open Sans read as "default web";
   a face that is excellent *and* less common carries more identity.
8. **Provenance/positioning** — as with the leaf: no false-flag signals.

## Audit (measured with fontTools, 2026-06-11)

| Family | tnum | Digits equal by default | x-height | wght axis | wdth axis | FR glyphs |
|---|---|---|---|---|---|---|
| Lato (incumbent) | yes | **yes** | 0.506 | static (400/700 files) | — | all |
| IBM Plex Sans | no | **yes** | 0.516 | 100–700 VF | **75–100** | all |
| Source Sans 3 | no | **yes** | 0.478 | 200–900 VF | — | all |
| Public Sans | yes | **NO (10 widths)** | 0.517 | 100–900 VF | — | all |
| Libre Franklin | no | **NO (9 widths)** | 0.530 | 100–900 VF | — | all |
| Radio-Canada | yes | **yes** | 0.515 | 300–700 VF | **75–100** | all |

**Eliminated: Public Sans and Libre Franklin** — proportional default digits
fail criterion 1 outright (and Public Sans carries a faint wrong-flag signal as
the US federal design-system face). Note the audit also cleared the incumbent:
Lato's digits are tabular by default, contrary to its reputation.

## Finalists

- **Radio-Canada — recommended.** Clears every craft criterion including the
  width axis; designed by Montréal type designers for Canada's bilingual public
  broadcaster, so French-first legibility is its founding brief — the only
  candidate whose *story* matches the site's mission the way the botanical leaf
  does. Distinctive without being showy; institutional register. The one caveat
  to accept consciously: a faint CBC/Radio-Canada association for media-savvy
  readers (it is a free OFL font used well beyond the broadcaster; laypeople
  will not register it).
- **IBM Plex Sans — runner-up.** The best pure engineering: superb small sizes,
  condensed axis, massive family. Register is "technical/corporate"; story is
  IBM's, not ours.
- **Source Sans 3 — safe third.** Excellent UI font, smallest x-height of the
  set, mild personality; chooses invisibility.
- **Lato — status quo, defensible.** Audited better than its reputation; its
  weaknesses are ubiquity (default-web flavour), no variable font, no condensed,
  and the theme's Google-CDN loading.

## Implementation plan (when the owner decides)

1. Self-host woff2 subsets under `visual_assets/brand/fonts/` (latin +
   latin-ext); preload; drop the theme's Google CDN import.
2. `custom.scss`: `$font-family-sans-serif` + navbar wordmark rules.
3. `pipeline/charts.py`: set the family in the global Plotly defaults so all
   ~140 charts match the page (this fixes the Verdana accident even if the
   answer is "keep Lato").
4. Re-render SVG lockups/social cards with the chosen face (then outline text
   in the masters).
5. Mono for code blocks stays the Quarto default; no serif planned.
