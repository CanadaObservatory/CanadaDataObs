"""
Fetch and clean data from OECD via their SDMX REST API.
Uses direct HTTP requests to the new OECD SDMX endpoint (sdmx.oecd.org).
"""

import time
import io
import requests
import pandas as pd
from pipeline.config import (
    DATA_DIR, PEER_CODES, PEER_COUNTRIES,
    OECD_REQUEST_DELAY_SECONDS,
)
from pipeline.metadata import save_metadata, validate_columns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OECD_BASE_URL = "https://sdmx.oecd.org/public/rest/data"
CSV_HEADERS = {"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"}


def _rate_limit():
    """Simple rate limiter: sleep between requests."""
    time.sleep(OECD_REQUEST_DELAY_SECONDS)


def _fetch_oecd_csv(dataflow, key, start_period=2000):
    """
    Fetch data from OECD SDMX API as CSV.

    Parameters
    ----------
    dataflow : str
        Full dataflow reference, e.g. "OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3"
    key : str
        SDMX key string, e.g. "CAN+USA.A.G.PT_B1GQ.."
    start_period : int
        Start year for data

    Returns
    -------
    pd.DataFrame or None
    """
    url = f"{OECD_BASE_URL}/{dataflow}/{key}?startPeriod={start_period}"
    logger.info(f"Fetching: {url}")

    try:
        r = requests.get(url, headers=CSV_HEADERS, timeout=60)
        _rate_limit()

        if r.status_code == 200:
            df = pd.read_csv(io.StringIO(r.text))
            logger.info(f"  Got {len(df)} rows")
            return df
        else:
            logger.error(f"  HTTP {r.status_code}: {r.text[:200]}")
            return None
    except Exception as e:
        logger.error(f"  Request failed: {e}")
        return None


