"""
Fetch and clean data from Statistics Canada Web Data Service.
Uses the stats_can library for simplified API access.
"""

import pandas as pd
import stats_can
from pipeline.config import DATA_DIR, STATCAN_TABLES
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_population_quarterly():
    """
    Fetch quarterly population estimates for Canada and provinces.
    StatCan Table: 17-10-0009-01
    """
    logger.info("Fetching StatCan population estimates (quarterly)...")
    table_id = STATCAN_TABLES["population_quarterly"]

    try:
        df = stats_can.sc.table_to_df(table_id)
    except Exception as e:
        logger.error(f"Failed to fetch StatCan table {table_id}: {e}")
        return None

    # Clean and reshape
    # The raw table has columns like REF_DATE, GEO, VALUE, etc.
    df = df.rename(columns={"REF_DATE": "date", "GEO": "geography", "VALUE": "population"})

    # Filter to key columns
    keep_cols = ["date", "geography", "population"]
    available_cols = [c for c in keep_cols if c in df.columns]
    df = df[available_cols].copy()

    # Convert date
    df["date"] = pd.to_datetime(df["date"])

    # Remove rows with missing population
    df = df.dropna(subset=["population"])

    # Sort
    df = df.sort_values(["geography", "date"]).reset_index(drop=True)

    # Save
    out_path = DATA_DIR / "population" / "statcan_population_quarterly.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def fetch_population_components():
    """
    Fetch components of population growth (births, deaths, immigration, emigration).
    StatCan Table: 17-10-0014-01
    """
    logger.info("Fetching StatCan population components...")
    table_id = STATCAN_TABLES["population_components"]

    try:
        df = stats_can.sc.table_to_df(table_id)
    except Exception as e:
        logger.error(f"Failed to fetch StatCan table {table_id}: {e}")
        return None

    df = df.rename(columns={
        "REF_DATE": "date",
        "GEO": "geography",
        "Components of population growth": "component",
        "VALUE": "value",
    })

    keep_cols = ["date", "geography", "component", "value"]
    available_cols = [c for c in keep_cols if c in df.columns]
    df = df[available_cols].copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["value"])
    df = df.sort_values(["geography", "component", "date"]).reset_index(drop=True)

    out_path = DATA_DIR / "population" / "statcan_population_components.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


def fetch_cpi():
    """
    Fetch Consumer Price Index (monthly, all-items) for Canada.
    StatCan Table: 18-10-0004-01
    """
    logger.info("Fetching StatCan CPI (monthly, all-items)...")
    table_id = STATCAN_TABLES["cpi"]

    try:
        df = stats_can.sc.table_to_df(table_id)
    except Exception as e:
        logger.error(f"Failed to fetch StatCan table {table_id}: {e}")
        return None

    df = df.rename(columns={
        "REF_DATE": "date",
        "GEO": "geography",
        "Products and product groups": "product_group",
        "VALUE": "cpi_value",
    })

    # Filter to All-items CPI for Canada
    keep_cols = ["date", "geography", "product_group", "cpi_value"]
    available_cols = [c for c in keep_cols if c in df.columns]
    df = df[available_cols].copy()

    # Keep only "All-items" and Canada-level
    if "product_group" in df.columns:
        df = df[df["product_group"].str.contains("All-items", case=False, na=False)]
    if "geography" in df.columns:
        df = df[df["geography"] == "Canada"]

    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["cpi_value"])
    df = df.sort_values("date").reset_index(drop=True)

    # Calculate year-over-year inflation rate
    df["cpi_value"] = pd.to_numeric(df["cpi_value"], errors="coerce")
    df["inflation_yoy"] = df["cpi_value"].pct_change(periods=12) * 100

    out_path = DATA_DIR / "economics" / "statcan_cpi.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


if __name__ == "__main__":
    fetch_population_quarterly()
    fetch_population_components()
    fetch_cpi()
