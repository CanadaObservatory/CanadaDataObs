# Icon experiments — for consideration (2026-06-25)

Exploration only. **The live `brand/favicon/` is untouched.** Prompted by the owner adding
the site to an iPhone home screen (the web-app / apple-touch icon = maroon square + the
off-white line leaf) and asking to try a **thinner line** and a **cells** version, plus a
**favicon workup of the leaf outline**.

The leaf path is identical across favicon / apple-touch / the `outline/` family — the only
levers are **stroke weight** (favicon/app-icon = 5; outline family = 2.4) and **ground**.

## What's here
- `appicon-line-sw{5,4.2,3.5,2.4}.svg` — maroon square + line leaf at four weights (5 = current).
- `appicon-cells-offwhite.svg` — the cells leaf as the icon (off-white = the only ground
  where all six colours read; kept for possible future use). Maroon/navy dropped: each eats
  its same-colour segment.
- `favicon-seal-sw5.svg` (= current), `favicon-outline-disc-sw2.4.svg`,
  `favicon-outline-bare-maroon.svg`.
- `board_appicon.svg(.png)`, `board_favicon.svg(.png)` — the comparison boards.

## Findings
- **Context decides the weight.** A web-app/home-screen icon renders large (~120px+) and is
  **never** shown tiny, so a **thinner line reads as more refined** there with no downside —
  sw **4.2 / 3.5** are the sweet spot, and even **2.4 (the outline weight)** is clean. The
  current sw 5 is a touch heavy at that size. The browser-**tab favicon (16px)** is the
  opposite case: at 16px the thin outline fades to a ghost, so the **tab should stay bold
  (the seal, sw 5)** — that's exactly why the seal exists.
- **Cells icon only works on off-white.** On maroon (and on navy) the same-colour cell
  vanishes into the ground, leaving a gap. On **off-white all six colours read** and it's
  striking — but an off-white icon is a big departure from the recognizable maroon brand
  icon, so it's an *alternative/seasonal* option, not a like-for-like swap.
- **The bare outline leaf (no disc)** is lovely at 48–64px but vanishes at 16–32px — it
  needs a disc/solid ground for any small use (the documented strokes-fade-below-~48px rule).

## Decision (owner, 2026-06-25) — DONE
- **Web-app / apple-touch icon: thinned to sw 4** — applied to live
  `brand/favicon/apple-touch.svg` and re-exported `apple-touch-icon.png` / `icon-192.png` /
  `icon-512.png`. More refined; keeps the maroon-square recognizability.
- **Browser-tab favicon + 16/32 PNGs:** unchanged (the seal, sw 5) — thin doesn't survive 16px.
- **Cells icon:** maroon/navy **dropped** (each eats its same-colour segment). Only
  `appicon-cells-offwhite.svg` kept on file for possible future use — caveat (owner): at the
  small end the off-white skeleton can read as the leaf being *divided*, so it needs the right
  context if ever used.
