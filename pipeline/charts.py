"""
Reusable Plotly chart-building functions for DataCan.
Enforces consistent styling across all topics.
"""

import plotly.graph_objects as go
from pipeline.config import (
    CANADA_COLOR, PEER_COLOR, OECD_AVG_COLOR,
    HIGHLIGHT_WIDTH, PEER_WIDTH, HIGHLIGHT_COUNTRY,
    PEER_COUNTRIES, COMPARATOR_COLORS, SNAPSHOT_SPECS, DATA_DATE, get_data_date,
)


def _base_layout(title, yaxis_title, xaxis_title="Year", range_slider=True,
                  has_legend=True, data_date=None):
    """Standard layout for all DataCan charts."""
    xaxis_config = dict(title=xaxis_title, gridcolor="#e0e0e0")
    if range_slider:
        xaxis_config["rangeselector"] = dict(
            buttons=[
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=2, label="2Y", step="year", stepmode="backward"),
                dict(count=5, label="5Y", step="year", stepmode="backward"),
                dict(count=10, label="10Y", step="year", stepmode="backward"),
                dict(count=20, label="20Y", step="year", stepmode="backward"),
                dict(step="all", label="All"),
            ],
            x=0, xanchor="left", y=1.01,
        )

    # Spacing depends on whether there's a legend below the chart
    if has_legend:
        legend_y = -0.08
        legend_yanchor = "top"
        source_y = -0.52
        bottom_margin = 200
    else:
        legend_y = -0.2
        legend_yanchor = "bottom"
        source_y = -0.2
        bottom_margin = 80

    return go.Layout(
        xaxis=xaxis_config,
        yaxis=dict(title=yaxis_title, gridcolor="#e0e0e0"),
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor=legend_yanchor,
            y=legend_y,
            xanchor="center",
            x=0.5,
            itemclick="toggle",
            itemdoubleclick="toggleothers",
        ),
        margin=dict(b=bottom_margin, t=40),
        annotations=[
            dict(
                text=f"Data as of: {data_date or DATA_DATE}",
                xref="paper", yref="paper",
                x=1, y=source_y,
                showarrow=False,
                font=dict(size=10, color="#999"),
            )
        ],
    )


def peer_comparison_line(df, x_col, y_col, title, yaxis_title,
                         country_col="country_code", name_col="country_name",
                         highlight=None, show_average=False,
                         avg_name="OECD peer average"):
    """
    Line chart comparing Canada against OECD peers.
    Canada is highlighted in red; peers are grey; legend toggles on/off.

    Parameters
    ----------
    df : DataFrame with columns for country, x-axis, and y-axis values
    x_col : column name for x-axis (typically 'year')
    y_col : column name for y-axis values
    title : chart title
    yaxis_title : y-axis label
    country_col : column with country codes
    name_col : column with country display names
    highlight : list of country codes to highlight (default: just Canada)
    show_average : if True, add a dashed blue peer-average line
    avg_name : legend label for the average line
    """
    if highlight is None:
        highlight = [HIGHLIGHT_COUNTRY]

    def _name(code):
        s = df[df[country_col] == code]
        return s[name_col].iloc[0] if (name_col in df.columns and not s.empty) else code

    codes = list(df[country_col].unique())
    comparators = sorted([c for c in codes
                          if c in COMPARATOR_COLORS and c not in highlight], key=_name)
    others = sorted([c for c in codes
                     if c not in COMPARATOR_COLORS and c not in highlight], key=_name)

    fig = go.Figure()

    # 1) Non-highlighted peers: light grey, drawn behind; alphabetical in legend
    for i, code in enumerate(others):
        s = df[df[country_col] == code]
        name = _name(code)
        fig.add_trace(go.Scatter(
            x=s[x_col], y=s[y_col], name=name, mode="lines",
            line=dict(color=PEER_COLOR, width=PEER_WIDTH), opacity=0.8,
            legendrank=100 + i,
            hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>",
        ))

    # 2) Peer average (dark-grey dashed). Only for years where >= half the peer
    #    group reports, so the line reflects movement rather than changing coverage.
    if show_average:
        n_countries = df[country_col].nunique()
        counts = df.dropna(subset=[y_col]).groupby(x_col)[y_col].count()
        valid_years = counts[counts >= n_countries / 2].index
        avg = (df[df[x_col].isin(valid_years)]
               .groupby(x_col)[y_col].mean().reset_index())
        fig.add_trace(go.Scatter(
            x=avg[x_col], y=avg[y_col], name=avg_name, mode="lines",
            line=dict(color=OECD_AVG_COLOR, width=2, dash="dash"),
            legendrank=300,
            hovertemplate=f"{avg_name}: %{{y:.2f}}<extra></extra>",
        ))

    # 3) Named comparators: distinct colours, drawn above the grey cloud
    for i, code in enumerate(comparators):
        s = df[df[country_col] == code]
        name = _name(code)
        fig.add_trace(go.Scatter(
            x=s[x_col], y=s[y_col], name=name, mode="lines",
            line=dict(color=COMPARATOR_COLORS[code], width=2),
            legendrank=10 + i,
            hovertemplate=f"<b>{name}</b>: %{{y:.2f}}<extra></extra>",
        ))

    # 4) Highlighted country (Canada): red, bold, on top and first in legend
    for code in highlight:
        s = df[df[country_col] == code]
        if s.empty:
            continue
        name = _name(code)
        fig.add_trace(go.Scatter(
            x=s[x_col], y=s[y_col], name=name, mode="lines+markers",
            line=dict(color=CANADA_COLOR, width=HIGHLIGHT_WIDTH), marker=dict(size=5),
            legendrank=1,
            hovertemplate=f"<b>{name}: %{{y:.2f}}</b><extra></extra>",
        ))

    fig.update_layout(_base_layout(title, yaxis_title))
    return fig


