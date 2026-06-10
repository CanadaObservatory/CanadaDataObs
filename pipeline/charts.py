"""
Reusable Plotly chart-building functions for DataCan.
Enforces consistent styling across all topics.
"""

import plotly.graph_objects as go
from pipeline.config import (
    CANADA_COLOR, PEER_COLOR, OECD_AVG_COLOR,
    HIGHLIGHT_WIDTH, PEER_WIDTH, HIGHLIGHT_COUNTRY,
    PEER_COUNTRIES, COMPARATOR_COLORS, SNAPSHOT_SPECS, DATA_DATE, get_data_date, BRAND,
)


# --- Site attribution on every figure (one cross-cutting interceptor) ----------
# Source notes are rendered in ~140 places site-wide and in several shapes: a
# builder's `source_note=` annotation, an inline `fig.update_layout(annotations=…)`,
# `fig.add_annotation(text="Source…")`, etc. Rather than brand each one (and risk
# missing some or doing it inconsistently), we intercept `Figure.show()` — which
# every chart block calls — and append a "<br>{BRAND}" line to the figure's source
# annotation (the one whose text contains "Source"). It is idempotent (skips if the
# brand is already present), a no-op for figures without a source note, and uses
# Plotly's own `<br>` line break (which only works inside a Plotly annotation — a
# source note rendered as Quarto *markdown* must add the brand in its markdown, since
# `<br>` there renders literally).
if not getattr(go.Figure, "_datacan_branded", False):
    _orig_show = go.Figure.show

    def _branded_show(self, *args, **kwargs):
        for _ann in (self.layout.annotations or ()):
            _t = _ann.text or ""
            if "Source" in _t and BRAND not in _t:
                _ann.text = f"{_t}<br>{BRAND}"
                break
        return _orig_show(self, *args, **kwargs)

    go.Figure.show = _branded_show
    go.Figure._datacan_branded = True



def _base_layout(title, yaxis_title, xaxis_title="", range_slider=True,
                  has_legend=True, data_date=None):
    """Standard layout for all DataCan charts.

    `xaxis_title` defaults to empty: on a time series the x-axis is self-evidently
    years, and a "Year" title only collides with the legend/source note below it.
    """
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


def _year_to_dt(years):
    """Plot an integer-year axis as real Jan-1 dates so Plotly's range slider and
    range-selector buttons (which only work on date axes) function; the axis and
    hover are formatted back to bare years (%Y)."""
    import pandas as pd
    return list(pd.to_datetime(pd.Index(years).astype(int).astype(str), format="%Y"))


def _apply_peer_line_layout(fig, df, x_col, yaxis_title, source_note,
                            rangeslider, initial_start, extra_top=40):
    """Shared layout for the peer-comparison line charts: right-hand vertical legend
    (so a draggable range slider can own the bottom without colliding), range-
    selector buttons + slider on a year axis shown as %Y, and a builder-owned source
    note below the slider. `initial_start` (a year) opens the view on a recent window
    while the slider still spans all history."""
    xaxis = dict(
        title="", gridcolor="#e0e0e0", type="date", tickformat="%Y", hoverformat="%Y",
        rangeselector=dict(buttons=[
            dict(count=5, label="5Y", step="year", stepmode="backward"),
            dict(count=10, label="10Y", step="year", stepmode="backward"),
            dict(count=20, label="20Y", step="year", stepmode="backward"),
            dict(step="all", label="All"),
        ], x=0, xanchor="left", y=1.01),
    )
    if rangeslider:
        xaxis["rangeslider"] = dict(visible=True, thickness=0.08, bgcolor="#f5f5f5")
    if initial_start is not None:
        xaxis["range"] = [_year_to_dt([initial_start])[0],
                          _year_to_dt([int(df[x_col].max())])[0]]
    fig.update_layout(
        xaxis=xaxis,
        yaxis=dict(title=yaxis_title, gridcolor="#e0e0e0"),
        plot_bgcolor="white", hovermode="x unified", height=520,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02,
                    itemclick="toggle", itemdoubleclick="toggleothers"),
        margin=dict(l=10, r=175, t=extra_top, b=(120 if rangeslider else 80)),
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           y=(-0.34 if rangeslider else -0.18), showarrow=False,
                           font=dict(size=10, color="#999"))


def peer_comparison_line(df, x_col, y_col, title, yaxis_title,
                         country_col="country_code", name_col="country_name",
                         highlight=None, show_average=False,
                         avg_name="OECD peer average", source_note=None,
                         rangeslider=True, initial_start=None, hide_peers=True):
    """
    Line chart comparing Canada against OECD peers.

    Canada is red; named comparators get distinct colours; the rest of the peer group
    is light grey. By default (`hide_peers=True`) only Canada, the coloured comparators
    and the peer average are drawn at load — the grey peers start legend-hidden and the
    reader adds them by clicking the right-hand legend, which keeps the busy 17-line
    charts legible. A draggable range slider sits below the chart; `initial_start`
    (a year) opens the view on a recent window while the slider still spans all history.
    Pass `source_note` and the builder places it below the slider.
    """
    if highlight is None:
        highlight = [HIGHLIGHT_COUNTRY]

    def _name(code):
        s = df[df[country_col] == code]
        v = s[name_col].iloc[0] if (name_col in df.columns and not s.empty) else code
        return str(v) if v == v else str(code)   # always a str so the name-sort can't
        #                                           crash on a NaN name (a bad data row
        #                                           must never fail the whole site render)

    codes = list(df[country_col].unique())
    comparators = sorted([c for c in codes
                          if c in COMPARATOR_COLORS and c not in highlight], key=_name)
    others = sorted([c for c in codes
                     if c not in COMPARATOR_COLORS and c not in highlight], key=_name)

    fig = go.Figure()

    # 1) Non-highlighted peers: light grey, behind; hidden at load when hide_peers
    #    (added back via the legend), so only Canada/comparators/average show first.
    for i, code in enumerate(others):
        s = df[df[country_col] == code]
        name = _name(code)
        fig.add_trace(go.Scatter(
            x=_year_to_dt(s[x_col]), y=s[y_col], name=name, mode="lines",
            line=dict(color=PEER_COLOR, width=PEER_WIDTH), opacity=0.8,
            legendrank=100 + i, visible=("legendonly" if hide_peers else True),
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
            x=_year_to_dt(avg[x_col]), y=avg[y_col], name=avg_name, mode="lines",
            line=dict(color=OECD_AVG_COLOR, width=2, dash="dash"),
            legendrank=300,
            hovertemplate=f"{avg_name}: %{{y:.2f}}<extra></extra>",
        ))

    # 3) Named comparators: distinct colours, drawn above the grey cloud
    for i, code in enumerate(comparators):
        s = df[df[country_col] == code]
        name = _name(code)
        fig.add_trace(go.Scatter(
            x=_year_to_dt(s[x_col]), y=s[y_col], name=name, mode="lines",
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
            x=_year_to_dt(s[x_col]), y=s[y_col], name=name, mode="lines+markers",
            line=dict(color=CANADA_COLOR, width=HIGHLIGHT_WIDTH), marker=dict(size=5),
            legendrank=1,
            hovertemplate=f"<b>{name}: %{{y:.2f}}</b><extra></extra>",
        ))

    _apply_peer_line_layout(fig, df, x_col, yaxis_title, source_note,
                            rangeslider, initial_start)
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


def _ranked_footnote(source_note, year):
    """A ranked bar shows exactly one year. Drop a trailing "| Data as of: <year>"
    the caller appended (which duplicated the ranked year — the "year twice" the
    review flagged) and label the displayed year once, clearly."""
    import re
    src = re.sub(r"\s*\|\s*Data as of:.*$", "", source_note or "").rstrip()
    sep = " &nbsp;·&nbsp; " if src else ""
    return f"{src}{sep}{year} data"