def fetch_rd_expenditure():
    """
    Fetch Gross Domestic Expenditure on R&D (GERD) as % of GDP.
    OECD MSTI database.
    Dimensions: REF_AREA.FREQ.MEASURE.UNIT_MEASURE.PRICE_BASE.TRANSFORMATION
    GERD as % of GDP: MEASURE=G, UNIT_MEASURE=PT_B1GQ
    """
    logger.info("Fetching OECD R&D expenditure (GERD as % of GDP)...")

    country_str = "+".join(PEER_CODES)
    df = _fetch_oecd_csv(
        dataflow="OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3",
        key=f"{country_str}.A.G.PT_B1GQ..",
        start_period=2000,
    )

    if df is None:
        return None

    # Validate and clean
    validate_columns(df, ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"], "rd_expenditure")
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df = df.rename(columns={
        "REF_AREA": "country_code",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "rd_pct_gdp",
    })

    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df["year"] = df["year"].astype(int)
    df["rd_pct_gdp"] = pd.to_numeric(df["rd_pct_gdp"], errors="coerce")
    df = df.dropna(subset=["rd_pct_gdp"])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    # Save
    out_path = DATA_DIR / "science" / "oecd_rd_expenditure.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="OECD",
        source_table="MSTI_PUB (Main Science and Technology Indicators)",
        frequency="annual",
        unit="% of GDP",
        transformations=["filtered to GERD as % of GDP for 20 OECD peers"],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def fetch_gdp_per_capita():
    """
    Fetch GDP per capita (current prices, PPP, USD) for OECD peers.
    Uses SNA_TABLE1 — GDP per head of population.
    Dimensions: REF_AREA.MEASURE.ACTIVITY.PRICE_BASE.TRANSFORMATION.UNIT_MEASURE
    """
    logger.info("Fetching OECD GDP per capita (PPP, current prices)...")

    country_str = "+".join(PEER_CODES)
    # Dataflow v2.0 has 13 dimensions:
    # FREQ.REF_AREA.SECTOR.COUNTERPART_SECTOR.TRANSACTION.INSTR_ASSET.
    # ACTIVITY.EXPENDITURE.UNIT_MEASURE.PRICE_BASE.TRANSFORMATION.TABLE_IDENTIFIER
    df = _fetch_oecd_csv(
        dataflow="OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE_HCPC,2.0",
        key=f"A.{country_str}.S1.S1.B1GQ_POP._Z._Z._Z.USD_PPP_PS.V.N.T0102",
        start_period=2000,
    )

    if df is None:
        return None

    validate_columns(df, ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"], "gdp_per_capita")
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df = df.rename(columns={
        "REF_AREA": "country_code",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "gdp_per_capita",
    })

    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df["year"] = df["year"].astype(int)
    df["gdp_per_capita"] = pd.to_numeric(df["gdp_per_capita"], errors="coerce")
    df = df.dropna(subset=["gdp_per_capita"])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    out_path = DATA_DIR / "economics" / "oecd_gdp_per_capita.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="OECD",
        source_table="SNA_TABLE1 (National Accounts)",
        frequency="annual",
        unit="USD (PPP, current prices)",
        transformations=["filtered to GDP per capita, PPP, for 20 OECD peers"],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def fetch_labour_productivity():
    """
    Fetch GDP per hour worked (USD, PPP) for OECD peers.
    OECD Productivity database (PDB_LV).
    Dimensions: REF_AREA.FREQ.MEASURE.ACTIVITY.UNIT_MEASURE.PRICE_BASE.TRANSFORMATION.ADJUSTMENT.CONVERSION_TYPE
    """
    logger.info("Fetching OECD labour productivity (GDP per hour worked)...")

    country_str = "+".join(PEER_CODES)
    df = _fetch_oecd_csv(
        dataflow="OECD.SDD.TPS,DSD_PDB@DF_PDB_LV,1.0",
        key=f"{country_str}.A.GDPHRS._T.USD_PPP_H.Q._Z._Z._Z",
        start_period=2000,
    )

    if df is None:
        return None

    validate_columns(df, ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"], "labour_productivity")
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df = df.rename(columns={
        "REF_AREA": "country_code",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "gdp_per_hour",
    })

    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df["year"] = df["year"].astype(int)
    df["gdp_per_hour"] = pd.to_numeric(df["gdp_per_hour"], errors="coerce")
    df = df.dropna(subset=["gdp_per_hour"])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    out_path = DATA_DIR / "economics" / "oecd_labour_productivity.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="OECD",
        source_table="PDB_LV (Productivity Database)",
        frequency="annual",
        unit="USD PPP per hour worked",
        transformations=["filtered to GDP per hour worked for 20 OECD peers"],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def fetch_unemployment():
    """
    Fetch harmonised unemployment rate (% of labour force) for OECD peers.
    OECD Key Economic Indicators (KEI).
    Dimensions: REF_AREA.FREQ.MEASURE.UNIT_MEASURE.ACTIVITY.ADJUSTMENT.TRANSFORMATION
    """
    logger.info("Fetching OECD unemployment rate...")

    country_str = "+".join(PEER_CODES)
    df = _fetch_oecd_csv(
        dataflow="OECD.SDD.STES,DSD_KEI@DF_KEI,4.0",
        key=f"{country_str}.A.UNEMP.PT_LF._T..",
        start_period=2000,
    )

    if df is None:
        return None

    validate_columns(df, ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"], "unemployment")
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df = df.rename(columns={
        "REF_AREA": "country_code",
        "TIME_PERIOD": "year",
        "OBS_VALUE": "unemployment_rate",
    })

    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df["year"] = df["year"].astype(int)
    df["unemployment_rate"] = pd.to_numeric(df["unemployment_rate"], errors="coerce")
    df = df.dropna(subset=["unemployment_rate"])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    out_path = DATA_DIR / "economics" / "oecd_unemployment.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="OECD",
        source_table="KEI (Key Economic Indicators)",
        frequency="annual",
        unit="% of labour force",
        transformations=["filtered to harmonised unemployment rate for 20 OECD peers"],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def _fetch_green_growth(measure, unit_measure, value_col, csv_name, description,
                         unit, start_period=1990):
    """Shared helper for Green Growth indicators."""
    country_str = "+".join(PEER_CODES)
    df = _fetch_oecd_csv(
        dataflow="OECD.ENV.EPI,DSD_GG@DF_GREEN_GROWTH,1.1",
        key=f"{country_str}.A.{measure}.{unit_measure}._T",
        start_period=start_period,
    )

    if df is None:
        return None

    validate_columns(df, ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"], csv_name)
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].copy()
    df = df.rename(columns={
        "REF_AREA": "country_code",
        "TIME_PERIOD": "year",
        "OBS_VALUE": value_col,
    })

    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df["year"] = df["year"].astype(int)
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
    df = df.dropna(subset=[value_col])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    out_path = DATA_DIR / "environment" / f"oecd_{csv_name}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="OECD",
        source_table="Green Growth Indicators",
        frequency="annual",
        unit=unit,
        transformations=[f"filtered to {description} for 20 OECD peers"],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def fetch_co2_per_capita():
    """Fetch production-based CO2 emissions per capita (tonnes CO2e per person)."""
    logger.info("Fetching OECD CO2 emissions per capita...")
    return _fetch_green_growth(
        measure="CO2_PBEMCAP", unit_measure="T_CO2E_PS",
        value_col="co2_per_capita", csv_name="co2_per_capita",
        description="production-based CO2 per capita",
        unit="tonnes CO2 per capita",
    )


def fetch_co2_intensity():
    """Fetch CO2 emissions per unit of GDP (USD per kg CO2)."""
    logger.info("Fetching OECD CO2 emissions intensity...")
    return _fetch_green_growth(
        measure="CO2_PBPROD", unit_measure="USD_CO2",
        value_col="co2_productivity", csv_name="co2_intensity",
        description="CO2 productivity (GDP per unit of CO2)",
        unit="USD per kg CO2",
    )


def fetch_co2_indexed():
    """Fetch production-based CO2 emissions, indexed (2000=100)."""
    logger.info("Fetching OECD CO2 emissions indexed...")
    return _fetch_green_growth(
        measure="CO2_PBEM", unit_measure="IX",
        value_col="co2_index", csv_name="co2_indexed",
        description="production-based CO2 emissions (indexed 2000=100)",
        unit="index (2000=100)",
    )


def fetch_renewables_share():
    """Fetch renewable energy as % of total primary energy supply."""
    logger.info("Fetching OECD renewable energy share...")
    return _fetch_green_growth(
        measure="RE_TPES", unit_measure="PT_SUP_NRG",
        value_col="renewables_pct", csv_name="renewables_share",
        description="renewable energy share of total energy supply",
        unit="% of total primary energy supply",
    )


if __name__ == "__main__":
    fetch_rd_expenditure()
    fetch_gdp_per_capita()
    fetch_labour_productivity()
    fetch_unemployment()
    fetch_co2_per_capita()
    fetch_co2_intensity()
    fetch_co2_indexed()
    fetch_renewables_share()
