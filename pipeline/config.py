"""
Central configuration for DataCan data pipeline.
Defines peer groups, data source IDs, and shared constants.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Fallback shown only if a dataset's metadata sidecar is missing. Real freshness
# always comes from the metadata sidecar via get_data_date(); we intentionally do
# NOT default to today's date — that would imply the data is fresher than it is.
DATA_DATE = "date unavailable"


def get_data_date(csv_path):
    """Get the latest observation date from a dataset's metadata sidecar.

    Falls back to today's date if no metadata file exists.
    """
    import json
    meta_path = Path(csv_path).with_suffix(".json")
    if meta_path.exists():
        with open(meta_path) as f:
            meta = json.load(f)
        return meta.get("latest_observation_date", DATA_DATE)
    return DATA_DATE


def get_retrieved_date(csv_path):
    """Date the dataset was last fetched (metadata sidecar `retrieved_at`), as
    YYYY-MM-DD — i.e. when the data was *accessed*, distinct from its latest
    observation year. Falls back to today's date."""
    import json
    meta_path = Path(csv_path).with_suffix(".json")
    if meta_path.exists():
        with open(meta_path) as f:
            ra = json.load(f).get("retrieved_at")
        if ra:
            return str(ra)[:10]
    return DATA_DATE

# --- OECD Peer Group ---
# Broader than G7: includes all comparable advanced economies

PEER_COUNTRIES = {
    # G7
    "CAN": "Canada",
    "USA": "United States",
    "GBR": "United Kingdom",
    "DEU": "Germany",
    "FRA": "France",
    "ITA": "Italy",
    "JPN": "Japan",
    # Extended peers
    "AUS": "Australia",
    "KOR": "South Korea",
    "NLD": "Netherlands",
    "SWE": "Sweden",
    "CHE": "Switzerland",
    "NOR": "Norway",
    "DNK": "Denmark",
    "FIN": "Finland",
    "ISR": "Israel",
    "NZL": "New Zealand",
    # Dropped 2026-05: Belgium & Austria (small EU economies, little distinct
    # signal) and Ireland (GDP per capita distorted by multinational accounting).
}

PEER_CODES = list(PEER_COUNTRIES.keys())

# Country to highlight in charts
HIGHLIGHT_COUNTRY = "CAN"

# Named comparators get their own colour (Canada itself stays red). Every other
# peer is drawn in light grey. Kept here so the highlighted set is a one-line
# change. Order in legends is handled in charts.py (alphabetical, these on top).
COMPARATOR_COLORS = {
    "USA": "#1f77b4",  # blue
    "AUS": "#ff7f0e",  # orange
    "DEU": "#2ca02c",  # green
    "GBR": "#9467bd",  # purple
    "SWE": "#8c564b",  # brown
}

# The other 11 peers each ALSO own a fixed identity colour, but their lines draw
# grey + legend-hidden until the reader activates one from the legend, then it
# snaps to this colour (and back to grey when toggled off). The swap is wired
# site-wide in _includes/peer-legend-colours.html, which reads each grey trace's
# fixed colour from its Plotly `meta.fixedColor` (stashed by the chart builders).
# Keeping the default view calm (only Canada + the 5 comparators + average in
# colour) while giving every country a distinct, CONSISTENT colour the moment it
# is shown — and because inactive peers are grey, a colour clash can only ever
# appear between two countries the reader deliberately shows together.
#
# Palette = matplotlib tab20: COMPARATOR_COLORS above are its saturated members;
# these are tab20's remaining saturated hues (cyan/pink/olive) + light tints,
# each tint sitting in its dark partner's hue family but separated by lightness
# (Korea light-blue vs USA blue, Finland light-purple vs UK purple, …). The one
# soft pair is Israel/France (both pink), only visible if both are activated.
PEER_EXTRA_COLORS = {
    "JPN": "#17becf",  # cyan
    "FRA": "#e377c2",  # pink
    "ITA": "#bcbd22",  # olive
    "KOR": "#aec7e8",  # light blue    (vs USA blue, by lightness)
    "NLD": "#ffbb78",  # light orange  (vs AUS orange)
    "CHE": "#98df8a",  # light green   (vs DEU green)
    "NOR": "#9edae5",  # light cyan    (vs JPN cyan)
    "DNK": "#ff9896",  # salmon        (vs CAN red — Canada is bold + markers)
    "FIN": "#c5b0d5",  # light purple  (vs GBR purple)
    "ISR": "#f7b6d2",  # light pink    (vs FRA pink)
    "NZL": "#c49c94",  # taupe         (vs SWE brown)
}

# Comparators shown ON LOAD for the peer line charts (owner, 2026-06-18 site review):
# Canada + US + Australia + Germany + the peer average. The other named comparators
# (Sweden, UK) keep their colour + top-of-legend rank but start hidden (legendonly),
# and the 11 grey peers stay hidden too, so a busy 17-line chart opens legible. Global
# default for peer_comparison_line / _by_age; a chart passes initial_visible=[...] to
# override (e.g. ["USA"] on fertility, or ["GBR"] where the prose singles out the UK).
DEFAULT_VISIBLE_COMPARATORS = ["USA", "AUS", "DEU"]

# --- Statistics Canada Table IDs ---
STATCAN_TABLES = {
    "population_quarterly": "17-10-0009-01",  # Population estimates, quarterly
    "population_components": "17-10-0008-01",  # Components of demographic growth
    "cpi": "18-10-0004-01",  # Consumer Price Index, monthly
}

# --- OECD Rate Limiting ---
OECD_MAX_REQUESTS_PER_HOUR = 60
OECD_REQUEST_DELAY_SECONDS = 2  # Conservative delay between requests

# --- Chart Styling ---
CANADA_COLOR = "#d62728"  # Red for Canada
PEER_COLOR = "#bdbdbd"    # Light grey for non-highlighted peers
OECD_AVG_COLOR = "#555555"  # Dark grey for OECD average (blue is now the US)
HIGHLIGHT_WIDTH = 3
PEER_WIDTH = 1.5
PEER_ACTIVE_WIDTH = 2.6  # a grey peer's width once activated from the legend
#                          (between PEER_WIDTH and HIGHLIGHT_WIDTH; thick enough
#                           that the lighter tab20 tints read clearly as lines)

# Site attribution appended beneath every chart's source note (see the Figure.show
# interceptor in charts.py). Change here to update it everywhere.
BRAND = "Canada Observatory"


# ============================================================================
# Indicator registry
# ----------------------------------------------------------------------------
# A single declarative source of truth for every dataset the pipeline fetches.
# run_pipeline.py iterates this list; adding an indicator means adding a row
# here (plus, for a new chart, a block in the relevant .qmd page).
#
# source dispatch (see run_pipeline.py):
#   "oecd"    -> generic SDMX fetch via fetch_oecd_indicator(ind)
#   "statcan" -> generic single-series table fetch via fetch_statcan_indicator(ind)
#   "worldbank" -> generic World Bank API fetch via fetch_worldbank_indicator(ind)
#   "custom"  -> bespoke function named by `fetch_fn` (irregular reshaping)
#
# OECD `key` uses the literal placeholder {countries}, replaced at fetch time
# with the "+"-joined peer codes. All keys below were validated against the live
# SDMX API (sdmx.oecd.org) — see the dimension comments.
# ============================================================================

