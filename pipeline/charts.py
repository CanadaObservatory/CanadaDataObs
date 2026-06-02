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
                   center=None, zoom=2.6, height=640, zmin=None, zmax=None):
    """Zoomable choropleth map (Plotly Choroplethmapbox, free carto-positron
    basemap — no API token). The `geojson` features must carry a top-level `id`
    equal to df[location_col]. Used for the census-tract maps so users can pan/
    zoom to their own area. Pass `name_col` for a human-readable hover label."""
    center = center or {"lat": 58.0, "lon": -96.0}
    customdata = df[[name_col]].to_numpy() if name_col else None
    name_line = "<b>%{customdata[0]}</b><br>" if name_col else ""
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=df[location_col], z=df[value_col],
        zmin=zmin, zmax=zmax,
        featureidkey="id", colorscale=colorscale, reversescale=reversescale,
        marker=dict(line=dict(width=0.2, color="rgba(255,255,255,0.4)"), opacity=0.82),
        colorbar=dict(title=colorbar_title, tickprefix=value_prefix, ticksuffix=value_suffix),
        customdata=customdata,
        hovertemplate=f"{name_line}{colorbar_title}: {value_prefix}%{{z:{value_fmt}}}{value_suffix}<extra></extra>",
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
                          colorscale="Purples", source_note=None,
                          center=None, zoom=2.6, height=660):
    """Choropleth with a dropdown to switch the mapped variable across `groups`
    (list of (column, label)). Used for the descriptive visible-minority maps —
    neutral single-hue scale (no red/green valence), each option auto-caps its
    colour range to its 5th–95th percentile. Values are percentages."""
    center = center or {"lat": 56.0, "lon": -96.0}
    locs = df[location_col]
    custom = df[[name_col]].to_numpy()

    def cap(col):
        return float(df[col].quantile(0.05)), float(df[col].quantile(0.95))

    c0, l0 = groups[0]
    lo0, hi0 = cap(c0)
    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=locs, z=df[c0].tolist(), featureidkey="id",
        colorscale=colorscale, zmin=lo0, zmax=hi0,
        marker=dict(line=dict(width=0.2, color="rgba(255,255,255,0.4)"), opacity=0.82),
        colorbar=dict(title=f"% {l0}", ticksuffix="%"),
        customdata=custom,
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>{l0}: %{{z:.1f}}%<extra></extra>",
    ))
    buttons = []
    for col, label in groups:
        lo, hi = cap(col)
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


VM_GROUP_COLORS = {
    "All visible minorities": "#111111",   # headline (thick)
    "Not a visible minority": "#9e9e9e",
    "South Asian": "#1f77b4", "Chinese": "#d62728", "Black": "#2ca02c",
    "Filipino": "#9467bd", "Arab": "#ff7f0e", "Latin American": "#17becf",
}


def vm_history_lines(df, *, value_col="share", default_geo="Canada",
                     source_note=None, nhs_year=2011, height=560,
                     yaxis_title="% of population (aged 15+)"):
    """Visible-minority composition over census years, with a dropdown to switch the
    geography (Canada / a province / a city). Mirrors `choropleth_groups_map`'s
    dropdown idiom: one fixed line trace per group, and each dropdown button
    `restyle`s every trace's y to the chosen geography's values (x — the census
    years — is shared, so only y changes). `df` is the tidy long output of
    `build_vm_history` (geography, geo_level, year, group, share). 2011 (voluntary
    NHS) is flagged rather than hidden."""
    import pandas as pd
    df = df.copy()
    df["year"] = df["year"].astype(int)
    years = sorted(df["year"].unique())

    pref = list(VM_GROUP_COLORS.keys())
    present = set(df["group"])
    groups = [g for g in pref if g in present] + [g for g in df["group"].unique()
                                                  if g not in pref]

    order = {"national": 0, "province": 1, "cma": 2}
    geos = (df.drop_duplicates("geography")[["geography", "geo_level"]]
            .assign(o=lambda d: d["geo_level"].map(order))
            .sort_values(["o", "geography"])["geography"].tolist())
    if default_geo in geos:
        geos = [default_geo] + [g for g in geos if g != default_geo]

    def yvals(geo, group):
        s = df[(df["geography"] == geo) & (df["group"] == group)].set_index("year")[value_col]
        return [float(s.loc[y]) if y in s.index else None for y in years]

    fig = go.Figure()
    for g in groups:
        fig.add_trace(go.Scatter(
            x=years, y=yvals(default_geo, g), name=g, mode="lines+markers",
            visible=("legendonly" if g == "Not a visible minority" else True),
            line=dict(color=VM_GROUP_COLORS.get(g, "#888"),
                      width=3 if g == "All visible minorities" else 1.8),
            marker=dict(size=6),
            hovertemplate=f"{g}: %{{y:.1f}}%<extra></extra>"))

    buttons = [dict(method="restyle", label=geo,
                    args=[{"y": [yvals(geo, g) for g in groups]}]) for geo in geos]

    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=dict(title="Census year", gridcolor="#e0e0e0",
                   tickmode="array", tickvals=years),
        yaxis=dict(title=yaxis_title, gridcolor="#e0e0e0", rangemode="tozero"),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=10, r=180, t=70, b=90),
        updatemenus=[dict(buttons=buttons, active=0, x=0.0, y=1.14,
                          xanchor="left", yanchor="top", bgcolor="white",
                          bordercolor="#ccc", borderwidth=1, showactive=True)],
    )
    fig.add_annotation(text="Geography:", xref="paper", yref="paper",
                       x=0.0, y=1.20, xanchor="left", yanchor="bottom",
                       showarrow=False, font=dict(size=11, color="#666"))
    if nhs_year in years:
        fig.add_vrect(x0=nhs_year - 0.25, x1=nhs_year + 0.25, line_width=0,
                      fillcolor="#000", opacity=0.05)
        fig.add_annotation(x=nhs_year, y=1.0, yref="paper", yanchor="bottom",
                           text="2011: voluntary NHS", showarrow=False,
                           font=dict(size=9, color="#999"))
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper",
                           x=0, xanchor="left", y=-0.18, showarrow=False,
                           font=dict(size=10, color="#999"))
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