def ranked_bar(df, value_col, xaxis_title, source_note,
               country_col="country_code", name_col="country_name",
               year_col="year", ascending=True, min_countries=10,
               tickformat=None, hover_template=None, height=600):
    """
    Horizontal ranked bar of the latest comparable year — Canada red, peers grey.

    Replaces the bar-chart block that was previously copy-pasted into every page.
    `source_note` is the full footer string (the caller builds it, typically
    f"Source: ... | Data as of: {get_data_date(path)}"). A ranked bar shows exactly
    one year, so the builder strips any trailing "| Data as of: <year>" the caller
    appended (it duplicated the ranked year) and shows the displayed year once.
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
        margin=dict(t=30, b=90, l=10, r=20),
        annotations=[dict(
            text=_ranked_footnote(source_note, year),
            xref="paper", yref="paper", x=1, y=-0.15,
            showarrow=False, font=dict(size=10, color="#999"),
        )],
    )
    return fig


def peer_comparison_line_by_age(df, x_col, y_col, age_col, yaxis_title, *,
                                ages, default_age,
                                country_col="country_code", name_col="country_name",
                                show_average=True, avg_name="OECD peer average",
                                hover_suffix="%", hover_decimals=1,
                                source_note=None, rangeslider=True,
                                initial_start=None, hide_peers=True,
                                option_layouts=None, menu_label="Age group:"):
    """Peer-comparison line chart with a category dropdown.

    Same declutter as `peer_comparison_line` (Canada/comparators/average shown, grey
    peers legend-hidden, right-hand legend, range slider, builder-owned source note),
    but `df` is long over an extra `age_col`; a Plotly dropdown restyles every trace
    to the selected category. `ages` is the dropdown order; `default_age` shows first.

    The original use is age brackets (one unit, shared y-axis). For options that DON'T
    share a unit (e.g. tobacco use in %, alcohol in litres), pass `option_layouts`
    (a dict option->y-axis title): the dropdown then also rewrites the y-axis title and
    `autorange`s on switch, so each option gets its own scale. `menu_label` overrides
    the small "Age group:" caption above the menu (e.g. "Substance:")."""
    highlight = [HIGHLIGHT_COUNTRY]

    def _name(code):
        s = df[df[country_col] == code]
        v = s[name_col].iloc[0] if (name_col in df.columns and not s.empty) else code
        return str(v) if v == v else str(code)   # always a str so the name-sort can't
        #                                           crash on a NaN name (a bad data row
        #                                           must never fail the whole site render)

    codes = list(df[country_col].unique())
    comparators = sorted([c for c in codes
                          if c in COMPARATOR_COLORS and c not in highlight], key=_name)
    others = sorted([c for c in codes
                     if c not in COMPARATOR_COLORS and c not in highlight], key=_name)

    def series(code, age):
        s = df[(df[country_col] == code) & (df[age_col] == age)].sort_values(x_col)
        return _year_to_dt(s[x_col]), s[y_col].tolist()

    def avg_series(age):
        d = df[df[age_col] == age]
        n = d[country_col].nunique()
        counts = d.dropna(subset=[y_col]).groupby(x_col)[y_col].count()
        valid = counts[counts >= n / 2].index
        a = d[d[x_col].isin(valid)].groupby(x_col)[y_col].mean()
        return _year_to_dt(a.index), a.values.tolist()

    # Fixed trace order (used for both add-order and the per-age restyle arrays):
    # grey others, [average], coloured comparators, Canada on top.
    order = [("other", c) for c in others]
    if show_average:
        order.append(("avg", None))
    order += [("cmp", c) for c in comparators]
    order += [("can", HIGHLIGHT_COUNTRY)]

    def _hov(label, bold=False):
        lab = f"<b>{label}</b>" if bold else label
        return f"{lab}: %{{y:.{hover_decimals}f}}{hover_suffix}<extra></extra>"

    fig = go.Figure()
    oi = 0
    for kind, code in order:
        x, y = (avg_series(default_age) if kind == "avg" else series(code, default_age))
        if kind == "other":
            name = _name(code)
            fig.add_trace(go.Scatter(x=x, y=y, name=name, mode="lines",
                line=dict(color=PEER_COLOR, width=PEER_WIDTH), opacity=0.8,
                legendrank=100 + oi, visible=("legendonly" if hide_peers else True),
                hovertemplate=_hov(name)))
            oi += 1
        elif kind == "avg":
            fig.add_trace(go.Scatter(x=x, y=y, name=avg_name, mode="lines",
                line=dict(color=OECD_AVG_COLOR, width=2, dash="dash"),
                legendrank=300, hovertemplate=_hov(avg_name)))
        elif kind == "cmp":
            name = _name(code)
            fig.add_trace(go.Scatter(x=x, y=y, name=name, mode="lines",
                line=dict(color=COMPARATOR_COLORS[code], width=2),
                legendrank=10 + comparators.index(code), hovertemplate=_hov(name, True)))
        else:
            name = _name(code)
            fig.add_trace(go.Scatter(x=x, y=y, name=name, mode="lines+markers",
                line=dict(color=CANADA_COLOR, width=HIGHLIGHT_WIDTH), marker=dict(size=5),
                legendrank=1, hovertemplate=_hov(name, True)))

    buttons = []
    for age in ages:
        xs, ys = [], []
        for kind, code in order:
            x, y = (avg_series(age) if kind == "avg" else series(code, age))
            xs.append(x); ys.append(y)
        if option_layouts:
            buttons.append(dict(method="update", label=age, args=[{"x": xs, "y": ys},
                {"yaxis.title.text": option_layouts.get(age, yaxis_title),
                 "yaxis.autorange": True}]))
        else:
            buttons.append(dict(method="restyle", label=age, args=[{"x": xs, "y": ys}]))

    _apply_peer_line_layout(fig, df, x_col, yaxis_title, source_note,
                            rangeslider, initial_start, extra_top=70)
    fig.update_layout(
        updatemenus=[dict(buttons=buttons, active=ages.index(default_age),
            direction="down", showactive=True, x=1, xanchor="right",
            y=1.13, yanchor="top", bgcolor="white", bordercolor="#ccc", borderwidth=1)])
    fig.add_annotation(text=menu_label, xref="paper", yref="paper",
        x=1, xanchor="right", y=1.17, yanchor="bottom", showarrow=False,
        font=dict(size=11, color="#666"))
    return fig


def ranked_bar_by_age(df, value_col, age_col, xaxis_title, source_note, *,
                      ages, default_age, country_col="country_code",
                      name_col="country_name", year_col="year", ascending=True,
                      min_countries=10, tickformat=None, hover_template=None,
                      height=600):
    """Ranked horizontal bar with an age-bracket dropdown. Each bracket re-ranks on
    its own latest comparable year (Canada always kept), and the dropdown reorders
    the bars, recolours them (Canada red), and updates the year in the footnote."""
    def _bar_color(c):
        return CANADA_COLOR if c == HIGHLIGHT_COUNTRY else COMPARATOR_COLORS.get(c, PEER_COLOR)

    per_age = {}
    for age in ages:
        d = df[df[age_col] == age]
        year = _latest_year_with_coverage(d, value_col, year_col, min_countries,
                                          country_col=country_col,
                                          require_code=HIGHLIGHT_COUNTRY)
        latest = (d[d[year_col] == year].dropna(subset=[value_col])
                  .sort_values(value_col, ascending=ascending))
        names = (latest[name_col] if name_col in latest.columns
                 else latest[country_col]).tolist()
        per_age[age] = dict(x=latest[value_col].tolist(), y=names,
                            colors=[_bar_color(c) for c in latest[country_col]],
                            year=int(year))

    d0 = per_age[default_age]
    fig = go.Figure(go.Bar(x=d0["x"], y=d0["y"], orientation="h",
        marker_color=d0["colors"],
        hovertemplate=hover_template or "%{y}: %{x}<extra></extra>"))

    xaxis = dict(gridcolor="#e0e0e0", title=xaxis_title)
    if tickformat:
        xaxis["tickformat"] = tickformat

    buttons = []
    for age in ages:
        a = per_age[age]
        buttons.append(dict(method="update", label=age,
            args=[{"x": [a["x"]], "y": [a["y"]], "marker.color": [a["colors"]]},
                  {"yaxis.categoryarray": a["y"], "yaxis.categoryorder": "array",
                   "annotations[0].text": _ranked_footnote(source_note, a['year'])}]))

    fig.update_layout(
        xaxis=xaxis,
        yaxis=dict(title="", categoryorder="array", categoryarray=d0["y"]),
        plot_bgcolor="white", showlegend=False, height=height,
        margin=dict(t=60, b=90, l=10, r=20),
        updatemenus=[dict(buttons=buttons, active=ages.index(default_age),
            direction="down", showactive=True, x=1, xanchor="right",
            y=1.06, yanchor="bottom", bgcolor="white", bordercolor="#ccc", borderwidth=1)],
        annotations=[dict(text=_ranked_footnote(source_note, d0['year']),
            xref="paper", yref="paper", x=1, y=-0.15, showarrow=False,
            font=dict(size=10, color="#999"))])
    fig.add_annotation(text="Age group:", xref="paper", yref="paper",
        x=1, xanchor="right", y=1.10, yanchor="bottom", showarrow=False,
        font=dict(size=11, color="#666"))
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


# CARTO's free, token-less raster basemap, split into two layers so place/street
# names render ON TOP of the choropleth fill instead of being washed out beneath it
# (the orientation problem on the dense tract/DA maps). The no-labels base is drawn
# below the data (`below="traces"`); the labels-only layer omits `below`, which
# Plotly inserts above every trace. Visually identical to the built-in
# "carto-positron" style, just with the labels lifted above the fill.
_CARTO = "https://a.basemaps.cartocdn.com"
_BASEMAP_ATTR = "© OpenStreetMap contributors © CARTO"


def _labelled_basemap():
    return [
        {"sourcetype": "raster", "below": "traces",
         "source": [f"{_CARTO}/light_nolabels/{{z}}/{{x}}/{{y}}.png"],
         "sourceattribution": _BASEMAP_ATTR},
        {"sourcetype": "raster",          # no `below` → drawn above the choropleth
         "source": [f"{_CARTO}/light_only_labels/{{z}}/{{x}}/{{y}}.png"],
         "sourceattribution": _BASEMAP_ATTR},
    ]


def _hover_toggle():
    """Two-button menu (floated bottom-left of a map) to show/hide the hover tooltip —
    the review noted it is useful but sometimes distracting. Toggles the layout-level
    `hovermode` via relayout ("closest" on / `False` off). We must NOT toggle the
    trace's `hoverinfo` here: a Choroplethmapbox/Scattermapbox with a `hovertemplate`
    set ignores `hoverinfo` (the template wins, even `hoverinfo="skip"`), so that does
    nothing — whereas `hovermode=False` reliably suppresses hover for the whole map.
    Returned as one updatemenus entry; append to a map's `updatemenus` list (it
    composes with a group/dropdown menu)."""
    return dict(type="buttons", direction="right", showactive=True, active=0,
                x=0.01, y=0.01, xanchor="left", yanchor="bottom",
                pad=dict(t=2, b=2, l=2, r=2), bgcolor="white", bordercolor="#ccc",
                borderwidth=1, font=dict(size=11),
                buttons=[dict(label="Hover on", method="relayout", args=[{"hovermode": "closest"}]),
                         dict(label="Hover off", method="relayout", args=[{"hovermode": False}])])


# A handful of major cities to orient the physical-geography maps (name, lat, lon).
MAJOR_CITIES = [
    ("Vancouver", 49.28, -123.12), ("Calgary", 51.05, -114.07),
    ("Edmonton", 53.55, -113.49), ("Winnipeg", 49.90, -97.14),
    ("Toronto", 43.65, -79.38), ("Ottawa", 45.42, -75.70),
    ("Montréal", 45.50, -73.57), ("Halifax", 44.65, -63.58),
    ("St. John's", 47.56, -52.71), ("Whitehorse", 60.72, -135.06),
    ("Yellowknife", 62.45, -114.37), ("Iqaluit", 63.75, -68.52),
]


def add_city_markers(fig, cities=MAJOR_CITIES, textposition="top center"):
    """Overlay major cities (small dark dots + labels) to orient the physical-geography
    maps (ecozones, land cover, wildfire), where the data carries no city names. Drawn
    above the choropleth fill and kept out of the legend."""
    fig.add_trace(go.Scattermapbox(
        lat=[c[1] for c in cities], lon=[c[2] for c in cities],
        mode="markers+text", text=[c[0] for c in cities],
        textposition=textposition, textfont=dict(size=9, color="#222"),
        marker=dict(size=6, color="#111"), hoverinfo="skip", showlegend=False,
        name="cities"))
    return fig


def add_boundaries(fig, geojson, *, color="#9aa0a6", width=0.8, below="traces"):
    """Overlay administrative boundaries (province/territory or national) on a map by
    adding the polygon GeoJSON as a mapbox **line** layer — the polygon rings render as
    outlines. Inserted with `below="traces"` so the data fills (e.g. the lakes) and the
    place labels stay on top; call it twice to layer a light internal-division set under
    a heavier national outline (the later call draws above the earlier where they share
    the perimeter). Returns the figure for chaining."""
    layer = dict(sourcetype="geojson", source=geojson, type="line",
                 color=color, line=dict(width=width))
    if below is not None:
        layer["below"] = below   # below=None → drawn on top (e.g. rivers over basin fills)
    existing = [l.to_plotly_json() for l in (fig.layout.mapbox.layers or [])]
    fig.update_layout(mapbox_layers=existing + [layer])
    return fig


def add_line_features(fig, geojson, *, name_key="name", color="#0d2b5e", width=1.1,
                      name="lines"):
    """Overlay line features (e.g. rivers) from a LineString/MultiLineString GeoJSON as a
    Scattermapbox trace. Unlike `add_boundaries` (a static mapbox line *layer*, no hover),
    this is a real trace, so each feature carries a hover label from `name_key`. Segments are
    joined with None breaks so separate features don't connect. Drawn above the choropleth
    fills but below the basemap place-labels. Kept out of the legend. Returns the figure."""
    lats, lons, cd = [], [], []
    for f in geojson.get("features", []):
        nm = (f.get("properties") or {}).get(name_key) or ""
        geom = f.get("geometry") or {}
        coords = geom.get("coordinates") or []
        segs = coords if geom.get("type") == "MultiLineString" else [coords]
        for seg in segs:
            for pt in seg:
                lons.append(pt[0]); lats.append(pt[1]); cd.append(nm)
            lons.append(None); lats.append(None); cd.append(None)
    fig.add_trace(go.Scattermapbox(
        lat=lats, lon=lons, mode="lines", line=dict(color=color, width=width),
        customdata=cd, hovertemplate="<b>%{customdata}</b><extra></extra>",
        name=name, showlegend=False))
    return fig


def relief_map(image_uri, coordinates, *, boundary_geojson=None, boundary_color="#8a8f96",
               boundary_width=0.5, source_note=None, center=None, zoom=2.3, height=660):
    """Raster-image overlay map: places a pre-rendered **Web-Mercator** image (e.g. the
    elevation relief PNG, warped to EPSG:3857) over the free carto basemap as a mapbox
    `image` layer, positioned by its lon/lat **corner coordinates** (clockwise TL, TR, BR,
    BL — the order Plotly expects; the image is rendered in 3857 but the corners are WGS84).
    `boundary_geojson` draws province/territory lines over the image; place labels stay on
    top. The image is the surface, so there's no hover or legend — an invisible
    Scattermapbox trace just anchors the mapbox subplot."""
    center = center or {"lat": 62.0, "lon": -96.0}
    base = _labelled_basemap()
    layers = [base[0],
              dict(sourcetype="image", source=image_uri, coordinates=coordinates, below="traces")]
    if boundary_geojson is not None:
        layers.append(dict(sourcetype="geojson", source=boundary_geojson, type="line",
                           color=boundary_color, line=dict(width=boundary_width), below="traces"))
    layers.append(base[1])
    fig = go.Figure(go.Scattermapbox(lat=[None], lon=[None], hoverinfo="skip", showlegend=False))
    fig.update_layout(mapbox_style="white-bg", mapbox_layers=layers,
                      mapbox_zoom=zoom, mapbox_center=center,
                      margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white")
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0, xanchor="left",
                           y=-0.04, showarrow=False, font=dict(size=10, color="#999"))
    return fig


def population_pyramid(df, *, year_col="year", age_col="age", gender_col="gender",
                       value_col="value", men_label="Men", women_label="Women",
                       men_color="#4477aa", women_color="#ee8866",
                       source_note=None, height=640):
    """Two-sided age pyramid (single-year ages) with a year slider.

    `df` is tidy: one row per (year, gender, age), `age` numeric (0–100, where
    100 = "100 and over") and `value` the head-count. A Plotly slider restyles
    both bar traces' x arrays across years (the same restyle idiom as the
    dropdown maps — no animation frames), opening on the latest year. The x-axis
    is FIXED to the all-year maximum so dragging the slider reads as the cohorts
    moving through the pyramid, not as an axis rescale. The men side is plotted
    negative but displayed positive everywhere (tick labels and hover read from
    abs customdata). Colours are a neutral colourblind-safe blue/orange pair —
    Canada-red stays reserved for Canada-vs-peer charts."""
    import numpy as np
    import pandas as pd

    ages = np.sort(pd.to_numeric(df[age_col], errors="coerce").dropna().unique())
    years = sorted(pd.to_numeric(df[year_col], errors="coerce").dropna().unique().astype(int))

    def side(year, gender):
        s = (df[(df[year_col] == year) & (df[gender_col] == gender)]
             .set_index(age_col)[value_col].reindex(ages))
        return s.to_numpy(dtype=float)

    data = {y: (side(y, men_label), side(y, women_label)) for y in years}
    y0 = years[-1]
    xmax = max(np.nanmax(np.concatenate(v)) for v in data.values())
    step = 10 ** np.floor(np.log10(xmax))
    if xmax / step < 4:
        step /= 2
    ticks = np.arange(0, xmax + step, step)
    tickvals = np.concatenate([-ticks[:0:-1], ticks])
    ticktext = [f"{abs(t) / 1000:,.0f}k" if abs(t) >= 1000 else f"{abs(t):,.0f}"
                for t in tickvals]

    m0, w0 = data[y0]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=ages, x=-m0, customdata=m0, name=men_label, orientation="h",
        marker_color=men_color,
        hovertemplate=f"{men_label}, age %{{y}}: %{{customdata:,.0f}}<extra></extra>"))
    fig.add_trace(go.Bar(
        y=ages, x=w0, customdata=w0, name=women_label, orientation="h",
        marker_color=women_color,
        hovertemplate=f"{women_label}, age %{{y}}: %{{customdata:,.0f}}<extra></extra>"))

    steps = [dict(method="restyle", label=str(y),
                  args=[{"x": [-data[y][0], data[y][1]],
                         "customdata": [data[y][0], data[y][1]]}])
             for y in years]

    fig.update_layout(
        barmode="overlay", bargap=0.08,
        xaxis=dict(tickvals=tickvals, ticktext=ticktext, title="Population",
                   gridcolor="#e0e0e0", zeroline=True, zerolinecolor="#bbb",
                   range=[-xmax * 1.06, xmax * 1.06]),
        yaxis=dict(title="Age", dtick=10, gridcolor="#e0e0e0"),
        legend=dict(orientation="h", x=0, y=1.04, xanchor="left"),
        plot_bgcolor="white", height=height,
        margin=dict(l=60, r=20, t=30, b=130),
        sliders=[dict(active=len(steps) - 1, steps=steps,
                      currentvalue=dict(prefix="Year: ", font=dict(size=13)),
                      font=dict(size=10), pad=dict(t=34, b=6))],
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper",
                           x=0, xanchor="left", y=-0.31, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def choropleth_map(geojson, df, location_col, value_col, *, name_col=None,
                   colorbar_title="", colorscale="Viridis", reversescale=False,
                   value_prefix="", value_suffix="", value_fmt=",.0f", source_note=None,
                   center=None, zoom=2.6, height=640, zmin=None, zmax=None, log=False,
                   line_color="rgba(255,255,255,0.4)", line_width=0.2, opacity=0.82,
                   extra_hover=None):
    """Zoomable choropleth map (Plotly Choroplethmapbox, free carto-positron
    basemap — no API token). The `geojson` features must carry a top-level `id`
    equal to df[location_col]. Used for the census-tract maps so users can pan/
    zoom to their own area. Pass `name_col` for a human-readable hover label.

    `log=True` colours on a base-10 log scale (for heavily skewed quantities like
    population density, where a few dense provinces would otherwise flatten the
    rest); the colourbar ticks are relabelled to the real values and zmin/zmax are
    ignored. The hover always shows the true (un-logged) value, read from
    customdata so the displayed number is identical whether or not log is set.

    `line_color`/`line_width` style the polygon outline (default a hairline white
    separator, right for dense tract maps); pass a dark colour + a slightly larger
    width for sparse polygons over a basemap (e.g. the major-lakes map) so small,
    light-filled features still read. `opacity` is the polygon fill opacity.

    `extra_hover` (optional) appends hover lines beyond the coloured value, without
    changing what the map colours: a list of (label, column, fmt, suffix) tuples,
    e.g. [("0–14", "share_0_14", ".0f", "%")] → one "label: value" line each. Pass
    fmt="" to insert the column's value verbatim (for pre-formatted strings such as
    comma-grouped populations, dodging the bundled-Plotly d3-format quirk)."""
    import math
    import numpy as np
    import pandas as pd
    center = center or {"lat": 58.0, "lon": -96.0}
    vals = pd.to_numeric(df[value_col], errors="coerce")
    base = df.copy()
    base["_v"] = vals.to_numpy()
    extra_hover = extra_hover or []
    cols = ([name_col] if name_col else []) + ["_v"] + [c for _, c, _, _ in extra_hover]
    customdata = base[cols].to_numpy()
    name_line = "<b>%{customdata[0]}</b><br>" if name_col else ""
    vidx = 1 if name_col else 0
    extra_lines = "".join(
        f"<br>{lbl}: %{{customdata[{vidx + 1 + i}]" + (f":{fmt}" if fmt else "") + f"}}{suf}"
        for i, (lbl, _, fmt, suf) in enumerate(extra_hover))

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
        marker=dict(line=dict(width=line_width, color=line_color), opacity=opacity),
        colorbar=colorbar,
        customdata=customdata,
        hovertemplate=f"{name_line}{colorbar_title}: {value_prefix}%{{customdata[{vidx}]:{value_fmt}}}{value_suffix}{extra_lines}<extra></extra>",
    ))
    fig.update_layout(
        mapbox_style="white-bg", mapbox_layers=_labelled_basemap(),
        mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white",
        updatemenus=[_hover_toggle()],
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper",
                           x=0, xanchor="left", y=-0.04, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def choropleth_groups_map(geojson, df, location_col, groups, name_col, *,
                          colorscale="Viridis", source_note=None,
                          center=None, zoom=2.6, height=660, cap_quantiles=(0.0, 1.0),
                          opacity=0.82, breakdown=True, breakdown_min=0.5,
                          breakdown_exclude=(), pop_col=None,
                          value_fmt=".1f", value_suffix="%", cbar_title="% {label}",
                          cbar_ticksuffix="%"):
    """Choropleth with a dropdown to switch the mapped variable across `groups`
    (list of (column, label)). Used for the descriptive share maps (visible
    minority, religion, land cover); values are percentages and each option
    rescales its own colour range + colorbar.

    `breakdown=True` (default) makes the hover show the area's **full composition**
    across every group — all visible-minority groups, all religions, or all
    land-cover classes — sorted high→low, dropping anything below `breakdown_min`
    percent. So hovering any neighbourhood reads as a profile ("Not a vis. min. 62%,
    Chinese 12%, South Asian 9%…") regardless of which group the dropdown is
    colouring; the map colour shows the selected group, the hover gives the whole
    picture. Set `breakdown=False` to fall back to a single selected-group hover
    (for non-compositional group sets where a full breakdown would be meaningless).
    `breakdown_exclude` lists columns to keep OUT of the composition — pass the
    aggregate "all visible minorities" total there so it isn't double-counted
    alongside its own component groups.

    `cap_quantiles` = the (low, high) quantiles each group's colour range is clipped
    to. Default (0, 1) = the group's true min–max — correct for *share* layers where
    the high values are the subject (so Toronto's 57% visible-minority reads
    differently from Calgary's 39% instead of both clamping to the darkest colour).
    Pass a high quantile < 1 (e.g. (0, 0.98)) for the ~6,000-tract maps, where a few
    near-100% enclave tracts would otherwise stretch the scale and flatten the
    typical range. The default colour scale is **Viridis** — perceptually uniform and
    colourblind-safe, with no red/green valence, and higher contrast than Cividis so
    the socially meaningful mid-range (e.g. 3% vs 13%) stays distinguishable while
    these sensitive layers keep a neutral, descriptive reading.

    `pop_col` (optional) names a population column; when given, the hover gains a
    "Population: N,NNN" line — the area's head-count, i.e. the denominator the shares
    are computed on (so a 50% share in a 90-person block reads differently from a
    5,000-person tract). Pre-formatted to a comma string to dodge the bundled-Plotly
    d3-format quirk.

    The layer defaults to **share/percentage** semantics (hover `:.1f%`, colourbar
    "% {label}"). For a non-percentage value such as a crime **rate per 100,000**,
    pass `value_fmt`/`value_suffix` (the hover number) and `cbar_title`/
    `cbar_ticksuffix` (the colourbar) — e.g. `value_fmt=".0f"`,
    `value_suffix=" per 100k"`, `cbar_title="{label}"`, `cbar_ticksuffix=""` — and
    set `breakdown=False`, since rates don't compose into a profile."""
    import numpy as np
    import pandas as pd
    center = center or {"lat": 56.0, "lon": -96.0}
    locs = df[location_col]
    qlo, qhi = cap_quantiles

    def rng(col):
        return float(df[col].quantile(qlo)), float(df[col].quantile(qhi))

    def gfmt(g):
        # A groups item is (col, label) or (col, label, {fmt?, suffix?, cbar_suffix?}).
        # The optional dict lets each dropdown option carry its own units — e.g. a Crime
        # Severity *index* sitting alongside *rate per 100k* offences in one map.
        o = g[2] if len(g) > 2 else {}
        return (g[0], g[1], o.get("fmt", value_fmt), o.get("suffix", value_suffix),
                o.get("cbar_suffix", cbar_ticksuffix))

    c0, l0, fmt0, suf0, cbsuf0 = gfmt(groups[0])
    lo0, hi0 = rng(c0)

    # Optional population column → "Population: N,NNN" line in the hover (the area's
    # head-count, the denominator the shares are computed on). Pre-formatted to a
    # comma string in Python: Quarto's bundled Plotly does not reliably honour a d3
    # number-format inside hovertemplate (same quirk as the CPI/quarterly-GDP hovers).
    pop = (pd.to_numeric(df[pop_col], errors="coerce").fillna(0).round().astype(int)
           .map("{:,}".format).to_numpy() if (pop_col and pop_col in df.columns) else None)

    # Hover content: either the area's full composition across every group (default)
    # or a single selected-group readout. The breakdown is baked per-area into
    # customdata so it stays put as the dropdown swaps which group colours the map.
    if breakdown:
        excl = set(breakdown_exclude)
        def _profile(row):
            pairs = [(lab, row[col]) for col, lab in groups
                     if col not in excl and pd.notna(row[col]) and row[col] >= breakdown_min]
            pairs.sort(key=lambda t: t[1], reverse=True)
            return "<br>".join(f"{lab}: {v:.1f}%" for lab, v in pairs)
        prof = df.apply(_profile, axis=1).to_numpy()
        if pop is not None:
            custom = np.column_stack([df[name_col].to_numpy(), pop, prof])
            hovertemplate = ("<b>%{customdata[0]}</b><br>Population: %{customdata[1]}"
                             "<br>%{customdata[2]}<extra></extra>")
        else:
            custom = np.column_stack([df[name_col].to_numpy(), prof])
            hovertemplate = "<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>"
    else:
        pop_line = "Population: %{customdata[1]}<br>" if pop is not None else ""
        custom = (np.column_stack([df[name_col].to_numpy(), pop]) if pop is not None
                  else df[[name_col]].to_numpy())
        hovertemplate = f"<b>%{{customdata[0]}}</b><br>{pop_line}{l0}: %{{z:{fmt0}}}{suf0}<extra></extra>"

    fig = go.Figure(go.Choroplethmapbox(
        geojson=geojson, locations=locs, z=df[c0].tolist(), featureidkey="id",
        colorscale=colorscale, zmin=lo0, zmax=hi0,
        marker=dict(line=dict(width=0.2, color="rgba(255,255,255,0.4)"), opacity=opacity),
        colorbar=dict(title=cbar_title.format(label=l0), ticksuffix=cbsuf0),
        customdata=custom,
        hovertemplate=hovertemplate,
    ))
    buttons = []
    for g in groups:
        col, label, fmt, suf, cbsuf = gfmt(g)
        lo, hi = rng(col)
        args = {"z": [df[col].tolist()], "zmin": lo, "zmax": hi,
                "colorbar.title.text": cbar_title.format(label=label),
                "colorbar.ticksuffix": cbsuf}
        if not breakdown:   # keep the full-composition hover stable across the dropdown
            args["hovertemplate"] = f"<b>%{{customdata[0]}}</b><br>{pop_line}{label}: %{{z:{fmt}}}{suf}<extra></extra>"
        buttons.append(dict(method="restyle", label=label, args=[args]))
    fig.update_layout(
        mapbox_style="white-bg", mapbox_layers=_labelled_basemap(),
        mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=46, b=36), height=height,
        updatemenus=[dict(buttons=buttons, active=0, x=0.01, y=0.99,
                          xanchor="left", yanchor="top", bgcolor="white",
                          bordercolor="#ccc", borderwidth=1, showactive=True),
                     _hover_toggle()],
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
                           legend_orientation="v", detail_col=None):
    """Categorical choropleth — each polygon coloured by a *discrete* category
    rather than a continuous value (used for ecozones and permafrost zones).

    Plotly's Choroplethmapbox is value-based, so each category is mapped to an
    integer code laid over a hard-stepped discrete colourscale (value i sits in
    the middle of band i via zmin=-0.5/zmax=n-0.5); the colourbar is hidden and a
    real legend is drawn with invisible Scattermapbox proxies (one per category).
    Pass `ordered` to fix the legend order (and, for an ordinal ramp like the
    permafrost zones, the colour order); `color_map` to set exact colours, else
    CATEGORICAL_PALETTE is cycled. `geojson` features must carry a top-level `id`
    equal to df[location_col]; `name_col` adds a per-feature hover label. Pass `detail_col`
    to show a custom per-feature string (e.g. a full composition breakdown, like the
    diversity/religion maps) in the hover instead of the bare category."""
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

    hover_col = detail_col or cat_col   # detail_col (e.g. a composition breakdown) shows in
    custom = (df[[name_col, hover_col]].to_numpy() if name_col   # the hover instead of the
              else df[[hover_col]].to_numpy())                    # bare category
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
    legend = (dict(orientation="v", yanchor="top", y=0.93, xanchor="left", x=1.01)
              if legend_orientation == "v"
              else dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5))
    if legend_title:
        legend["title"] = dict(text=legend_title)
    fig.update_layout(
        mapbox_style="white-bg", mapbox_layers=_labelled_basemap(),
        mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white",
        legend=legend, showlegend=True, updatemenus=[_hover_toggle()],
    )
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=-0.04, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def bubble_map(df, lat_col, lon_col, size_col, *, color="#e3492a", opacity=0.5,
               max_px=42, customdata=None, hovertemplate=None, source_note=None,
               center=None, zoom=2.3, height=640):
    """Proportional-symbol ("bubble") map — points sized by `size_col`, drawn over the
    same labelled basemap and with the same hover on/off toggle as the choropleths.
    Marker AREA is proportional to the value (Plotly `sizemode="area"`), so a fire that
    burned 4× the area shows ~2× the radius; tiny values clamp to a 2-px floor. First
    use: the 2023 wildfire-locations map, where a handful of enormous boreal fires must
    visibly dominate the thousands of small ones."""
    center = center or {"lat": 60.0, "lon": -100.0}
    s = df[size_col]
    sizeref = 2.0 * float(s.max()) / (max_px ** 2) if float(s.max()) > 0 else 1
    fig = go.Figure(go.Scattermapbox(
        lat=df[lat_col], lon=df[lon_col], mode="markers",
        marker=dict(size=s, sizemode="area", sizeref=sizeref, sizemin=2,
                    color=color, opacity=opacity),
        customdata=customdata,
        hovertemplate=hovertemplate or "%{customdata}<extra></extra>"))
    fig.update_layout(
        mapbox_style="white-bg", mapbox_layers=_labelled_basemap(),
        mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white",
        updatemenus=[_hover_toggle()])
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=-0.04, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def point_value_map(df, lat_col, lon_col, groups, *, colorscale="RdBu", reversescale=False,
                    cmid=None, cmin=None, cmax=None, cbar_title="", value_suffix="",
                    value_fmt=".1f", marker_size=7, opacity=0.9, name_col=None,
                    source_note=None, center=None, zoom=2.3, height=640):
    """Coloured-point map — one constant-size dot per row, **coloured** by value on a shared
    scale, with an optional dropdown to switch the coloured variable across `groups` (list of
    (col, label)). Unlike `bubble_map` (size ∝ value, for magnitudes), this colours a fixed
    marker, so it suits **diverging** quantities like temperature — pass a diverging
    `colorscale` + `cmid` (e.g. RdBu, reversescale=True, cmid=0 → blue below freezing, red
    above). Hover shows `name_col` + the selected value (pre-formatted to dodge the bundled-
    Plotly d3-format quirk). Same labelled basemap + hover-toggle as the choropleths."""
    import pandas as pd
    center = center or {"lat": 60.0, "lon": -96.0}

    def vals(col):
        return pd.to_numeric(df[col], errors="coerce").tolist()

    def cdata(col):
        v = pd.to_numeric(df[col], errors="coerce")
        names = list(df[name_col]) if name_col else [""] * len(df)
        return [[n, ("—" if pd.isna(x) else f"{x:{value_fmt}}")] for n, x in zip(names, v)]

    name_line = "<b>%{customdata[0]}</b><br>" if name_col else ""
    htmpl = f"{name_line}{cbar_title}: %{{customdata[1]}}{value_suffix}<extra></extra>"
    c0 = groups[0][0]
    fig = go.Figure(go.Scattermapbox(
        lat=df[lat_col], lon=df[lon_col], mode="markers",
        marker=dict(size=marker_size, color=vals(c0), colorscale=colorscale,
                    reversescale=reversescale, cmid=cmid, cmin=cmin, cmax=cmax,
                    opacity=opacity, colorbar=dict(title=cbar_title, ticksuffix=value_suffix)),
        customdata=cdata(c0), hovertemplate=htmpl, name=""))
    menus = [_hover_toggle()]
    if len(groups) > 1:
        menus.append(dict(
            type="dropdown", direction="down", showactive=True, x=0.01, y=0.99,
            xanchor="left", yanchor="top", bgcolor="white", bordercolor="#ccc", borderwidth=1,
            buttons=[dict(label=label, method="restyle",
                          args=[{"marker.color": [vals(col)], "customdata": [cdata(col)]}, [0]])
                     for col, label in groups]))
    fig.update_layout(
        mapbox_style="white-bg", mapbox_layers=_labelled_basemap(),
        mapbox_zoom=zoom, mapbox_center=center,
        margin=dict(l=0, r=0, t=10, b=36), height=height, plot_bgcolor="white",
        updatemenus=menus)
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=-0.04, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