def _latest_year_with_coverage(df, value_col, year_col="year", min_countries=10,
                               country_col="country_code", require_code=None):
    """Most recent year with at least `min_countries` reporting; else max year.

    Ranked bars look broken when the newest year only has a couple of countries
    reporting (common for OECD series with staggered releases). If `require_code`
    is given, only years where that country also reports are eligible — so the
    highlighted country (Canada) is never dropped from a ranked bar just because
    it reports a year or two behind its peers.
    """
    valid = df.dropna(subset=[value_col])
    counts = valid.groupby(year_col)[country_col].nunique()
    eligible = list(counts[counts >= min_countries].index)
    if require_code is not None:
        have = set(valid.loc[valid[country_col] == require_code, year_col])
        with_country = [y for y in eligible if y in have]
        if with_country:
            return int(max(with_country))
    if eligible:
        return int(max(eligible))
    return int(df[year_col].max())


def ranked_bar(df, value_col, xaxis_title, source_note,
               country_col="country_code", name_col="country_name",
               year_col="year", ascending=True, min_countries=10,
               tickformat=None, hover_template=None, height=600):
    """
    Horizontal ranked bar of the latest comparable year — Canada red, peers grey.

    Replaces the bar-chart block that was previously copy-pasted into every page.
    `source_note` is the full footer string (the caller builds it, typically
    f"Source: ... | Data as of: {get_data_date(path)}"); the chosen year is
    appended automatically.
    """
    year = _latest_year_with_coverage(df, value_col, year_col, min_countries,
                                      country_col=country_col,
                                      require_code=HIGHLIGHT_COUNTRY)
    latest = df[df[year_col] == year].dropna(subset=[value_col]).copy()
    latest = latest.sort_values(value_col, ascending=ascending)

    def _bar_color(c):
        if c == HIGHLIGHT_COUNTRY:
            return CANADA_COLOR
        return COMPARATOR_COLORS.get(c, PEER_COLOR)
    colors = [_bar_color(c) for c in latest[country_col]]
    names = latest[name_col] if name_col in latest.columns else latest[country_col]

    fig = go.Figure(go.Bar(
        x=latest[value_col],
        y=names,
        orientation="h",
        marker_color=colors,
        hovertemplate=hover_template or "%{y}: %{x}<extra></extra>",
    ))

    xaxis = dict(gridcolor="#e0e0e0", title=xaxis_title)
    if tickformat:
        xaxis["tickformat"] = tickformat

    fig.update_layout(
        xaxis=xaxis,
        yaxis=dict(title=""),
        plot_bgcolor="white",
        showlegend=False,
        height=height,
        margin=dict(t=30, b=60, l=10, r=20),
        annotations=[dict(
            text=f"{source_note} &nbsp;({year})",
            xref="paper", yref="paper", x=1, y=-0.09,
            showarrow=False, font=dict(size=10, color="#999"),
        )],
    )
    return fig


