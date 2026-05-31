"""
Fetch and clean data from Statistics Canada Web Data Service.
Uses the stats_can library for simplified API access.
"""

import pandas as pd
from pipeline.config import DATA_DIR, STATCAN_TABLES
from pipeline.metadata import save_metadata, validate_columns, SchemaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_table(table_id):
    """Download a StatCan table and return as DataFrame.

    Downloads the CSV zip directly from StatCan's bulk download endpoint.
    This avoids caching issues with the stats_can library's h5 store.
    """
    import zipfile, io, requests

    # Build direct download URL (works reliably on fresh CI environments)
    # StatCan table IDs like "17-10-0008-01" → URL uses "17100008" (first 3 groups)
    parts = table_id.split("-")
    table_num = "".join(parts[:3])  # e.g., "17100008"
    url = f"https://www150.statcan.gc.ca/n1/tbl/csv/{table_num}-eng.zip"
    logger.info(f"  Downloading zip from: {url}")

    r = requests.get(url, timeout=120)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        csv_names = [n for n in z.namelist() if n.endswith('.csv')]
        if not csv_names:
            raise ValueError(f"No CSV found in zip for table {table_id}")
        with z.open(csv_names[0]) as f:
            return pd.read_csv(f, low_memory=False)


def fetch_statcan_indicator(ind):
    """Generic single-series StatCan fetch driven by an Indicator registry entry.

    Downloads the table, applies the entry's equality filters (column -> value),
    and emits a simple [date, <value_col>] CSV for a single Canada-wide series.
    Used for indicators like NHPI, median income, and the low-income rate; the
    multi-geography population tables and CPI keep their bespoke functions.
    """
    logger.info(f"StatCan indicator: {ind.id} ({ind.title})")
    try:
        df = _get_table(ind.statcan_table)
    except Exception as e:
        logger.error(f"  Failed to fetch StatCan table {ind.statcan_table}: {e}")
        return None

    for col, val in ind.statcan_filters.items():
        if col not in df.columns:
            raise SchemaError(
                f"{ind.id}: filter column '{col}' missing from table "
                f"{ind.statcan_table}. Available: {list(df.columns)}"
            )
        df = df[df[col] == val]

    validate_columns(df, ["REF_DATE", "VALUE"], ind.id)
    df = df[["REF_DATE", "VALUE"]].rename(
        columns={"REF_DATE": "date", "VALUE": ind.value_col})
    df["date"] = pd.to_datetime(df["date"].astype(str), format=ind.date_format,
                                errors="coerce")
    df[ind.value_col] = pd.to_numeric(df[ind.value_col], errors="coerce")
    df = (df.dropna(subset=["date", ind.value_col])
            .sort_values("date").reset_index(drop=True))
    if df.empty:
        logger.warning(f"  {ind.id}: no rows after filtering — check filter values")
        return None

    out_path = ind.out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    save_metadata(out_path, df=df, date_column="date",
        source="Statistics Canada",
        source_table=ind.source_table,
        frequency=ind.frequency,
        unit=ind.unit,
        transformations=[f"filtered to {ind.statcan_filters}"],
    )
    logger.info(f"  saved {len(df)} rows -> {out_path.name}")
    return df


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

    validate_columns(df, ["REF_DATE", "GEO", "Components of population growth", "VALUE"],
                     "population_components")

    df = df.rename(columns={
        "REF_DATE": "date",
        "GEO": "geography",
        "Components of population growth": "component",
        "VALUE": "value",
    })
    df = df[["date", "geography", "component", "value"]].copy()

    # Dates are fiscal year format "1971/1972" — use the ending year as July 1
    df["date"] = df["date"].astype(str).str.extract(r"(\d{4})$")[0]
    df["date"] = pd.to_datetime(df["date"], format="%Y")
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


PROVINCES = ["Newfoundland and Labrador", "Prince Edward Island", "Nova Scotia",
             "New Brunswick", "Quebec", "Ontario", "Manitoba", "Saskatchewan",
             "Alberta", "British Columbia"]


