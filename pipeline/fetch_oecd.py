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
    df = _fetch_oecd_csv(
        dataflow="OECD.SDD.NAD,DSD_NAMAIN1@DF_TABLE1_EXPENDITURE_HCPC,1.0",
        key=f"{country_str}.A.B1GQ_POP.V.N.USD_PPP",
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


if __name__ == "__main__":
    fetch_rd_expenditure()
    fetch_gdp_per_capita()