def ranking_strip(items, source_note=None, year_col="year",
                  country_col="country_code", name_col="country_name",
                  min_countries=8, height=None):
    """"Where Canada stands" snapshot — one row per indicator, every peer plotted
    as a dot positioned by its latest-year value (min–max normalised so all rows
    share a scale). Oriented as a scorecard: more favourable is always on the right
    (lower-is-better measures are flipped), rank 1 = best. Canada red, comparators
    coloured, others light grey; hover shows the real value and rank.

    `items`: list of (label, csv_path, value_col, fmt[, good]) where fmt is a Python
    format string ("${:,.0f}", "{:.1f}%") and good is "high" (default) or "low"
    to indicate which direction is more favourable.
    """
    import os
    import pandas as pd

    pts, labels = [], []
    rowmeta = {}        # display label -> dict(ca, rank, n, med) for the right column
    row_year = {}       # display label -> latest year used
    for item in items:
        label, path, value_col, fmt = item[0], item[1], item[2], item[3]
        good = item[4] if len(item) > 4 else "high"   # "high" or "low" is better
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        if value_col not in df.columns or country_col not in df.columns:
            continue
        year = _latest_year_with_coverage(df, value_col, year_col,
                                          min_countries=min_countries,
                                          country_col=country_col,
                                          require_code=HIGHLIGHT_COUNTRY)
        sub = df[df[year_col] == year].dropna(subset=[value_col]).copy()
        if sub.empty:
            continue
        # rank 1 = best (direction-aware); position by rank so spacing is even and
        # immune to outliers, and "more favourable" (rank 1) sits on the right.
        sub["_rank"] = sub[value_col].rank(ascending=(good == "low"), method="min").astype(int)
        n = len(sub)
        med_fmt = fmt.format(sub[value_col].median())
        labels.append(label)
        row_year[label] = int(year)
        ca = sub[sub[country_col] == HIGHLIGHT_COUNTRY]
        if not ca.empty:
            cr = ca.iloc[0]
            rowmeta[label] = dict(ca=fmt.format(cr[value_col]),
                                  rank=int(cr["_rank"]), n=n, med=med_fmt)
        for _, r in sub.iterrows():
            rank = int(r["_rank"])
            pos = (n - rank) / (n - 1) if n > 1 else 0.5
            pts.append(dict(
                label=label, x=pos, code=r[country_col],
                name=(r[name_col] if name_col in sub.columns else r[country_col]),
                val=fmt.format(r[value_col]), rank=rank, n=n, year=int(year),
                med=med_fmt,
            ))
    if not pts:
        return go.Figure()

    # Coverage flag: if a row's latest year lags the newest row, show it in the label
    newest = max(row_year.values())
    disp = {lab: (f"{lab} ({row_year[lab]})" if row_year[lab] != newest else lab)
            for lab in labels}
    for p in pts:
        p["dlabel"] = disp[p["label"]]
    dlabels = [disp[l] for l in labels]

    def _key(code):
        if code == HIGHLIGHT_COUNTRY:
            return "CAN"
        return code if code in COMPARATOR_COLORS else "_other"

    fig = go.Figure()

    def _add(key, color, size, legend, rank):
        sp = [p for p in pts if _key(p["code"]) == key]
        if not sp:
            return
        fig.add_trace(go.Scatter(
            x=[p["x"] for p in sp], y=[p["dlabel"] for p in sp],
            mode="markers", name=legend, legendrank=rank,
            marker=dict(color=color, size=size, line=dict(width=0.5, color="white")),
            customdata=[[p["name"], p["val"], p["rank"], p["n"], p["year"], p["med"]] for p in sp],
            hovertemplate="%{customdata[0]}: %{customdata[1]}  ·  rank "
                          "%{customdata[2]} of %{customdata[3]} (%{customdata[4]})"
                          "  ·  peer median %{customdata[5]}<extra></extra>",
        ))

    _add("_other", PEER_COLOR, 9, "Other peers", 999)
    for i, code in enumerate(sorted(COMPARATOR_COLORS, key=lambda c: PEER_COUNTRIES.get(c, c))):
        _add(code, COMPARATOR_COLORS[code], 11, PEER_COUNTRIES.get(code, code), 10 + i)
    _add("CAN", CANADA_COLOR, 15, "Canada", 1)

    # Always-on magnitude column on the right: Canada's value · rank · peer median.
    # Dots are positioned by rank (even spacing, outlier-immune), so this text is
    # what conveys actual magnitude and how far Canada sits from the peer middle.
    for lab in labels:
        m = rowmeta.get(lab)
        if not m:
            continue
        fig.add_annotation(
            xref="paper", yref="y", x=1.005, xanchor="left", y=disp[lab],
            text=f"<b>{m['ca']}</b> · {m['rank']}/{m['n']} · med {m['med']}",
            showarrow=False, font=dict(size=10, color="#444"), align="left")

    fig.update_layout(
        xaxis=dict(range=[-0.06, 1.06], showticklabels=False, showgrid=False,
                   zeroline=False, title="less favourable  →  more favourable"),
        yaxis=dict(categoryorder="array", categoryarray=dlabels[::-1],
                   showgrid=True, gridcolor="#eee", ticksuffix="  "),
        plot_bgcolor="white",
        height=height or (140 + 48 * len(labels)),
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5),
        margin=dict(l=10, r=165, t=20, b=120),
        hovermode="closest",
    )
    fig.add_annotation(text="Canada: value · rank · peer median →", xref="paper", yref="paper",
                       x=1.005, xanchor="left", y=1.0, yanchor="bottom",
                       showarrow=False, font=dict(size=9, color="#aaa"))
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper",
                           x=0, xanchor="left", y=-0.42, showarrow=False,
                           font=dict(size=9, color="#aaa"))
    return fig


def page_snapshot(section, **kwargs):
    """'Where Canada Stands' ranking strip for a page, from SNAPSHOT_SPECS."""
    return ranking_strip(SNAPSHOT_SPECS.get(section, []), **kwargs)


