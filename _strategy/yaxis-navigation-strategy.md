# Y-axis navigation strategy

**Owner priority (2026-06-18): do this first.** Status: recommendation + prototype below.

## The problem

Several time-series open on a recent x-window but keep a **fixed y-range**, so when the
reader widens the window (rangeselector buttons, a rangeslider, or box-zoom) the y-scale
doesn't follow. Recent variation then looks flat against historical extremes:

- **Inflation** (CPI bars): the 2022 spike (~8%) and the early-1980s peak (~12%) dominate, so
  the last decade reads as a thin strip. Owner: *"a very important chart to polish"* — also
  wants an x-slider here.
- **Headline / core / food**: same — the spikes make the recent scale too tall. Owner suggested
  opening near −5/+12.
- **Borrowing costs** (mortgage/policy since 1980): the ~21% 1981 peak permanently compresses
  the recent range. Owner tried Plotly's **autoscale** after narrowing the x-slider and it
  *reset the x-axis too* — so the native tool doesn't solve this.
- **Bond yields**, and to a lesser extent any long peer line opened on a recent `initial_start`.

Native Plotly does **not** rescale y to the visible x-window, and its "Autoscale" modebar
button resets **both** axes. So the fix has to be ours.

## Options considered

| | Approach | Verdict |
|---|---|---|
| A | **Native Plotly** (`yaxis.autorange`, rangeslider's own y) | ✗ Doesn't track the x-window; "Autoscale" resets both axes. |
| B | **Static per-chart default ranges** (open inflation at −5/+12, etc.) | ◑ Good *baseline* — sets a sensible opening view — but doesn't adapt as the reader explores. Keep as a fallback. |
| C | **Custom "Rescale Y to view" modebar button** | ◑ No feedback-loop risk, but it's a manual extra click and most readers won't find it. |
| D | **JS `plotly_relayout` handler** — on any x-range change, rescale y to the data now visible | ✓ **Recommended.** Automatic, continuous (follows a slider drag), and exactly the behaviour the owner described. |

## Recommendation — D + B

A **site-wide include** (`_includes/yaxis-autoscale.html`) that mirrors the existing
`peer-legend-colours.html` pattern: resolve Plotly via `requirejs` (Quarto's AMD bundle leaves
`window.Plotly` undefined), bounded-poll for async-rendered charts, and wire each **opted-in**
chart once. On every x-range change it recomputes the y-extent of the data visible in the
current x-window and relayouts **only** `yaxis.range`. A busy-flag + an x-only event filter
prevent feedback loops; a `requestAnimationFrame` debounce keeps slider-drag smooth.

Charts opt in from the Python builder via `layout.meta` (free-form, ignored by Plotly):

```python
fig.update_layout(meta=dict(autoscaleY=True))
# or, with options:
fig.update_layout(meta=dict(autoscaleY=dict(include=[0, 3], padFrac=0.08, min=-5, max=12)))
#   include : y-values always kept in range (e.g. the 1–3% target band + zero baseline)
#   padFrac : fractional padding above/below the visible extent (default 0.08)
#   min/max : hard clamps the range never exceeds
```

Keep a **sensible static initial range** (option B) on each opted-in chart as the pre-JS
fallback (works if scripts are blocked); the handler also runs once on load so the opening y
already fits the opening x-window.

### Why `meta`, not a CSS class or auto-detection
`layout.meta` is Plotly's documented free-form field (survives JSON serialisation, untouched by
rendering) and matches the project's existing `meta.fixedColor` convention. Explicit opt-in is
safer than auto-applying to every chart with a rangeselector (some charts *want* a fixed scale —
indexed series, the vaccination 50–100 floor, etc.).

### Known gotchas (carried from the earlier CPI attempt)
- `window.Plotly` is undefined under Quarto's AMD bundle → resolve via `requirejs('plotly')`.
- The earlier note claimed rangeselector clicks don't fire `plotly_relayout`; in current Plotly
  they do (with `xaxis.range[0]`/`[1]`), and the handler accepts every key form
  (`xaxis.range`, `xaxis.range[0]`, `xaxis.range[1]`, `xaxis.autorange`). The on-load call covers
  any event that slips through.

## Rollout (after owner sign-off on the prototype)
1. **Inflation (CPI bars)** — add the x-rangeslider the owner asked for + `autoscaleY(include=[0,3])`.
2. **Headline / core / food** — `autoscaleY(include=[0,3])`.
3. **Borrowing costs**, **bond yields** — `autoscaleY()`.
4. **Peer line charts** opened on a recent `initial_start` (GDP, etc.) — opt in via the builder
   so widening the window keeps them legible. (Evaluate per chart; indexed-level charts excluded.)

Prototype lives on `economics/cost-of-living.qmd` (both inflation charts). Verify: click 20Y/All
and drag the slider → y refits the visible window with no clipping and no jitter.

## Verified (prototype, 2026-06-18)

In the rendered `_site` preview:
- **Dynamic rescale works.** CPI bars: y = `[-0.2, 3.2]` on the 1-year window (calm ~2%),
  `[-21, 24.8]` on full history (back to 1915; 21.6% peak). Headline/core/food: `[-3.3, 11.4]`
  on 2015→now, `[-1.2, 8.0]` narrowed to 2024→now.
- **Real rangeselector clicks fire it** — clicking "20Y" moved y from `[-0.2, 3.2]` to
  `[-1.7, 8.9]`. So the old "rangeselector clicks don't fire `plotly_relayout`" note no longer
  applies with the requirejs-resolved handler; no polling needed.
- **Opt-in respected** — the policy-rate chart on the same page (no `meta.autoscaleY`) is left
  alone.
- **Layout clean** — the new x-rangeslider on the CPI bar chart, and the source notes moved
  below it, clear the figure by ~90px (clip-detector: no clipping, no slider overlap).

Ready for owner sign-off, then roll out to borrowing costs / bond yields / recent-window peer
lines per the list above.