@dataclass(frozen=True)
class Indicator:
    id: str
    section: str                       # data/<section>/ subfolder + page grouping
    source: str                        # "oecd" | "statcan" | "custom"
    title: str
    unit: str
    frequency: str                     # "annual" | "monthly" | "quarterly"
    value_col: str = "value"           # output value column name
    source_table: str = ""             # human label stored in metadata sidecar
    chart_recipe: str = "line"         # "line" | "ranked_bar" | "single"
    # --- OECD SDMX ---
    dataflow: Optional[str] = None     # e.g. "OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3"
    key: Optional[str] = None          # SDMX key with {countries} placeholder
    start_period: int = 2000
    # --- World Bank API (generic, fetch_worldbank_indicator) ---
    wb_indicator: Optional[str] = None  # e.g. "NE.GDI.FTOT.ZS"
    # --- Bank of Canada Valet API (generic, fetch_boc_indicator) ---
    boc_series: dict = field(default_factory=dict)  # output column -> Valet series code
    # --- StatCan generic single-series ---
    statcan_table: Optional[str] = None
    statcan_filters: dict = field(default_factory=dict)  # column -> exact value
    date_format: Optional[str] = None  # REF_DATE parse format, e.g. "%Y-%m" / "%Y"
    # --- bespoke fetchers (population, cpi, energy, happiness) ---
    fetch_fn: Optional[str] = None     # function name resolved in run_pipeline
    # --- optional post-clean hook: df -> df (e.g. cap EO projection years) ---
    transform: Optional[Callable] = None
    # --- output ---
    output_subpath: Optional[str] = None  # default f"{source}_{id}.csv"
    notes: str = ""

    @property
    def out_path(self):
        sub = self.output_subpath or f"{self.source}_{self.id}.csv"
        return DATA_DIR / self.section / sub


# Convenience for keys that span the full peer group
_C = "{countries}"


def _drop_future_years(df):
    """Drop projection years beyond the current calendar year.

    The OECD Economic Outlook publishes ~2 years of forecasts past the latest
    actual; we cap at the current year and label the recent tail as projections
    in the chart, rather than presenting forecasts as observed history.
    """
    from datetime import date
    return df[df["year"] <= date.today().year].copy()