def choropleth_map(geojson, df, location_col, value_col, *, name_col=None,
                   colorbar_title="", colorscale="Viridis", reversescale=False,
                   value_prefix="", value_suffix="", value_fmt=",.0f", source_note=None,
                   center=None, zoom=2.6, height=640, zmin=None, zmax=None, log=False):
    """Zoomable choropleth map (Plotly Choroplethmapbox, free carto-positron
    basemap — no API token). The `geojson` features must carry a top-level `id`
    equal to df[location_col]. Used for the census-tract maps so users can pan/
    zoom to their own area. Pass `name_col` for a human-readable hover label.

    `log=True` colours on a base-10 log scale (for heavily skewed quantities like
    population density, where a few dense provinces would otherwise flatten the
    rest); the colourbar ticks are relabelled to the real values and zmin/zmax are
    ignored. The hover always shows the true (un-logged) value, read from
    customdata so the displayed number is identical whether or not log is set."""
    import math
    import numpy as np
    import pandas as pd
    center = center or {"lat": 58.0, "lon": -96.0}
    vals = pd.to_numeric(df[value_col], errors="coerce")
    base = df.copy()
    base["_v"] = vals.to_numpy()
    cols = ([name_col] if name_col else []) + ["_v"]
    customdata = base[cols].to_numpy()
    name_line = "<b>%{customdata[0]}</b><br>" if name_col else ""
    vidx = 1 if name_col else 0

    if log:
        z = np.where(vals.to_numpy() > 0, np.log10(vals.where(vals > 0).to_numpy()), np.nan)
        finite = [v for v in z if v == v]
        lo, hi = math.floor(min(finite)), math.ceil(max(finite))
        tickvals = list(range(lo, hi + 1))
        ticktext = [f"{10 ** t:,.0f}" if t >= 0 else f"{10 ** t:g}" for t in tickvals]
        colorbar = dict(title=colorbar_title, tickvals=tickvals, ticktext=ticktext,
                        tickprefix=value_prefix, ticksuffix=value_suffix)
        z_, zmin_, zmax_ = z, None, None
    else:
        colorbar = dict(title=colorbar_title, tickprefix=value_prefix, ticksuffix=value_suffix)
        z_, zmin_, zmax_ = vals, zmin, zmax

    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=df[location_col], z=z_,
        zmin=zmin_, zmax=zmax_,
        featureidkey="id", colorscale=colorscale, reversescale=reversescale,
        marker=dict(line=dict(width=0.2, color="rgba(255,255,255,0.4)"), opacity=0.82),
        colorbar=colorbar,
        customdata=customdata,
        hovertemplate=f"{name_line}{colorbar_title}: {value_prefix}%{{customdata[{vidx}]:{value_fmt}}}{value_suffix}<extra></extra>",
    ))
    fig.update_layout(
        mapbox_style="carto-positron", mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white",
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper",
                           x=0, xanchor="left", y=-0.04, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def choropleth_groups_map(geojson, df, location_col, groups, name_col, *,
                          colorscale="Cividis", source_note=None,
                          center=None, zoom=2.6, height=660, cap_quantiles=(0.0, 1.0),
                          opacity=0.82):
    """Choropleth with a dropdown to switch the mapped variable across `groups`
    (list of (column, label)). Used for the descriptive share maps (visible
    minority, religion, land cover); values are percentages and each option
    rescales its own colour range + colorbar.

    `cap_quantiles` = the (low, high) quantiles each group's colour range is clipped
    to. Default (0, 1) = the group's true min–max — correct for *share* layers where
    the high values are the subject (so Toronto's 57% visible-minority reads
    differently from Calgary's 39% instead of both clamping to the darkest colour).
    Pass a high quantile < 1 (e.g. (0, 0.98)) for the ~6,000-tract maps, where a few
    near-100% enclave tracts would otherwise stretch the scale and flatten the
    typical range. The default colour scale is **Cividis** — perceptually uniform and
    colourblind-safe, with no red/green valence — so wide spreads stay legible while
    these sensitive layers keep a neutral, descriptive reading."""
    center = center or {"lat": 56.0, "lon": -96.0}
    locs = df[location_col]
    custom = df[[name_col]].to_numpy()
    qlo, qhi = cap_quantiles

    def rng(col):
        return float(df[col].quantile(qlo)), float(df[col].quantile(qhi))

    c0, l0 = groups[0]
    lo0, hi0 = rng(c0)
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=locs, z=df[c0].tolist(), featureidkey="id",
        colorscale=colorscale, zmin=lo0, zmax=hi0,
        marker=dict(line=dict(width=0.2, color="rgba(255,255,255,0.4)"), opacity=opacity),
        colorbar=dict(title=f"% {l0}", ticksuffix="%"),
        customdata=custom,
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>{l0}: %{{z:.1f}}%<extra></extra>",
    ))
    buttons = []
    for col, label in groups:
        lo, hi = rng(col)
        buttons.append(dict(method="restyle", label=label, args=[{
            "z": [df[col].tolist()], "zmin": lo, "zmax": hi,
            "colorbar.title.text": f"% {label}",
            "hovertemplate": f"<b>%{{customdata[0]}}</b><br>{label}: %{{z:.1f}}%<extra></extra>",
        }]))
    fig.update_layout(
        mapbox_style="carto-positron", mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=46, b=36), height=height,
        updatemenus=[dict(buttons=buttons, active=0, x=0.01, y=0.99,
                          xanchor="left", yanchor="top", bgcolor="white",
                          bordercolor="#ccc", borderwidth=1, showactive=True)],
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0, xanchor="left",
                           y=-0.04, showarrow=False, font=dict(size=10, color="#999"))
    return fig


# Qualitative palette for categorical maps (ecozones etc.) — distinct, print-safe.
CATEGORICAL_PALETTE = [
    "#4e79a7", "#59a14f", "#9c755f", "#e15759", "#f28e2b", "#edc948",
    "#b07aa1", "#76b7b2", "#ff9da7", "#86bcb6", "#d37295", "#a0cbe8",
    "#8cd17d", "#b6992d", "#bab0ac",
]


