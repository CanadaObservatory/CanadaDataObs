# chart-palette — Canada Observatory chart colour references

Focused summary of the **locked chart colour system** (2026-06-22).
Full rationale & journey: [`_strategy/colour-system-story.md`](../../../_strategy/colour-system-story.md).
Authoritative hex values: [`_strategy/colour-registers.json`](../../../_strategy/colour-registers.json).
Wired into [`pipeline/config.py`](../../../pipeline/config.py).

## Summary files (where we landed)

- **`country_colours_line_reference.*`** — the final 17-comparator palette (focal seven
  incl. Japan + 10 grey-until-activated peers) as lines, with the full hex legend.
  Matches `config.py`. Global normal-vision min ΔE 15.7.
- **`country_colours_line_reference_v0.*`** — the original matplotlib *tab20* defaults,
  kept for the before/after comparison (min ΔE 12.1; 12 of 17 too pale for lines).
- **`province_colours_line_reference.*`** — the final 13 provinces/territories: the
  **muted** (default lines), **deep** (moodier lines), and **pastel** (map fills)
  registers of one shared identity, as a line test with the full hex legend.
- **`canada_province_map.*`** — the province identities on the Canada map.

## `archive/`

The iteration history — province maps v1–v7, the early country swatch sheets
(`comparator_country_colours*`), the deep/muted/pastel register experiments
(`register_*`), the province line tests, and the white-vs-dark "paint-on-glass" demo.
Kept for the record; not part of the summary.
