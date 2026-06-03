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

    # ----- Government & Public Finances (OECD Economic Outlook) -----
    Indicator("govt_debt", "fiscal", "oecd",
              "Government gross debt", "% of GDP", "annual",
              value_col="govt_debt", chart_recipe="ranked_bar",
              dataflow="OECD.ECO.MAD,DSD_EO@DF_EO", key=f"{_C}.GGFLQ.A",
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
    Indicator("avoidable_mortality", "health", "oecd",
              "Avoidable mortality", "deaths per 100,000", "annual",
              value_col="avoidable_mortality", chart_recipe="ranked_bar",
              # AVM=avoidable (preventable+treatable), age-standardised deaths/100k
              dataflow="OECD.ELS.HD,DSD_HEALTH_STAT@DF_AM,1.1",
              key=f"{_C}.A.AVM.DT_10P5HB._T._T._Z._Z.STANDARD._Z._Z._Z._Z",
              source_table="OECD Health Statistics"),

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
    Indicator("energy_mix", "environment", "custom",
              "Energy mix by source", "% of primary energy", "annual",
              fetch_fn="fetch_energy_mix", output_subpath="owid_energy_mix.csv",
              source_table="Our World in Data (Energy Institute)"),
    Indicator("provincial_electricity", "environment", "custom",
              "Electricity generation by province & source", "% of generation", "annual",
              fetch_fn="fetch_provincial_electricity",
              output_subpath="statcan_provincial_electricity.csv",
              source_table="Statistics Canada 25-10-0015-01"),

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
        ("Avoidable mortality", "data/health/oecd_avoidable_mortality.csv", "avoidable_mortality", "{:.0f}/100k", "low"),
    ],
    "science": [
        ("R&D spending", "data/science/oecd_rd_expenditure.csv", "rd_pct_gdp", "{:.2f}% GDP", "high"),
        ("Business R&D", "data/science/oecd_berd.csv", "berd_pct_gdp", "{:.2f}% GDP", "high"),
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
