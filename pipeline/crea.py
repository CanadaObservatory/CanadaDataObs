"""CREA MLS® Home Price Index — public educational charts.

Used **with written permission from CREA for educational public use** on this site.
Per that permission we publish *charts* (display), not the raw dataset: this module
loads the monthly HPI workbook at **render time** and builds figures, and **never
writes CREA data to `data/` or commits it** — only the rendered charts are published.

The monthly zip is cached in the git-ignored `internal/` dir (reused locally; a fresh
CI checkout downloads the latest month). Every figure carries the CREA attribution.

Data: `Seasonally Adjusted (M).xlsx` inside `MLS_HPI_<Month>_<Year>.zip` — per-market
sheets with `*_Benchmark_SA` columns + an `AGGREGATE` sheet (`Composite_Benchmark_SA`).
"""

import io
import os
import zipfile
import requests
import pandas as pd
import plotly.graph_objects as go

ATTRIB = ("Source: CREA MLS® Home Price Index, © The Canadian Real Estate Association. "
          "Used with permission for educational purposes.")
_HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}

# (CREA workbook sheet name, display label)
MARKETS = [
    ("GREATER_VANCOUVER", "Greater Vancouver"),
    ("GREATER_TORONTO",   "Greater Toronto"),
    ("OTTAWA",            "Ottawa"),
    ("MONTREAL_CMA",      "Montreal CMA"),
    ("CALGARY",           "Calgary"),
    ("EDMONTON",          "Edmonton"),
    ("WINNIPEG",          "Winnipeg"),
    ("HALIFAX_DARTMOUTH", "Halifax"),
]
TYPES = [
    ("Single_Family_Benchmark_SA", "Detached (single-family)", "#1f77b4"),
    ("Townhouse_Benchmark_SA",     "Townhouse",                "#ff7f0e"),
    ("Apartment_Benchmark_SA",     "Apartment / condo",        "#2ca02c"),
]
CITY_PALETTE = ["#d62728", "#1f77b4", "#2ca02c", "#9467bd", "#ff7f0e",
                "#8c564b", "#17becf", "#bcbd22"]


def _zip_bytes(cache_dir):
    """Reuse a cached MLS_HPI_*.zip in `cache_dir` (git-ignored internal/), else
    download the latest available month. Raises if none can be obtained."""
    if os.path.isdir(cache_dir):
        cached = sorted(f for f in os.listdir(cache_dir)
                        if f.startswith("MLS_HPI_") and f.endswith(".zip"))
        if cached:
            return open(os.path.join(cache_dir, cached[-1]), "rb").read()
    import datetime  # current month is fine here; only used to pick a filename
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    # try the last few months across the plausible current/previous year
    candidates = []
    for yr in (2026, 2025):
        for m in months:
            candidates.append((m, yr))
    for m, yr in candidates:
        url = f"https://www.crea.ca/files/mls-hpi-data/MLS_HPI_{m}_{yr}.zip"
        try:
            r = requests.get(url, headers=_HDR, timeout=90)
        except Exception:
            continue
        if r.status_code == 200 and r.content[:2] == b"PK":
            os.makedirs(cache_dir, exist_ok=True)
            open(os.path.join(cache_dir, f"MLS_HPI_{m}_{yr}.zip"), "wb").write(r.content)
            return r.content
    raise RuntimeError("CREA MLS HPI zip unavailable (no cache, download failed)")


def load_crea(root="."):
    """Return (sheets dict, aggregate df, month label) from the latest CREA workbook."""
    z = zipfile.ZipFile(io.BytesIO(_zip_bytes(os.path.join(root, "internal"))))
    xls = pd.ExcelFile(io.BytesIO(z.read("Seasonally Adjusted (M).xlsx")))
    sheets = {s: xls.parse(s) for s, _ in MARKETS}
    agg = xls.parse("AGGREGATE")
    month = pd.Timestamp(agg["Date"].max()).strftime("%B %Y")
    return sheets, agg, month


def _src(fig, note, y=-0.18):
    fig.add_annotation(text=note, xref="paper", yref="paper", x=0, xanchor="left",
                       y=y, showarrow=False, font=dict(size=10, color="#999"))


