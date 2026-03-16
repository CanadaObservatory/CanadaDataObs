"""
Reusable Plotly chart-building functions for DataCan.
Enforces consistent styling across all topics.
"""

import plotly.graph_objects as go
from pipeline.config import (
    CANADA_COLOR, PEER_COLOR, OECD_AVG_COLOR,
    HIGHLIGHT_WIDTH, PEER_WIDTH, HIGHLIGHT_COUNTRY,
    PEER_COUNTRIES, DATA_DATE,
)


def _base_layout(title, yaxis_title, xaxis_title="Year", range_slider=True,
                  has_legend=True):
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
            x=0, xanchor="left", y=1.18,
        )

    # Spacing depends on whether there's a legend below the chart
    if has_legend:
        legend_y = -0.3
        source_y = -0.42
        bottom_margin = 140
    else:
        legend_y = -0.2
        source_y = -0.2
        bottom_margin = 80

    return go.Layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis=xaxis_config,
        yaxis=dict(title=yaxis_title, gridcolor="#e0e0e0"),
        plot_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=legend_y,
            xanchor="center",
            x=0.5,
            itemclick="toggle",
            itemdoubleclick="toggleothers",
        ),
        margin=dict(b=bottom_margin, t=100),
        annotations=[
            dict(
                text=f"Data as of: {DATA_DATE}",
                xref="paper", yref="paper",
                x=1, y=source_y,
                showarrow=False,
                font=dict(size=10, color="#999"),
            )
        ],
    )


def peer_comparison_line(df, x_col, y_col, title, yaxis_title,
                         country_col="country_code", name_col="country_name",
                         highlight=None):
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
    """
    if highlight is None:
        highlight = [HIGHLIGHT_COUNTRY]

    fig = go.Figure()

    # Add peer countries first (grey, behind)
    countries = df[country_col].unique()

    for code in sorted(countries):
        if code in highlight:
            continue
        subset = df[df[country_col] == code]
        name = subset[name_col].iloc[0] if name_col in subset.columns else code
        fig.add_trace(go.Scatter(
            x=subset[x_col],
            y=subset[y_col],
            name=name,
            mode="lines",
            line=dict(color=PEER_COLOR, width=PEER_WIDTH),
            opacity=0.6,
            hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>",
        ))

    # Add highlighted countries on top (red, bold)
    for code in highlight:
        subset = df[df[country_col] == code]
        if subset.empty:
            continue
        name = subset[name_col].iloc[0] if name_col in subset.columns else code
        fig.add_trace(go.Scatter(
            x=subset[x_col],
            y=subset[y_col],
            name=name,
            mode="lines+markers",
            line=dict(color=CANADA_COLOR, width=HIGHLIGHT_WIDTH),
            marker=dict(size=5),
            hovertemplate=f"<b>{name}: %{{y:.2f}}</b><extra></extra>",
        ))

    fig.update_layout(_base_layout(title, yaxis_title))
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
