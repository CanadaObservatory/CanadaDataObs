"""
Reusable Plotly chart-building functions for DataCan.
Enforces consistent styling across all topics.
"""

import plotly.graph_objects as go
from pipeline.config import (
    CANADA_COLOR, PEER_COLOR, OECD_AVG_COLOR,
    HIGHLIGHT_WIDTH, PEER_WIDTH, HIGHLIGHT_COUNTRY,
    PEER_COUNTRIES, COMPARATOR_COLORS, DATA_DATE, get_data_date,
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


def single_line(df, x_col, y_col, title, yaxis_title, color=CANADA_COLOR):
    """Simple single-line time series chart."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode="lines+markers",
        line=dict(color=color, width=HIGHLIGHT_WIDTH),
        marker=dict(size=5),
        hovertemplate="%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(_base_layout(title, yaxis_title))
    fig.update_layout(showlegend=False)
    return fig
