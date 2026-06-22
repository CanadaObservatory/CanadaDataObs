# DRAFT (for the future Education section): Making a clean map of Canada by province

*Working draft, written 2026-06-20 after we rebuilt the "How much of Canada is protected"
map. Plain-language tutorial aimed at a curious reader who wants to make their own
province-level map. Convert to a `.qmd` page when the Education section is ready.*

---

You see these maps everywhere: Canada split into its provinces and territories, each one
shaded by some number — a vote share, an unemployment rate, how much land is protected. They
look simple, and the good news is they *are* simple to make. The only trick is knowing where to
get the map and avoiding one classic trap. Here's the whole recipe.

## 1. Get the map (the easy way)

You need a file that describes the *shape* of each province and territory. The instinct is to go
to the official government source — Statistics Canada publishes exactly this. **Resist that
instinct for a first map.** The StatCan boundary files are authoritative but huge (one is
133 MB) and come in two flavours that trip people up (see the trap below).

For a clean national map, use **[Natural Earth](https://www.naturalearthdata.com/)** instead.
It's a free, public-domain map dataset maintained by cartographers, it's *generalized* (smooth
coastlines, not every tiny fjord), and the whole world's provinces are a 2 MB download. It is
what most newsroom tools quietly use under the hood.

The file you want is **`ne_50m_admin_1_states_provinces`** (the "1:50 million" scale — detailed
enough to recognize Vancouver Island and Newfoundland, smooth enough to look clean). You can
load it straight from the web:

```python
import geopandas as gpd

url = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
       "master/geojson/ne_50m_admin_1_states_provinces.geojson")
provinces = gpd.read_file(url)
canada = provinces[provinces["iso_a2"] == "CA"][["name", "postal", "geometry"]]
```

`canada` now has 13 rows — one per province/territory — each with a name, a two-letter `postal`
code (BC, AB, ON…), and its shape. The Arctic islands, Newfoundland, and Vancouver Island are all
there as real islands.

## 2. Bring your numbers

Your data just needs one value per province, with a column you can match on. The `postal` code is
the easiest key:

```python
import pandas as pd

# whatever you're mapping — here, a made-up "score" per province
data = pd.DataFrame({
    "postal": ["NL","PE","NS","NB","QC","ON","MB","SK","AB","BC","YT","NT","NU"],
    "score":  [ 7,   5,  14,  10,  17,  11,  11,  10,  16,  20,  21,  16,  10],
})
canada = canada.merge(data, on="postal")
```

## 3. Draw it

A clean choropleth — no road map underneath, crisp borders — is a few lines with Plotly:

```python
import json
import plotly.graph_objects as go

gj = json.loads(canada.to_json())   # geopandas writes each feature's id = the row index

fig = go.Figure(go.Choropleth(
    geojson=gj, featureidkey="id",
    locations=canada.index, z=canada["score"],
    colorscale="Greens",
    marker_line_color="white", marker_line_width=0.6,   # thin white borders
))
fig.update_geos(
    visible=False, fitbounds="locations",     # no base map; zoom to Canada
    projection_type="albers",                 # the standard, area-honest Canada look
    projection_parallels=[49, 77], projection_rotation=dict(lon=-96),
)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="white")
fig.show()
```

That's it — a clean Canada choropleth. A few optional touches: a colour bar title, a one-line
source note, and value labels printed on each province (place them at each shape's centroid; for
the tiny Atlantic provinces, nudge the labels into the surrounding water so they don't collide).

## The one trap worth knowing about

If you *do* use the Statistics Canada files, know that they come in two versions, and the
difference is the whole ballgame:

- **Digital Boundary Files** draw each province to its *legal* limit — which runs **out into the
  ocean**. On a map that means Nunavut and the Northwest Territories become solid triangles
  reaching the North Pole, Hudson Bay and the Great Lakes are filled in as land, and the islands
  fuse to the mainland. (This is the version we used by mistake the first time, and the map looked
  wrong in exactly that way.)
- **Cartographic Boundary Files** clip the same boundaries **to the coastline**, so islands are
  islands and bays are water — what you actually want for a map.

Natural Earth sidesteps this entirely (it's coastline-based to begin with), which is one more
reason it's the better starting point. The rule of thumb: for a *map*, you want coastline-clipped
("cartographic") boundaries; the full administrative ("digital") extent is for legal/area work, not
for a picture people will recognize.

## Why Albers?

`projection_type="albers"` is an *equal-area* projection: it keeps each province's relative size
honest, so a choropleth (which is all about comparing areas of colour) isn't lying to the eye.
It's also just the shape Canadians are used to seeing. Web-Mercator (the Google-Maps look) badly
inflates the North, so avoid it for national maps.

---

*That's the whole thing: a free generalized map from Natural Earth, your numbers keyed by province
code, and a dozen lines of Plotly. No GIS degree required.*
