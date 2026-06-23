"""
Fetchers for the **Innovation** page (data lands in data/science/, like BERD).

Bespoke OECD SDMX series the generic single-value fetcher can't handle:
  * triadic patents *per million population* — needs two MSTI series divided;
  * government support for business R&D split *direct vs tax* — two measures of
    the R&D-tax-incentive dataflow merged.

Both reuse `_fetch_oecd_csv` and emit the canonical peer shape
[country_code, country_name, year, <value>] so the chart builders work unchanged.
Descriptive peer comparisons — no scorecard valence.
"""
import logging

import pandas as pd

from pipeline.config import PEER_CODES, PEER_COUNTRIES, DATA_DIR
from pipeline.fetch_oecd import _fetch_oecd_csv
from pipeline.metadata import save_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUT_DIR = DATA_DIR / "science"
_MSTI = "OECD.STI.STP,DSD_MSTI@DF_MSTI,1.3"


def _tidy(df, col):
    """OECD SDMX CSV -> [country_code, year, <col>] (numeric)."""
    d = (df[["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]]
         .rename(columns={"REF_AREA": "country_code", "TIME_PERIOD": "year",
                          "OBS_VALUE": col}))
    d["year"] = d["year"].astype(int)
    d[col] = pd.to_numeric(d[col], errors="coerce")
    return d


def fetch_triadic_patents():
    """Triadic patent families per million population (OECD MSTI).

    Triadic families (a patent filed at the EPO, USPTO and JPO for the same
    invention) screen out low-value domestic-only filings, so this is a
    quality-controlled innovation-output measure. P_TRIAD ÷ population
    (TOT_POP is in thousands, so ÷ (pop/1000) = per million).
    """
    logger.info("fetch_triadic_patents (OECD MSTI P_TRIAD / TOT_POP)")
    codes = "+".join(PEER_CODES)
    pat = _fetch_oecd_csv(_MSTI, f"{codes}.A.P_TRIAD.PATN.._Z", start_period=2000)
    pop = _fetch_oecd_csv(_MSTI, f"{codes}.A.TOT_POP.PS.._Z", start_period=2000)
    if pat is None or pop is None or pat.empty or pop.empty:
        return None
    m = _tidy(pat, "patents").merge(_tidy(pop, "pop"), on=["country_code", "year"])
    m = m[m["country_code"].isin(PEER_CODES)].copy()
    m = m[(m["pop"] > 0) & m["patents"].notna()]
    m["patents_per_million"] = (m["patents"] / (m["pop"] / 1000.0)).round(2)
    m["country_name"] = m["country_code"].map(PEER_COUNTRIES)
    out = (m[["country_code", "country_name", "year", "patents_per_million"]]
           .dropna().sort_values(["country_code", "year"]).reset_index(drop=True))
    if out.empty:
        return None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "oecd_triadic_patents.csv"
    out.to_csv(path, index=False)
    save_metadata(path, df=out, date_column="year", source="OECD",
                  source_table="OECD MSTI (triadic patent families; population)",
                  frequency="annual", unit="patents per million population",
                  transformations=["P_TRIAD / (TOT_POP/1000); 17 OECD peers"])
    logger.info(f"  saved {len(out)} rows -> {path.name}")
    return out


def fetch_rd_tax_support():
    """Government support for business R&D, % of GDP — direct funding vs tax
    incentives (OECD R&D Tax Incentive indicators, DSD_RDTAX).

    `DF` = direct government funding of BERD; `DF_GTARD` = the cost of R&D tax
    incentives (e.g. Canada's SR&ED). Canada is unusual for leaning on tax
    incentives more than direct grants. A country reporting only one type is
    treated as ~zero of the other (the OECD's own convention for this series).
    """
    logger.info("fetch_rd_tax_support (OECD DSD_RDTAX direct + tax)")
    codes = "+".join(PEER_CODES)
    flow = "OECD.STI.STP,DSD_RDTAX@DF_RDTAX,1.0"
    direct = _fetch_oecd_csv(flow, f"{codes}.A.DF.PT_B1GQ._Z._Z", start_period=2000)
    tax = _fetch_oecd_csv(flow, f"{codes}.A.DF_GTARD.PT_B1GQ._Z._Z", start_period=2000)
    if direct is None or tax is None or direct.empty or tax.empty:
        return None
    m = _tidy(direct, "direct").merge(_tidy(tax, "tax"),
                                      on=["country_code", "year"], how="outer")
    m = m[m["country_code"].isin(PEER_CODES)].copy()
    m["direct"] = m["direct"].fillna(0.0)
    m["tax"] = m["tax"].fillna(0.0)
    m["total"] = (m["direct"] + m["tax"]).round(4)
    m = m[m["total"] > 0]
    m["country_name"] = m["country_code"].map(PEER_COUNTRIES)
    out = (m[["country_code", "country_name", "year", "direct", "tax", "total"]]
           .sort_values(["country_code", "year"]).reset_index(drop=True))
    if out.empty:
        return None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "oecd_rd_support.csv"
    out.to_csv(path, index=False)
    save_metadata(path, df=out, date_column="year", source="OECD",
                  source_table="OECD R&D Tax Incentive indicators (DSD_RDTAX)",
                  frequency="annual", unit="% of GDP",
                  transformations=["direct (DF) + tax incentives (DF_GTARD), % of GDP; 17 OECD peers"])
    logger.info(f"  saved {len(out)} rows -> {path.name}")
    return out
