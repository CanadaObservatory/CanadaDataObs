"""
Fetch energy mix data from Our World in Data (OWID).
Source: Energy Institute Statistical Review + Ember + EIA, aggregated by OWID.
License: CC-BY-4.0
"""

import requests
import io
import pandas as pd
from pipeline.config import DATA_DIR, PEER_CODES, PEER_COUNTRIES
from pipeline.metadata import save_metadata, validate_columns
import logging

logger = logging.getLogger(__name__)

OWID_ENERGY_URL = "https://owid-public.owid.io/data/energy/owid-energy-data.csv"


def fetch_energy_mix():
    """
    Fetch primary energy consumption by source for OECD peers.
    Returns shares of total primary energy: coal, oil, gas, nuclear, renewables.
    """
    logger.info("Fetching OWID energy mix data...")
    logger.info(f"  URL: {OWID_ENERGY_URL}")

    try:
        r = requests.get(OWID_ENERGY_URL, timeout=120)
        r.raise_for_status()
    except Exception as e:
        logger.error(f"  Failed to fetch OWID energy data: {e}")
        return None

    df = pd.read_csv(io.StringIO(r.text))
    logger.info(f"  Got {len(df)} total rows")

    validate_columns(df, [
        "iso_code", "country", "year",
        "coal_share_energy", "oil_share_energy", "gas_share_energy",
        "nuclear_share_energy", "renewables_share_energy",
        "primary_energy_consumption",
    ], "energy_mix")

    # Filter to our peer countries
    df = df[df["iso_code"].isin(PEER_CODES)].copy()

    # Keep relevant columns
    keep_cols = [
        "iso_code", "country", "year",
        "coal_share_energy", "oil_share_energy", "gas_share_energy",
        "nuclear_share_energy", "renewables_share_energy",
        "hydro_share_energy", "solar_share_energy", "wind_share_energy",
        "biofuel_share_energy",
        "primary_energy_consumption",
    ]
    available = [c for c in keep_cols if c in df.columns]
    df = df[available].copy()

    # Rename for consistency
    df = df.rename(columns={
        "iso_code": "country_code",
        "country": "country_name",
    })

    # Convert numeric columns
    numeric_cols = [c for c in df.columns if c not in ("country_code", "country_name", "year")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["year"] = df["year"].astype(int)
    df = df.dropna(subset=["primary_energy_consumption"])
    df = df.sort_values(["country_code", "year"]).reset_index(drop=True)

    # Use our standard country names
    df["country_name"] = df["country_code"].map(PEER_COUNTRIES)

    out_path = DATA_DIR / "environment" / "owid_energy_mix.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="year",
        source="Our World in Data (Energy Institute, Ember, EIA)",
        source_table="owid-energy-data",
        frequency="annual",
        unit="% of primary energy",
        transformations=["filtered to 20 OECD peers, selected energy share columns"],
    )
    logger.info(f"Saved {len(df)} rows to {out_path}")

    return df


if __name__ == "__main__":
    fetch_energy_mix()