# Dropdown order for the diversity ("population groups") maps — CMA, census-tract and
# dissemination-area. Leads with the three-way partition that tiles to exactly 100%
# (All visible minorities · White · Indigenous), then the visible-minority subgroups.
# `white` and `indigenous` are derived in build_census_geo (see DERIVED_GROUPS): White
# is the non-Indigenous remainder of "Not a visible minority", Indigenous is the
# single-response identity count. Shared by every diversity .qmd so the layers stay in
# lockstep; pair with breakdown_exclude=["all_vm"] so the hover composition (White +
# Indigenous + the visible-minority subgroups) isn't double-counted by the aggregate.
DIVERSITY_MAP_GROUPS = [
    ("all_vm", "All visible minorities"),
    ("white", "White"),
    ("indigenous", "Indigenous"),
    ("south_asian", "South Asian"), ("chinese", "Chinese"), ("black", "Black"),
    ("filipino", "Filipino"), ("arab", "Arab"), ("latin_american", "Latin American"),
    ("southeast_asian", "Southeast Asian"), ("west_asian", "West Asian"),
    ("korean", "Korean"), ("japanese", "Japanese"),
]

VM_GROUP_COLORS = {
    "All visible minorities": "#111111",   # headline (thick)
    "Not a visible minority": "#9e9e9e",
    "South Asian": "#1f77b4", "Chinese": "#d62728", "Black": "#2ca02c",
    "Filipino": "#9467bd", "Arab": "#ff7f0e", "Latin American": "#17becf",
}

