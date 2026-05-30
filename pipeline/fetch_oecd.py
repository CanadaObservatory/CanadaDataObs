"""
Fetch and clean data from OECD via their SDMX REST API.

A single generic fetcher, `fetch_oecd_indicator`, serves every OECD series in
the indicator registry (pipeline/config.py). Each registry entry supplies the
dataflow reference and SDMX key; this module handles the HTTP request, the
standard REF_AREA/TIME_PERIOD/OBS_VALUE reshaping, and the metadata sidecar.
"""

import time
import io
import requests
import pandas as pd
from pipeline.config import (
    PEER_CODES, PEER_COUNTRIES, OECD_REQUEST_DELAY_SECONDS,
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


def fetch_oecd_indicator(ind):
    """
    Generic OECD SDMX fetch driven by an Indicator registry entry.

    Substitutes the peer-group countries into the key's {countries} placeholder,
    fetches the CSV, reshapes to the canonical
    [country_code, year, <value_col>, country_name] columns, and writes the CSV
    plus its metadata sidecar to ind.out_path.

    Returns the DataFrame, or None on empty/failed fetch (the pipeline driver
    then preserves any existing CSV — see run_pipeline.py).
    """
    logger.info(f"OECD indicator: {ind.id} ({ind.title})")
    key = ind.key.replace("{countries}", "+".join(PEER_CODES))
    df = _fetch_oecd_csv(ind.dataflow, key, start_period=ind.start_period)
    if df is None or df.empty:
        return None

    validate_columns(df, ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"], ind.id)
    df = df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]].rename(columns={
        "REF_AREA": "country_code",
        "TIME_PERIOD": "year",
        "OBS_VALUE": ind.value_col,
    })
    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)
    df["year"] = df["year"].astype(int)
    df[ind.value_col] = pd.to_numeric(df[ind.value_col], errors="coerce")
    df = (df.dropna(subset=[ind.value_col])
            .drop_duplicates(subset=["country_code", "year"], keep="last")
            .sort_values(["country_code", "year"])
            .reset_index(drop=True))

    if ind.transform is not None:
        df = ind.transform(df).reset_index(drop=True)

    out_path = ind.out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="OECD",
        source_table=ind.source_table,
        frequency=ind.frequency,
        unit=ind.unit,
        transformations=[f"filtered to {ind.title} for OECD peer group"],
    )
    logger.info(f"  saved {len(df)} rows -> {out_path.name}")
    return df