def choropleth_categorical(geojson, df, location_col, cat_col, *, name_col=None,
                           color_map=None, ordered=None, source_note=None,
                           center=None, zoom=2.4, height=660, legend_title=None,
                           legend_orientation="v"):
    """Categorical choropleth — each polygon coloured by a *discrete* category
    rather than a continuous value (used for ecozones and permafrost zones).

    Plotly's Choroplethmapbox is value-based, so each category is mapped to an
    integer code laid over a hard-stepped discrete colourscale (value i sits in
    the middle of band i via zmin=-0.5/zmax=n-0.5); the colourbar is hidden and a
    real legend is drawn with invisible Scattermapbox proxies (one per category).
    Pass `ordered` to fix the legend order (and, for an ordinal ramp like the
    permafrost zones, the colour order); `color_map` to set exact colours, else
    CATEGORICAL_PALETTE is cycled. `geojson` features must carry a top-level `id`
    equal to df[location_col]; `name_col` adds a per-feature hover label."""
    center = center or {"lat": 62.0, "lon": -96.0}
    cats = list(ordered) if ordered else sorted(df[cat_col].dropna().unique())
    if color_map is None:
        color_map = {c: CATEGORICAL_PALETTE[i % len(CATEGORICAL_PALETTE)]
                     for i, c in enumerate(cats)}
    code = {c: i for i, c in enumerate(cats)}
    n = len(cats)
    colorscale = []
    for i, c in enumerate(cats):
        colorscale += [[i / n, color_map[c]], [(i + 1) / n, color_map[c]]]

    custom = (df[[name_col, cat_col]].to_numpy() if name_col else df[[cat_col]].to_numpy())
    name_line = "<b>%{customdata[0]}</b><br>" if name_col else ""
    cat_idx = 1 if name_col else 0
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=df[location_col],
        z=[code.get(v) for v in df[cat_col]],
        zmin=-0.5, zmax=n - 0.5, featureidkey="id",
        colorscale=colorscale, showscale=False,
        marker=dict(line=dict(width=0.3, color="rgba(255,255,255,0.5)"), opacity=0.85),
        customdata=custom,
        hovertemplate=f"{name_line}%{{customdata[{cat_idx}]}}<extra></extra>",
    ))
    # Choroplethmapbox shows no legend entry, so draw category swatches as
    # zero-point Scattermapbox proxies (nothing rendered on the map; legend only).
    for c in cats:
        fig.add_trace(go.Scattermapbox(
            lat=[None], lon=[None], mode="markers",
            marker=dict(size=12, color=color_map[c]), name=c, showlegend=True,
        ))
    legend = (dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01)
              if legend_orientation == "v"
              else dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5))
    if legend_title:
        legend["title"] = dict(text=legend_title)
    fig.update_layout(
        mapbox_style="carto-positron", mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white",
        legend=legend, showlegend=True,
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=-0.04, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


VM_GROUP_COLORS = {
    "All visible minorities": "#111111",   # headline (thick)
    "Not a visible minority": "#9e9e9e",
    "South Asian": "#1f77b4", "Chinese": "#d62728", "Black": "#2ca02c",
    "Filipino": "#9467bd", "Arab": "#ff7f0e", "Latin American": "#17becf",
}

RELIGION_HISTORY_COLORS = {
    "Christian": "#1f77b4", "No religion / secular": "#7f7f7f",
    "Muslim": "#2ca02c", "Hindu": "#ff7f0e", "Sikh": "#d62728",
    "Buddhist": "#9467bd", "Jewish": "#8c564b",
    "Traditional Indigenous spirituality": "#e377c2", "Other religions": "#17becf",
}


def history_lines(df, *, group_colors, hidden_groups=(), thick_group=None,
                  value_col="share", default_geo="Canada", source_note=None,
                  nhs_year=2011, nhs_label="2011: voluntary NHS", height=560,
                  yaxis_title="% of population", dropdown=True, measures=None):
    """Composition over census years, with a dropdown to switch the geography
    (Canada / a province / a city). Mirrors `choropleth_groups_map`'s dropdown idiom:
    one fixed line trace per group; each dropdown button `restyle`s every trace's y to
    the chosen geography's values (x — the census years — is shared, so only y changes).
    `df` is a tidy long frame (geography, geo_level, year, group, <value_col>).
    `group_colors` (dict group->colour) sets the legend order; `hidden_groups` start
    legend-hidden; `thick_group` is bold. A voluntary-NHS year is flagged, not hidden.
    `dropdown=False` plots `default_geo` only with no geography selector — used for the
    Canada long-run series, whose deep history exists for one geography only.
    `measures` (list of {label, col, fmt, suffix, ytitle}) adds a Show: selector that
    `update`s every trace's y + the y-axis title — e.g. share (%) vs absolute counts."""
    import pandas as pd
    df = df.copy()
    df["year"] = df["year"].astype(int)
    years = sorted(df["year"].unique())

    pref = list(group_colors.keys())
    present = set(df["group"])
    groups = [g for g in pref if g in present] + [g for g in df["group"].unique()
                                                  if g not in pref]

    order = {"national": 0, "province": 1, "cma": 2}
    geos = (df.drop_duplicates("geography")[["geography", "geo_level"]]
            .assign(o=lambda d: d["geo_level"].map(order))
            .sort_values(["o", "geography"])["geography"].tolist())
    if default_geo in geos:
        geos = [default_geo] + [g for g in geos if g != default_geo]

    def yvals(geo, group, col=value_col):
        s = (df[(df["geography"] == geo) & (df["group"] == group)]
             .drop_duplicates("year").set_index("year")[col])
        return [float(s.loc[y]) if y in s.index else None for y in years]

    init = measures[0] if measures else dict(col=value_col, fmt=".1f", suffix="%", ytitle=yaxis_title)
    def hover(g, m):           # per-group hovertemplate for a measure spec
        return f"{g}: %{{y:{m.get('fmt', '.1f')}}}{m.get('suffix', '')}<extra></extra>"

    fig = go.Figure()
    for g in groups:
        fig.add_trace(go.Scatter(
            x=years, y=yvals(default_geo, g, init["col"]), name=g, mode="lines+markers",
            visible=("legendonly" if g in hidden_groups else True),
            line=dict(color=group_colors.get(g, "#888"),
                      width=3 if g == thick_group else 1.8),
            marker=dict(size=6), hovertemplate=hover(g, init)))

    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=dict(title="Census year", gridcolor="#e0e0e0",
                   tickmode="array", tickvals=years),
        yaxis=dict(title=init.get("ytitle", yaxis_title), gridcolor="#e0e0e0", rangemode="tozero"),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=10, r=180, t=70 if (dropdown or measures) else 40, b=90),
    )
    if dropdown:
        buttons = [dict(method="restyle", label=geo,
                        args=[{"y": [yvals(geo, g) for g in groups]}]) for geo in geos]
        fig.update_layout(updatemenus=[dict(buttons=buttons, active=0, x=0.0, y=1.14,
                          xanchor="left", yanchor="top", bgcolor="white",
                          bordercolor="#ccc", borderwidth=1, showactive=True)])
        fig.add_annotation(text="Geography:", xref="paper", yref="paper",
                           x=0.0, y=1.20, xanchor="left", yanchor="bottom",
                           showarrow=False, font=dict(size=11, color="#666"))
    if measures:
        mbtns = [dict(method="update", label=m["label"], args=[
                     {"y": [yvals(default_geo, g, m["col"]) for g in groups],
                      "hovertemplate": [hover(g, m) for g in groups]},
                     {"yaxis.title.text": m.get("ytitle", yaxis_title)}]) for m in measures]
        fig.update_layout(updatemenus=[dict(buttons=mbtns, active=0, x=0.0, y=1.14,
                          xanchor="left", yanchor="top", bgcolor="white",
                          bordercolor="#ccc", borderwidth=1, showactive=True)])
        fig.add_annotation(text="Show:", xref="paper", yref="paper",
                           x=0.0, y=1.20, xanchor="left", yanchor="bottom",
                           showarrow=False, font=dict(size=11, color="#666"))
    if nhs_year in years:
        fig.add_vrect(x0=nhs_year - 0.25, x1=nhs_year + 0.25, line_width=0,
                      fillcolor="#000", opacity=0.05)
        fig.add_annotation(x=nhs_year, y=1.0, yref="paper", yanchor="bottom",
                           text=nhs_label, showarrow=False,
                           font=dict(size=9, color="#999"))
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper",
                           x=0, xanchor="left", y=-0.18, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def change_bars(df, *, group_colors, year_start, year_end, value_col="share",
                geography="Canada", geo_col="geography", source_note=None, height=460):
    """Diverging horizontal bars of each group's change in <value_col> between two years
    for one geography — the 'scale of change' view that quantifies what the long-run line
    chart shows. Bars are coloured by group (same palette as the lines), diverge around
    zero, and are sorted by signed change (largest decline at the bottom, largest gain at
    the top); each y-label carries the group's start→end values."""
    d = df[df[geo_col] == geography].copy()
    d["year"] = d["year"].astype(int)
    rows = []
    for g in group_colors:                       # palette order; skip groups absent in either year
        sub = d[d["group"] == g]
        s0, s1 = sub[sub["year"] == year_start][value_col], sub[sub["year"] == year_end][value_col]
        if len(s0) and len(s1):
            a, b = float(s0.iloc[0]), float(s1.iloc[0])
            rows.append((g, a, b, b - a))
    rows.sort(key=lambda r: r[3])                 # ascending → most-negative first (bottom)
    deltas = [round(r[3], 1) for r in rows]        # round for display (avoids float noise like 4.4799…)
    labels = [f"{g}<br>{a:.0f}% → {b:.0f}%" for g, a, b, _ in rows]
    fig = go.Figure(go.Bar(
        x=deltas, y=labels, orientation="h",
        marker_color=[group_colors.get(g, "#888") for g, *_ in rows],
        text=[f"{dl:+.1f} pp" for dl in deltas], textposition="auto",
        cliponaxis=False, hovertemplate="%{text}<extra></extra>"))
    pad = max(abs(min(deltas)), abs(max(deltas))) * 0.15
    fig.update_layout(
        plot_bgcolor="white", height=height, showlegend=False,
        xaxis=dict(title=f"Change in share, {year_start}→{year_end} (percentage points)",
                   gridcolor="#e0e0e0", zeroline=True, zerolinecolor="#888", zerolinewidth=1.5,
                   range=[min(deltas) - pad, max(deltas) + pad]),
        yaxis=dict(gridcolor="white"),
        margin=dict(l=160, r=40, t=20, b=70),
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0, xanchor="left",
                           y=-0.2, showarrow=False, font=dict(size=10, color="#999"))
    return fig