# Dropdown order for the religion ("religious affiliation") share maps — CMA,
# census-tract and dissemination-area. Shared by every religion .qmd so the layers
# stay in lockstep. Leads with **No religion / secular** (not Christian) so the map
# opens on a neutral default rather than implying a preferred faith — a deliberate
# editorial choice for this descriptive, non-partisan layer. The many Christian
# denominations are rolled into a single "Christian" total upstream.
RELIGION_MAP_GROUPS = [
    ("no_religion", "No religion / secular"),
    ("christian", "Christian"),
    ("muslim", "Muslim"), ("hindu", "Hindu"), ("sikh", "Sikh"),
    ("buddhist", "Buddhist"), ("jewish", "Jewish"),
    ("indigenous_spirituality", "Indigenous"),
    ("other_religion", "Other religions & spiritual traditions"),
]

RELIGION_HISTORY_COLORS = {
    "Christian": "#1f77b4", "No religion / secular": "#7f7f7f",
    "Muslim": "#2ca02c", "Hindu": "#ff7f0e", "Sikh": "#d62728",
    "Buddhist": "#9467bd", "Jewish": "#8c564b",
    "Indigenous": "#e377c2", "Other religions": "#17becf",
}


def history_lines(df, *, group_colors, hidden_groups=(), thick_group=None,
                  value_col="share", default_geo="Canada", source_note=None,
                  nhs_year=2011, nhs_label="2011: voluntary NHS", height=560,
                  yaxis_title="% of population", dropdown=True, measures=None,
                  rangeslider=False):
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

    xaxis = dict(title="Census year", gridcolor="#e0e0e0",
                 tickmode="array", tickvals=years)
    if rangeslider:   # draggable time window for the deep (1871–) long-run series
        xaxis["rangeslider"] = dict(visible=True, thickness=0.07, bgcolor="#f5f5f5")
    b_margin = 120 if rangeslider else 90
    src_y = -0.30 if rangeslider else -0.18
    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=xaxis,
        yaxis=dict(title=init.get("ytitle", yaxis_title), gridcolor="#e0e0e0", rangemode="tozero"),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=10, r=180, t=70 if (dropdown or measures) else 40, b=b_margin),
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
                           x=0, xanchor="left", y=src_y, showarrow=False,
                           align="left", font=dict(size=10, color="#999"))
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
                yaxis_tickformat=None, customdata=None, initial_full=False):
    """Single Canada-only time series.

    Set rangeslider=True for long series (more than a decade or two) to add a
    draggable time slider below the chart. Because these charts have no legend,
    the slider only has to coexist with the source note, which this function
    places below the slider (no overlap). Pass source_note to have it positioned
    correctly for the slider; pass hovertemplate / yaxis_tickformat as needed.

    `initial_full=True` opens on the entire history instead of the recent ~25-year
    window (e.g. the population total, where the long sweep is the point).
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
        # initial_full=True opens on the whole record instead.
        import pandas as pd
        xmin, xmax = df[x_col].min(), df[x_col].max()
        xaxis["range"] = [xmin if initial_full else max(xmin, pd.Timestamp("1999-01-01")), xmax]
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
                    hover_decimals=0, legend_orientation="v", rangemode="tozero",
                    measures=None):
    """Plain multi-line time series for annual data — integer-year safe (no
    date-axis range buttons, unlike the OECD peer charts). `df` is long:
    (x_col, group_col, value_col). Used for government employment by level and
    federal revenue-vs-expenditure.

    `measures`: optional list of {col, label, yaxis_title} — adds a dropdown that
    switches every line between alternative value columns (e.g. nominal vs real),
    re-scaling the y-axis and updating its title. When given, the first measure is
    shown initially and `value_col` is ignored."""
    groups = group_order or list(df[group_col].drop_duplicates())
    cmap = _series_colors(groups, colors)
    subsets = {g: df[df[group_col] == g].sort_values(x_col) for g in groups}
    init_col = measures[0]["col"] if measures else value_col
    init_title = measures[0].get("yaxis_title", yaxis_title) if measures else yaxis_title
    fig = go.Figure()
    for g in groups:
        s = subsets[g]
        fig.add_trace(go.Scatter(
            x=s[x_col], y=s[init_col], name=str(g), mode="lines+markers",
            line=dict(color=cmap[g], width=2.5), marker=dict(size=5),
            hovertemplate=f"{g}: {ytickprefix}%{{y:,.{hover_decimals}f}}{yticksuffix}<extra></extra>"))
    legend = (dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
              if legend_orientation == "v"
              else dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5))
    yaxis = dict(title=init_title, gridcolor="#e0e0e0", rangemode=rangemode,
                 tickprefix=ytickprefix, ticksuffix=yticksuffix)
    if yaxis_tickformat:
        yaxis["tickformat"] = yaxis_tickformat
    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=dict(title="", gridcolor="#e0e0e0"), yaxis=yaxis, legend=legend,
        margin=dict(l=10, r=(175 if legend_orientation == "v" else 20),
                    t=(60 if measures else 30), b=80))
    if measures:
        buttons = [dict(method="update", label=m["label"],
                        args=[{"y": [subsets[g][m["col"]].tolist() for g in groups]},
                              {"yaxis.title.text": m.get("yaxis_title", yaxis_title),
                               "yaxis.autorange": True}])
                   for m in measures]
        fig.update_layout(updatemenus=[dict(buttons=buttons, active=0, x=0,
            xanchor="left", y=1.14, yanchor="top", bgcolor="white",
            bordercolor="#ccc", borderwidth=1, showactive=True)])
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=-0.18, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig


def lines_over_time_geo_select(df, *, group_col, value_col, colors, yaxis_title,
                               div_id, year_col="year", geo_col="geography",
                               geo_level_col="geo_level", geo_name_col="name",
                               default_geo="Canada", source_note=None, height=520,
                               level_labels=None, line_width=2.2, hover_unit="",
                               rangeslider=False, hover_toggle=True, title=None):
    """Multi-line annual time series with a grouped, **searchable native `<select>`**
    to switch which geography is shown — a drop-in replacement for Plotly's
    `updatemenus` dropdown when there are too many options to list flat (the Plotly
    menu overflows and offers no search). The select carries `<optgroup>`s by
    geography level and uses native browser type-ahead, so it scales to dozens of
    options with no need to trim the list.

    `df` is long: (geo_col, geo_level_col, geo_name_col, group_col, year_col,
    value_col). `colors` (dict group->colour) fixes the line set + legend order (only
    groups present in it are drawn). Returns **(fig, controls_html)**: in the .qmd,
    wrap the cell in a `::: {#div_id}` fence, `display(HTML(controls_html))`, then
    `fig.show()`. The select's JS resolves Plotly via `requirejs` (the AMD-bundle
    gotcha) and `restyle`s every line to the chosen geography's data, scoped to
    `#div_id .plotly-graph-div`; the per-geography data blob + handler are namespaced
    by `div_id`, so several can coexist on one page. Works on file:// (no fetch).

    `level_labels` maps a geo_level value to its optgroup label (None → bare options
    listed before the groups); defaults cover national / province / cma.

    `rangeslider=True` adds a draggable x-axis range slider under the chart (with extra
    bottom margin + the source note pushed below it). `hover_toggle=True` (default)
    appends small **Hover on/off** buttons to the controls row, right-aligned next to
    the `<select>`, that flip the figure's `hovermode` via `relayout` — the maps'
    in-chart hover toggle, but placed outside the plot area. `title` (e.g. "Crime
    rates by type") draws an in-figure title "`title` — {geography}" that the selector
    JS keeps in sync — so a downloaded PNG still shows which geography it is (the
    `<select>` itself isn't captured in the image)."""
    import json as _json
    import re as _re
    import html as _html
    import pandas as pd
    groups = [g for g in colors if g in set(df[group_col])]
    years = sorted(df[year_col].unique())
    piv = (df[df[group_col].isin(groups)]
           .pivot_table(index=[geo_col, group_col], columns=year_col, values=value_col))

    def yvals(geo, grp):
        if (geo, grp) in piv.index:
            row = piv.loc[(geo, grp)]
            return [None if (y not in row.index or pd.isna(row[y])) else round(float(row[y]), 1)
                    for y in years]
        return [None] * len(years)

    labels = {"national": None, "province": "Provinces & territories",
              "cma": "Census metropolitan areas"}
    if level_labels:
        labels.update(level_labels)
    order = {"national": 0, "province": 1, "cma": 2}
    meta = (df.drop_duplicates(geo_col)[[geo_col, geo_level_col, geo_name_col]]
            .assign(_o=lambda x: x[geo_level_col].map(lambda l: order.get(l, 9)))
            .sort_values(["_o", geo_name_col]))

    fig = go.Figure()
    for g in groups:
        fig.add_trace(go.Scatter(
            x=years, y=yvals(default_geo, g), name=str(g), mode="lines",
            line=dict(color=colors[g], width=line_width),
            hovertemplate=f"{g}: %{{y:,.0f}}{hover_unit}<extra></extra>"))
    xaxis = dict(title="", gridcolor="#e0e0e0", dtick=5)
    if rangeslider:
        xaxis["rangeslider"] = dict(visible=True, thickness=0.08, bgcolor="#f5f5f5")
    # A title carrying the selected geography keeps that context in a downloaded PNG
    # (the <select> sits outside the figure, so it isn't captured otherwise); the
    # geography-select JS keeps it in sync.
    _dn = df[df[geo_col] == default_geo][geo_name_col]
    default_name = _dn.iloc[0] if len(_dn) else default_geo
    fig.update_layout(
        plot_bgcolor="white", height=height, hovermode="x unified",
        xaxis=xaxis,
        yaxis=dict(title=yaxis_title, gridcolor="#e0e0e0", rangemode="tozero"),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
        margin=dict(l=10, r=190, t=(50 if title else 20), b=(130 if rangeslider else 80)))
    if title:
        fig.update_layout(title=dict(text=f"{title} — {default_name}", x=0, xanchor="left",
                                     font=dict(size=15, color="#333")))
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=0,
                           xanchor="left", y=(-0.30 if rangeslider else -0.16),
                           showarrow=False, font=dict(size=10, color="#999"))

    # Grouped <select> + per-geography data blob + a namespaced restyle handler.
    geo_data, bare, optgroups = {}, [], {}
    for _, r in meta.iterrows():
        geo, lvl, nm = r[geo_col], r[geo_level_col], r[geo_name_col]
        geo_data[geo] = [yvals(geo, g) for g in groups]
        opt = (f'<option value="{_html.escape(str(geo))}"'
               f'{" selected" if geo == default_geo else ""}>{_html.escape(str(nm))}</option>')
        grp_label = labels.get(lvl, lvl)
        (bare if grp_label is None else optgroups.setdefault(grp_label, [])).append(opt)
    sel_inner = "".join(bare) + "".join(
        f'<optgroup label="{_html.escape(str(lbl))}">{"".join(opts)}</optgroup>'
        for lbl, opts in optgroups.items())
    jsid = _re.sub(r"\W", "_", div_id)
    fn = f"geoSel_{jsid}"
    hfn = f"hoverSet_{jsid}"
    # Optional Hover on/off buttons, right-aligned in the controls row (outside the
    # plot), flipping hovermode via relayout — the maps' toggle, but out of the chart.
    hover_html, hover_js = "", ""
    if hover_toggle:
        _bs = ("font-size:0.8em;padding:2px 9px;border:1px solid #ccc;background:#fff;"
               "border-radius:4px;cursor:pointer;color:#555;")
        hover_html = (
            '<span style="margin-left:auto;display:inline-flex;align-items:center;gap:4px;">'
            '<span style="font-size:0.82em;color:#888;">Hover:</span>'
            f'<button type="button" onclick="{hfn}(true)" style="{_bs}">on</button>'
            f'<button type="button" onclick="{hfn}(false)" style="{_bs}">off</button></span>')
        hover_js = (
            f'function {hfn}(on){{'
            f'var gd=document.querySelector("#{div_id} .plotly-graph-div");'
            'var P=window.Plotly;try{if(!P&&window.requirejs)P=window.requirejs("plotly");}catch(e){}'
            f'if(!P||!gd){{return setTimeout(function(){{{hfn}(on);}},300);}}'
            'P.relayout(gd,{hovermode: on ? "x unified" : false});}')
    title_js = ""
    if title:
        title_js = (f'var s=document.getElementById("sel_{jsid}");'
                    'var nm=s?s.options[s.selectedIndex].text:v;'
                    f'P.relayout(gd,{{"title.text":{_json.dumps(title + " — ")}+nm}});')
    controls = (
        '<div style="display:flex;align-items:center;gap:0.5em;flex-wrap:wrap;margin-bottom:0.4em;">'
        f'<label for="sel_{jsid}" style="font-size:0.9em;color:#555;">Geography:</label>'
        f'<select id="sel_{jsid}" onchange="{fn}(this.value)" '
        'style="font-size:0.9em;padding:3px 6px;border:1px solid #ccc;border-radius:4px;">'
        f'{sel_inner}</select>'
        f'{hover_html}</div>'
        f'<script>window.__geo_{jsid}={_json.dumps(geo_data)};'
        f'function {fn}(v){{'
        f'var gd=document.querySelector("#{div_id} .plotly-graph-div");'
        'var P=window.Plotly;try{if(!P&&window.requirejs)P=window.requirejs("plotly");}catch(e){}'
        f'if(!P||!gd||!window.__geo_{jsid}){{return setTimeout(function(){{{fn}(v);}},300);}}'
        f'var ys=window.__geo_{jsid}[v];if(!ys)return;'
        'P.restyle(gd,{y:ys},ys.map(function(_,i){return i;}));'
        f'{title_js}}}'
        f'{hover_js}</script>')
    return fig, controls


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


def category_bar_views(views, label_col, value_col, *, xaxis_title, source_note=None,
                       color="#4e79a7", value_scale=1.0, value_fmt=",.0f",
                       tickprefix="", ticksuffix="", text_col=None, text_fmt="{}",
                       bar_px=24, base_px=170):
    """Horizontal ranked bar with a dropdown to switch among `views`, each a
    (label, dataframe) pair — e.g. size views (top 25 / 50) and thematic groups
    (science, security, regional agencies). Each view's frame is sorted by value;
    selecting a view restyles the bar's x/y/text, resizes the chart to that view's
    bar count, and rescales the x-axis to its range. `text_col` (formatted with
    `text_fmt`) labels each bar — e.g. a share-of-total computed on the full set,
    carried in each view's frame so the labels stay comparable across views."""
    import pandas as pd

    def prep(sub):
        s = sub.copy()
        s["_v"] = pd.to_numeric(s[value_col], errors="coerce") / value_scale
        s = s.dropna(subset=["_v"]).sort_values("_v")     # ascending → largest on top
        y = s[label_col].astype(str).tolist()
        t = ([text_fmt.format(v) for v in s[text_col]]
             if text_col and text_col in s.columns else None)
        return s["_v"].tolist(), y, t

    prepped = [(lab, prep(sub)) for lab, sub in views]
    x0, y0, t0 = prepped[0][1]
    def height(n):
        return base_px + bar_px * n
    fig = go.Figure(go.Bar(
        x=x0, y=y0, orientation="h", marker_color=color,
        text=t0, textposition="auto", cliponaxis=False,
        hovertemplate=f"%{{y}}: {tickprefix}%{{x:{value_fmt}}}{ticksuffix}<extra></extra>"))
    buttons = [dict(method="update", label=lab,
                    args=[{"x": [x], "y": [y], "text": [t]},
                          {"height": height(len(y)), "yaxis.categoryarray": y,
                           "yaxis.categoryorder": "array", "xaxis.autorange": True}])
               for lab, (x, y, t) in prepped]
    fig.update_layout(
        plot_bgcolor="white", showlegend=False, height=height(len(y0)),
        xaxis=dict(title=xaxis_title, gridcolor="#e0e0e0",
                   tickprefix=tickprefix, ticksuffix=ticksuffix),
        yaxis=dict(title="", categoryorder="array", categoryarray=y0),
        margin=dict(l=10, r=70, t=52, b=70),
        updatemenus=[dict(buttons=buttons, active=0, x=0, xanchor="left", y=1.0,
                          yanchor="bottom", bgcolor="white", bordercolor="#ccc",
                          borderwidth=1, showactive=True)])
    if source_note:
        fig.add_annotation(text=source_note, xref="paper", yref="paper", x=1,
                           xanchor="right", y=-0.06, showarrow=False,
                           font=dict(size=10, color="#999"))
    return fig
