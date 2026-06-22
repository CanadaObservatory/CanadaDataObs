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
    PEER_CODES, PEER_COUNTRIES, OECD_REQUEST_DELAY_SECONDS, DATA_DIR,
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


# Age brackets for the labour-market by-age charts (OECD LFS codes -> friendly
# labels). "Total (15–64)" is the working-age aggregate shown by default.
LABOUR_AGE_LABELS = {
    "Y15T24": "Youth (15–24)",
    "Y25T54": "Prime-age (25–54)",
    "Y55T64": "Older (55–64)",
    "Y15T64": "Total (15–64)",
}


def fetch_labour_by_age():
    """Unemployment and employment rates by age bracket for the peer group.

    One OECD LFS indicators flow (DSD_LFS@DF_IALFS_INDIC) carries both the
    unemployment rate (UNE_LF, % of labour force) and the employment rate
    (EMP_WAP, % of working-age population) by age, annual, for all 17 peers.
    Writes two tidy long CSVs (country_code, year, age, <rate>, country_name) that
    drive the age-dropdown trend + ranked-bar charts on the economics page. The
    total (15–64) unemployment line matches the headline KEI series to <0.3 pp,
    so this LFS basis is used for the whole age family for internal consistency.
    """
    logger.info("OECD: unemployment + employment rates by age (LFS indicators)...")
    peers = "+".join(PEER_CODES)
    ages = "+".join(LABOUR_AGE_LABELS)
    # dims: REF_AREA.MEASURE.UNIT.TRANSFORMATION.ADJUSTMENT.SEX.AGE.ACTIVITY.FREQ
    key = (f"{peers}.UNE_LF+EMP_WAP.PT_LF_SUB+PT_WAP_SUB..Y._T.{ages}..A")
    df = _fetch_oecd_csv("OECD.SDD.TPS,DSD_LFS@DF_IALFS_INDIC", key, start_period=2000)
    if df is None or df.empty:
        return None
    validate_columns(df, ["REF_AREA", "MEASURE", "AGE", "TIME_PERIOD", "OBS_VALUE"],
                     "labour_by_age")
    df = df[df["ADJUSTMENT"].astype(str) == "Y"].copy()   # one adjustment only
    df["year"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["age"] = df["AGE"].map(LABOUR_AGE_LABELS)
    df["country_name"] = df["REF_AREA"].map(PEER_COUNTRIES)
    df = df.dropna(subset=["year", "value", "age"])

    written = []
    for measure, value_col, fname in [
        ("UNE_LF", "unemployment_rate", "oecd_unemployment_by_age.csv"),
        ("EMP_WAP", "employment_rate", "oecd_employment_by_age.csv"),
    ]:
        sub = (df[df["MEASURE"] == measure]
               [["REF_AREA", "year", "age", "value", "country_name"]]
               .rename(columns={"REF_AREA": "country_code", "value": value_col}))
        sub = (sub.drop_duplicates(subset=["country_code", "year", "age"], keep="last")
                  .sort_values(["country_code", "age", "year"])
                  .reset_index(drop=True))
        sub["year"] = sub["year"].astype(int)
        if sub.empty:
            continue
        out_path = DATA_DIR / "economics" / fname
        out_path.parent.mkdir(parents=True, exist_ok=True)
        sub.to_csv(out_path, index=False)
        save_metadata(out_path, df=sub, date_column="year", source="OECD",
            source_table="OECD Labour Force Statistics (DSD_LFS@DF_IALFS_INDIC)",
            frequency="annual", unit="% (harmonised, by age bracket)",
            transformations=["unemployment (% of labour force) / employment "
                             "(% of working-age pop) by age, OECD peer group"])
        logger.info(f"  saved {len(sub)} rows -> {out_path.name}")
        written.append(sub)
    return written if written else None


# OECD Revenue Statistics standard tax categories (codes T_x000 sum to total taxation).
TAX_CATEGORY_LABELS = {
    "T_1000": "Income & profits",
    "T_2000": "Social security",
    "T_3000": "Payroll",
    "T_4000": "Property",
    "T_5000": "Goods & services",
    "T_6000": "Other",
}


def fetch_tax_structure():
    """Tax structure (the revenue mix) for the peer group — each main category of
    tax as a share of GDP, from the OECD Revenue Statistics comparative tables
    (DSD_REV_COMP_OECD@DF_RSOECD). General government (S13); the six standard
    categories sum to total taxation: income & profits, social security
    contributions, payroll, property, goods & services, and other taxes.

    The total burden (the sum) is already discussed elsewhere; the *mix* is the
    story here — e.g. Canada leans on income and property taxes and raises less
    through social-security contributions and consumption taxes than most European
    peers. Annual since 2010 for all 17 peers; the page draws the latest year as a
    stacked bar so both the total (bar height) and the composition (segments) read.
    """
    logger.info("OECD: tax structure / revenue mix (Revenue Statistics)...")
    peers = "+".join(PEER_CODES)
    cats = "+".join(TAX_CATEGORY_LABELS)   # T_1000+...+T_6000
    # dims: REF_AREA.MEASURE.SECTOR.STANDARD_REVENUE.CTRY_SPECIFIC.UNIT_MEASURE.FREQ
    key = f"{peers}.TAX_REV.S13.{cats}._T.PT_B1GQ.A"
    df = _fetch_oecd_csv("OECD.CTP.TPS,DSD_REV_COMP_OECD@DF_RSOECD,2.0", key, start_period=2010)
    if df is None or df.empty:
        return None
    validate_columns(df, ["REF_AREA", "STANDARD_REVENUE", "TIME_PERIOD", "OBS_VALUE"],
                     "tax_structure")
    df["year"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce").astype("Int64")
    df["pct_gdp"] = pd.to_numeric(df["OBS_VALUE"], errors="coerce")
    df["tax_type"] = df["STANDARD_REVENUE"].map(TAX_CATEGORY_LABELS)
    df["country_name"] = df["REF_AREA"].map(PEER_COUNTRIES)
    out = (df.dropna(subset=["year", "pct_gdp", "tax_type"])
             [["REF_AREA", "country_name", "year", "tax_type", "pct_gdp"]]
             .rename(columns={"REF_AREA": "country_code"})
             .drop_duplicates(["country_code", "year", "tax_type"], keep="last")
             .sort_values(["country_code", "year", "tax_type"]).reset_index(drop=True))
    out["year"] = out["year"].astype(int)
    if out.empty:
        return None
    out_path = DATA_DIR / "fiscal" / "oecd_tax_structure.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)
    save_metadata(out_path, df=out, date_column="year", source="OECD",
        source_table="OECD Revenue Statistics (DSD_REV_COMP_OECD@DF_RSOECD)",
        frequency="annual", unit="% of GDP (general government, by tax category)",
        transformations=["six standard tax categories (income / social security / "
                         "payroll / property / goods & services / other) as % of GDP, "
                         "general government, OECD peer group"])
    logger.info(f"  saved {len(out)} rows -> {out_path.name}")
    return out
