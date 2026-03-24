"""
Orchestrator: fetch all data sources, clean, and save CSVs.
Run this script to update all data files.
"""

import sys
import logging

from pipeline.fetch_statcan import fetch_population_quarterly, fetch_population_components, fetch_cpi
from pipeline.fetch_oecd import (
    fetch_rd_expenditure, fetch_gdp_per_capita,
    fetch_labour_productivity, fetch_unemployment,
    fetch_co2_per_capita, fetch_co2_intensity, fetch_co2_indexed,
    fetch_renewables_share,
)
from pipeline.fetch_owid import fetch_energy_mix
from pipeline.fetch_whr import fetch_happiness

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run_all():
    results = {}

    # Statistics Canada
    logger.info("=" * 50)
    logger.info("STATISTICS CANADA")
    logger.info("=" * 50)

    try:
        df = fetch_population_quarterly()
        results["population_quarterly"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"population_quarterly: {e}")
        results["population_quarterly"] = "ERROR"

    try:
        df = fetch_population_components()
        results["population_components"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"population_components: {e}")
        results["population_components"] = "ERROR"

    try:
        df = fetch_cpi()
        results["cpi"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"cpi: {e}")
        results["cpi"] = "ERROR"

    # OECD
    logger.info("=" * 50)
    logger.info("OECD")
    logger.info("=" * 50)

    try:
        df = fetch_rd_expenditure()
        results["rd_expenditure"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"rd_expenditure: {e}")
        results["rd_expenditure"] = "ERROR"

    try:
        df = fetch_gdp_per_capita()
        results["gdp_per_capita"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"gdp_per_capita: {e}")
        results["gdp_per_capita"] = "ERROR"

    try:
        df = fetch_labour_productivity()
        results["labour_productivity"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"labour_productivity: {e}")
        results["labour_productivity"] = "ERROR"

    try:
        df = fetch_unemployment()
        results["unemployment"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"unemployment: {e}")
        results["unemployment"] = "ERROR"

    # OECD Green Growth (Environment)
    logger.info("=" * 50)
    logger.info("OECD GREEN GROWTH")
    logger.info("=" * 50)

    try:
        df = fetch_co2_per_capita()
        results["co2_per_capita"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"co2_per_capita: {e}")
        results["co2_per_capita"] = "ERROR"

    try:
        df = fetch_co2_intensity()
        results["co2_intensity"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"co2_intensity: {e}")
        results["co2_intensity"] = "ERROR"

    try:
        df = fetch_co2_indexed()
        results["co2_indexed"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"co2_indexed: {e}")
        results["co2_indexed"] = "ERROR"

    try:
        df = fetch_renewables_share()
        results["renewables_share"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"renewables_share: {e}")
        results["renewables_share"] = "ERROR"

    # OWID
    logger.info("=" * 50)
    logger.info("OUR WORLD IN DATA")
    logger.info("=" * 50)

    try:
        df = fetch_energy_mix()
        results["energy_mix"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"energy_mix: {e}")
        results["energy_mix"] = "ERROR"

    # World Happiness Report
    logger.info("=" * 50)
    logger.info("WORLD HAPPINESS REPORT")
    logger.info("=" * 50)

    try:
        df = fetch_happiness()
        results["happiness"] = "OK" if df is not None else "FAILED"
    except Exception as e:
        logger.error(f"happiness: {e}")
        results["happiness"] = "ERROR"

    # Summary
    logger.info("=" * 50)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 50)
    all_ok = True
    for name, status in results.items():
        logger.info(f"  {name}: {status}")
        if status != "OK":
            all_ok = False

    if not all_ok:
        logger.warning("Some datasets failed — site will use stale data for those.")
        sys.exit(1)
    else:
        logger.info("All datasets updated successfully.")


if __name__ == "__main__":
    run_all()