INDICATORS = [
    # ----- Population (bespoke: multi-geography / fiscal-year reshaping) -----
    Indicator("population_quarterly", "population", "custom",
              "Population estimates (quarterly)", "persons", "quarterly",
              fetch_fn="fetch_population_quarterly",
              output_subpath="statcan_population_quarterly.csv",
              source_table="Statistics Canada 17-10-0009-01"),
    Indicator("population_components", "population", "custom",
              "Components of population change", "persons", "annual",
              fetch_fn="fetch_population_components",
              output_subpath="statcan_population_components.csv",
              source_table="Statistics Canada 17-10-0008-01"),
    Indicator("temp_residents", "population", "statcan",
              "Non-permanent residents", "persons", "quarterly",
              value_col="npr_count", date_format="%Y-%m",
              statcan_table="17-10-0121-01",
              statcan_filters={"GEO": "Canada",
                               "Non-permanent resident types": "Total, non-permanent residents"},
              source_table="Statistics Canada 17-10-0121-01"),
    # Age & aging (2026-06 Branch-1 demographics expansion)
    Indicator("age_structure", "population", "custom",
              "Population by age and gender", "persons", "annual",
              fetch_fn="fetch_age_structure",
              output_subpath="statcan_age_structure.csv",
              source_table="Statistics Canada 17-10-0005-01"),
    Indicator("interprovincial_migration", "population", "custom",
              "Net interprovincial migration", "persons (net)", "annual",
              fetch_fn="fetch_interprovincial_migration",
              output_subpath="statcan_interprovincial_migration.csv",
              source_table="Statistics Canada 17-10-0020-01"),
    Indicator("fertility_rate", "population", "worldbank",
              "Total fertility rate", "births per woman", "annual",
              value_col="fertility_rate", chart_recipe="line",
              wb_indicator="SP.DYN.TFRT.IN", start_period=1960,
              source_table="World Bank WDI (UN World Population Prospects)"),
    Indicator("old_age_dependency", "population", "worldbank",
              "Old-age dependency ratio", "people 65+ per 100 aged 15–64", "annual",
              value_col="old_age_dependency", chart_recipe="line",
              wb_indicator="SP.POP.DPND.OL", start_period=1960,
              source_table="World Bank WDI (UN World Population Prospects)"),

    # ----- Economy & Jobs (OECD) -----
    Indicator("gdp_per_capita", "economics", "oecd",
              "GDP per capita (PPP)", "USD (PPP, current prices)", "annual",
              value_col="gdp_per_capita", chart_recipe="ranked_bar",
              dataflow="OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_HCPC,2.0",
              key=f"A.{_C}.S1.S1.B1GQ_POP._Z._Z._Z.USD_PPP_PS.V.N.T0102",
              source_table="OECD National Accounts (SNA_TABLE1)"),
    Indicator("labour_productivity", "economics", "oecd",
              "Labour productivity (GDP per hour)", "USD PPP per hour", "annual",
              value_col="gdp_per_hour", chart_recipe="ranked_bar",
              dataflow="OECD.SDD.TPS,DSD_PDB@DF_PDB_LV,1.0",
              key=f"{_C}.A.GDPHRS._T.USD_PPP_H.Q._Z._Z._Z",
              source_table="OECD Productivity Database (PDB_LV)"),
    Indicator("unemployment", "economics", "oecd",
              "Unemployment rate", "% of labour force", "annual",
              value_col="unemployment_rate", chart_recipe="ranked_bar",
              dataflow="OECD.SDD.STES,DSD_KEI@DF_KEI,4.0",
              key=f"{_C}.A.UNEMP.PT_LF._T..",
              source_table="OECD Key Economic Indicators (KEI)"),
    Indicator("real_gdp_growth", "economics", "oecd",
              "Real GDP growth", "annual % change", "annual",
              value_col="real_gdp_growth", chart_recipe="line",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.GDPV_ANNPCT.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("employment_rate", "economics", "oecd",
              "Employment rate (15–64)", "% of working-age population", "annual",
              value_col="employment_rate", chart_recipe="ranked_bar",
              dataflow="OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP_WAP_Q",
              key=f"{_C}.EMP_WAP.PT_WAP_SUB..Y._T.Y15T64..A", start_period=2005,
              source_table="OECD Labour Force Statistics"),
    Indicator("current_account", "economics", "oecd",
              "Current account balance", "% of GDP", "annual",
              value_col="current_account", chart_recipe="line",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.CBGDPR.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("business_investment", "economics", "worldbank",
              "Investment (gross fixed capital formation)", "% of GDP", "annual",
              value_col="investment_pct_gdp", chart_recipe="ranked_bar",
              wb_indicator="NE.GDI.FTOT.ZS",
              source_table="World Bank / OECD National Accounts"),
    # CPI is bespoke (All-items + Canada filter, computes YoY inflation)
    Indicator("cpi", "economics", "custom",
              "Consumer Price Index (inflation)", "index (2002=100)", "monthly",
              fetch_fn="fetch_cpi", output_subpath="statcan_cpi.csv",
              source_table="Statistics Canada 18-10-0004-01"),
    # Quarterly real GDP level (chained 2017$, SAAR) — the "are we in a recession?"
    # series; the chart computes quarter-over-quarter % change (StatCan's published
    # "% change" is q/q, validated against the table). Canada-only, 1961–.
    Indicator("gdp_quarterly", "economics", "statcan",
              "Real GDP (quarterly)", "chained 2017 $ (SAAR)", "quarterly",
              value_col="gdp", date_format="%Y-%m",
              statcan_table="36-10-0104-01",
              statcan_filters={"GEO": "Canada",
                               "Estimates": "Gross domestic product at market prices",
                               "Prices": "Chained (2017) dollars",
                               "Seasonal adjustment": "Seasonally adjusted at annual rates"},
              output_subpath="statcan_gdp_quarterly.csv",
              source_table="Statistics Canada 36-10-0104-01"),
    # Food CPI (the most-felt cost-of-living component) as its own series, like
    # rent_cpi — kept separate from statcan_cpi.csv so the all-items deflator used
    # elsewhere (crea.py) stays single-series.
    Indicator("food_cpi", "economics", "statcan",
              "Food CPI", "index (2002=100)", "monthly",
              value_col="food_index", date_format="%Y-%m",
              statcan_table="18-10-0004-01",
              statcan_filters={"GEO": "Canada",
                               "Products and product groups": "Food"},
              output_subpath="statcan_food_cpi.csv",
              source_table="Statistics Canada 18-10-0004-01"),
    # CPI-trim, the Bank of Canada's preferred core-inflation measure — published
    # directly as a year-over-year % change (no computation needed).
    Indicator("cpi_trim", "economics", "statcan",
              "CPI-trim (core inflation)", "% (year-over-year)", "monthly",
              value_col="cpi_trim_yoy", date_format="%Y-%m",
              statcan_table="18-10-0256-01",
              statcan_filters={"GEO": "Canada",
                               "Alternative measures": "Measure of core inflation based on a trimmed mean approach, CPI-trim (year-over-year percent change)"},
              output_subpath="statcan_cpi_trim.csv",
              source_table="Statistics Canada 18-10-0256-01"),
    # Merchandise trade with the US (export dependence + balances) — bespoke
    # multi-series; the salient US-tariff/trade exposure indicator.
    Indicator("trade_us", "economics", "custom",
              "Merchandise trade with the US", "$ millions", "monthly",
              fetch_fn="fetch_trade_us", output_subpath="statcan_trade_us.csv",
              source_table="Statistics Canada 12-10-0011-01"),
    # Current unemployment rate by CMA (LFS 3-month moving average) — the live
    # by-city map source, replacing the frozen 2021-Census snapshot.
    Indicator("cma_unemployment", "economics", "custom",
              "Unemployment rate by CMA (current)", "%", "monthly",
              fetch_fn="fetch_cma_unemployment",
              output_subpath="statcan_cma_unemployment.csv",
              source_table="Statistics Canada 14-10-0459-01 (Labour Force Survey)"),
    # Unemployment + employment rate by age bracket (one OECD LFS flow → two CSVs;
    # out_path tracks the unemployment file for the STALE fallback).
    Indicator("labour_by_age", "economics", "custom",
              "Unemployment & employment rate by age", "%", "annual",
              fetch_fn="fetch_labour_by_age",
              output_subpath="oecd_unemployment_by_age.csv",
              source_table="OECD Labour Force Statistics (DSD_LFS@DF_IALFS_INDIC)"),

    # ----- Bank of Canada (Valet API) — interest rates, exchange rate -----
    # Policy rate: the Bank Rate (V122530) is the consistent long-run series (1935–),
    # charted against CPI inflation on the cost-of-living page.
    Indicator("boc_policy_rate", "economics", "boc",
              "Bank of Canada policy rate", "%", "monthly",
              boc_series={"policy_rate": "V122530"}, start_period=1935,
              output_subpath="boc_policy_rate.csv",
              source_table="Bank of Canada (Bank Rate, V122530)"),
    Indicator("boc_usdcad", "economics", "boc",
              "CAD/US dollar exchange rate", "USD per CAD", "daily",
              boc_series={"usdcad": "FXUSDCAD"}, start_period=2017,
              output_subpath="boc_usdcad.csv",
              source_table="Bank of Canada (daily average exchange rate)"),
    Indicator("boc_rates", "housing", "boc",
              "Prime & 5-year mortgage rate", "%", "weekly",
              boc_series={"prime": "V80691311", "mortgage_5yr": "V80691335"},
              start_period=1980, output_subpath="boc_rates.csv",
              source_table="Bank of Canada (prime rate; conventional 5-year mortgage rate)"),
    Indicator("boc_bond_yields", "economics", "boc",
              "Government of Canada bond yields by term", "%", "daily",
              boc_series={"y2": "BD.CDN.2YR.DQ.YLD", "y3": "BD.CDN.3YR.DQ.YLD",
                          "y5": "BD.CDN.5YR.DQ.YLD", "y7": "BD.CDN.7YR.DQ.YLD",
                          "y10": "BD.CDN.10YR.DQ.YLD", "ylong": "BD.CDN.LONG.DQ.YLD"},
              start_period=2001, output_subpath="boc_bond_yields.csv",
              source_table="Bank of Canada (Government of Canada benchmark bond yields)"),

    # ----- Government & Public Finances (OECD Economic Outlook) -----
    Indicator("govt_debt", "fiscal", "oecd",
              "Government gross debt", "% of GDP", "annual",
              value_col="govt_debt", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.GGFLQ.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("net_debt", "fiscal", "oecd",
              "Government net debt", "% of GDP", "annual",
              value_col="net_debt", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.GNFLQ.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("govt_balance", "fiscal", "oecd",
              "Government budget balance", "% of GDP (surplus +/deficit −)", "annual",
              value_col="govt_balance", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.NLGQ.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("govt_revenue", "fiscal", "oecd",
              "Government revenue", "% of GDP", "annual",
              value_col="govt_revenue", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.YRGTQ.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("govt_interest", "fiscal", "oecd",
              "Government interest costs", "% of GDP", "annual",
              value_col="govt_interest", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.GNINTQ.A",
              transform=_drop_future_years,
              source_table="OECD Economic Outlook"),
    Indicator("defence", "fiscal", "worldbank",
              "Defence spending", "% of GDP", "annual",
              value_col="defence_pct_gdp", chart_recipe="ranked_bar",
              wb_indicator="MS.MIL.XPND.GD.ZS",
              source_table="World Bank (data from SIPRI)"),

    # ----- Government (workforce + federal spending) -----
    # Grouped under the "Public Finances" nav dropdown alongside the fiscal
    # peer-comparison page. Descriptive only — no scorecard valence (size of
    # government and spending levels are political choices, like govt revenue).
    #   OECD peer anchor (general government employment as a share of employment):
    Indicator("govt_employment", "government", "oecd",
              "Government employment", "% of total employment", "annual",
              value_col="govt_emp_pct", chart_recipe="ranked_bar",
              dataflow="OECD.GOV.GIP,DSD_GOV@DF_GOV_EMPPS_REP_2025,1.0",
              key=f"A.{_C}.EMPG.PT_EMP.S13.2025.EMPPS_REP", start_period=2007,
              source_table="OECD Government at a Glance 2025"),
    #   Workforce (bespoke multi-series — see pipeline/fetch_government.py):
    Indicator("govt_employment_by_level", "government", "custom",
              "Government employment by level", "jobs", "annual",
              fetch_fn="fetch_govt_employment_by_level",
              output_subpath="statcan_govt_employment_by_level.csv",
              source_table="Statistics Canada 36-10-0489-01"),
    Indicator("public_sector_composition", "government", "custom",
              "Public sector by institutional sector", "persons", "annual",
              fetch_fn="fetch_public_sector_composition",
              output_subpath="statcan_public_sector_composition.csv",
              source_table="Statistics Canada 10-10-0025-01 (archived)"),
    Indicator("fps_population", "government", "custom",
              "Federal public service population", "employees", "annual",
              fetch_fn="fetch_fps_population",
              output_subpath="tbs_fps_population.csv",
              source_table="TBS Federal public service statistics"),
    Indicator("fps_by_department", "government", "custom",
              "Federal public service by department", "employees", "annual",
              fetch_fn="fetch_fps_by_department",
              output_subpath="tbs_fps_by_department.csv",
              source_table="TBS Federal public service statistics"),
    Indicator("fps_demographics", "government", "custom",
              "Federal public service demographics", "employees", "annual",
              fetch_fn="fetch_fps_demographics",
              output_subpath="tbs_fps_demographics.csv",
              source_table="TBS Federal public service statistics"),
    Indicator("fps_executive", "government", "custom",
              "Federal public service executives", "employees", "annual",
              fetch_fn="fetch_fps_executive",
              output_subpath="infobase_fps_executive.csv",
              source_table="GC InfoBase (employee population by executive level)"),
    #   Spending:
    Indicator("federal_finance", "government", "custom",
              "Federal revenue & expenditure (long run)", "$ millions / % of GDP", "annual",
              fetch_fn="fetch_federal_finance_longrun",
              output_subpath="statcan_federal_finance.csv",
              source_table="Statistics Canada 36-10-0477-01, 36-10-0222-01"),
    Indicator("federal_expense_by_type", "government", "custom",
              "Federal expense by economic type", "$ millions", "annual",
              fetch_fn="fetch_federal_expense_by_type",
              output_subpath="statcan_federal_expense_by_type.csv",
              source_table="Statistics Canada 10-10-0016-01"),
    Indicator("govt_spending_by_function", "government", "custom",
              "Government spending by function (COFOG)", "$ millions", "annual",
              fetch_fn="fetch_govt_spending_by_function",
              output_subpath="statcan_govt_spending_by_function.csv",
              source_table="Statistics Canada 10-10-0005-01 (CCOFOG)"),
    Indicator("federal_spending_by_object", "government", "custom",
              "Federal spending by standard object", "$", "annual",
              fetch_fn="fetch_federal_spending_by_object",
              output_subpath="infobase_federal_by_object.csv",
              source_table="GC InfoBase / Public Accounts of Canada"),
    Indicator("federal_spending_by_dept", "government", "custom",
              "Federal spending by department", "$", "annual",
              fetch_fn="fetch_federal_spending_by_dept",
              output_subpath="infobase_federal_by_dept.csv",
              source_table="GC InfoBase / Public Accounts of Canada"),

    # ----- Housing & Cost of Living -----
    Indicator("house_price_real", "housing", "oecd",
              "Real house price index", "index (2015=100)", "annual",
              value_col="house_price_real", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0",
              key=f"{_C}.A.RHP.",   # dims: REF_AREA.FREQ.MEASURE.UNIT_MEASURE
              source_table="OECD Analytical House Prices"),
    Indicator("house_price_income", "housing", "oecd",
              "House-price-to-income ratio", "index (2015=100)", "annual",
              value_col="price_to_income", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MPD,DSD_AN_HOUSE_PRICES@DF_HOUSE_PRICES,1.0",
              key=f"{_C}.A.HPI_YDH.",
              source_table="OECD Analytical House Prices"),
    Indicator("household_debt", "housing", "oecd",
              "Household debt", "% of net disposable income", "annual",
              value_col="household_debt", chart_recipe="ranked_bar",
              # dims: FREQ.REF_AREA.MEASURE.UNIT_MEASURE (REF_AREA is 2nd)
              dataflow="OECD.SDD.NAD,DSD_HHDASH@DF_HHDASH_CTRY,1.0",
              key=f"A.{_C}.LES1M_FD4.PT_B6G_S1M",
              source_table="OECD Household Dashboard"),
    Indicator("nhpi", "housing", "statcan",
              "New Housing Price Index", "index (Dec 2016=100)", "monthly",
              value_col="nhpi", date_format="%Y-%m",
              statcan_table="18-10-0205-01",
              statcan_filters={"GEO": "Canada",
                               "New housing price indexes": "Total (house and land)"},
              source_table="Statistics Canada 18-10-0205-01"),
    Indicator("rent_cpi", "housing", "statcan",
              "Rent (CPI)", "index (2002=100)", "monthly",
              value_col="rent_index", date_format="%Y-%m",
              statcan_table="18-10-0004-01",
              statcan_filters={"GEO": "Canada",
                               "Products and product groups": "Rent"},
              source_table="Statistics Canada 18-10-0004-01"),
    Indicator("housing_starts", "housing", "statcan",
              "Housing starts", "units (monthly)", "monthly",
              value_col="housing_starts", date_format="%Y-%m",
              statcan_table="34-10-0143-01",
              statcan_filters={"GEO": "Canada", "Housing estimates": "Housing starts",
                               "Type of unit": "Total units"},
              source_table="Statistics Canada 34-10-0143-01 (CMHC)"),
    Indicator("vacancy_rate", "housing", "statcan",
              "Rental vacancy rate", "% of rental units", "annual",
              value_col="vacancy_rate", date_format="%Y",
              statcan_table="34-10-0127-01",
              statcan_filters={"GEO": "Census metropolitan areas"},
              source_table="Statistics Canada 34-10-0127-01 (CMHC)"),

    # ----- Income & Inequality -----
    Indicator("gini", "income", "oecd",
              "Gini coefficient (disposable income)", "0–1 (lower = more equal)",
              "annual", value_col="gini", chart_recipe="ranked_bar",
              # dims: REF_AREA.FREQ.MEASURE.STAT_OP.UNIT.AGE.METHODOLOGY.DEFINITION.POVERTY_LINE
              dataflow="OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,1.0",
              key=f"{_C}.A.INC_DISP_GINI..._T.METH2012.D_CUR.",
              source_table="OECD Income Distribution Database (IDD)"),
    Indicator("poverty", "income", "oecd",
              "Relative poverty rate (<50% median)", "% of population", "annual",
              value_col="poverty_rate", chart_recipe="ranked_bar",
              dataflow="OECD.WISE.INE,DSD_WISE_IDD@DF_IDD,1.0",
              key=f"{_C}.A.PR_INC_DISP..._T.METH2012.D_CUR.PL_50",
              source_table="OECD Income Distribution Database (IDD)"),
    Indicator("avg_wage", "income", "oecd",
              "Average annual wage (real)", "USD PPP, constant prices", "annual",
              value_col="avg_wage", chart_recipe="ranked_bar",
              # dims: REF_AREA.MEASURE.UNIT.PAY_PERIOD.PRICE_BASE.AGG_OP.SEX
              dataflow="OECD.ELS.SAE,DSD_EARNINGS@AV_AN_WAGE,1.0",
              key=f"{_C}.WG.USD_PPP.A.Q.MEAN._Z",
              source_table="OECD Average Annual Wages"),
    Indicator("disposable_income", "income", "oecd",
              "Real household disposable income per capita", "index (real, per capita)", "annual",
              value_col="disposable_income_index", chart_recipe="line",
              # HHDASH: FREQ.REF_AREA.MEASURE.UNIT — real gross disposable income per cap, index
              dataflow="OECD.SDD.NAD,DSD_HHDASH@DF_HHDASH_CTRY,1.0",
              key=f"A.{_C}.B6GS1M_R_POP.IX",
              source_table="OECD Household Dashboard"),
    Indicator("median_income", "income", "statcan",
              "Median after-tax income (real)", "2024 constant dollars", "annual",
              value_col="median_income", date_format="%Y",
              statcan_table="11-10-0190-01",
              statcan_filters={"GEO": "Canada",
                               "Income concept": "Median after-tax income",
                               "Economic family type":
                                   "Economic families and persons not in an economic family",
                               "UOM": "2024 constant dollars"},
              source_table="Statistics Canada 11-10-0190-01"),
    Indicator("low_income", "income", "statcan",
              "Low-income rate (LIM-AT)", "% of persons", "annual",
              value_col="low_income_rate", date_format="%Y",
              statcan_table="11-10-0135-01",
              statcan_filters={"GEO": "Canada",
                               "Persons in low income": "All persons",
                               "Low income lines": "Low income measure after tax",
                               "Statistics": "Percentage of persons in low income"},
              source_table="Statistics Canada 11-10-0135-01"),
    Indicator("food_insecurity", "income", "statcan",
              "Household food insecurity", "% of persons", "annual",
              value_col="food_insecurity_rate", date_format="%Y",
              statcan_table="13-10-0835-01",
              statcan_filters={"GEO": "Canada", "Demographic characteristics": "All persons",
                               "Household food security status": "Food insecure",
                               "Statistics": "Percentage of persons"},
              source_table="Statistics Canada 13-10-0835-01"),

    # ----- Health -----
    Indicator("life_expectancy", "health", "oecd",
              "Life expectancy at birth", "years", "annual",
              value_col="life_expectancy", chart_recipe="ranked_bar",
              # 13 dims: REF_AREA.FREQ.MEASURE.UNIT.AGE.SEX + 7 wildcards
              dataflow="OECD.ELS.HD,DSD_HEALTH_STAT@DF_LE,1.1",
              key=f"{_C}.A.LFEXP.Y.Y0._T.......",
              source_table="OECD Health Statistics"),
    Indicator("health_spending_gdp", "health", "oecd",
              "Health spending", "% of GDP", "annual",
              value_col="health_pct_gdp", chart_recipe="ranked_bar",
              # 12 dims; current expenditure (EXP_HEALTH), all financing/function/provider
              dataflow="OECD.ELS.HD,DSD_SHA@DF_SHA,1.0",
              key=f"{_C}.A.EXP_HEALTH.PT_B1GQ._T._Z._T._T._T._Z._Z._Z",
              source_table="OECD Health Expenditure (SHA)"),
    Indicator("health_spending_pc", "health", "oecd",
              "Health spending per person", "USD PPP per capita", "annual",
              value_col="health_pc_usd", chart_recipe="ranked_bar",
              # USD PPP per capita needs current prices (PRICE_BASE=V), not _Z
              dataflow="OECD.ELS.HD,DSD_SHA@DF_SHA,1.0",
              key=f"{_C}.A.EXP_HEALTH.USD_PPP_PS._T._Z._T._T._T._Z._Z.V",
              source_table="OECD Health Expenditure (SHA)"),
    Indicator("hospital_beds", "health", "oecd",
              "Hospital beds", "per 1,000 population", "annual",
              value_col="hospital_beds", chart_recipe="ranked_bar",
              dataflow="OECD.ELS.HD,DSD_HEALTH_REAC_HOSP@DF_BEDS_FUNC",
              key=f"{_C}.HB.10P3HB..._T._T..",  # total beds, all functions/care
              source_table="OECD Health Statistics"),
    Indicator("physicians", "health", "oecd",
              "Practising physicians", "per 1,000 population", "annual",
              value_col="physicians", chart_recipe="ranked_bar",
              dataflow="OECD.ELS.HD,DSD_HEALTH_EMP_REAC@DF_PHYS",
              key=f"{_C}.HSE.10P3HB...PHYS..P.",  # practising physicians
              source_table="OECD Health Statistics"),
    Indicator("mri_units", "health", "oecd",
              "MRI units", "per million population", "annual",
              value_col="mri_units", chart_recipe="ranked_bar",
              dataflow="OECD.ELS.HD,DSD_HEALTH_REAC_HOSP@DF_MED_TECH",
              key=f"{_C}.MTU.10P6HB.....MRI._T",  # MRI scanners, all providers
              source_table="OECD Health Statistics"),
    Indicator("nurses", "health", "oecd",
              "Practising nurses", "per 1,000 population", "annual",
              value_col="nurses", chart_recipe="ranked_bar",
              dataflow="OECD.ELS.HD,DSD_HEALTH_REAC_EMP@DF_NURSE",
              key=f"{_C}.HSE.10P3HB._Z._Z.MINU._Z.P._Z",  # total practising nurses
              source_table="OECD Health Statistics"),
    # NOTE: "avoidable mortality" (OECD DSD_HEALTH_STAT@DF_AM, MEASURE=AVM) was removed
    # 2026-06-10 — see project_health_expansion_2026-06 memory. The measure is sound but
    # the "avoidable" label embeds a contestable evaluative judgment; held for revival.
    # Population health & risk factors — World Bank (one config row each via the
    # generic fetcher). These are sourced by the WB from WHO / UN / IDF, NOT OECD,
    # so they add new topics (mental health, risk factors, financial protection)
    # with no overlap with our OECD health set above. All cover the full 17 peers.
    Indicator("suicide", "health", "worldbank",
              "Suicide mortality rate", "per 100,000", "annual",
              value_col="suicide_rate", chart_recipe="line",
              wb_indicator="SH.STA.SUIC.P5",
              source_table="World Bank / WHO Global Health Observatory"),
    Indicator("overweight", "health", "worldbank",
              "Overweight (adults)", "% of adults", "annual",
              value_col="overweight_pct", chart_recipe="line",
              wb_indicator="SH.STA.OWAD.ZS",
              source_table="World Bank / WHO Global Health Observatory"),
    Indicator("smoking", "health", "worldbank",
              "Tobacco use (adults)", "% of adults", "annual",
              value_col="smoking_pct", chart_recipe="line",
              wb_indicator="SH.PRV.SMOK",
              source_table="World Bank / WHO Global Health Observatory"),
    Indicator("diabetes", "health", "worldbank",
              "Diabetes prevalence", "% of adults 20–79", "annual",
              value_col="diabetes_pct", chart_recipe="ranked_bar",
              wb_indicator="SH.STA.DIAB.ZS",
              source_table="World Bank / IDF Diabetes Atlas"),
    Indicator("alcohol", "health", "worldbank",
              "Alcohol consumption", "litres per capita", "annual",
              value_col="alcohol_lpc", chart_recipe="line",
              wb_indicator="SH.ALC.PCAP.LI",
              source_table="World Bank / WHO Global Health Observatory"),
    Indicator("health_oop", "health", "worldbank",
              "Out-of-pocket health spending", "% of health spending", "annual",
              value_col="oop_pct", chart_recipe="line",
              wb_indicator="SH.XPD.OOPC.CH.ZS",
              source_table="World Bank / WHO Global Health Expenditure Database"),
    Indicator("uhc_index", "health", "worldbank",
              "Universal health coverage index", "index (0–100)", "annual",
              value_col="uhc_index", chart_recipe="line",
              # WB API expects the underscore form; the dotted variants are archived
              wb_indicator="SH_UHC_SCI",
              source_table="World Bank / WHO Universal Health Coverage"),
    Indicator("maternal_mortality", "health", "worldbank",
              "Maternal mortality ratio", "per 100,000 live births", "annual",
              value_col="maternal_mortality", chart_recipe="line",
              wb_indicator="SH.STA.MMRT",
              source_table="World Bank (WHO/UNICEF/UNFPA/World Bank/UNDESA)"),
    # Health-care access set (2026-06 Branch 2)
    Indicator("family_doctor", "health", "statcan",
              "Has a regular healthcare provider", "% aged 12+", "annual",
              value_col="pct_regular_provider", chart_recipe="single",
              date_format="%Y", statcan_table="13-10-0096-01",
              statcan_filters={"GEO": "Canada (excluding territories)",
                               "Age group": "Total, 12 years and over",
                               "Sex": "Both sexes",
                               "Indicators": "Has a regular healthcare provider",
                               "Characteristics": "Percent"},
              source_table="Statistics Canada 13-10-0096-01 (CCHS)"),
    Indicator("mental_health", "health", "statcan",
              "Perceived mental health, very good or excellent", "% aged 12+", "annual",
              value_col="pct_mh_very_good", chart_recipe="single",
              date_format="%Y", statcan_table="13-10-0096-01",
              statcan_filters={"GEO": "Canada (excluding territories)",
                               "Age group": "Total, 12 years and over",
                               "Sex": "Both sexes",
                               "Indicators": "Perceived mental health, very good or excellent",
                               "Characteristics": "Percent"},
              source_table="Statistics Canada 13-10-0096-01 (CCHS)"),
    Indicator("ltc_beds", "health", "oecd",
              "Long-term care beds", "per 1,000 aged 65+", "annual",
              value_col="ltc_beds_per_1k_65plus", chart_recipe="ranked_bar",
              dataflow="OECD.ELS.HD,DSD_HEALTH_LTCR@DF_HEALTH_LTCR_BED",
              key=f"{_C}.LTCB.10P3HB_Y_GE65........",
              source_table="OECD Health Statistics (Long-Term Care Resources)"),
    Indicator("pharma_spending_pc", "health", "oecd",
              "Pharmaceutical spending per person", "USD PPP per capita", "annual",
              value_col="pharma_pc_usd", chart_recipe="ranked_bar",
              # retail pharmaceuticals & medical non-durables (HC51), current prices
              dataflow="OECD.ELS.HD,DSD_SHA@DF_SHA,1.0",
              key=f"{_C}.A.EXP_HEALTH.USD_PPP_PS._T._Z.HC51._T._T._Z._Z.V",
              source_table="OECD Health Expenditure (SHA)"),
    Indicator("measles_vaccination", "health", "worldbank",
              "Measles immunization", "% of children 12–23 months", "annual",
              value_col="measles_immunization_pct", chart_recipe="line",
              wb_indicator="SH.IMM.MEAS", start_period=1980,
              source_table="World Bank (WHO/UNICEF estimates)"),
    Indicator("dtp_vaccination", "health", "worldbank",
              "DTP3 immunization", "% of children 12–23 months", "annual",
              value_col="dtp_immunization_pct", chart_recipe="line",
              wb_indicator="SH.IMM.IDPT", start_period=1980,
              source_table="World Bank (WHO/UNICEF estimates)"),
    # Opioid- & stimulant-related harms (PHAC Substance-Related Harms). One small
    # quarterly CSV → national time series + provincial death-rate map + who's
    # affected + drug-supply breakdowns. Drives health/substance-use.qmd.
    Indicator("opioid_harms", "health", "custom",
              "Opioid- and stimulant-related harms", "deaths / hospitalizations",
              "quarterly", fetch_fn="fetch_opioid_harms",
              output_subpath="phac_opioid_national.csv",
              source_table="Public Health Agency of Canada, Substance-Related Harms"),

    # ----- Education & Innovation (OECD MSTI reuses the R&D dataflow) -----
    Indicator("rd_expenditure", "science", "oecd",
              "R&D expenditure (GERD)", "% of GDP", "annual",
              value_col="rd_pct_gdp", chart_recipe="ranked_bar",
              dataflow="OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3",
              key=f"{_C}.A.G.PT_B1GQ..",
              source_table="OECD MSTI"),
    Indicator("berd", "science", "oecd",
              "Business R&D (BERD)", "% of GDP", "annual",
              value_col="berd_pct_gdp", chart_recipe="ranked_bar",
              dataflow="OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3",
              key=f"{_C}.A.B.PT_B1GQ.._Z",
              source_table="OECD MSTI"),
    Indicator("researchers", "science", "oecd",
              "Researchers per 1,000 employed", "per 1,000 employment", "annual",
              value_col="researchers_per_1000", chart_recipe="ranked_bar",
              dataflow="OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3",
              key=f"{_C}.A.T_RS.10P3EMP.._Z",
              source_table="OECD MSTI"),

    # ----- Education (university tuition; StatCan TLAC — bespoke multi-series) -----
    Indicator("tuition", "education", "custom",
              "University tuition by level & province", "current $", "annual",
              fetch_fn="fetch_tuition", output_subpath="statcan_tuition.csv",
              source_table="Statistics Canada 37-10-0045-01"),
    Indicator("tuition_by_field", "education", "custom",
              "Undergraduate tuition by field of study", "current $", "annual",
              fetch_fn="fetch_tuition_by_field", output_subpath="statcan_tuition_by_field.csv",
              source_table="Statistics Canada 37-10-0003-01"),

    # ----- Environment (OECD Green Growth) -----
    Indicator("co2_per_capita", "environment", "oecd",
              "CO2 emissions per capita", "tonnes CO2 per capita", "annual",
              value_col="co2_per_capita", chart_recipe="ranked_bar",
              dataflow="OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1",
              key=f"{_C}.A.CO2_PBEMCAP.T_CO2E_PS._T", start_period=1990,
              source_table="OECD Green Growth Indicators"),
    Indicator("co2_intensity", "environment", "oecd",
              "CO2 productivity (GDP per unit CO2)", "USD per kg CO2", "annual",
              value_col="co2_productivity", chart_recipe="line",
              dataflow="OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1",
              key=f"{_C}.A.CO2_PBPROD.USD_CO2._T", start_period=1990,
              source_table="OECD Green Growth Indicators"),
    Indicator("co2_indexed", "environment", "oecd",
              "CO2 emissions (indexed, 2000=100)", "index (2000=100)", "annual",
              value_col="co2_index", chart_recipe="line",
              dataflow="OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1",
              key=f"{_C}.A.CO2_PBEM.IX._T", start_period=1990,
              source_table="OECD Green Growth Indicators"),
    Indicator("consumption_co2", "environment", "custom",
              "Consumption-based CO2 per capita", "tonnes CO2 per capita", "annual",
              value_col="consumption_co2_pc", chart_recipe="ranked_bar",
              fetch_fn="fetch_consumption_co2", output_subpath="owid_consumption_co2.csv",
              source_table="Our World in Data (Global Carbon Project)"),
    Indicator("co2_per_gdp", "environment", "custom",
              "CO2 emissions intensity (per unit GDP)", "kg CO2 per $ of GDP", "annual",
              value_col="co2_per_gdp", chart_recipe="ranked_bar",
              fetch_fn="fetch_co2_per_gdp", output_subpath="owid_co2_per_gdp.csv",
              source_table="Our World in Data (Global Carbon Project)"),
    Indicator("energy_mix", "environment", "custom",
              "Energy mix by source", "% of primary energy", "annual",
              fetch_fn="fetch_energy_mix", output_subpath="owid_energy_mix.csv",
              source_table="Our World in Data (Energy Institute)"),
    Indicator("provincial_electricity", "environment", "custom",
              "Electricity generation by province & source", "% of generation", "annual",
              fetch_fn="fetch_provincial_electricity",
              output_subpath="statcan_provincial_electricity.csv",
              source_table="Statistics Canada 25-10-0015-01"),
    # GHG emissions (ECCC National Inventory Report basis — the series the 2030
    # target is defined against). Year-stamped URL; bump GHG_RELEASE each spring.
    Indicator("ghg_total", "environment", "custom",
              "GHG emissions (national, NIR basis)", "Mt CO2e", "annual",
              fetch_fn="fetch_ghg", output_subpath="eccc_ghg.csv",
              source_table="ECCC National Inventory Report / CESI"),
    Indicator("ghg_by_sector", "environment", "custom",
              "GHG emissions by economic sector", "Mt CO2e", "annual",
              fetch_fn="fetch_ghg_by_sector", output_subpath="eccc_ghg_by_sector.csv",
              source_table="ECCC CESI (by economic sector)"),

    # ----- Air Quality (the Environment > Air Quality page) -----
    # CESI national concentration trends (population-weighted, built on NAPS;
    # OGL-Canada). Year-stamped URL — bump CESI_AQ_RELEASE in fetch_air_quality.py.
    Indicator("cesi_air_quality", "environment", "custom",
              "Air-pollutant concentrations (2009=100)", "index (2009=100)", "annual",
              fetch_fn="fetch_cesi_air_quality", output_subpath="cesi_air_quality.csv",
              source_table="ECCC CESI air-quality indicators (NAPS)"),
    # APEI national emissions of the criteria air contaminants, 1990– (explains
    # why concentrations fell — e.g. the acid-rain-era SOx controls).
    Indicator("apei_emissions", "environment", "custom",
              "Air-pollutant emissions (national)", "tonnes/year", "annual",
              fetch_fn="fetch_apei_emissions", output_subpath="apei_emissions.csv",
              source_table="ECCC Air Pollutant Emissions Inventory (APEI)"),
    # Mean population exposure to PM2.5 — OECD Green Growth (SAME dataflow as the
    # CO2 indicators). International peer comparison; satellite-derived; 16/17 peers
    # (no South Korea), annual 1990–2020. Leave UNIT_MEASURE blank (..._T).
    Indicator("pm25_exposure", "environment", "oecd",
              "Mean population exposure to PM2.5", "µg/m³", "annual",
              value_col="pm25", chart_recipe="ranked_bar",
              dataflow="OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1",
              key=f"{_C}.A.PM_PWM..._T", start_period=1990,
              source_table="OECD Green Growth Indicators"),
    # Share of population exposed to PM2.5 above the WHO 2021 guideline (>5 µg/m³).
    Indicator("pm25_above_who", "environment", "oecd",
              "Population exposed to PM2.5 above WHO guideline", "% of population", "annual",
              value_col="pct_above_who", chart_recipe="ranked_bar",
              dataflow="OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1",
              key=f"{_C}.A.PM_SPEX5..._T", start_period=1990,
              source_table="OECD Green Growth Indicators"),

    # ----- Climate Change / Temperature (Environment > Climate Change page) -----
    # National annual temperature departure vs 1961–1990 (CESI; year-stamped URL,
    # bump CESI_TEMP_RELEASE in fetch_climate.py).
    Indicator("cesi_temperature", "environment", "custom",
              "National temperature departure", "°C vs 1961–1990", "annual",
              fetch_fn="fetch_cesi_temperature", output_subpath="cesi_temperature.csv",
              source_table="ECCC CESI (temperature change)"),
    # Per-region warming trend 1948– (CTVB summary table; Arctic amplification).
    Indicator("ctvb_regional", "environment", "custom",
              "Regional warming trends", "°C trend 1948–latest", "annual",
              fetch_fn="fetch_ctvb_regional", output_subpath="cesi_ctvb_regional.csv",
              source_table="ECCC Climate Trends and Variations Bulletin"),
    # Long-run city temperatures: homogenized AHCCD spine (to 2020) + raw daily
    # tail to present, via GeoMet (two-trace, never spliced).
    Indicator("city_temperatures", "environment", "custom",
              "Long-run city temperatures", "°C annual mean", "annual",
              fetch_fn="fetch_city_temperatures", output_subpath="city_temperatures.csv",
              source_table="ECCC AHCCD + MSC daily (GeoMet)"),
    # Seasonal homogenized means per city (warming-by-season view).
    Indicator("city_temperatures_seasonal", "environment", "custom",
              "Seasonal city temperatures", "°C seasonal mean", "annual",
              fetch_fn="fetch_city_temperatures_seasonal",
              output_subpath="city_temperatures_seasonal.csv",
              source_table="ECCC AHCCD seasonal (GeoMet)"),
    # Monthly homogenized means per city (input for the climate-spiral chart).
    Indicator("city_temperatures_monthly", "environment", "custom",
              "Monthly city temperatures", "°C monthly mean", "monthly",
              fetch_fn="fetch_city_temperatures_monthly",
              output_subpath="city_temperatures_monthly.csv",
              source_table="ECCC AHCCD monthly (GeoMet)"),

    # ----- Society & Well-being (bespoke XLSX parse) -----
    Indicator("happiness", "wellbeing", "custom",
              "Happiness & well-being", "Cantril ladder (0–10)", "annual",
              fetch_fn="fetch_happiness", output_subpath="whr_happiness.csv",
              source_table="World Happiness Report"),
    Indicator("crime_severity", "wellbeing", "statcan",
              "Crime Severity Index", "index (2006=100)", "annual",
              value_col="crime_severity_index", date_format="%Y",
              statcan_table="35-10-0026-01",
              statcan_filters={"GEO": "Canada", "Statistics": "Crime severity index"},
              source_table="Statistics Canada 35-10-0026-01"),
    Indicator("homicide_rate", "wellbeing", "statcan",
              "Homicide rate", "per 100,000 population", "annual",
              value_col="homicide_rate", date_format="%Y",
              statcan_table="35-10-0068-01",
              statcan_filters={"GEO": "Canada",
                               "Homicides": "Homicide rates per 100,000 population"},
              source_table="Statistics Canada 35-10-0068-01"),

    # ----- Geography (weekly/annual series; static map assets are built once by
    #        pipeline/build_geography.py and are not part of this registry) -----
    Indicator("wildfire", "geography", "custom",
              "Wildfire area burned", "hectares", "annual",
              fetch_fn="fetch_wildfire", output_subpath="nfdb_wildfire.csv",
              source_table="NRCan Canadian National Fire Database (NFDB)"),
    Indicator("sea_ice", "geography", "custom",
              "Arctic sea-ice extent", "million km²", "monthly",
              fetch_fn="fetch_sea_ice", output_subpath="nsidc_sea_ice.csv",
              source_table="NSIDC Sea Ice Index (G02135)"),
]

# Quick lookup by id
INDICATORS_BY_ID = {ind.id: ind for ind in INDICATORS}


# --- "Where Canada Stands" page snapshots ---
# Per section: (row label, csv path, value column, hover format, good-direction).
# good = "high" (higher is more favourable, default) | "low" (lower is better).
# The snapshot is a scorecard: charts.ranking_strip flips "low" rows so that
# "more favourable for Canada" is always on the right, and rank 1 = best.
SNAPSHOT_SPECS = {
    "economics": [
        ("Real GDP growth", "data/economics/oecd_real_gdp_growth.csv", "real_gdp_growth", "{:.1f}%", "high"),
        ("GDP per capita", "data/economics/oecd_gdp_per_capita.csv", "gdp_per_capita", "${:,.0f}", "high"),
        ("Labour productivity", "data/economics/oecd_labour_productivity.csv", "gdp_per_hour", "${:.0f}/hr", "high"),
        ("Business investment", "data/economics/worldbank_business_investment.csv", "investment_pct_gdp", "{:.1f}% GDP", "high"),
        ("Unemployment", "data/economics/oecd_unemployment.csv", "unemployment_rate", "{:.1f}%", "low"),
        ("Employment rate", "data/economics/oecd_employment_rate.csv", "employment_rate", "{:.1f}%", "high"),
    ],
    "housing": [
        ("Real house prices vs 2015", "data/housing/oecd_house_price_real.csv", "house_price_real", "{:.0f}", "low"),
        ("Price-to-income vs 2015", "data/housing/oecd_house_price_income.csv", "price_to_income", "{:.0f}", "low"),
        ("Household debt", "data/housing/oecd_household_debt.csv", "household_debt", "{:.0f}%", "low"),
    ],
    "income": [
        ("Average wage (real)", "data/income/oecd_avg_wage.csv", "avg_wage", "${:,.0f}", "high"),
        ("Disposable income (vs 2007)", "data/income/oecd_disposable_income.csv", "disposable_income_index", "{:.0f}", "high"),
        ("Income inequality (Gini)", "data/income/oecd_gini.csv", "gini", "{:.3f}", "low"),
        ("Relative poverty", "data/income/oecd_poverty.csv", "poverty_rate", "{:.1f}%", "low"),
    ],
    "health": [
        ("Life expectancy", "data/health/oecd_life_expectancy.csv", "life_expectancy", "{:.1f} yrs", "high"),
        ("Health spending", "data/health/oecd_health_spending_gdp.csv", "health_pct_gdp", "{:.1f}% GDP", "high"),
        ("Hospital beds", "data/health/oecd_hospital_beds.csv", "hospital_beds", "{:.1f}/1k", "high"),
        ("Physicians", "data/health/oecd_physicians.csv", "physicians", "{:.1f}/1k", "high"),
        ("Nurses", "data/health/oecd_nurses.csv", "nurses", "{:.1f}/1k", "high"),
        ("MRI units", "data/health/oecd_mri_units.csv", "mri_units", "{:.1f}/M", "high"),
        ("Suicide rate", "data/health/worldbank_suicide.csv", "suicide_rate", "{:.1f}/100k", "low"),
        ("Smoking", "data/health/worldbank_smoking.csv", "smoking_pct", "{:.0f}%", "low"),
        ("Overweight", "data/health/worldbank_overweight.csv", "overweight_pct", "{:.0f}%", "low"),
        ("Diabetes", "data/health/worldbank_diabetes.csv", "diabetes_pct", "{:.1f}%", "low"),
        ("Maternal mortality", "data/health/worldbank_maternal_mortality.csv", "maternal_mortality", "{:.0f}/100k", "low"),
        ("UHC coverage", "data/health/worldbank_uhc_index.csv", "uhc_index", "{:.0f}", "high"),
        ("Out-of-pocket health", "data/health/worldbank_health_oop.csv", "oop_pct", "{:.0f}%", "low"),
        ("Measles immunization", "data/health/worldbank_measles_vaccination.csv", "measles_immunization_pct", "{:.0f}%", "high"),
    ],
    "science": [
        ("R&D spending", "data/science/oecd_rd_expenditure.csv", "rd_pct_gdp", "{:.2f}% GDP", "high"),
        ("Researchers", "data/science/oecd_researchers.csv", "researchers_per_1000", "{:.1f}/1k", "high"),
    ],
    "environment": [
        ("CO2 per capita", "data/environment/oecd_co2_per_capita.csv", "co2_per_capita", "{:.1f} t", "low"),
        ("Consumption CO2", "data/environment/owid_consumption_co2.csv", "consumption_co2_pc", "{:.1f} t", "low"),
        ("CO2 vs 2000", "data/environment/oecd_co2_indexed.csv", "co2_index", "{:.0f}", "low"),
        ("Clean electricity", "data/environment/owid_energy_mix.csv", "low_carbon_share_elec", "{:.0f}%", "high"),
    ],
    "fiscal": [
        ("Government debt", "data/fiscal/oecd_govt_debt.csv", "govt_debt", "{:.0f}% GDP", "low"),
        ("Budget balance", "data/fiscal/oecd_govt_balance.csv", "govt_balance", "{:.1f}% GDP", "high"),
        ("Interest costs", "data/fiscal/oecd_govt_interest.csv", "govt_interest", "{:.1f}% GDP", "low"),
    ],
}