def fetch_provincial_electricity():
    """Provincial electricity generation mix, with fossil fuels split by type.

    The base mix comes from StatCan 25-10-0015-01 (latest 12 months, generation
    by turbine type → Hydro / Nuclear / Wind / Solar / Biomass + a single fossil
    total). That table only knows turbine type, not fuel, so the fossil slice is
    split into Coal / Natural gas / Oil using the fuel-level generation shares
    from 25-10-0084-01 (latest annual). Coal matters because it emits roughly
    twice the CO2 of natural gas per kWh. This is generation (output), not
    installed capacity.
    """
    logger.info("Fetching StatCan provincial electricity generation (with fuel split)...")
    try:
        gen = _get_table("25-10-0015-01")
        fuel = _get_table("25-10-0084-01")
    except Exception as e:
        logger.error(f"  failed to fetch provincial electricity tables: {e}")
        return None

    # --- base mix from 25-10-0015 (latest 12 months) ---
    TYPE = "Type of electricity generation"
    CLASS = "Class of electricity producer"
    validate_columns(gen, ["REF_DATE", "GEO", CLASS, TYPE, "VALUE"], "provincial_electricity")
    gen = gen[(gen[CLASS] == "Total all classes of electricity producer")
              & gen["GEO"].isin(PROVINCES)].copy()
    gen["VALUE"] = pd.to_numeric(gen["VALUE"], errors="coerce")
    months = sorted(gen["REF_DATE"].dropna().unique())[-12:]
    gen = gen[gen["REF_DATE"].isin(months)]

    FOSSIL = "Total electricity production from non-renewable combustible fuels"
    base_map = {
        "Hydraulic turbine": "Hydro",
        "Nuclear steam turbine": "Nuclear",
        "Wind power turbine": "Wind",
        "Solar": "Solar",
        "Total electricity production from biomass": "Biomass",
        FOSSIL: "Fossil",
    }
    gen = gen[gen[TYPE].isin(base_map)].copy()
    gen["bucket"] = gen[TYPE].map(base_map)
    base = gen.groupby(["GEO", "bucket"])["VALUE"].sum().unstack(fill_value=0.0)

    # --- fossil split (Coal/Natural gas/Oil) from 25-10-0084 (latest annual) ---
    NAICS = "North American Industry Classification System (NAICS)"
    validate_columns(fuel, ["REF_DATE", "GEO", NAICS, "Fuel type", "UOM", "VALUE"],
                     "provincial_electricity_fuel")
    fuel = fuel[(fuel["UOM"] == "Megawatt hours")
                & (fuel[NAICS] == "Total all classes of electricity")
                & fuel["GEO"].isin(PROVINCES)].copy()
    fuel["VALUE"] = pd.to_numeric(fuel["VALUE"], errors="coerce")
    fyear = sorted(fuel["REF_DATE"].dropna().unique())[-1]
    fuel = fuel[fuel["REF_DATE"] == fyear]
    fuel_map = {
        "Total coal, electricity generated": "Coal",
        "Natural gas, electricity generated": "Natural gas",
        "Total petroleum products, electricity generated": "Oil",
    }
    fuel = fuel[fuel["Fuel type"].isin(fuel_map)].copy()
    fuel["fbucket"] = fuel["Fuel type"].map(fuel_map)
    fsplit = fuel.groupby(["GEO", "fbucket"])["VALUE"].sum().unstack(fill_value=0.0)

    # --- combine: split each province's fossil total by its fuel proportions ---
    rows = []
    for prov in PROVINCES:
        if prov not in base.index:
            continue
        b = base.loc[prov]
        fossil_total = float(b.get("Fossil", 0.0))
        if prov in fsplit.index and fsplit.loc[prov].sum() > 0:
            p = fsplit.loc[prov] / fsplit.loc[prov].sum()
            coal, gas, oil = (fossil_total * p.get("Coal", 0.0),
                              fossil_total * p.get("Natural gas", 0.0),
                              fossil_total * p.get("Oil", 0.0))
        else:                                  # no fuel detail → leave as gas
            coal, gas, oil = 0.0, fossil_total, 0.0
        by_src = {"Hydro": float(b.get("Hydro", 0.0)), "Nuclear": float(b.get("Nuclear", 0.0)),
                  "Wind": float(b.get("Wind", 0.0)), "Solar": float(b.get("Solar", 0.0)),
                  "Biomass": float(b.get("Biomass", 0.0)),
                  "Natural gas": gas, "Oil": oil, "Coal": coal}
        total = sum(by_src.values())
        if total <= 0:
            continue
        for src, val in by_src.items():
            rows.append({"province": prov, "source": src,
                         "generation_mwh": val, "share": val / total * 100})
    g = pd.DataFrame(rows)

    out_path = DATA_DIR / "environment" / "statcan_provincial_electricity.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    g.to_csv(out_path, index=False)
    save_metadata(out_path, df=g, latest_observation_date=str(months[-1]),
        source="Statistics Canada", source_table="25-10-0015-01, 25-10-0084-01",
        frequency="annual", unit="% of provincial electricity generation",
        transformations=[f"base mix 25-10-0015-01 latest 12 months ({months[0]}–{months[-1]}); "
                         f"fossil split into Coal/Natural gas/Oil by 25-10-0084-01 fuel shares ({fyear})"])
    logger.info(f"  saved {len(g)} rows -> {out_path.name}")
    return g


if __name__ == "__main__":
    fetch_population_quarterly()
    fetch_population_components()
    fetch_cpi()
