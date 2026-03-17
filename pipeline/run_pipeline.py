"""
Orchestrator: fetch all data sources, clean, and save CSVs.
Run this script to update all data files.
"""

import sys
import logging

from pipeline.fetch_statcan import fetch_population_quarterly, fetch_population_components, fetch_cpi
from pipeline.fetch_oecd import fetch_rd_expenditure, fetch_gdp_per_capita

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
