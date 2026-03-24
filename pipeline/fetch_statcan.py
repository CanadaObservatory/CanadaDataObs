"""
Fetch and clean data from Statistics Canada Web Data Service.
Uses the stats_can library for simplified API access.
"""

import pandas as pd
import stats_can
from pipeline.config import DATA_DIR, STATCAN_TABLES, PROJECT_ROOT
from pipeline.metadata import save_metadata, validate_columns
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_table(table_id):
    """Download a StatCan table and return as DataFrame.

    Downloads the CSV zip from StatCan, caches locally in an h5 file,
    and returns as a DataFrame. Works on fresh environments (e.g., GitHub Actions).
    """
    # First try to download/update the table
    try:
        stats_can.update_tables(table_id, path=str(PROJECT_ROOT))
    except Exception:
        pass  # May fail if table not yet downloaded

    try:
        return stats_can.table_to_df(table_id, path=str(PROJECT_ROOT))
    except Exception:
        # If h5 doesn't exist yet, download via zip
        from stats_can.scwds import get_full_table_download
        import zipfile, io, tempfile, requests

        url = get_full_table_download(table_id)
        logger.info(f"  Downloading zip from: {url}")
        r = requests.get(url, timeout=120)
        r.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            csv_names = [n for n in z.namelist() if n.endswith('.csv')]
            if not csv_names:
                raise ValueError(f"No CSV found in zip for table {table_id}")
            with z.open(csv_names[0]) as f:
                return pd.read_csv(f)


def fetch_population_quarterly():
    """
    Fetch quarterly population estimates for Canada and provinces.
    StatCan Table: 17-10-0009-01
    """
    logger.info("Fetching StatCan population estimates (quarterly)...")
    table_id = STATCAN_TABLES["population_quarterly"]

    try:
        df = _get_table(table_id)
    except Exception as e:
        logger.error(f"Failed to fetch StatCan table {table_id}: {e}")
        return None

    # Validate expected columns from StatCan
    validate_columns(df, ["REF_DATE", "GEO", "VALUE"], "population_quarterly")

    # Clean and reshape
    df = df.rename(columns={"REF_DATE": "date", "GEO": "geography", "VALUE": "population"})
    df = df[["date", "geography", "population"]].copy()

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
    save_metadata(out_path, df=df,
        source="Statistics Canada",
        source_table="17-10-0009-01",
        frequency="quarterly",
        unit="persons",
        transformations=["filtered to date, geography, population columns"],
    )
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
        df = _get_table(table_id)
    except Exception as e:
        logger.error(f"Failed to fetch StatCan table {table_id}: {e}")
        return None

    validate_columns(df, ["REF_DATE", "GEO", "Components of demographic growth", "VALUE"],
                     "population_components")

    df = df.rename(columns={
        "REF_DATE": "date",
        "GEO": "geography",
        "Components of demographic growth": "component",
        "VALUE": "value",
    })
    df = df[["date", "geography", "component", "value"]].copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["value"])
    df = df.sort_values(["geography", "component", "date"]).reset_index(drop=True)

    out_path = DATA_DIR / "population" / "statcan_population_components.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df,
        source="Statistics Canada",
        source_table="17-10-0008-01",
        frequency="quarterly",
        unit="persons",
        transformations=["filtered to date, geography, component, value columns"],
    )
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
        df = _get_table(table_id)
    except Exception as e:
        logger.error(f"Failed to fetch StatCan table {table_id}: {e}")
        return None

    validate_columns(df, ["REF_DATE", "GEO", "Products and product groups", "VALUE"], "cpi")

    df = df.rename(columns={
        "REF_DATE": "date",
        "GEO": "geography",
        "Products and product groups": "product_group",
        "VALUE": "cpi_value",
    })
    df = df[["date", "geography", "product_group", "cpi_value"]].copy()

    # Keep only All-items CPI for Canada
    df = df[df["product_group"] == "All-items"]
    df = df[df["geography"] == "Canada"]

    df["date"] = pd.to_datetime(df["date"])
    df["cpi_value"] = pd.to_numeric(df["cpi_value"], errors="coerce")
    df = df.dropna(subset=["cpi_value"])
    df = df.sort_values("date").reset_index(drop=True)

    # Calculate year-over-year inflation rate (12 months back, single series)
    df["inflation_yoy"] = df["cpi_value"].pct_change(periods=12) * 100

    out_path = DATA_DIR / "economics" / "statcan_cpi.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df,
        source="Statistics Canada",
        source_table="18-10-0004-01",
        frequency="monthly",
        unit="index (2002=100)",
        transformations=[
            "filtered to All-items CPI, Canada only",
            "computed year-over-year inflation rate (12-month pct_change)",
        ],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


if __name__ == "__main__":
    fetch_population_quarterly()
    fetch_population_components()
    fetch_cpi()