def fig_price_by_type(sheets, month):
    """Grouped bar: latest benchmark price by city × dwelling type."""
    rows = []
    for sheet, label in MARKETS:
        last = sheets[sheet].dropna(subset=["Single_Family_Benchmark_SA"]).iloc[-1]
        rows.append({"city": label, **{c: last[c] for c, _, _ in TYPES}})
    table = pd.DataFrame(rows).sort_values("Single_Family_Benchmark_SA", ascending=False)
    fig = go.Figure()
    for col, name, color in TYPES:
        fig.add_trace(go.Bar(x=table["city"], y=table[col], name=name, marker_color=color,
                             hovertemplate=f"{name}: $%{{y:,.0f}}<extra>%{{x}}</extra>"))
    fig.update_layout(barmode="group", plot_bgcolor="white",
        yaxis=dict(title="Benchmark price", tickprefix="$", tickformat=",", gridcolor="#e0e0e0"),
        xaxis=dict(title=""), height=520, margin=dict(b=110, t=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
    _src(fig, f"{ATTRIB} Benchmark (seasonally adjusted), {month}.", y=-0.22)
    return fig


def fig_price_time_series(sheets):
    """Detached (single-family) benchmark price over time, by city (with slider)."""
    fig = go.Figure()
    for (sheet, label), color in zip(MARKETS, CITY_PALETTE):
        df = sheets[sheet][["Date", "Single_Family_Benchmark_SA"]].dropna()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Single_Family_Benchmark_SA"],
                                 name=label, mode="lines", line=dict(color=color, width=2),
                                 hovertemplate=f"{label}: $%{{y:,.0f}}<extra>%{{x|%b %Y}}</extra>"))
    fig.update_layout(plot_bgcolor="white",
        yaxis=dict(title="Benchmark price (detached)", tickprefix="$", tickformat=",", gridcolor="#e0e0e0"),
        xaxis=dict(title="", gridcolor="#e0e0e0",
                   rangeslider=dict(visible=True, thickness=0.08, bgcolor="#f5f5f5")),
        height=560, margin=dict(b=120, t=30, r=160),
        legend=dict(orientation="v", x=1.02, y=1))
    _src(fig, ATTRIB, y=-0.30)
    return fig


def fig_price_to_income(agg, root="."):
    """National composite benchmark ÷ median after-tax income, over time.

    CREA composite is nominal $; median income is in 2024 constant $. Deflate the
    benchmark to 2024 $ via CPI, then divide → "years of median after-tax income"."""
    inc = pd.read_csv(os.path.join(root, "data/income/statcan_median_income.csv"),
                      parse_dates=["date"])
    inc = inc.assign(year=inc["date"].dt.year).set_index("year")["median_income"]
    cpi = pd.read_csv(os.path.join(root, "data/economics/statcan_cpi.csv"),
                      parse_dates=["date"])
    cpi = cpi.assign(year=cpi["date"].dt.year).groupby("year")["cpi_value"].mean()
    cpi2024 = cpi.loc[2024]
    agg_a = (agg.assign(year=agg["Date"].dt.year)
                .groupby("year")["Composite_Benchmark_SA"].mean())
    rows = []
    for yr in sorted(set(agg_a.index) & set(inc.index)):
        bench_real = agg_a.loc[yr] * (cpi2024 / cpi.loc[yr])
        rows.append({"year": yr, "ratio": bench_real / inc.loc[yr]})
    ratio = pd.DataFrame(rows)
    fig = go.Figure(go.Scatter(x=ratio["year"], y=ratio["ratio"], mode="lines+markers",
                               line=dict(color="#d62728", width=3),
                               hovertemplate="%{y:.1f}× income<extra>%{x}</extra>"))
    fig.update_layout(plot_bgcolor="white",
        yaxis=dict(title="Years of median after-tax income", gridcolor="#e0e0e0", rangemode="tozero"),
        xaxis=dict(title="", gridcolor="#e0e0e0"), height=480, margin=dict(b=90, t=30),
        showlegend=False)
    _src(fig, f"{ATTRIB} Benchmark deflated to 2024 $ via CPI; income: StatCan 11-10-0190-01.", y=-0.16)
    return fig