def composition_bars(df, *, group_colors, year, geographies=None, value_col="share",
                     geo_col="geography", source_note=None, height=520):
    """100%-stacked horizontal bars of composition by geography for one year — one bar per
    geography, a segment per group (same palette as the lines). Shows how the mix differs
    across places. `geographies` (ordered list) selects and orders the rows top-to-bottom."""
    import pandas as pd
    d = df[df["year"].astype(int) == year].copy()
    geos = geographies or sorted(d[geo_col].unique())
    d = d[d[geo_col].isin(geos)]
    groups = [g for g in group_colors if g in set(d["group"])]
    piv = d.pivot_table(index=geo_col, columns="group", values=value_col, aggfunc="first")
    fig = go.Figure()
    for g in groups:
        fig.add_trace(go.Bar(
            y=geos, orientation="h", name=g, marker_color=group_colors.get(g, "#888"),
            x=[float(piv.loc[geo, g]) if (geo in piv.index and g in piv.columns
               and pd.notna(piv.loc[geo, g])) else 0 for geo in geos],
            hovertemplate=f"{g}: %{{x:.1f}}%<extra></extra>"))
    fig.update_layout(
        barmode="stack", plot_bgcolor="white", height=height, hovermode="y unified",
        xaxis=dict(title=None, gridcolor="#e0e0e0", ticksuffix="%", range=[0, 100]),
        yaxis=dict(autorange="reversed"),         # first geography at top
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=110, r=20, t=70, b=70),
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0, xanchor="left",
                           y=-0.16, showarrow=False, font=dict(size=10, color="#999"))
    return fig


def time_series_multi(df, x_col, y_col, group_col, title, yaxis_title,
                      colors=None):
    """
    Multi-line time series chart (e.g., provinces, components).

    Parameters
    ----------
    df : DataFrame
    x_col : column for x-axis (date or year)
    y_col : column for y-axis values
    group_col : column to group lines by (e.g., province, component)
    title : chart title
    yaxis_title : y-axis label
    colors : optional dict mapping group values to colors
    """
    fig = go.Figure()

    default_colors = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
        "#aec7e8", "#ffbb78", "#98df8a", "#ff9896", "#c5b0d5",
    ]

    groups = df[group_col].unique()
    for i, group in enumerate(sorted(groups)):
        subset = df[df[group_col] == group]
        color = (colors or {}).get(group, default_colors[i % len(default_colors)])
        fig.add_trace(go.Scatter(
            x=subset[x_col],
            y=subset[y_col],
            name=str(group),
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=f"{group}: %{{y:,.0f}}<extra></extra>",
        ))

    fig.update_layout(_base_layout(title, yaxis_title))
    return fig


