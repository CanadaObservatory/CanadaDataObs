"""
Orchestrator: iterate the indicator registry, fetch each dataset, save CSVs.

    python -m pipeline.run_pipeline

Dispatch is driven by Indicator.source (see pipeline/config.py):
  "oecd"    -> fetch_oecd_indicator       (generic SDMX)
  "statcan" -> fetch_statcan_indicator    (generic single-series table)
  "custom"  -> a bespoke function named by Indicator.fetch_fn

Robustness: each indicator is isolated. If a fetch returns empty / errors but a
previous CSV exists on disk, that CSV is preserved and the indicator is marked
STALE (the site keeps showing the last good data). The run only exits non-zero
on a hard failure — a dataset with no data and no prior CSV.
"""

import sys
import logging

from pipeline.config import INDICATORS
from pipeline.fetch_oecd import fetch_oecd_indicator
from pipeline.fetch_statcan import (
    fetch_statcan_indicator,
    fetch_population_quarterly, fetch_population_components, fetch_cpi,
    fetch_provincial_electricity, fetch_tuition, fetch_tuition_by_field,
    fetch_trade_us,
)
from pipeline.fetch_owid import fetch_energy_mix, fetch_consumption_co2
from pipeline.fetch_whr import fetch_happiness
from pipeline.fetch_worldbank import fetch_worldbank_indicator
from pipeline.fetch_geography import fetch_wildfire, fetch_sea_ice
from pipeline.fetch_environment import fetch_ghg, fetch_ghg_by_sector
from pipeline.fetch_government import (
    fetch_govt_employment_by_level, fetch_public_sector_composition,
    fetch_fps_population, fetch_fps_by_department, fetch_fps_demographics,
    fetch_fps_executive, fetch_federal_finance_longrun, fetch_federal_expense_by_type,
    fetch_govt_spending_by_function, fetch_federal_spending_by_object,
    fetch_federal_spending_by_dept,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Bespoke fetchers referenced by Indicator.fetch_fn (source="custom").
CUSTOM_FETCHERS = {
    "fetch_population_quarterly": fetch_population_quarterly,
    "fetch_population_components": fetch_population_components,
    "fetch_cpi": fetch_cpi,
    "fetch_energy_mix": fetch_energy_mix,
    "fetch_consumption_co2": fetch_consumption_co2,
    "fetch_happiness": fetch_happiness,
    "fetch_provincial_electricity": fetch_provincial_electricity,
    "fetch_tuition": fetch_tuition,
    "fetch_tuition_by_field": fetch_tuition_by_field,
    "fetch_trade_us": fetch_trade_us,
    "fetch_wildfire": fetch_wildfire,
    "fetch_sea_ice": fetch_sea_ice,
    "fetch_ghg": fetch_ghg,
    "fetch_ghg_by_sector": fetch_ghg_by_sector,
    # Government (workforce + federal spending)
    "fetch_govt_employment_by_level": fetch_govt_employment_by_level,
    "fetch_public_sector_composition": fetch_public_sector_composition,
    "fetch_fps_population": fetch_fps_population,
    "fetch_fps_by_department": fetch_fps_by_department,
    "fetch_fps_demographics": fetch_fps_demographics,
    "fetch_fps_executive": fetch_fps_executive,
    "fetch_federal_finance_longrun": fetch_federal_finance_longrun,
    "fetch_federal_expense_by_type": fetch_federal_expense_by_type,
    "fetch_govt_spending_by_function": fetch_govt_spending_by_function,
    "fetch_federal_spending_by_object": fetch_federal_spending_by_object,
    "fetch_federal_spending_by_dept": fetch_federal_spending_by_dept,
}


def _run_one(ind):
    if ind.source == "oecd":
        return fetch_oecd_indicator(ind)
    if ind.source == "statcan":
        return fetch_statcan_indicator(ind)
    if ind.source == "worldbank":
        return fetch_worldbank_indicator(ind)
    if ind.source == "custom":
        return CUSTOM_FETCHERS[ind.fetch_fn]()
    raise ValueError(f"Unknown source '{ind.source}' for indicator {ind.id}")


def run_all():
    results = {}
    for ind in INDICATORS:
        out_path = ind.out_path
        try:
            df = _run_one(ind)
            if df is None or len(df) == 0:
                if out_path.exists():
                    logger.warning(f"{ind.id}: empty fetch — keeping existing CSV (STALE)")
                    results[ind.id] = "STALE"
                else:
                    logger.error(f"{ind.id}: empty fetch and no prior CSV (FAILED)")
                    results[ind.id] = "FAILED"
            else:
                results[ind.id] = "OK"
        except Exception as e:
            logger.error(f"{ind.id}: {e}")
            results[ind.id] = "STALE" if out_path.exists() else "ERROR"

    # Summary
    logger.info("=" * 56)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 56)
    for name, status in results.items():
        logger.info(f"  {status:7s} {name}")
    counts = {}
    for s in results.values():
        counts[s] = counts.get(s, 0) + 1
    logger.info(f"  totals: {counts}")

    stale = [n for n, s in results.items() if s == "STALE"]
    if stale:
        logger.warning(f"{len(stale)} dataset(s) kept stale (empty fetch): {stale}")

    # Hard failure only when a dataset has no data at all (no prior CSV).
    hard_fail = [n for n, s in results.items() if s in ("FAILED", "ERROR")]
    if hard_fail:
        logger.error(f"Hard failures (no data, no prior CSV): {hard_fail}")
        sys.exit(1)
    logger.info("Pipeline complete.")


if __name__ == "__main__":
    run_all()