def single_line(df, x_col, y_col, title, yaxis_title, color=CANADA_COLOR,
                rangeslider=False, source_note=None, hovertemplate=None,
                yaxis_tickformat=None, customdata=None):
    """Single Canada-only time series.

    Set rangeslider=True for long series (more than a decade or two) to add a
    draggable time slider below the chart. Because these charts have no legend,
    the slider only has to coexist with the source note, which this function
    places below the slider (no overlap). Pass source_note to have it positioned
    correctly for the slider; pass hovertemplate / yaxis_tickformat as needed.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col], mode="lines",
        line=dict(color=color, width=HIGHLIGHT_WIDTH),
        customdata=customdata,
        hovertemplate=hovertemplate or "%{y:,.0f}<extra></extra>",
    ))
    xaxis = dict(
        title="", gridcolor="#e0e0e0",
        rangeselector=dict(buttons=[
            dict(count=1, label="1Y", step="year", stepmode="backward"),
            dict(count=5, label="5Y", step="year", stepmode="backward"),
            dict(count=10, label="10Y", step="year", stepmode="backward"),
            dict(count=20, label="20Y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ], x=0, xanchor="left", y=1.01),
    )
    if rangeslider:
        xaxis["rangeslider"] = dict(visible=True, thickness=0.10, bgcolor="#f5f5f5")
        # Open on the most recent ~25 years (from 1999, so the 2000 tick anchors
        # the view); the slider still spans all history and "All" resets it.
        import pandas as pd
        xmin, xmax = df[x_col].min(), df[x_col].max()
        xaxis["range"] = [max(xmin, pd.Timestamp("1999-01-01")), xmax]
    yaxis = dict(title=yaxis_title, gridcolor="#e0e0e0")
    if yaxis_tickformat:
        yaxis["tickformat"] = yaxis_tickformat
    fig.update_layout(
        xaxis=xaxis, yaxis=yaxis, plot_bgcolor="white",
        hovermode="x", showlegend=False,
        margin=dict(t=40, b=(140 if rangeslider else 80)),
    )
    if source_note:
        fig.add_annotation(
            text=source_note, xref="paper", yref="paper",
            x=0, y=(-0.34 if rangeslider else -0.18),
            showarrow=False, font=dict(size=10, color="#999"))
    return fig


# Neutral qualitative palette for non-country categorical series (government
# levels, public-sector sectors, spending categories) — distinct and print-safe,
# with no red/green valence (the Government section is descriptive, not a
# scorecard). Canada-red is reserved for the single highlighted series.
SERIES_PALETTE = [
    "#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#edc948",
    "#b07aa1", "#9c755f", "#ff9da7", "#86bcb6", "#bab0ac", "#d37295",
]


def _series_colors(groups, colors):
    if colors:
        return {g: colors.get(g, "#888") for g in groups}
    return {g: SERIES_PALETTE[i % len(SERIES_PALETTE)] for i, g in enumerate(groups)}


def lines_over_time(df, x_col, value_col, group_col, *, yaxis_title,
                    colors=None, group_order=None, source_note=None, height=460,
                    yaxis_tickformat=None, ytickprefix="", yticksuffix="",
                    hover_decimals=0, legend_orientation="v", rangemode="tozero"):
    """Plain multi-line time series for annual data — integer-year safe (no
    date-axis range buttons, unlike the OECD peer charts). `df` is long:
    (x_col, group_col, value_col). Used for government employment by level and
    federal revenue-vs-expenditure."""
    groups = group_order or list(df[group_col].drop_duplicates())
    cmap = _series_colors(groups, colors)
    fig = go.Figure()
    for g in groups:
        s = df[df[group_col] == g].sort_values(x_col)
        fig.add_trace(go.Scatter(
            x=s[x_col], y=s[value_col], name=str(g), mode="lines+markers",
            line=dict(color=cmap[g], width=2.5), marker=dict(size=5),
            hovertemplate=f"{g}: {ytickprefix}%{{y:,.{hover_decimals}f}}{yticksuffix}<extra></extra>"))
    legend = (dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
              if legend_orientation == "v"
              else dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5))
    yaxis = dict(title=yaxis_title, gridcolor="#e0e0e0", rangemode=rangemode,
                 tickprefix=ytickprefix, ticksuffix=yticksuffix)
    if yaxis_tickformat:
        yaxis["tickformat"] = yaxis_tickformat
    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=dict(title="", gridcolor="#e0e0e0"), yaxis=yaxis, legend=legend,
        margin=dict(l=10, r=(175 if legend_orientation == "v" else 20), t=30, b=80))
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=-0.18, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def single_line_multi(df, x_col, options, *, color=CANADA_COLOR, rangeslider=True,
                      source_note=None, height=None):
    """Single Canada-only series with a dropdown to switch among `options`
    (alternative y-columns on the same chart — e.g. an absolute total vs a
    per-capita view), plus the standard range buttons and an optional range
    slider. Each option is a dict: {col, label, yaxis_title, hovertemplate}. The
    dropdown toggles which series is shown and updates the y-axis title; the axis
    re-scales automatically to the visible series."""
    fig = go.Figure()
    for i, o in enumerate(options):
        fig.add_trace(go.Scatter(
            x=df[x_col], y=df[o["col"]], mode="lines", name=o["label"],
            line=dict(color=color, width=HIGHLIGHT_WIDTH), visible=(i == 0),
            hovertemplate=o.get("hovertemplate", "%{y}<extra></extra>")))
    buttons = [dict(method="update", label=o["label"],
                    args=[{"visible": [j == i for j in range(len(options))]},
                          {"yaxis.title.text": o["yaxis_title"]}])
               for i, o in enumerate(options)]
    xaxis = dict(title="", gridcolor="#e0e0e0", rangeselector=dict(buttons=[
        dict(count=1, label="1Y", step="year", stepmode="backward"),
        dict(count=5, label="5Y", step="year", stepmode="backward"),
        dict(count=10, label="10Y", step="year", stepmode="backward"),
        dict(step="all", label="All")], x=0, xanchor="left", y=1.01))
    if rangeslider:
        xaxis["rangeslider"] = dict(visible=True, thickness=0.10, bgcolor="#f5f5f5")
    fig.update_layout(
        xaxis=xaxis, yaxis=dict(title=options[0]["yaxis_title"], gridcolor="#e0e0e0"),
        plot_bgcolor="white", hovermode="x", showlegend=False, height=height,
        margin=dict(t=60, b=(140 if rangeslider else 80)),
        updatemenus=[dict(buttons=buttons, active=0, x=1, xanchor="right", y=1.13,
                          yanchor="top", bgcolor="white", bordercolor="#ccc",
                          borderwidth=1, showactive=True)])
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           y=(-0.34 if rangeslider else -0.18), showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def stacked_area(df, x_col, value_col, group_col, *, yaxis_title, colors=None,
                 group_order=None, source_note=None, height=480,
                 ytickprefix="", yticksuffix="", hover_decimals=0, value_scale=1.0,
                 legend_orientation="v"):
    """Stacked area over time — the composition of a total by category
    (public-sector sectors, federal expense by type, government spending by
    function). `df` is long: (x_col, group_col, value_col). `value_scale` divides
    values for display (e.g. 1000 to show $millions as $billions). Bands are
    ordered largest-total first unless `group_order` is given."""
    import pandas as pd
    d = df.copy()
    d["_v"] = pd.to_numeric(d[value_col], errors="coerce") / value_scale
    groups = group_order or list(
        d.groupby(group_col)["_v"].sum().sort_values(ascending=False).index)
    cmap = _series_colors(groups, colors)
    xs = sorted(d[x_col].unique())
    fig = go.Figure()
    for g in groups:
        s = d[d[group_col] == g].set_index(x_col)["_v"]
        fig.add_trace(go.Scatter(
            x=xs, y=[s.get(x) for x in xs], name=str(g), mode="lines",
            stackgroup="one", line=dict(width=0.5, color=cmap[g]), fillcolor=cmap[g],
            hovertemplate=f"{g}: {ytickprefix}%{{y:,.{hover_decimals}f}}{yticksuffix}<extra></extra>"))
    if legend_orientation == "h":   # legend below the plot → x-axis uses full width
        legend = dict(orientation="h", yanchor="top", y=-0.07, xanchor="left", x=0)
        margin = dict(l=10, r=20, t=30, b=130)
        src_y = -0.40
    else:                            # legend stacked on the right (default)
        legend = dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        margin = dict(l=10, r=200, t=30, b=80)
        src_y = -0.18
    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=dict(title="", gridcolor="#e0e0e0"),
        yaxis=dict(title=yaxis_title, gridcolor="#e0e0e0",
                   tickprefix=ytickprefix, ticksuffix=yticksuffix),
        legend=legend, margin=margin)
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=src_y, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def category_bar(df, label_col, value_col, *, xaxis_title, source_note=None,
                 color="#4e79a7", value_scale=1.0, value_fmt=",.0f",
                 tickprefix="", ticksuffix="", top_n=None, height=None,
                 hovertemplate=None, highlight=None, highlight_color=CANADA_COLOR,
                 text_col=None, text_fmt="{}"):
    """Horizontal ranked bar for non-country categories (departments, spending
    objects, public-sector sectors). Sorted descending with an optional `top_n`;
    single neutral colour by default, with an optional `highlight` set of labels
    to colour differently."""
    import pandas as pd
    d = df.copy()
    d["_v"] = pd.to_numeric(d[value_col], errors="coerce") / value_scale
    d = d.dropna(subset=["_v"]).sort_values("_v", ascending=False)
    if top_n:
        d = d.head(top_n)
    d = d.sort_values("_v")          # ascending → largest bar on top
    hl = set(highlight or [])
    colors = [highlight_color if str(l) in hl else color for l in d[label_col]]
    text = ([text_fmt.format(v) for v in d[text_col]]
            if text_col and text_col in d.columns else None)
    fig = go.Figure(go.Bar(
        x=d["_v"], y=d[label_col].astype(str), orientation="h", marker_color=colors,
        text=text, textposition="auto", cliponaxis=False,
        hovertemplate=hovertemplate or
        f"%{{y}}: {tickprefix}%{{x:{value_fmt}}}{ticksuffix}<extra></extra>"))
    fig.update_layout(
        plot_bgcolor="white", showlegend=False, height=height or (150 + 26 * len(d)),
        xaxis=dict(title=xaxis_title, gridcolor="#e0e0e0",
                   tickprefix=tickprefix, ticksuffix=ticksuffix),
        yaxis=dict(title=""), margin=dict(l=10, r=(70 if text else 20), t=20, b=70))
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=1,
                           xanchor="right", y=-0.12, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig
